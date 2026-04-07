"""
DRF Serializers for the stock API.

Provides serializers for stock levels, movements, operations,
and stock takes.
"""

from decimal import Decimal

from rest_framework import serializers

from apps.inventory.stock.models.stock_level import StockLevel
from apps.inventory.stock.models.stock_movement import StockMovement
from apps.inventory.stock.models.stock_take import StockTake
from apps.inventory.stock.models.stock_take_item import StockTakeItem


# ═══════════════════════════════════════════════════════════════════
# Task 73–74: StockLevel Serializers
# ═══════════════════════════════════════════════════════════════════


class StockLevelListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for stock level list views."""

    product_name = serializers.CharField(source="product.name", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)
    available_quantity = serializers.SerializerMethodField()
    stock_status = serializers.SerializerMethodField()

    class Meta:
        model = StockLevel
        fields = [
            "id",
            "product",
            "product_name",
            "product_sku",
            "variant",
            "warehouse",
            "warehouse_name",
            "location",
            "quantity",
            "reserved_quantity",
            "available_quantity",
            "incoming_quantity",
            "in_transit_quantity",
            "reorder_point",
            "stock_status",
            "cost_per_unit",
            "last_stock_update",
            "last_counted_date",
            "abc_classification",
        ]
        read_only_fields = fields

    def get_available_quantity(self, obj):
        return obj.available_quantity

    def get_stock_status(self, obj):
        return obj.get_stock_status_display()


class StockLevelDetailSerializer(StockLevelListSerializer):
    """Full serializer for stock level detail view."""

    projected_quantity = serializers.SerializerMethodField()
    stock_value = serializers.SerializerMethodField()

    class Meta(StockLevelListSerializer.Meta):
        fields = StockLevelListSerializer.Meta.fields + [
            "projected_quantity",
            "stock_value",
        ]

    def get_projected_quantity(self, obj):
        return obj.projected_quantity

    def get_stock_value(self, obj):
        return str(obj.stock_value)


# ═══════════════════════════════════════════════════════════════════
# Task 75: StockMovement Serializers
# ═══════════════════════════════════════════════════════════════════


class StockMovementSerializer(serializers.ModelSerializer):
    """Serializer for stock movement records."""

    product_name = serializers.CharField(source="product.name", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    from_warehouse_name = serializers.CharField(
        source="from_warehouse.name", read_only=True, default=None,
    )
    to_warehouse_name = serializers.CharField(
        source="to_warehouse.name", read_only=True, default=None,
    )
    movement_type_display = serializers.CharField(
        source="get_movement_type_display", read_only=True,
    )
    reason_display = serializers.CharField(
        source="get_reason_display", read_only=True,
    )
    created_by_name = serializers.SerializerMethodField()
    total_cost = serializers.SerializerMethodField()

    class Meta:
        model = StockMovement
        fields = [
            "id",
            "product",
            "product_name",
            "product_sku",
            "variant",
            "movement_type",
            "movement_type_display",
            "quantity",
            "reason",
            "reason_display",
            "from_warehouse",
            "from_warehouse_name",
            "to_warehouse",
            "to_warehouse_name",
            "from_location",
            "to_location",
            "cost_per_unit",
            "total_cost",
            "reference_type",
            "reference_id",
            "reference_number",
            "notes",
            "is_reversed",
            "transit_status",
            "dispatched_at",
            "received_at",
            "reserved_until",
            "movement_date",
            "created_by",
            "created_by_name",
            "created_on",
        ]
        read_only_fields = fields

    def get_created_by_name(self, obj):
        if obj.created_by:
            return str(obj.created_by)
        return None

    def get_total_cost(self, obj):
        return str(obj.total_cost)


# ═══════════════════════════════════════════════════════════════════
# Task 76: Stock Operation Serializers (write)
# ═══════════════════════════════════════════════════════════════════


class StockInSerializer(serializers.Serializer):
    """Serializer for stock-in operations."""

    product_id = serializers.UUIDField()
    variant_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    warehouse_id = serializers.UUIDField()
    location_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    quantity = serializers.DecimalField(max_digits=15, decimal_places=3, min_value=Decimal("0.001"))
    cost_per_unit = serializers.DecimalField(
        max_digits=15, decimal_places=3, required=False, allow_null=True, default=None,
    )
    reason = serializers.CharField(required=False, default="purchase")
    reference_type = serializers.CharField(required=False, default="")
    reference_id = serializers.CharField(required=False, default="")
    notes = serializers.CharField(required=False, default="", allow_blank=True)


class StockOutSerializer(serializers.Serializer):
    """Serializer for stock-out operations."""

    product_id = serializers.UUIDField()
    variant_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    warehouse_id = serializers.UUIDField()
    location_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    quantity = serializers.DecimalField(max_digits=15, decimal_places=3, min_value=Decimal("0.001"))
    reason = serializers.CharField(required=False, default="sale")
    reference_type = serializers.CharField(required=False, default="")
    reference_id = serializers.CharField(required=False, default="")
    notes = serializers.CharField(required=False, default="", allow_blank=True)


class StockTransferSerializer(serializers.Serializer):
    """Serializer for stock transfer operations."""

    product_id = serializers.UUIDField()
    variant_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    from_warehouse_id = serializers.UUIDField()
    to_warehouse_id = serializers.UUIDField()
    from_location_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    to_location_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    quantity = serializers.DecimalField(max_digits=15, decimal_places=3, min_value=Decimal("0.001"))
    notes = serializers.CharField(required=False, default="", allow_blank=True)

    def validate(self, data):
        if data["from_warehouse_id"] == data["to_warehouse_id"]:
            from_loc = data.get("from_location_id")
            to_loc = data.get("to_location_id")
            if from_loc == to_loc:
                raise serializers.ValidationError(
                    "Source and destination must differ."
                )
        return data


class StockAdjustmentWriteSerializer(serializers.Serializer):
    """Serializer for stock adjustment operations."""

    product_id = serializers.UUIDField()
    variant_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    warehouse_id = serializers.UUIDField()
    location_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    quantity = serializers.DecimalField(max_digits=15, decimal_places=3, min_value=Decimal("0.001"))
    direction = serializers.ChoiceField(choices=["up", "down"])
    reason = serializers.CharField()
    cost_per_unit = serializers.DecimalField(
        max_digits=15, decimal_places=3, required=False, allow_null=True, default=None,
    )
    reference_id = serializers.CharField(required=False, default="")
    notes = serializers.CharField(required=False, default="", allow_blank=True)


# ═══════════════════════════════════════════════════════════════════
# Task 77: StockTake Serializers
# ═══════════════════════════════════════════════════════════════════


class StockTakeItemSerializer(serializers.ModelSerializer):
    """Serializer for stock take items."""

    product_name = serializers.CharField(source="product.name", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    location_name = serializers.SerializerMethodField()
    variance_classification = serializers.SerializerMethodField()
    counted_by_name = serializers.SerializerMethodField()

    class Meta:
        model = StockTakeItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_sku",
            "variant",
            "location",
            "location_name",
            "expected_quantity",
            "counted_quantity",
            "system_quantity",
            "variance_quantity",
            "variance_percentage",
            "cost_per_unit",
            "expected_value",
            "counted_value",
            "variance_value",
            "status",
            "count_sequence",
            "is_locked",
            "requires_recount",
            "notes",
            "discrepancy_reason",
            "counted_by",
            "counted_by_name",
            "counted_at",
            "variance_classification",
            "item_approval_status",
            "item_approval_level",
            "item_approved_by",
            "item_approved_at",
            "item_rejection_reason",
        ]
        read_only_fields = fields

    def get_location_name(self, obj):
        return str(obj.location) if obj.location else None

    def get_variance_classification(self, obj):
        return obj.get_variance_classification()

    def get_counted_by_name(self, obj):
        return str(obj.counted_by) if obj.counted_by else None


class BlindStockTakeItemSerializer(serializers.ModelSerializer):
    """Item serializer for blind counts — hides expected quantities."""

    product_name = serializers.CharField(source="product.name", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    location_name = serializers.SerializerMethodField()

    class Meta:
        model = StockTakeItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_sku",
            "variant",
            "location",
            "location_name",
            "counted_quantity",
            "status",
            "count_sequence",
            "is_locked",
            "notes",
        ]
        read_only_fields = fields

    def get_location_name(self, obj):
        return str(obj.location) if obj.location else None


class StockTakeListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for stock take list views."""

    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)
    created_by_name = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = StockTake
        fields = [
            "id",
            "reference",
            "name",
            "warehouse",
            "warehouse_name",
            "status",
            "scope",
            "is_blind_count",
            "scheduled_date",
            "started_at",
            "completed_at",
            "total_items",
            "counted_items",
            "items_with_variance",
            "total_variance_value",
            "approval_status",
            "created_by",
            "created_by_name",
            "progress_percentage",
            "created_on",
        ]
        read_only_fields = fields

    def get_created_by_name(self, obj):
        return str(obj.created_by) if obj.created_by else None

    def get_progress_percentage(self, obj):
        return str(obj.progress_percentage)


class StockTakeDetailSerializer(StockTakeListSerializer):
    """Full serializer for stock take detail with nested items."""

    items = serializers.SerializerMethodField()

    class Meta(StockTakeListSerializer.Meta):
        fields = StockTakeListSerializer.Meta.fields + [
            "description",
            "cancelled_at",
            "completed_by",
            "approved_by",
            "items",
            "updated_on",
        ]

    def get_items(self, obj):
        items_qs = obj.items.select_related(
            "product", "variant", "location", "counted_by"
        ).order_by("count_sequence")

        if obj.is_blind_count and obj.status == "counting":
            return BlindStockTakeItemSerializer(items_qs, many=True).data
        return StockTakeItemSerializer(items_qs, many=True).data


class CreateStockTakeSerializer(serializers.Serializer):
    """Write serializer for creating a stock take."""

    warehouse_id = serializers.UUIDField()
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, default="", allow_blank=True)
    scope = serializers.ChoiceField(
        choices=["full", "partial", "cycle"], default="full",
    )
    is_blind_count = serializers.BooleanField(required=False, default=False)
    scheduled_date = serializers.DateField(required=False, allow_null=True, default=None)


# ═══════════════════════════════════════════════════════════════════
# Task 82: Bulk Count Serializer
# ═══════════════════════════════════════════════════════════════════


class CountEntrySerializer(serializers.Serializer):
    """Single count entry within a bulk count request."""

    item_id = serializers.UUIDField()
    counted_quantity = serializers.DecimalField(max_digits=15, decimal_places=3, min_value=Decimal("0"))
    notes = serializers.CharField(required=False, default="", allow_blank=True)


class BulkCountSerializer(serializers.Serializer):
    """Serializer for bulk count operations."""

    counts = CountEntrySerializer(many=True)

    def validate_counts(self, value):
        if not value:
            raise serializers.ValidationError("At least one count entry is required.")
        return value


# ═══════════════════════════════════════════════════════════════════
# Task 83: Availability Serializer
# ═══════════════════════════════════════════════════════════════════


class CheckAvailabilitySerializer(serializers.Serializer):
    """Serializer for multi-product availability check."""

    product_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        max_length=100,
    )
    warehouse_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        default=None,
    )


# ═══════════════════════════════════════════════════════════════════
# Task 55: StockLot Serializer
# ═══════════════════════════════════════════════════════════════════


class StockLotSerializer(serializers.ModelSerializer):
    """Serializer for stock lot / batch records."""

    product_name = serializers.CharField(source="product.name", read_only=True)
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)
    is_depleted = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    lot_value = serializers.SerializerMethodField()

    class Meta:
        from apps.inventory.stock.models.stock_lot import StockLot

        model = StockLot
        fields = [
            "id",
            "lot_number",
            "product",
            "product_name",
            "variant",
            "warehouse",
            "warehouse_name",
            "original_quantity",
            "remaining_quantity",
            "cost_per_unit",
            "received_date",
            "expiry_date",
            "status",
            "is_depleted",
            "is_expired",
            "lot_value",
            "created_on",
        ]
        read_only_fields = fields

    def get_lot_value(self, obj):
        return str(obj.lot_value)


# ═══════════════════════════════════════════════════════════════════
# Task 72: CycleCountSchedule Serializer
# ═══════════════════════════════════════════════════════════════════


class CycleCountScheduleSerializer(serializers.ModelSerializer):
    """Serializer for cycle count schedule records."""

    product_name = serializers.CharField(source="product.name", read_only=True)
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)
    is_due = serializers.BooleanField(read_only=True)
    days_until_due = serializers.IntegerField(read_only=True)

    class Meta:
        from apps.inventory.stock.models.cycle_count_schedule import CycleCountSchedule

        model = CycleCountSchedule
        fields = [
            "id",
            "product",
            "product_name",
            "variant",
            "warehouse",
            "warehouse_name",
            "abc_classification",
            "count_interval_days",
            "last_count_date",
            "next_count_date",
            "status",
            "is_due",
            "days_until_due",
            "last_stock_take",
            "created_on",
        ]
        read_only_fields = [
            "id", "product_name", "warehouse_name", "is_due",
            "days_until_due", "created_on",
        ]
