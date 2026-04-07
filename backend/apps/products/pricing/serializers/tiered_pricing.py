"""
TieredPricing serializers.
"""

from rest_framework import serializers

from ..models import TieredPricing, VariantTieredPricing
from ..utils import format_lkr


class TieredPricingSerializer(serializers.ModelSerializer):
    price_per_unit_formatted = serializers.SerializerMethodField()
    quantity_range_display = serializers.SerializerMethodField()
    savings_vs_base = serializers.SerializerMethodField()
    savings_percentage = serializers.SerializerMethodField()

    class Meta:
        model = TieredPricing
        fields = [
            "id",
            "product",
            "name",
            "min_quantity",
            "max_quantity",
            "tier_price",
            "tier_type",
            "price_per_unit_formatted",
            "quantity_range_display",
            "savings_vs_base",
            "savings_percentage",
            "is_active",
        ]
        read_only_fields = ["id", "savings_vs_base", "savings_percentage"]

    def get_price_per_unit_formatted(self, obj):
        return format_lkr(obj.tier_price)

    def get_quantity_range_display(self, obj):
        return obj.get_tier_range()

    def get_savings_vs_base(self, obj):
        pp = getattr(obj.product, "product_price", None)
        if pp:
            return str(pp.base_price - obj.tier_price)
        return None

    def get_savings_percentage(self, obj):
        pp = getattr(obj.product, "product_price", None)
        if pp and pp.base_price:
            return str(obj.get_discount_percentage(pp.base_price))
        return None

    def validate(self, data):
        min_q = data.get("min_quantity")
        max_q = data.get("max_quantity")
        if max_q is not None and min_q is not None and max_q <= min_q:
            raise serializers.ValidationError({"max_quantity": "Must be greater than min_quantity."})
        price = data.get("tier_price")
        if price is not None and price <= 0:
            raise serializers.ValidationError({"tier_price": "Must be positive."})
        return data


class VariantTieredPricingSerializer(serializers.ModelSerializer):
    price_per_unit_formatted = serializers.SerializerMethodField()
    quantity_range_display = serializers.SerializerMethodField()

    class Meta:
        model = VariantTieredPricing
        fields = [
            "id",
            "variant",
            "name",
            "min_quantity",
            "max_quantity",
            "tier_price",
            "tier_type",
            "price_per_unit_formatted",
            "quantity_range_display",
            "is_active",
        ]
        read_only_fields = ["id"]

    def get_price_per_unit_formatted(self, obj):
        return format_lkr(obj.tier_price)

    def get_quantity_range_display(self, obj):
        return obj.get_tier_range()
