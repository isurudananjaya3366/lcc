"""Invoice serializers."""

from rest_framework import serializers

from apps.invoices.constants import InvoiceStatus, InvoiceType
from apps.invoices.models import Invoice
from apps.invoices.serializers.line_item import InvoiceLineItemListSerializer


class InvoiceListSerializer(serializers.ModelSerializer):
    """Compact serializer for list views."""

    status_display = serializers.SerializerMethodField()
    type_display = serializers.SerializerMethodField()
    customer_display = serializers.SerializerMethodField()
    line_items_count = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            "id",
            "invoice_number",
            "type",
            "type_display",
            "status",
            "status_display",
            "customer",
            "customer_display",
            "customer_name",
            "issue_date",
            "due_date",
            "total",
            "balance_due",
            "currency",
            "currency_symbol",
            "is_draft",
            "is_overdue",
            "line_items_count",
            "created_on",
        ]
        read_only_fields = fields

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_type_display(self, obj):
        return obj.get_type_display()

    def get_customer_display(self, obj):
        if obj.customer:
            return str(obj.customer)
        return obj.customer_name or obj.customer_email or "Guest"

    def get_line_items_count(self, obj):
        return obj.line_items.count()


class InvoiceSerializer(serializers.ModelSerializer):
    """Full serializer for create/update/detail."""

    line_items = InvoiceLineItemListSerializer(many=True, read_only=True)
    status_display = serializers.SerializerMethodField()
    type_display = serializers.SerializerMethodField()
    customer_display = serializers.SerializerMethodField()
    is_draft = serializers.BooleanField(read_only=True)
    is_editable = serializers.BooleanField(read_only=True)
    is_paid = serializers.BooleanField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    is_cancellable = serializers.BooleanField(read_only=True)
    is_voidable = serializers.BooleanField(read_only=True)
    days_overdue = serializers.IntegerField(read_only=True)
    aging_bucket = serializers.CharField(read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "invoice_number",
            "type",
            "type_display",
            "status",
            "status_display",
            # Customer
            "customer",
            "customer_display",
            "customer_name",
            "customer_email",
            "customer_phone",
            "customer_address",
            # Business
            "business_name",
            "business_address",
            "business_phone",
            "business_email",
            "business_website",
            # Compliance
            "business_registration_number",
            "vat_registration_number",
            "svat_number",
            "tax_scheme",
            # Dates
            "issue_date",
            "due_date",
            "paid_date",
            "cancelled_date",
            "voided_date",
            # Financial
            "subtotal",
            "discount_type",
            "discount_value",
            "discount_amount",
            "tax_amount",
            "total",
            "amount_paid",
            "balance_due",
            "tax_breakdown",
            # References
            "order",
            "related_invoice",
            "external_reference",
            # Metadata
            "terms_and_conditions",
            "payment_instructions",
            "footer_text",
            "notes",
            "internal_notes",
            "custom_fields",
            "tags",
            # Currency
            "currency",
            "exchange_rate",
            "currency_symbol",
            "base_currency_total",
            # PDF
            "pdf_file",
            "pdf_generated_at",
            # Tracking
            "created_by",
            "updated_by",
            "created_on",
            "updated_on",
            # Line items
            "line_items",
            # Computed
            "is_draft",
            "is_editable",
            "is_paid",
            "is_overdue",
            "is_cancellable",
            "is_voidable",
            "days_overdue",
            "aging_bucket",
        ]
        read_only_fields = [
            "id",
            "invoice_number",
            "status",
            "subtotal",
            "discount_amount",
            "tax_amount",
            "total",
            "amount_paid",
            "balance_due",
            "base_currency_total",
            "pdf_file",
            "pdf_generated_at",
            "tax_breakdown",
            "created_by",
            "updated_by",
            "created_on",
            "updated_on",
            "issue_date",
            "paid_date",
            "cancelled_date",
            "voided_date",
        ]

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_type_display(self, obj):
        return obj.get_type_display()

    def get_customer_display(self, obj):
        if obj.customer:
            return str(obj.customer)
        return obj.customer_name or obj.customer_email or "Guest"


class InvoiceCreateSerializer(serializers.Serializer):
    """Serializer for creating an invoice from scratch or from an order."""

    order_id = serializers.UUIDField(required=False, help_text="Create from order")
    customer_id = serializers.UUIDField(required=False)
    type = serializers.ChoiceField(
        choices=InvoiceType.choices, default=InvoiceType.STANDARD
    )
    notes = serializers.CharField(required=False, default="", allow_blank=True)
    internal_notes = serializers.CharField(required=False, default="", allow_blank=True)
    currency = serializers.CharField(required=False, default="LKR")


class InvoiceStatusActionSerializer(serializers.Serializer):
    """Serializer for status transition actions."""

    notes = serializers.CharField(required=False, default="", allow_blank=True)
    amount = serializers.DecimalField(
        max_digits=15, decimal_places=2, required=False,
        help_text="Payment amount (for mark-paid action)",
    )


class CreditNoteCreateSerializer(serializers.Serializer):
    """Serializer for creating a credit note."""

    original_invoice_id = serializers.UUIDField()
    reason = serializers.CharField()
    notes = serializers.CharField(required=False, default="", allow_blank=True)
    line_items = serializers.ListField(child=serializers.DictField(), required=False)


class DebitNoteCreateSerializer(serializers.Serializer):
    """Serializer for creating a debit note."""

    original_invoice_id = serializers.UUIDField()
    reason = serializers.CharField()
    notes = serializers.CharField(required=False, default="", allow_blank=True)
    line_items = serializers.ListField(child=serializers.DictField(), required=False)
