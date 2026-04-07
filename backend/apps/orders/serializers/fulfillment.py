"""
Fulfillment serializers (Task 88).
"""

from rest_framework import serializers

from apps.orders.models.fulfillment import Fulfillment
from apps.orders.models.fulfillment_item import FulfillmentLineItem


class FulfillmentLineItemSerializer(serializers.ModelSerializer):
    """Serializer for fulfillment line items."""

    item_name = serializers.CharField(
        source="order_line_item.item_name", read_only=True
    )

    class Meta:
        model = FulfillmentLineItem
        fields = [
            "id",
            "order_line_item",
            "item_name",
            "quantity",
            "bin_location",
            "serial_numbers",
            "batch_number",
            "picked_at",
            "packed_at",
            "qc_passed",
            "qc_notes",
        ]
        read_only_fields = ["id", "picked_at", "packed_at"]


class FulfillmentSerializer(serializers.ModelSerializer):
    """Full serializer for fulfillment detail."""

    fulfillment_items = FulfillmentLineItemSerializer(
        source="line_items", many=True, read_only=True
    )
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Fulfillment
        fields = [
            "id",
            "order",
            "fulfillment_number",
            "status",
            "status_display",
            "warehouse",
            "carrier",
            "tracking_number",
            "tracking_url",
            "shipped_at",
            "delivered_at",
            "weight",
            "dimensions",
            "notes",
            "fulfillment_items",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "fulfillment_number",
            "status",
            "shipped_at",
            "delivered_at",
            "created_on",
            "updated_on",
        ]

    def get_status_display(self, obj):
        return obj.get_status_display()


class FulfillmentListSerializer(serializers.ModelSerializer):
    """Compact serializer for fulfillment list views."""

    class Meta:
        model = Fulfillment
        fields = [
            "id",
            "fulfillment_number",
            "status",
            "carrier",
            "tracking_number",
            "shipped_at",
            "delivered_at",
            "created_on",
        ]
        read_only_fields = fields
