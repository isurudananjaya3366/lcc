"""
DRF Serializers for the warehouse & locations API.

Provides serializers for warehouses, storage locations, zones,
transfer routes, and capacity with different strategies:
- List serializers: Lightweight for list views
- Detail serializers: Complete info with nested relations
- Tree serializers: Recursive nested structures (locations)
"""

from rest_framework import serializers

from apps.inventory.warehouses.constants import LOCATION_PARENT_RULES
from apps.inventory.warehouses.models import (
    DefaultWarehouseConfig,
    POSWarehouseMapping,
    StorageLocation,
    TransferRoute,
    Warehouse,
    WarehouseCapacity,
    WarehouseZone,
)


# ═══════════════════════════════════════════════════════════════════
# Task 67: WarehouseSerializer
# ═══════════════════════════════════════════════════════════════════


class WarehouseListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for warehouse list views."""

    class Meta:
        model = Warehouse
        fields = [
            "id",
            "name",
            "code",
            "warehouse_type",
            "status",
            "city",
            "district",
            "is_default",
        ]
        read_only_fields = ["id"]


class WarehouseSerializer(serializers.ModelSerializer):
    """
    Full serializer for Warehouse with calculated fields.

    Includes address display, location count, and capacity summary.
    """

    address_display = serializers.SerializerMethodField()
    location_count = serializers.SerializerMethodField()
    capacity_summary = serializers.SerializerMethodField()
    operating_hours_display = serializers.SerializerMethodField()

    class Meta:
        model = Warehouse
        fields = [
            "id",
            "name",
            "code",
            "warehouse_type",
            "status",
            "address_line_1",
            "address_line_2",
            "city",
            "district",
            "postal_code",
            "phone",
            "email",
            "manager_name",
            "is_default",
            "opens_at",
            "closes_at",
            "latitude",
            "longitude",
            "address_display",
            "location_count",
            "capacity_summary",
            "operating_hours_display",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "created_on",
            "updated_on",
            "address_display",
            "location_count",
            "capacity_summary",
            "operating_hours_display",
        ]

    def get_address_display(self, obj) -> str:
        parts = [
            p
            for p in [
                obj.address_line_1,
                obj.address_line_2,
                obj.city,
                obj.district,
                obj.postal_code,
            ]
            if p
        ]
        return ", ".join(parts)

    def get_location_count(self, obj) -> int:
        return getattr(obj, "_location_count", obj.storage_locations.count())

    def get_capacity_summary(self, obj) -> dict:
        cap = getattr(obj, "capacity", None)
        if cap is None:
            return {"used": 0, "total": 0, "percentage": 0.0}
        return {
            "used": cap.current_item_count,
            "total": cap.max_item_capacity,
            "percentage": cap.utilization_percentage,
        }

    def get_operating_hours_display(self, obj) -> str:
        if obj.opens_at and obj.closes_at:
            return f"{obj.opens_at.strftime('%H:%M')} - {obj.closes_at.strftime('%H:%M')}"
        return "Not set"

    def validate_is_default(self, value):
        """Ensure only one default warehouse per tenant."""
        if value:
            qs = Warehouse.objects.filter(is_default=True)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    "Another warehouse is already set as default. "
                    "Unset it first or use the set-default endpoint."
                )
        return value


class WarehouseCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating / updating warehouses."""

    class Meta:
        model = Warehouse
        fields = [
            "name",
            "code",
            "warehouse_type",
            "status",
            "address_line_1",
            "address_line_2",
            "city",
            "district",
            "postal_code",
            "phone",
            "email",
            "manager_name",
            "is_default",
            "opens_at",
            "closes_at",
            "latitude",
            "longitude",
        ]

    def validate_is_default(self, value):
        if value:
            qs = Warehouse.objects.filter(is_default=True)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    "Another warehouse is already set as default."
                )
        return value


# ═══════════════════════════════════════════════════════════════════
# Task 68: StorageLocationSerializer
# ═══════════════════════════════════════════════════════════════════


class StorageLocationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for location list views."""

    warehouse_name = serializers.CharField(
        source="warehouse.name", read_only=True
    )

    class Meta:
        model = StorageLocation
        fields = [
            "id",
            "code",
            "name",
            "location_type",
            "warehouse",
            "warehouse_name",
            "parent",
            "barcode",
            "is_active",
            "is_pickable",
            "is_receivable",
        ]
        read_only_fields = ["id"]


class StorageLocationSerializer(serializers.ModelSerializer):
    """
    Full serializer for StorageLocation with hierarchy info.

    Includes depth, path, and children count.
    """

    warehouse_name = serializers.CharField(
        source="warehouse.name", read_only=True
    )
    parent_code = serializers.CharField(
        source="parent.code", read_only=True, default=None
    )
    location_path = serializers.SerializerMethodField()
    children_count = serializers.SerializerMethodField()
    depth = serializers.SerializerMethodField()
    capacity_percentage = serializers.SerializerMethodField()
    has_stock = serializers.SerializerMethodField()

    class Meta:
        model = StorageLocation
        fields = [
            "id",
            "warehouse",
            "warehouse_name",
            "parent",
            "parent_code",
            "zone",
            "name",
            "code",
            "location_type",
            "barcode",
            "description",
            "max_weight",
            "max_volume",
            "max_items",
            "max_pallets",
            "capacity_notes",
            "is_active",
            "is_pickable",
            "is_receivable",
            "utilization_status",
            "last_activity_at",
            "location_path",
            "children_count",
            "depth",
            "capacity_percentage",
            "has_stock",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "barcode",
            "created_on",
            "updated_on",
            "location_path",
            "children_count",
            "depth",
            "capacity_percentage",
            "has_stock",
        ]

    def get_location_path(self, obj) -> str:
        return obj.location_path

    def get_children_count(self, obj) -> int:
        return getattr(obj, "_children_count", obj.children.count())

    def get_depth(self, obj) -> int:
        return obj.depth

    def get_capacity_percentage(self, obj) -> float:
        if obj.max_items and obj.max_items > 0:
            # Placeholder — actual stock count integration in later SP
            return 0.0
        return 0.0

    def get_has_stock(self, obj) -> bool:
        """Placeholder — returns True when utilization is not EMPTY."""
        return obj.utilization_status != "empty"

    def validate(self, attrs):
        parent = attrs.get("parent", getattr(self.instance, "parent", None))
        warehouse = attrs.get(
            "warehouse", getattr(self.instance, "warehouse", None)
        )
        location_type = attrs.get(
            "location_type",
            getattr(self.instance, "location_type", None),
        )

        # Parent must belong to same warehouse
        if parent and warehouse and parent.warehouse_id != warehouse.pk:
            raise serializers.ValidationError(
                {"parent": "Parent must belong to the same warehouse."}
            )

        # Hierarchy validation
        if parent and location_type:
            allowed = LOCATION_PARENT_RULES.get(location_type)
            if allowed and parent.location_type not in allowed:
                raise serializers.ValidationError(
                    {
                        "parent": (
                            f"A {location_type} cannot be a child of "
                            f"{parent.location_type}."
                        )
                    }
                )

        # Prevent circular reference
        if parent and self.instance:
            ancestor = parent
            while ancestor:
                if ancestor.pk == self.instance.pk:
                    raise serializers.ValidationError(
                        {"parent": "Circular parent reference detected."}
                    )
                ancestor = ancestor.parent

        return attrs


# ═══════════════════════════════════════════════════════════════════
# Task 69: LocationTreeSerializer
# ═══════════════════════════════════════════════════════════════════


class LocationTreeSerializer(serializers.ModelSerializer):
    """
    Recursive serializer for hierarchical tree view.

    Renders location tree with nested children arrays.
    """

    children = serializers.SerializerMethodField()
    is_leaf = serializers.SerializerMethodField()

    class Meta:
        model = StorageLocation
        fields = [
            "id",
            "code",
            "name",
            "location_type",
            "barcode",
            "is_active",
            "is_leaf",
            "children",
        ]

    def get_children(self, obj):
        max_depth = self.context.get("max_depth", 10)
        current_depth = self.context.get("_current_depth", 0)
        if current_depth >= max_depth:
            return []
        children_qs = obj.children.filter(is_active=True).order_by("code")
        ctx = {**self.context, "_current_depth": current_depth + 1}
        return LocationTreeSerializer(children_qs, many=True, context=ctx).data

    def get_is_leaf(self, obj) -> bool:
        return not obj.children.exists()


# ═══════════════════════════════════════════════════════════════════
# Task 70: WarehouseZoneSerializer
# ═══════════════════════════════════════════════════════════════════


class WarehouseZoneSerializer(serializers.ModelSerializer):
    """Serializer for WarehouseZone with location count."""

    warehouse_code = serializers.CharField(
        source="warehouse.code", read_only=True
    )
    location_count = serializers.SerializerMethodField()

    class Meta:
        model = WarehouseZone
        fields = [
            "id",
            "warehouse",
            "warehouse_code",
            "name",
            "code",
            "purpose",
            "description",
            "is_active",
            "location_count",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "created_on", "updated_on"]

    def get_location_count(self, obj) -> int:
        return obj.storage_locations.count()


# ═══════════════════════════════════════════════════════════════════
# Task 71: TransferRouteSerializer
# ═══════════════════════════════════════════════════════════════════


class TransferRouteSerializer(serializers.ModelSerializer):
    """Serializer for TransferRoute with cost info."""

    source_name = serializers.CharField(
        source="source_warehouse.name", read_only=True
    )
    destination_name = serializers.CharField(
        source="destination_warehouse.name", read_only=True
    )

    class Meta:
        model = TransferRoute
        fields = [
            "id",
            "source_warehouse",
            "source_name",
            "destination_warehouse",
            "destination_name",
            "transit_days",
            "distance_km",
            "primary_carrier",
            "notes",
            "is_preferred",
            "is_active",
            "estimated_cost",
            "cost_per_kg",
            "cost_per_m3",
            "minimum_cost",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "created_on", "updated_on"]

    def validate(self, attrs):
        source = attrs.get(
            "source_warehouse",
            getattr(self.instance, "source_warehouse", None),
        )
        dest = attrs.get(
            "destination_warehouse",
            getattr(self.instance, "destination_warehouse", None),
        )
        if source and dest and source == dest:
            raise serializers.ValidationError(
                "Source and destination warehouses must differ."
            )
        return attrs


# ═══════════════════════════════════════════════════════════════════
# Task 72: WarehouseCapacitySerializer
# ═══════════════════════════════════════════════════════════════════


class WarehouseCapacitySerializer(serializers.ModelSerializer):
    """Serializer for WarehouseCapacity with utilization metrics."""

    warehouse_code = serializers.CharField(
        source="warehouse.code", read_only=True
    )
    capacity_percentage = serializers.SerializerMethodField()
    available_capacity = serializers.SerializerMethodField()
    utilization_status = serializers.SerializerMethodField()
    needs_alert = serializers.SerializerMethodField()

    class Meta:
        model = WarehouseCapacity
        fields = [
            "id",
            "warehouse",
            "warehouse_code",
            "max_item_capacity",
            "current_item_count",
            "max_weight_capacity",
            "current_weight",
            "max_volume_capacity",
            "current_volume",
            "last_calculated",
            "capacity_percentage",
            "available_capacity",
            "utilization_status",
            "needs_alert",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "last_calculated",
            "created_on",
            "updated_on",
            "capacity_percentage",
            "available_capacity",
            "utilization_status",
            "needs_alert",
        ]

    def get_capacity_percentage(self, obj) -> float:
        return obj.utilization_percentage

    def get_available_capacity(self, obj) -> int:
        return max(0, obj.max_item_capacity - obj.current_item_count)

    def get_utilization_status(self, obj) -> str:
        pct = obj.utilization_percentage
        if pct < 50:
            return "LOW"
        if pct < 75:
            return "MEDIUM"
        if pct < 90:
            return "HIGH"
        return "CRITICAL"

    def get_needs_alert(self, obj) -> bool:
        return obj.utilization_percentage >= 90


# ═══════════════════════════════════════════════════════════════════
# Bulk location creation serializer (Task 77)
# ═══════════════════════════════════════════════════════════════════


class BulkLocationCreateSerializer(serializers.Serializer):
    """Validates payload for bulk location creation."""

    warehouse_id = serializers.UUIDField()
    parent_id = serializers.UUIDField(required=False, allow_null=True)
    location_type = serializers.CharField(max_length=10)
    name_template = serializers.CharField(max_length=100)
    count = serializers.IntegerField(min_value=1, max_value=100)
    start_number = serializers.IntegerField(min_value=0, default=1)

    def validate_warehouse_id(self, value):
        try:
            Warehouse.objects.get(pk=value)
        except Warehouse.DoesNotExist:
            raise serializers.ValidationError("Warehouse not found.")
        return value

    def validate_parent_id(self, value):
        if value is None:
            return value
        try:
            StorageLocation.objects.get(pk=value)
        except StorageLocation.DoesNotExist:
            raise serializers.ValidationError("Parent location not found.")
        return value
