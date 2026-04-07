"""
Order serializers (Tasks 81, 83).
"""

from rest_framework import serializers

from apps.orders.constants import OrderStatus
from apps.orders.models import Order
from apps.orders.serializers.line_item import OrderLineItemListSerializer


class OrderListSerializer(serializers.ModelSerializer):
    """Compact serializer for list views (Task 83)."""

    status_display = serializers.SerializerMethodField()
    line_items_count = serializers.SerializerMethodField()
    customer_display = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "status",
            "status_display",
            "source",
            "customer",
            "customer_display",
            "customer_name",
            "total_amount",
            "currency",
            "payment_status",
            "is_draft",
            "priority",
            "line_items_count",
            "created_on",
            "updated_on",
        ]
        read_only_fields = fields

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_line_items_count(self, obj):
        return obj.line_items.count()

    def get_customer_display(self, obj):
        if obj.customer:
            return obj.customer.full_name
        return obj.customer_name or obj.customer_email or "Guest"


class OrderSerializer(serializers.ModelSerializer):
    """Full serializer for order create/update/detail (Task 81)."""

    line_items = OrderLineItemListSerializer(many=True, read_only=True)
    status_display = serializers.SerializerMethodField()
    customer_display = serializers.SerializerMethodField()
    currency_symbol = serializers.SerializerMethodField()
    is_editable = serializers.BooleanField(read_only=True)
    fulfillment_percentage = serializers.SerializerMethodField()
    can_cancel = serializers.BooleanField(read_only=True)
    source_display = serializers.SerializerMethodField()
    payment_status_display = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "status",
            "status_display",
            "source",
            "source_display",
            "priority",
            "is_draft",
            # Customer
            "customer",
            "customer_display",
            "customer_name",
            "customer_email",
            "customer_phone",
            # Addresses
            "billing_address",
            "shipping_address",
            # Financial
            "subtotal",
            "discount_type",
            "discount_value",
            "discount_amount",
            "tax_amount",
            "shipping_amount",
            "total_amount",
            "currency",
            "currency_symbol",
            # Payment
            "payment_status",
            "payment_status_display",
            "amount_paid",
            "balance_due",
            # Shipping
            "shipping_method",
            "tracking_number",
            # Timestamps
            "confirmed_at",
            "shipped_at",
            "delivered_at",
            "completed_at",
            "cancelled_at",
            # References
            "quote",
            "pos_session",
            "external_reference",
            # Notes
            "notes",
            "internal_notes",
            "tags",
            # Lock
            "is_locked",
            "is_editable",
            "can_cancel",
            "fulfillment_percentage",
            "total_items",
            # Nested
            "line_items",
            # Audit
            "created_by",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "order_number",
            "subtotal",
            "discount_amount",
            "tax_amount",
            "total_amount",
            "amount_paid",
            "balance_due",
            "confirmed_at",
            "shipped_at",
            "delivered_at",
            "completed_at",
            "cancelled_at",
            "is_locked",
            "created_by",
            "created_on",
            "updated_on",
        ]

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_customer_display(self, obj):
        if obj.customer:
            return obj.customer.full_name
        return obj.customer_name or obj.customer_email or "Guest"

    def get_currency_symbol(self, obj):
        from apps.orders.constants import CURRENCY_SYMBOLS
        return CURRENCY_SYMBOLS.get(obj.currency, obj.currency)

    def get_fulfillment_percentage(self, obj):
        from apps.orders.services.fulfillment_service import FulfillmentService
        progress = FulfillmentService.get_fulfillment_progress(obj)
        return float(progress["percentage"])

    def get_source_display(self, obj):
        return obj.get_source_display()

    def get_payment_status_display(self, obj):
        return obj.get_payment_status_display()

    def get_total_items(self, obj):
        return obj.line_items.count()

    def validate(self, attrs):
        if self.instance and self.instance.is_locked:
            raise serializers.ValidationError(
                "This order is locked and cannot be edited."
            )
        return attrs


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer specifically for order creation."""

    class Meta:
        model = Order
        fields = [
            "source",
            "priority",
            "customer",
            "customer_name",
            "customer_email",
            "customer_phone",
            "billing_address",
            "shipping_address",
            "currency",
            "discount_type",
            "discount_value",
            "shipping_method",
            "notes",
            "internal_notes",
            "tags",
        ]


class OrderStatusActionSerializer(serializers.Serializer):
    """Serializer for status-transition actions."""

    notes = serializers.CharField(required=False, allow_blank=True)
    reason = serializers.CharField(required=False, allow_blank=True)
