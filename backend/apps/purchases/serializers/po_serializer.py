"""
Purchase Order serializers.
"""

from rest_framework import serializers

from apps.purchases.models.po_line_item import POLineItem
from apps.purchases.models.purchase_order import PurchaseOrder


class POLineItemSerializer(serializers.ModelSerializer):
    """Full serializer for PO line items."""

    quantity_pending = serializers.ReadOnlyField()

    class Meta:
        model = POLineItem
        fields = [
            "id",
            "purchase_order",
            "line_number",
            "product",
            "variant",
            "vendor_sku",
            "product_name",
            "item_description",
            "is_service",
            "quantity_ordered",
            "quantity_received",
            "quantity_rejected",
            "quantity_cancelled",
            "quantity_pending",
            "unit_price",
            "discount_percentage",
            "discount_amount",
            "tax_rate",
            "tax_amount",
            "line_total",
            "status",
            "expected_delivery_date",
            "receiving_warehouse",
            "receiving_location",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "tax_amount",
            "line_total",
            "quantity_received",
            "quantity_rejected",
            "created_on",
            "updated_on",
        ]


class POLineItemCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating line items."""

    class Meta:
        model = POLineItem
        fields = [
            "product",
            "variant",
            "vendor_sku",
            "product_name",
            "item_description",
            "is_service",
            "quantity_ordered",
            "unit_price",
            "discount_percentage",
            "discount_amount",
            "tax_rate",
            "expected_delivery_date",
            "receiving_warehouse",
            "receiving_location",
        ]


class POListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for PO listings."""

    vendor_name = serializers.CharField(source="vendor.company_name", read_only=True)
    line_count = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrder
        fields = [
            "id",
            "po_number",
            "vendor",
            "vendor_name",
            "status",
            "order_date",
            "expected_delivery_date",
            "total",
            "currency",
            "payment_status",
            "line_count",
            "created_on",
        ]
        read_only_fields = fields

    def get_line_count(self, obj):
        return obj.line_items.count()


class PODetailSerializer(serializers.ModelSerializer):
    """Full serializer for PO detail view."""

    vendor_name = serializers.CharField(source="vendor.company_name", read_only=True)
    line_items = POLineItemSerializer(many=True, read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            "id",
            "po_number",
            "status",
            "vendor",
            "vendor_name",
            "vendor_reference",
            "order_date",
            "expected_delivery_date",
            "acknowledged_at",
            "received_at",
            "ship_to_address",
            "shipping_method",
            "shipping_cost",
            "carrier",
            "tracking_number",
            "subtotal",
            "discount_amount",
            "discount_percentage",
            "tax_amount",
            "total",
            "currency",
            "payment_terms",
            "payment_terms_days",
            "payment_due_date",
            "payment_status",
            "amount_paid",
            "created_by",
            "approved_by",
            "received_by",
            "notes",
            "internal_notes",
            "vendor_notes",
            "delivery_instructions",
            "requires_approval",
            "approved_at",
            "approval_notes",
            "rejected_at",
            "rejection_reason",
            "receiving_warehouse",
            "pdf_file",
            "pdf_generated_at",
            "pdf_version",
            "line_items",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "po_number",
            "subtotal",
            "tax_amount",
            "total",
            "created_on",
            "updated_on",
        ]


class POCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new PO."""

    line_items_data = POLineItemCreateSerializer(many=True, required=False, write_only=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            "vendor",
            "vendor_reference",
            "order_date",
            "expected_delivery_date",
            "ship_to_address",
            "shipping_method",
            "currency",
            "payment_terms",
            "payment_terms_days",
            "notes",
            "vendor_notes",
            "delivery_instructions",
            "receiving_warehouse",
            "line_items_data",
        ]

    def create(self, validated_data):
        from apps.purchases.services.po_service import POService

        line_items_data = validated_data.pop("line_items_data", [])
        user = self.context["request"].user
        return POService.create_po(
            vendor=validated_data.pop("vendor"),
            created_by=user,
            line_items_data=line_items_data,
            **validated_data,
        )


class POUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating an existing PO."""

    class Meta:
        model = PurchaseOrder
        fields = [
            "vendor_reference",
            "expected_delivery_date",
            "ship_to_address",
            "shipping_method",
            "currency",
            "payment_terms",
            "payment_terms_days",
            "notes",
            "internal_notes",
            "vendor_notes",
            "delivery_instructions",
            "receiving_warehouse",
        ]

    def update(self, instance, validated_data):
        from apps.purchases.services.po_service import POService

        return POService.update_po(instance.pk, validated_data)
