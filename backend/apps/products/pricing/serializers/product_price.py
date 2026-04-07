"""
ProductPrice and VariantPrice serializers.
"""

from decimal import Decimal

from rest_framework import serializers

from ..models import ProductPrice, VariantPrice
from ..services.price_resolution import PriceResolutionService
from ..utils import format_lkr


class ProductPriceSerializer(serializers.ModelSerializer):
    """Read serializer for ProductPrice with computed pricing fields."""

    base_price_formatted = serializers.SerializerMethodField()
    sale_price_formatted = serializers.SerializerMethodField()
    cost_formatted = serializers.SerializerMethodField()
    effective_price = serializers.SerializerMethodField()
    effective_price_formatted = serializers.SerializerMethodField()
    discount_amount = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()
    has_discount = serializers.SerializerMethodField()
    has_sale_price = serializers.SerializerMethodField()
    has_tiered_pricing = serializers.SerializerMethodField()
    profit_margin = serializers.SerializerMethodField()
    profit_margin_percentage = serializers.SerializerMethodField()

    class Meta:
        model = ProductPrice
        fields = [
            "id",
            "product",
            "base_price",
            "base_price_formatted",
            "sale_price",
            "sale_price_formatted",
            "sale_price_start",
            "sale_price_end",
            "wholesale_price",
            "cost_price",
            "cost_formatted",
            "is_taxable",
            "is_tax_inclusive",
            "tax_class",
            "effective_price",
            "effective_price_formatted",
            "discount_amount",
            "discount_percentage",
            "has_discount",
            "has_sale_price",
            "has_tiered_pricing",
            "profit_margin",
            "profit_margin_percentage",
        ]
        read_only_fields = [
            "id",
            "effective_price",
            "effective_price_formatted",
            "discount_amount",
            "discount_percentage",
            "has_discount",
            "has_sale_price",
            "has_tiered_pricing",
            "profit_margin",
            "profit_margin_percentage",
        ]

    def _get_resolution(self, obj):
        """Cached price resolution for the request lifecycle."""
        cache_key = f"_resolution_{obj.pk}"
        if not hasattr(self, cache_key):
            try:
                result = PriceResolutionService.get_effective_price(obj.product)
            except Exception:
                result = {
                    "price": obj.base_price,
                    "price_type": "base",
                    "discount_amount": Decimal("0"),
                    "discount_percentage": Decimal("0"),
                }
            setattr(self, cache_key, result)
        return getattr(self, cache_key)

    def get_base_price_formatted(self, obj):
        return format_lkr(obj.base_price)

    def get_sale_price_formatted(self, obj):
        return format_lkr(obj.sale_price) if obj.sale_price else None

    def get_cost_formatted(self, obj):
        return format_lkr(obj.cost_price) if obj.cost_price else None

    def get_effective_price(self, obj):
        return str(self._get_resolution(obj)["price"])

    def get_effective_price_formatted(self, obj):
        return format_lkr(self._get_resolution(obj)["price"])

    def get_discount_amount(self, obj):
        return str(self._get_resolution(obj)["discount_amount"])

    def get_discount_percentage(self, obj):
        return str(self._get_resolution(obj)["discount_percentage"])

    def get_has_discount(self, obj):
        return self._get_resolution(obj)["discount_amount"] > 0

    def get_has_sale_price(self, obj):
        return obj.is_on_sale

    def get_has_tiered_pricing(self, obj):
        return obj.product.tiered_prices.filter(is_active=True).exists()

    def get_profit_margin(self, obj):
        m = obj.profit_margin
        return str(m) if m is not None else None

    def get_profit_margin_percentage(self, obj):
        m = obj.markup_percentage
        return str(m) if m is not None else None


class ProductPriceUpdateSerializer(serializers.ModelSerializer):
    """Write serializer for creating/updating ProductPrice."""

    class Meta:
        model = ProductPrice
        fields = [
            "product",
            "base_price",
            "sale_price",
            "sale_price_start",
            "sale_price_end",
            "wholesale_price",
            "cost_price",
            "is_taxable",
            "is_tax_inclusive",
            "tax_class",
        ]

    def validate(self, data):
        base = data.get("base_price", getattr(self.instance, "base_price", None))
        sale = data.get("sale_price")
        if sale is not None and base is not None and sale >= base:
            raise serializers.ValidationError({"sale_price": "Sale price must be less than base price."})
        cost = data.get("cost_price")
        if cost is not None and cost < 0:
            raise serializers.ValidationError({"cost_price": "Cost cannot be negative."})
        return data


class VariantPriceSerializer(serializers.ModelSerializer):
    """Read serializer for VariantPrice with inheritance indicators."""

    price_formatted = serializers.SerializerMethodField()
    effective_price = serializers.SerializerMethodField()
    effective_price_formatted = serializers.SerializerMethodField()
    inherits_price = serializers.SerializerMethodField()

    class Meta:
        model = VariantPrice
        fields = [
            "id",
            "variant",
            "use_product_price",
            "base_price",
            "price_formatted",
            "sale_price",
            "wholesale_price",
            "cost_price",
            "price_adjustment_type",
            "price_adjustment_value",
            "effective_price",
            "effective_price_formatted",
            "inherits_price",
        ]
        read_only_fields = ["id", "effective_price", "effective_price_formatted", "inherits_price"]

    def get_price_formatted(self, obj):
        return format_lkr(obj.get_effective_price())

    def get_effective_price(self, obj):
        return str(obj.get_effective_price())

    def get_effective_price_formatted(self, obj):
        return format_lkr(obj.get_effective_price())

    def get_inherits_price(self, obj):
        return obj.use_product_price
