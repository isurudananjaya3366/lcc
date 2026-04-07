"""
Order line item serializers (Task 82).
"""

from rest_framework import serializers

from apps.orders.models import OrderLineItem


class OrderLineItemSerializer(serializers.ModelSerializer):
    """Full serializer for order line item create/update/detail."""

    product_display = serializers.SerializerMethodField()

    class Meta:
        model = OrderLineItem
        fields = [
            "id",
            "order",
            "position",
            "product",
            "variant",
            "product_display",
            "item_name",
            "item_sku",
            "item_description",
            "item_category",
            "item_image_url",
            "quantity_ordered",
            "quantity_fulfilled",
            "quantity_returned",
            "quantity_cancelled",
            "unit_price",
            "original_price",
            "cost_price",
            "currency",
            "discount_type",
            "discount_value",
            "discount_amount",
            "discount_reason",
            "is_taxable",
            "tax_rate",
            "tax_amount",
            "tax_code",
            "line_total",
            "status",
            "warehouse",
            "location",
            "notes",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "quantity_fulfilled",
            "quantity_returned",
            "quantity_cancelled",
            "discount_amount",
            "tax_amount",
            "line_total",
            "status",
            "created_on",
            "updated_on",
        ]

    def get_product_display(self, obj):
        if obj.product:
            name = str(obj.product)
            if obj.variant:
                name += f" — {obj.variant}"
            return name
        return obj.item_name or obj.item_sku or ""

    def validate_quantity_ordered(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be positive.")
        return value

    def validate_unit_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Unit price cannot be negative.")
        return value


class OrderLineItemListSerializer(serializers.ModelSerializer):
    """Compact serializer for listing line items within an order."""

    class Meta:
        model = OrderLineItem
        fields = [
            "id",
            "position",
            "item_name",
            "item_sku",
            "quantity_ordered",
            "quantity_fulfilled",
            "unit_price",
            "discount_amount",
            "tax_amount",
            "line_total",
            "status",
        ]
        read_only_fields = fields
