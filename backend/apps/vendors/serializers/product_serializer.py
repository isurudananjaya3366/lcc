"""Vendor product serializer."""

from rest_framework import serializers
from apps.vendors.models import VendorProduct


class VendorProductSerializer(serializers.ModelSerializer):
    """Serializer for VendorProduct."""
    product_name = serializers.SerializerMethodField()
    product_sku = serializers.SerializerMethodField()
    total_cost = serializers.SerializerMethodField()

    class Meta:
        model = VendorProduct
        fields = [
            "id", "product", "product_name", "product_sku",
            "vendor_sku", "vendor_product_name", "description",
            "unit_cost", "bulk_price", "bulk_qty", "currency",
            "min_order_qty", "order_multiple", "lead_time_days",
            "is_active", "is_preferred",
            "last_ordered_date", "last_cost", "notes",
            "total_cost",
        ]
        read_only_fields = ["id"]

    def get_product_name(self, obj) -> str:
        return str(obj.product) if obj.product_id else ""

    def get_product_sku(self, obj) -> str:
        if obj.product_id and hasattr(obj.product, "sku"):
            return obj.product.sku or ""
        return ""

    def get_total_cost(self, obj) -> float | None:
        if obj.unit_cost and obj.min_order_qty:
            return float(obj.unit_cost * obj.min_order_qty)
        return None
