"""
DRF ViewSets for the stock API.

Provides endpoints for stock levels, movements, operations,
and stock takes.
"""

from decimal import Decimal

from django.db.models import Sum, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet, ViewSet

from apps.inventory.stock.exceptions import StockOperationError
from apps.inventory.stock.models.stock_level import StockLevel
from apps.inventory.stock.models.stock_movement import StockMovement
from apps.inventory.stock.models.stock_take import StockTake
from apps.inventory.stock.models.stock_take_item import StockTakeItem
from apps.inventory.stock.services import (
    StockAdjustmentService,
    StockService,
    StockTakeService,
)

from .serializers import (
    BlindStockTakeItemSerializer,
    BulkCountSerializer,
    CheckAvailabilitySerializer,
    CreateStockTakeSerializer,
    StockAdjustmentWriteSerializer,
    StockInSerializer,
    StockLevelDetailSerializer,
    StockLevelListSerializer,
    StockMovementSerializer,
    StockOutSerializer,
    StockTakeDetailSerializer,
    StockTakeItemSerializer,
    StockTakeListSerializer,
    StockTransferSerializer,
)


# ═══════════════════════════════════════════════════════════════════
# Task 78: StockLevelViewSet
# ═══════════════════════════════════════════════════════════════════


class StockLevelViewSet(ReadOnlyModelViewSet):
    """
    ReadOnly ViewSet for stock levels.

    Endpoints:
        GET /stock-levels/             — list
        GET /stock-levels/{id}/        — detail
        GET /stock-levels/low_stock/   — low stock items
        GET /stock-levels/out_of_stock/ — out of stock items
        POST /stock-levels/check-availability/ — multi-product check
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["product", "warehouse", "location"]
    search_fields = ["product__name", "product__sku", "warehouse__name"]
    ordering_fields = ["quantity", "cost_per_unit", "last_stock_update"]
    ordering = ["-quantity"]

    def get_queryset(self):
        return StockLevel.objects.select_related(
            "product", "variant", "warehouse", "location",
        ).order_by("-quantity")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return StockLevelDetailSerializer
        return StockLevelListSerializer

    @action(detail=False, methods=["get"], url_path="low-stock")
    def low_stock(self, request):
        """Return items where available quantity is at or below reorder point."""
        qs = self.get_queryset().filter(
            quantity__gt=0,
        ).extra(
            where=["(quantity - reserved_quantity) <= reorder_point"],
        )
        # Fallback: filter in Python if extra() is not desired
        qs = self.get_queryset()
        low = [
            sl for sl in qs
            if sl.available_quantity > 0 and sl.available_quantity <= sl.reorder_point
        ]
        serializer = StockLevelListSerializer(low, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="out-of-stock")
    def out_of_stock(self, request):
        """Return items with zero or negative available quantity."""
        qs = self.get_queryset().filter(quantity__lte=0)
        serializer = StockLevelListSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="check-availability")
    def check_availability(self, request):
        """Check availability for multiple products (Task 83)."""
        serializer = CheckAvailabilitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_ids = serializer.validated_data["product_ids"]
        warehouse_ids = serializer.validated_data.get("warehouse_ids")

        qs = StockLevel.objects.filter(
            product_id__in=product_ids,
        ).select_related("product", "warehouse")

        if warehouse_ids:
            qs = qs.filter(warehouse_id__in=warehouse_ids)

        result = {}
        for sl in qs:
            pid = str(sl.product_id)
            if pid not in result:
                result[pid] = {
                    "product_id": pid,
                    "product_name": sl.product.name,
                    "product_sku": sl.product.sku,
                    "total_quantity": Decimal("0"),
                    "total_available": Decimal("0"),
                    "total_reserved": Decimal("0"),
                    "total_incoming": Decimal("0"),
                    "by_warehouse": [],
                }
            entry = result[pid]
            entry["total_quantity"] += sl.quantity
            entry["total_available"] += sl.available_quantity
            entry["total_reserved"] += sl.reserved_quantity
            entry["total_incoming"] += sl.incoming_quantity
            entry["by_warehouse"].append({
                "warehouse_id": str(sl.warehouse_id),
                "warehouse_name": sl.warehouse.name,
                "quantity": str(sl.quantity),
                "available": str(sl.available_quantity),
                "reserved": str(sl.reserved_quantity),
                "incoming": str(sl.incoming_quantity),
            })

        # Convert decimals to strings for JSON
        for pid, data in result.items():
            data["total_quantity"] = str(data["total_quantity"])
            data["total_available"] = str(data["total_available"])
            data["total_reserved"] = str(data["total_reserved"])
            data["total_incoming"] = str(data["total_incoming"])

        return Response(list(result.values()))


# ═══════════════════════════════════════════════════════════════════
# Task 79: StockMovementViewSet
# ═══════════════════════════════════════════════════════════════════


class StockMovementViewSet(ReadOnlyModelViewSet):
    """
    ReadOnly ViewSet for stock movements.

    Endpoints:
        GET /stock-movements/                — list
        GET /stock-movements/{id}/           — detail
        GET /stock-movements/for-product/    — product history
        GET /stock-movements/summary/        — movement summary
    """

    permission_classes = [IsAuthenticated]
    serializer_class = StockMovementSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        "product",
        "movement_type",
        "reason",
        "from_warehouse",
        "to_warehouse",
        "reference_type",
    ]
    search_fields = ["product__name", "product__sku", "reference_number", "notes"]
    ordering_fields = ["movement_date", "quantity", "created_on"]
    ordering = ["-movement_date"]

    def get_queryset(self):
        return StockMovement.objects.select_related(
            "product",
            "variant",
            "from_warehouse",
            "to_warehouse",
            "created_by",
        ).order_by("-movement_date")

    @action(detail=False, methods=["get"], url_path="for-product")
    def for_product(self, request):
        """Get movement history for a specific product."""
        product_id = request.query_params.get("product_id")
        if not product_id:
            return Response(
                {"detail": "product_id query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        qs = self.get_queryset().filter(product_id=product_id)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request):
        """Aggregate movements by type for a date range (Task 84)."""
        from django.utils import timezone
        import datetime

        days = int(request.query_params.get("days", 30))
        start_date = timezone.now() - datetime.timedelta(days=days)
        warehouse_id = request.query_params.get("warehouse_id")

        qs = self.get_queryset().filter(movement_date__gte=start_date)
        if warehouse_id:
            qs = qs.filter(
                Q(from_warehouse_id=warehouse_id) | Q(to_warehouse_id=warehouse_id)
            )

        agg = qs.values("movement_type").annotate(
            total_quantity=Sum("quantity"),
        ).order_by("movement_type")

        return Response(list(agg))


# ═══════════════════════════════════════════════════════════════════
# Task 80: StockOperationViewSet
# ═══════════════════════════════════════════════════════════════════


def _resolve_objects(data):
    """Resolve UUID fields to model instances."""
    from apps.products.models import Product, ProductVariant
    from apps.inventory.warehouses.models import StorageLocation, Warehouse

    product = Product.objects.get(pk=data["product_id"])
    variant = None
    if data.get("variant_id"):
        variant = ProductVariant.objects.get(pk=data["variant_id"])

    warehouse = None
    if "warehouse_id" in data:
        warehouse = Warehouse.objects.get(pk=data["warehouse_id"])

    location = None
    if data.get("location_id"):
        location = StorageLocation.objects.get(pk=data["location_id"])

    return product, variant, warehouse, location


class StockOperationViewSet(ViewSet):
    """
    POST-only ViewSet for stock operations.

    Endpoints:
        POST /stock-operations/stock-in/    — receive stock
        POST /stock-operations/stock-out/   — dispatch stock
        POST /stock-operations/transfer/    — transfer between warehouses
        POST /stock-operations/adjust/      — adjust stock
    """

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"], url_path="stock-in")
    def stock_in(self, request):
        """Receive stock into a warehouse."""
        serializer = StockInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            product, variant, warehouse, location = _resolve_objects(data)
            svc = StockService(user=request.user, notes=data.get("notes", ""))
            result = svc.stock_in(
                product=product,
                quantity=data["quantity"],
                warehouse=warehouse,
                variant=variant,
                location=location,
                cost_per_unit=data.get("cost_per_unit"),
                reason=data.get("reason", "purchase"),
                reference_type=data.get("reference_type", ""),
                reference_id=data.get("reference_id", ""),
            )
            return Response(result.to_dict(), status=status.HTTP_201_CREATED)
        except StockOperationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            return Response(
                {"detail": f"Operation failed: {exc}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["post"], url_path="stock-out")
    def stock_out(self, request):
        """Dispatch stock from a warehouse."""
        serializer = StockOutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            product, variant, warehouse, location = _resolve_objects(data)
            svc = StockService(user=request.user, notes=data.get("notes", ""))
            result = svc.stock_out(
                product=product,
                quantity=data["quantity"],
                warehouse=warehouse,
                variant=variant,
                location=location,
                reason=data.get("reason", "sale"),
                reference_type=data.get("reference_type", ""),
                reference_id=data.get("reference_id", ""),
            )
            return Response(result.to_dict(), status=status.HTTP_200_OK)
        except StockOperationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="transfer")
    def transfer(self, request):
        """Transfer stock between warehouses."""
        serializer = StockTransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            from apps.products.models import Product, ProductVariant
            from apps.inventory.warehouses.models import StorageLocation, Warehouse

            product = Product.objects.get(pk=data["product_id"])
            variant = None
            if data.get("variant_id"):
                variant = ProductVariant.objects.get(pk=data["variant_id"])
            from_wh = Warehouse.objects.get(pk=data["from_warehouse_id"])
            to_wh = Warehouse.objects.get(pk=data["to_warehouse_id"])
            from_loc = None
            to_loc = None
            if data.get("from_location_id"):
                from_loc = StorageLocation.objects.get(pk=data["from_location_id"])
            if data.get("to_location_id"):
                to_loc = StorageLocation.objects.get(pk=data["to_location_id"])

            svc = StockService(user=request.user, notes=data.get("notes", ""))
            result = svc.transfer(
                product=product,
                quantity=data["quantity"],
                from_warehouse=from_wh,
                to_warehouse=to_wh,
                variant=variant,
                from_location=from_loc,
                to_location=to_loc,
            )
            return Response(result.to_dict(), status=status.HTTP_200_OK)
        except StockOperationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="adjust")
    def adjust(self, request):
        """Manually adjust stock level."""
        serializer = StockAdjustmentWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            product, variant, warehouse, location = _resolve_objects(data)
            svc = StockAdjustmentService(user=request.user, notes=data.get("notes", ""))

            if data["direction"] == "up":
                result = svc.adjust_up(
                    product=product,
                    quantity=data["quantity"],
                    warehouse=warehouse,
                    reason=data["reason"],
                    variant=variant,
                    location=location,
                    cost_per_unit=data.get("cost_per_unit"),
                    reference_id=data.get("reference_id", ""),
                    notes=data.get("notes", ""),
                )
            else:
                result = svc.adjust_down(
                    product=product,
                    quantity=data["quantity"],
                    warehouse=warehouse,
                    reason=data["reason"],
                    variant=variant,
                    location=location,
                    reference_id=data.get("reference_id", ""),
                    notes=data.get("notes", ""),
                )
            return Response(result.to_dict(), status=status.HTTP_200_OK)
        except StockOperationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="dispatch/(?P<movement_pk>[^/.]+)")
    def dispatch_transfer(self, request, movement_pk=None):
        """Mark a transfer movement as dispatched (Task 43)."""
        try:
            svc = StockService(user=request.user)
            result = svc.mark_as_dispatched(movement_pk, user=request.user)
            return Response(result.to_dict(), status=status.HTTP_200_OK)
        except StockOperationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="receive/(?P<movement_pk>[^/.]+)")
    def receive_transfer(self, request, movement_pk=None):
        """Mark a transfer movement as received (Task 43)."""
        try:
            svc = StockService(user=request.user)
            result = svc.mark_as_received(movement_pk, user=request.user)
            return Response(result.to_dict(), status=status.HTTP_200_OK)
        except StockOperationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="release-by-movement/(?P<movement_pk>[^/.]+)")
    def release_by_movement(self, request, movement_pk=None):
        """Release reserved stock by movement ID (Task 45)."""
        try:
            svc = StockService(user=request.user)
            result = svc.release_by_movement(movement_pk)
            return Response(result.to_dict(), status=status.HTTP_200_OK)
        except StockOperationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="commit-by-movement/(?P<movement_pk>[^/.]+)")
    def commit_by_movement(self, request, movement_pk=None):
        """Commit reserved stock by movement ID (Task 46)."""
        try:
            svc = StockService(user=request.user)
            result = svc.commit_by_movement(movement_pk)
            return Response(result.to_dict(), status=status.HTTP_200_OK)
        except StockOperationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


# ═══════════════════════════════════════════════════════════════════
# Task 81: StockTakeViewSet
# ═══════════════════════════════════════════════════════════════════


class StockTakeViewSet(ModelViewSet):
    """
    ViewSet for managing stock takes.

    Endpoints:
        GET    /stock-takes/                 — list
        POST   /stock-takes/                 — create
        GET    /stock-takes/{id}/            — detail
        DELETE /stock-takes/{id}/            — delete (draft only)
        POST   /stock-takes/{id}/start/      — start counting
        POST   /stock-takes/{id}/count/      — record single count
        POST   /stock-takes/{id}/bulk-count/ — record multiple counts
        POST   /stock-takes/{id}/submit/     — submit for review
        POST   /stock-takes/{id}/approve/    — approve
        POST   /stock-takes/{id}/complete/   — complete
        POST   /stock-takes/{id}/cancel/     — cancel
        GET    /stock-takes/{id}/items/      — list items
        GET    /stock-takes/{id}/variances/  — items with variance
        GET    /stock-takes/{id}/report/     — report data
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["warehouse", "status", "scope", "approval_status"]
    search_fields = ["reference", "name", "warehouse__name"]
    ordering_fields = ["created_on", "started_at", "reference"]
    ordering = ["-created_on"]

    def get_queryset(self):
        return StockTake.objects.select_related(
            "warehouse", "created_by",
        ).order_by("-created_on")

    def get_serializer_class(self):
        if self.action == "list":
            return StockTakeListSerializer
        if self.action == "create":
            return CreateStockTakeSerializer
        return StockTakeDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = CreateStockTakeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            from apps.inventory.warehouses.models import Warehouse

            warehouse = Warehouse.objects.get(pk=data["warehouse_id"])
            svc = StockTakeService(user=request.user)
            result = svc.create_stock_take(
                warehouse=warehouse,
                name=data["name"],
                scope=data.get("scope", "full"),
                is_blind_count=data.get("is_blind_count", False),
                scheduled_date=data.get("scheduled_date"),
                description=data.get("description", ""),
            )
            return Response(result.to_dict(), status=status.HTTP_201_CREATED)
        except StockOperationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        stock_take = self.get_object()
        if stock_take.status != "draft":
            return Response(
                {"detail": "Only draft stock takes can be deleted."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        stock_take.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        """Start counting — populate items from StockLevel."""
        try:
            svc = StockTakeService(user=request.user)
            result = svc.start_stock_take(pk)
            return Response(result.to_dict())
        except StockOperationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def count(self, request, pk=None):
        """Record a single item count."""
        item_id = request.data.get("item_id")
        counted_quantity = request.data.get("counted_quantity")
        notes = request.data.get("notes", "")

        if not item_id or counted_quantity is None:
            return Response(
                {"detail": "item_id and counted_quantity are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            svc = StockTakeService(user=request.user)
            result = svc.record_count(
                stock_take_item_id=item_id,
                counted_quantity=counted_quantity,
                user=request.user,
                notes=notes,
            )
            return Response(result.to_dict())
        except StockOperationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="bulk-count")
    def bulk_count(self, request, pk=None):
        """Record counts for multiple items (Task 82)."""
        serializer = BulkCountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            svc = StockTakeService(user=request.user)
            result = svc.record_counts_bulk(
                counts_list=serializer.validated_data["counts"],
                user=request.user,
            )
            return Response(result.to_dict())
        except StockOperationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        """Submit for review."""
        try:
            svc = StockTakeService(user=request.user)
            result = svc.submit_for_review(pk)
            return Response(result.to_dict())
        except StockOperationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Approve stock take."""
        try:
            svc = StockTakeService(user=request.user)
            result = svc.approve_stock_take(pk, approver=request.user)
            return Response(result.to_dict())
        except StockOperationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """Complete stock take and create adjustments."""
        force = request.data.get("force", False)
        try:
            svc = StockTakeService(user=request.user)
            result = svc.complete_stock_take(pk, user=request.user, force=force)
            return Response(result.to_dict())
        except StockOperationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancel stock take."""
        try:
            svc = StockTakeService(user=request.user)
            result = svc.cancel_stock_take(pk)
            return Response(result.to_dict())
        except StockOperationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"])
    def items(self, request, pk=None):
        """List all items in a stock take."""
        stock_take = self.get_object()
        items_qs = stock_take.items.select_related(
            "product", "variant", "location", "counted_by",
        ).order_by("count_sequence")

        # Use blind serializer if applicable
        if stock_take.is_blind_count and stock_take.status == "counting":
            serializer = BlindStockTakeItemSerializer(items_qs, many=True)
        else:
            serializer = StockTakeItemSerializer(items_qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def variances(self, request, pk=None):
        """Return only items with variance."""
        stock_take = self.get_object()
        items_qs = stock_take.items.exclude(
            variance_quantity=Decimal("0"),
        ).filter(
            counted_quantity__isnull=False,
        ).select_related(
            "product", "variant", "location", "counted_by",
        ).order_by("-variance_value")

        serializer = StockTakeItemSerializer(items_qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def report(self, request, pk=None):
        """Generate report data for stock take (Task 70)."""
        try:
            svc = StockTakeService(user=request.user)
            data = svc.get_report_data(pk)
            return Response(data)
        except StockOperationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"])
    def report_csv(self, request, pk=None):
        """Export stock take report as CSV."""
        from django.http import HttpResponse as DjangoHttpResponse

        try:
            svc = StockTakeService(user=request.user)
            csv_content = svc.export_report_csv(pk)
            response = DjangoHttpResponse(csv_content, content_type="text/csv")
            response["Content-Disposition"] = f'attachment; filename="stock_take_{pk}.csv"'
            return response
        except StockOperationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"])
    def report_excel(self, request, pk=None):
        """Export stock take report as Excel."""
        from django.http import HttpResponse as DjangoHttpResponse

        try:
            svc = StockTakeService(user=request.user)
            excel_bytes = svc.export_report_excel(pk)
            response = DjangoHttpResponse(
                excel_bytes,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Content-Disposition"] = f'attachment; filename="stock_take_{pk}.xlsx"'
            return response
        except StockOperationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"])
    def report_pdf(self, request, pk=None):
        """Export stock take report as PDF."""
        from django.http import HttpResponse as DjangoHttpResponse

        try:
            svc = StockTakeService(user=request.user)
            pdf_bytes = svc.export_report_pdf(pk)
            content_type = "application/pdf"
            if isinstance(pdf_bytes, bytes) and pdf_bytes.startswith(b"<html"):
                content_type = "text/html"
            response = DjangoHttpResponse(pdf_bytes, content_type=content_type)
            response["Content-Disposition"] = f'attachment; filename="stock_take_{pk}.pdf"'
            return response
        except StockOperationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def determine_item_approvals(self, request, pk=None):
        """Determine per-item approval levels (Task 69)."""
        try:
            svc = StockTakeService(user=request.user)
            result = svc.determine_item_approvals(pk)
            return Response(result.to_dict())
        except StockOperationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="approve-item/(?P<item_pk>[^/.]+)")
    def approve_item(self, request, item_pk=None):
        """Approve a specific stock take item variance (Task 69)."""
        try:
            svc = StockTakeService(user=request.user)
            result = svc.approve_variance(
                item_pk,
                approver=request.user,
                notes=request.data.get("notes", ""),
            )
            return Response(result.to_dict())
        except StockOperationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="reject-item/(?P<item_pk>[^/.]+)")
    def reject_item(self, request, item_pk=None):
        """Reject a specific stock take item variance (Task 69)."""
        try:
            svc = StockTakeService(user=request.user)
            result = svc.reject_variance(
                item_pk,
                approver=request.user,
                reason=request.data.get("reason", ""),
            )
            return Response(result.to_dict())
        except StockOperationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
