"""
Goods Receipt Note serializers.
"""

from rest_framework import serializers

from apps.purchases.models.goods_receipt import GoodsReceipt
from apps.purchases.models.grn_line_item import GRNLineItem


class GRNLineItemSerializer(serializers.ModelSerializer):
    """Serializer for GRN line items."""

    quantity_accepted = serializers.ReadOnlyField()

    class Meta:
        model = GRNLineItem
        fields = [
            "id",
            "goods_receipt",
            "po_line",
            "line_number",
            "quantity_received",
            "quantity_rejected",
            "quantity_accepted",
            "condition",
            "rejection_reason",
            "quality_notes",
            "requires_followup",
            "receiving_warehouse",
            "receiving_location",
            "notes",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "created_on", "updated_on"]


class GRNListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for GRN listings."""

    po_number = serializers.CharField(
        source="purchase_order.po_number", read_only=True
    )

    class Meta:
        model = GoodsReceipt
        fields = [
            "id",
            "grn_number",
            "purchase_order",
            "po_number",
            "status",
            "received_by",
            "received_at",
            "inspection_status",
            "created_on",
        ]
        read_only_fields = fields


class GRNDetailSerializer(serializers.ModelSerializer):
    """Full serializer for GRN detail view."""

    po_number = serializers.CharField(
        source="purchase_order.po_number", read_only=True
    )
    line_items = GRNLineItemSerializer(many=True, read_only=True)

    class Meta:
        model = GoodsReceipt
        fields = [
            "id",
            "grn_number",
            "purchase_order",
            "po_number",
            "status",
            "received_by",
            "received_at",
            "delivery_note_number",
            "carrier",
            "delivery_date",
            "delivery_time",
            "driver_name",
            "vehicle_number",
            "inspection_status",
            "inspection_notes",
            "inspected_by",
            "inspected_at",
            "inspection_passed",
            "notes",
            "line_items",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "grn_number",
            "received_at",
            "created_on",
            "updated_on",
        ]
