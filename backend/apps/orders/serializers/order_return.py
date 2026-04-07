"""
Return serializers (Task 89).
"""

from rest_framework import serializers

from apps.orders.models.order_return import (
    OrderReturn,
    ReturnLineItem,
    ReturnReason,
    ReturnStatus,
)


class ReturnLineItemSerializer(serializers.ModelSerializer):
    """Serializer for return line items."""

    item_name = serializers.CharField(
        source="order_line_item.item_name", read_only=True
    )
    refund_subtotal = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        model = ReturnLineItem
        fields = [
            "id",
            "order_line_item",
            "item_name",
            "quantity",
            "condition",
            "inspected",
            "inspected_at",
            "inspection_notes",
            "unit_refund_amount",
            "restocking_fee_per_unit",
            "refund_subtotal",
            "stock_restored",
        ]
        read_only_fields = [
            "id",
            "inspected",
            "inspected_at",
            "unit_refund_amount",
            "restocking_fee_per_unit",
            "stock_restored",
        ]


class OrderReturnSerializer(serializers.ModelSerializer):
    """Full serializer for order return detail."""

    return_line_items = ReturnLineItemSerializer(many=True, read_only=True)
    status_display = serializers.SerializerMethodField()
    is_refund_eligible = serializers.BooleanField(read_only=True)

    class Meta:
        model = OrderReturn
        fields = [
            "id",
            "order",
            "return_number",
            "reason",
            "reason_detail",
            "status",
            "status_display",
            "requested_by",
            "requested_at",
            "approved_by",
            "approved_at",
            "rejected_by",
            "rejected_at",
            "rejection_reason",
            "received_by",
            "received_at",
            "refund_amount",
            "restocking_fee",
            "refund_shipping",
            "refund_method",
            "refunded_at",
            "is_refund_eligible",
            "notes",
            "return_line_items",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "return_number",
            "status",
            "requested_at",
            "approved_by",
            "approved_at",
            "rejected_by",
            "rejected_at",
            "received_by",
            "received_at",
            "refund_amount",
            "restocking_fee",
            "refunded_at",
            "created_on",
            "updated_on",
        ]

    def get_status_display(self, obj):
        return obj.get_status_display()


class OrderReturnListSerializer(serializers.ModelSerializer):
    """Compact serializer for return list views."""

    class Meta:
        model = OrderReturn
        fields = [
            "id",
            "return_number",
            "reason",
            "status",
            "refund_amount",
            "requested_at",
            "created_on",
        ]
        read_only_fields = fields


class ReturnCreateSerializer(serializers.Serializer):
    """Serializer for creating a return request."""

    reason = serializers.ChoiceField(choices=ReturnReason.choices)
    reason_detail = serializers.CharField(required=False, allow_blank=True)
    refund_shipping = serializers.BooleanField(required=False, default=False)
    notes = serializers.CharField(required=False, allow_blank=True)
    items = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
        help_text="List of {order_line_item: UUID, quantity: Decimal}",
    )


class ReturnActionSerializer(serializers.Serializer):
    """Serializer for return approval/rejection actions."""

    notes = serializers.CharField(required=False, allow_blank=True)
    rejection_reason = serializers.CharField(required=False, allow_blank=True)
