"""Invoice line item serializers."""

from rest_framework import serializers

from apps.invoices.models import InvoiceLineItem


class InvoiceLineItemListSerializer(serializers.ModelSerializer):
    """Compact line item serializer for list/nested views."""

    class Meta:
        model = InvoiceLineItem
        fields = [
            "id",
            "position",
            "description",
            "sku",
            "quantity",
            "unit_price",
            "discount_amount",
            "tax_rate",
            "tax_amount",
            "line_total",
        ]
        read_only_fields = fields


class InvoiceLineItemSerializer(serializers.ModelSerializer):
    """Full line item serializer for create/update."""

    class Meta:
        model = InvoiceLineItem
        fields = [
            "id",
            "invoice",
            "position",
            "product",
            "variant",
            "description",
            "sku",
            "quantity",
            "unit_price",
            "original_price",
            "unit_of_measure",
            "discount_type",
            "discount_value",
            "discount_amount",
            "tax_rate",
            "is_taxable",
            "tax_code",
            "tax_description",
            "tax_amount",
            "hsn_code",
            "line_total",
            "notes",
        ]
        read_only_fields = ["id", "discount_amount", "tax_amount", "line_total"]
