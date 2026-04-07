"""
Quote Line Item serializers.
"""

from rest_framework import serializers

from apps.quotes.models import QuoteLineItem


class QuoteLineItemSerializer(serializers.ModelSerializer):
    """Full serializer for create / update / detail of line items."""

    get_subtotal = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    product_display = serializers.SerializerMethodField()

    class Meta:
        model = QuoteLineItem
        fields = [
            "id",
            "quote",
            "position",
            "product",
            "variant",
            "product_display",
            "product_name",
            "custom_description",
            "custom_sku",
            "quantity",
            "unit_of_measure",
            "unit_price",
            "original_price",
            "cost_price",
            "discount_type",
            "discount_value",
            "discount_amount",
            "is_taxable",
            "tax_rate",
            "tax_amount",
            "line_total",
            "notes",
            "get_subtotal",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "discount_amount",
            "tax_amount",
            "line_total",
            "created_at",
            "updated_at",
        ]

    def get_product_display(self, obj):
        """Return a display string for the product/variant."""
        if obj.product:
            name = str(obj.product)
            if obj.variant:
                name += f" — {obj.variant}"
            return name
        return obj.product_name or obj.custom_description or ""

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be positive.")
        return value

    def validate_unit_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Unit price cannot be negative.")
        return value


class QuoteLineItemListSerializer(serializers.ModelSerializer):
    """Compact serializer for listing line items within a quote."""

    class Meta:
        model = QuoteLineItem
        fields = [
            "id",
            "position",
            "product_name",
            "custom_description",
            "quantity",
            "unit_price",
            "discount_amount",
            "tax_amount",
            "line_total",
        ]
        read_only_fields = fields
