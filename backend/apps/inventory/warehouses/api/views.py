"""
DRF ViewSets for the warehouse & locations API.

Provides CRUD endpoints plus custom actions for dashboard,
location tree, barcode lookup, and bulk creation.
"""

import time

from django.db import transaction
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from apps.inventory.warehouses.models import (
    BarcodeScan,
    DefaultWarehouseConfig,
    POSWarehouseMapping,
    StorageLocation,
    TransferRoute,
    Warehouse,
    WarehouseCapacity,
    WarehouseZone,
)
from apps.inventory.warehouses.services import (
    BarcodeLookup,
    WarehouseDashboard,
)

from .serializers import (
    BulkLocationCreateSerializer,
    LocationTreeSerializer,
    StorageLocationListSerializer,
    StorageLocationSerializer,
    TransferRouteSerializer,
    WarehouseCapacitySerializer,
    WarehouseCreateUpdateSerializer,
    WarehouseListSerializer,
    WarehouseSerializer,
    WarehouseZoneSerializer,
)


# ═══════════════════════════════════════════════════════════════════
# Task 73: WarehouseViewSet
# ═══════════════════════════════════════════════════════════════════


class WarehouseViewSet(ModelViewSet):
    """
    ViewSet for warehouses.

    Endpoints
    ---------
    GET    /warehouses/                     — list
    POST   /warehouses/                     — create
    GET    /warehouses/{id}/                — retrieve
    PUT    /warehouses/{id}/                — update
    PATCH  /warehouses/{id}/                — partial_update
    DELETE /warehouses/{id}/                — destroy
    POST   /warehouses/{id}/set_default/    — set as default
    GET    /warehouses/{id}/dashboard/      — warehouse stats
    GET    /warehouses/{id}/capacity/       — capacity report
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["code", "city", "district", "status", "warehouse_type", "is_default"]
    search_fields = ["code", "name", "city", "district"]
    ordering_fields = ["code", "name", "created_on"]
    ordering = ["name"]

    def get_queryset(self):
        return (
            Warehouse.objects.all()
            .select_related("capacity")
            .annotate(_location_count=Count("storage_locations"))
        )

    def get_serializer_class(self):
        if self.action == "list":
            return WarehouseListSerializer
        if self.action in ("create", "update", "partial_update"):
            return WarehouseCreateUpdateSerializer
        return WarehouseSerializer

    # ── Custom actions ──────────────────────────────────────────

    @action(detail=True, methods=["post"], url_path="set_default")
    def set_default(self, request, pk=None):
        """Set this warehouse as the tenant default."""
        warehouse = self.get_object()
        warehouse.set_as_default()
        return Response(
            {"detail": f"'{warehouse.name}' is now the default warehouse."},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get"], url_path="dashboard")
    def dashboard(self, request, pk=None):
        """Return warehouse dashboard statistics."""
        warehouse = self.get_object()
        dashboard_svc = WarehouseDashboard()
        stats = dashboard_svc.get_warehouse_stats(warehouse)
        return Response(stats)

    @action(detail=True, methods=["get"], url_path="capacity")
    def capacity(self, request, pk=None):
        """Return capacity report for the warehouse."""
        warehouse = self.get_object()
        cap = getattr(warehouse, "capacity", None)
        if cap is None:
            return Response(
                {"detail": "No capacity data configured for this warehouse."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = WarehouseCapacitySerializer(cap)
        return Response(serializer.data)


# ═══════════════════════════════════════════════════════════════════
# Task 74 + 75 + 76 + 77: StorageLocationViewSet
# ═══════════════════════════════════════════════════════════════════


class StorageLocationViewSet(ModelViewSet):
    """
    ViewSet for storage locations.

    Endpoints
    ---------
    GET    /locations/                          — list
    POST   /locations/                          — create
    GET    /locations/{id}/                     — retrieve
    PUT    /locations/{id}/                     — update
    PATCH  /locations/{id}/                     — partial_update
    DELETE /locations/{id}/                     — destroy
    GET    /locations/{id}/children/            — direct children
    GET    /locations/{id}/ancestors/           — parent chain
    GET    /locations/{id}/descendants/         — nested children
    GET    /locations/{id}/siblings/            — siblings
    GET    /locations/tree/                     — full tree
    GET    /locations/barcode_lookup/{barcode}/ — lookup by barcode
    POST   /locations/bulk_create/              — bulk create
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        "warehouse",
        "location_type",
        "parent",
        "is_active",
        "is_pickable",
        "is_receivable",
        "zone",
    ]
    search_fields = ["code", "name", "barcode"]
    ordering_fields = ["code", "name", "created_on"]
    ordering = ["code"]

    def get_queryset(self):
        return StorageLocation.objects.select_related(
            "warehouse", "parent", "zone"
        ).annotate(_children_count=Count("children"))

    def get_serializer_class(self):
        if self.action == "list":
            return StorageLocationListSerializer
        if self.action == "tree":
            return LocationTreeSerializer
        return StorageLocationSerializer

    # ── Hierarchy actions ───────────────────────────────────────

    @action(detail=True, methods=["get"])
    def children(self, request, pk=None):
        """Return direct children of this location."""
        location = self.get_object()
        qs = location.children.filter(is_active=True).order_by("code")
        serializer = StorageLocationListSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def ancestors(self, request, pk=None):
        """Return the chain of ancestors up to the root."""
        location = self.get_object()
        ancestors_list = []
        current = location.parent
        while current:
            ancestors_list.append(current)
            current = current.parent
        serializer = StorageLocationListSerializer(ancestors_list, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def descendants(self, request, pk=None):
        """Return all descendants (nested children) up to max_depth."""
        location = self.get_object()
        max_depth = min(int(request.query_params.get("depth", 10)), 10)
        result = []
        self._collect_descendants(location, result, 0, max_depth)
        serializer = StorageLocationListSerializer(result, many=True)
        return Response(serializer.data)

    def _collect_descendants(self, location, result, current_depth, max_depth):
        if current_depth >= max_depth:
            return
        for child in location.children.filter(is_active=True).order_by("code"):
            result.append(child)
            self._collect_descendants(child, result, current_depth + 1, max_depth)

    @action(detail=True, methods=["get"])
    def siblings(self, request, pk=None):
        """Return locations sharing the same parent."""
        location = self.get_object()
        qs = (
            StorageLocation.objects.filter(
                warehouse=location.warehouse,
                parent=location.parent,
                is_active=True,
            )
            .exclude(pk=location.pk)
            .order_by("code")
        )
        serializer = StorageLocationListSerializer(qs, many=True)
        return Response(serializer.data)

    # ── Task 75: Tree endpoint ──────────────────────────────────

    @action(detail=False, methods=["get"])
    def tree(self, request):
        """
        Return the full location hierarchy tree for a warehouse.

        Query params:
            warehouse (uuid, required) — warehouse ID
            location_type (str, optional) — filter root nodes
            max_depth (int, optional) — recursion depth (1-10)
        """
        warehouse_id = request.query_params.get("warehouse")
        if not warehouse_id:
            return Response(
                {"detail": "The 'warehouse' query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        max_depth = min(int(request.query_params.get("max_depth", 10)), 10)
        roots = StorageLocation.objects.filter(
            warehouse_id=warehouse_id,
            parent__isnull=True,
            is_active=True,
        ).order_by("code")

        location_type = request.query_params.get("location_type")
        if location_type:
            roots = roots.filter(location_type=location_type)

        ctx = {**self.get_serializer_context(), "max_depth": max_depth}
        serializer = LocationTreeSerializer(roots, many=True, context=ctx)
        return Response(serializer.data)

    # ── Task 76: Barcode lookup ─────────────────────────────────

    @action(
        detail=False,
        methods=["get"],
        url_path=r"barcode_lookup/(?P<barcode>[^/.]+)",
    )
    def barcode_lookup(self, request, barcode=None):
        """Look up a storage location by its barcode."""
        start = time.monotonic()
        lookup = BarcodeLookup()
        location = lookup.lookup_location(
            barcode,
            user=request.user,
            scan_type="INQUIRY",
        )
        if location is None:
            return Response(
                {"detail": "Location not found for this barcode."},
                status=status.HTTP_404_NOT_FOUND,
            )
        elapsed_ms = round((time.monotonic() - start) * 1000)
        serializer = StorageLocationSerializer(location)
        return Response(
            {
                "location": serializer.data,
                "metadata": {
                    "scan_timestamp": request._request.META.get(
                        "REQUEST_TIME", None
                    ),
                    "lookup_time_ms": elapsed_ms,
                },
            }
        )

    # ── Task 77: Bulk create ────────────────────────────────────

    @action(detail=False, methods=["post"], url_path="bulk_create")
    def bulk_create(self, request):
        """Create multiple storage locations at once (max 100)."""
        serializer = BulkLocationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        warehouse = Warehouse.objects.get(pk=data["warehouse_id"])
        parent = None
        if data.get("parent_id"):
            parent = StorageLocation.objects.get(pk=data["parent_id"])

        created = []
        with transaction.atomic():
            for i in range(data["count"]):
                number = data["start_number"] + i
                name = data["name_template"].replace("{number}", str(number))
                loc = StorageLocation.objects.create(
                    warehouse=warehouse,
                    parent=parent,
                    location_type=data["location_type"],
                    name=name,
                    code=f"{warehouse.code}-{name}".replace(" ", "-").upper(),
                )
                created.append(loc)

        result = StorageLocationListSerializer(created, many=True)
        return Response(result.data, status=status.HTTP_201_CREATED)


# ═══════════════════════════════════════════════════════════════════
# Additional ViewSets for zones, routes, and capacity
# ═══════════════════════════════════════════════════════════════════


class WarehouseZoneViewSet(ModelViewSet):
    """CRUD for warehouse zones."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["warehouse", "purpose", "is_active"]
    search_fields = ["code", "name"]
    ordering_fields = ["code", "name"]
    ordering = ["code"]
    serializer_class = WarehouseZoneSerializer

    def get_queryset(self):
        return WarehouseZone.objects.select_related("warehouse")


class TransferRouteViewSet(ModelViewSet):
    """CRUD for transfer routes."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        "source_warehouse",
        "destination_warehouse",
        "is_active",
        "is_preferred",
    ]
    search_fields = [
        "source_warehouse__code",
        "destination_warehouse__code",
        "primary_carrier",
    ]
    ordering_fields = ["transit_days", "estimated_cost"]
    ordering = ["source_warehouse"]
    serializer_class = TransferRouteSerializer

    def get_queryset(self):
        return TransferRoute.objects.select_related(
            "source_warehouse", "destination_warehouse"
        )


class WarehouseCapacityViewSet(ReadOnlyModelViewSet):
    """Read-only viewset for warehouse capacity."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["warehouse"]
    serializer_class = WarehouseCapacitySerializer

    def get_queryset(self):
        return WarehouseCapacity.objects.select_related("warehouse")
