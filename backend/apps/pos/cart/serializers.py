"""
POS Cart and CartItem serializers.

Provides serialization for POSCart and POSCartItem models
with nested items, customer detail, and computed totals.
"""

from decimal import Decimal

from django.db import models
from rest_framework import serializers

from apps.pos.cart.models import POSCart, POSCartItem
from apps.pos.constants import (
    DISCOUNT_TYPE_FIXED,
    DISCOUNT_TYPE_PERCENT,
)


# ── Nested Product Serializers ──────────────────────────────────────────


class CartItemProductSerializer(serializers.Serializer):
    """Lightweight product detail for cart item display."""

    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(read_only=True)
    sku = serializers.CharField(read_only=True)
    barcode = serializers.CharField(read_only=True)


class CartItemVariantSerializer(serializers.Serializer):
    """Lightweight variant detail for cart item display."""

    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(read_only=True)
    sku = serializers.CharField(read_only=True)
    barcode = serializers.CharField(read_only=True)


class SimpleCustomerSerializer(serializers.Serializer):
    """Lightweight customer serializer for cart display."""

    id = serializers.UUIDField(read_only=True)
    name = serializers.SerializerMethodField()
    email = serializers.EmailField(read_only=True)
    phone = serializers.CharField(read_only=True)

    def get_name(self, obj):
        first = getattr(obj, "first_name", "")
        last = getattr(obj, "last_name", "")
        full = f"{first} {last}".strip()
        return full or getattr(obj, "company_name", str(obj))


# ── POSCartItemSerializer ──────────────────────────────────────────────


class POSCartItemSerializer(serializers.ModelSerializer):
    """Serializer for cart line items."""

    product_detail = CartItemProductSerializer(
        source="product", read_only=True
    )
    variant_detail = CartItemVariantSerializer(
        source="variant", read_only=True
    )

    class Meta:
        model = POSCartItem
        fields = [
            "id",
            "cart",
            "product",
            "variant",
            "product_detail",
            "variant_detail",
            "line_number",
            "quantity",
            "original_price",
            "unit_price",
            "line_total",
            "discount_type",
            "discount_value",
            "discount_amount",
            "is_taxable",
            "tax_rate",
            "tax_amount",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "line_number",
            "original_price",
            "line_total",
            "discount_amount",
            "tax_amount",
            "created_on",
            "updated_on",
        ]
        extra_kwargs = {
            "cart": {"write_only": True, "required": False},
        }


class CartItemCreateSerializer(serializers.Serializer):
    """Serializer for adding an item to the cart."""

    product = serializers.UUIDField()
    variant = serializers.UUIDField(required=False, allow_null=True)
    quantity = serializers.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=Decimal("1.000"),
        min_value=Decimal("0.001"),
    )


class CartItemUpdateSerializer(serializers.Serializer):
    """Serializer for updating cart item quantity."""

    quantity = serializers.DecimalField(
        max_digits=10,
        decimal_places=3,
        min_value=Decimal("0.001"),
    )


class CartDiscountSerializer(serializers.Serializer):
    """Serializer for applying a cart or line discount."""

    discount_type = serializers.ChoiceField(
        choices=[DISCOUNT_TYPE_PERCENT, DISCOUNT_TYPE_FIXED]
    )
    discount_value = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=Decimal("0.01")
    )
    reason = serializers.CharField(required=False, allow_blank=True)


# ── POSCartSerializer ──────────────────────────────────────────────────


class POSCartSerializer(serializers.ModelSerializer):
    """Serializer for POSCart with nested items and customer detail."""

    items = serializers.SerializerMethodField()
    item_count = serializers.SerializerMethodField()
    customer_detail = SimpleCustomerSerializer(
        source="customer", read_only=True
    )
    payments_total = serializers.SerializerMethodField()
    remaining_amount = serializers.SerializerMethodField()

    class Meta:
        model = POSCart
        fields = [
            "id",
            "reference_number",
            "session",
            "customer",
            "customer_detail",
            "status",
            # totals
            "subtotal",
            "discount_total",
            "tax_total",
            "grand_total",
            # cart discount
            "cart_discount_type",
            "cart_discount_value",
            "cart_discount_amount",
            "cart_discount_reason",
            "coupon_code",
            # notes
            "notes",
            # computed
            "items",
            "item_count",
            "payments_total",
            "remaining_amount",
            # timestamps
            "completed_at",
            "voided_at",
            "held_at",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "reference_number",
            "status",
            "subtotal",
            "discount_total",
            "tax_total",
            "grand_total",
            "cart_discount_amount",
            "completed_at",
            "voided_at",
            "held_at",
            "created_on",
            "updated_on",
        ]
        extra_kwargs = {
            "session": {"write_only": True, "required": False},
            "customer": {"required": False, "allow_null": True},
        }

    def get_items(self, obj):
        items = (
            obj.items.filter(is_active=True, is_deleted=False)
            .select_related("product", "variant")
            .order_by("line_number")
        )
        return POSCartItemSerializer(items, many=True).data

    def get_item_count(self, obj):
        return obj.items.filter(is_active=True, is_deleted=False).count()

    def get_payments_total(self, obj):
        from apps.pos.constants import PAYMENT_STATUS_COMPLETED

        total = obj.payments.filter(
            status=PAYMENT_STATUS_COMPLETED
        ).aggregate(total=models.Sum("amount"))["total"]
        return str(total or Decimal("0.00"))

    def get_remaining_amount(self, obj):
        from apps.pos.constants import PAYMENT_STATUS_COMPLETED

        paid = obj.payments.filter(
            status=PAYMENT_STATUS_COMPLETED
        ).aggregate(total=models.Sum("amount"))["total"] or Decimal("0.00")
        remaining = obj.grand_total - paid
        return str(max(remaining, Decimal("0.00")))
