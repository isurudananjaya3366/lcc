"""Serializers for ReorderSuggestion model."""

from django.utils import timezone
from rest_framework import serializers

from apps.inventory.alerts.models import ReorderSuggestion

from .config import ProductSummarySerializer, WarehouseSummarySerializer


class SupplierSummarySerializer(serializers.Serializer):
    """Minimal supplier info for nesting."""

    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(read_only=True)
    code = serializers.CharField(read_only=True, required=False)
    is_active = serializers.BooleanField(read_only=True, required=False)


class ReorderSuggestionSerializer(serializers.ModelSerializer):
    """
    Full serializer for ReorderSuggestion with conversion capabilities.

    Includes velocity data and conversion status.
    """

    product = ProductSummarySerializer(read_only=True)
    warehouse = WarehouseSummarySerializer(read_only=True, allow_null=True)
    suggested_supplier = SupplierSummarySerializer(read_only=True, allow_null=True)

    urgency_display = serializers.CharField(
        source="get_urgency_display", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )

    estimated_stockout_date = serializers.SerializerMethodField()
    can_convert = serializers.SerializerMethodField()
    days_since_created = serializers.SerializerMethodField()

    class Meta:
        model = ReorderSuggestion
        fields = [
            "id",
            "product",
            "warehouse",
            "suggested_qty",
            "minimum_order_qty",
            "current_stock",
            "suggested_supplier",
            "urgency",
            "urgency_display",
            "status",
            "status_display",
            "days_until_stockout",
            "estimated_stockout_date",
            "daily_velocity",
            "safety_stock",
            "eoq",
            "reorder_point",
            "estimated_cost",
            "unit_cost",
            "notes",
            "calculation_details",
            "auto_generated",
            "converted_po_id",
            "status_changed_at",
            "dismissal_reason",
            "can_convert",
            "days_since_created",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "daily_velocity",
            "safety_stock",
            "eoq",
            "reorder_point",
            "calculation_details",
            "auto_generated",
            "converted_po_id",
            "status_changed_at",
            "created_at",
            "updated_at",
        ]

    def get_estimated_stockout_date(self, obj):
        d = obj.days_until_stockout
        if d is None or not obj.daily_velocity:
            return None
        from datetime import timedelta

        return (timezone.now() + timedelta(days=float(d))).date().isoformat()

    def get_can_convert(self, obj):
        can, _ = obj.can_convert()
        return can

    def get_days_since_created(self, obj):
        return (timezone.now() - obj.created_at).days

    def validate(self, data):
        suggested = data.get("suggested_qty")
        minimum = data.get("minimum_order_qty")
        if suggested and minimum and suggested < minimum:
            raise serializers.ValidationError(
                "Suggested quantity must be >= minimum order quantity"
            )
        return data


class ReorderSuggestionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for suggestion lists."""

    product_name = serializers.CharField(source="product.name", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    supplier_name = serializers.CharField(
        source="suggested_supplier.name", read_only=True, default=None
    )

    urgency_display = serializers.CharField(
        source="get_urgency_display", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )

    class Meta:
        model = ReorderSuggestion
        fields = [
            "id",
            "product_name",
            "product_sku",
            "supplier_name",
            "suggested_qty",
            "current_stock",
            "urgency",
            "urgency_display",
            "status",
            "status_display",
            "days_until_stockout",
            "estimated_cost",
            "created_at",
        ]
        read_only_fields = fields
