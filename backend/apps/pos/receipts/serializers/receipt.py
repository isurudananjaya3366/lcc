"""
Receipt serializers — Tasks 69, 72-75, 77.

Serializers for Receipt model CRUD, generation, print, email,
PDF download, and search endpoints.
"""

from decimal import Decimal

from rest_framework import serializers

from apps.pos.receipts.models import Receipt


class SimpleCartSerializer(serializers.Serializer):
    """Lightweight cart representation for receipt responses."""

    id = serializers.UUIDField(read_only=True)
    reference_number = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    grand_total = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )


class ReceiptListSerializer(serializers.ModelSerializer):
    """Compact receipt for list views."""

    cart_detail = SimpleCartSerializer(source="cart", read_only=True)
    was_printed = serializers.BooleanField(read_only=True)
    was_emailed = serializers.BooleanField(read_only=True)

    class Meta:
        model = Receipt
        fields = [
            "id",
            "receipt_number",
            "receipt_type",
            "cart",
            "cart_detail",
            "generated_at",
            "was_printed",
            "was_emailed",
            "reprint_count",
            "created_on",
        ]
        read_only_fields = fields


class ReceiptDetailSerializer(serializers.ModelSerializer):
    """Full receipt detail with all data."""

    cart_detail = SimpleCartSerializer(source="cart", read_only=True)
    was_printed = serializers.BooleanField(read_only=True)
    was_emailed = serializers.BooleanField(read_only=True)
    watermark_text = serializers.SerializerMethodField()
    template_name = serializers.SerializerMethodField()
    pdf_url = serializers.SerializerMethodField()
    print_url = serializers.SerializerMethodField()
    email_url = serializers.SerializerMethodField()

    class Meta:
        model = Receipt
        fields = [
            "id",
            "receipt_number",
            "receipt_type",
            "cart",
            "cart_detail",
            "transaction_id",
            "template",
            "template_name",
            "generated_at",
            "printed_at",
            "emailed_at",
            "was_printed",
            "was_emailed",
            "receipt_data",
            "original_receipt",
            "reprint_count",
            "generated_by",
            "watermark_text",
            "pdf_url",
            "print_url",
            "email_url",
            "created_on",
            "updated_on",
        ]
        read_only_fields = fields

    def get_watermark_text(self, obj):
        return obj.get_watermark_text()

    def get_template_name(self, obj):
        if obj.template:
            return obj.template.name
        return None

    def get_pdf_url(self, obj):
        request = self.context.get("request")
        if request:
            from django.urls import reverse
            return request.build_absolute_uri(
                reverse("pos:receipt-pdf", kwargs={"pk": obj.pk})
            )
        return None

    def get_print_url(self, obj):
        request = self.context.get("request")
        if request:
            from django.urls import reverse
            return request.build_absolute_uri(
                reverse("pos:receipt-print-receipt", kwargs={"pk": obj.pk})
            )
        return None

    def get_email_url(self, obj):
        request = self.context.get("request")
        if request:
            from django.urls import reverse
            return request.build_absolute_uri(
                reverse("pos:receipt-email", kwargs={"pk": obj.pk})
            )
        return None


# ── Action Request Serializers ─────────────────────────────────


class ReceiptGenerateSerializer(serializers.Serializer):
    """Request schema for generating a receipt from a cart."""

    cart = serializers.UUIDField(help_text="Cart UUID to generate receipt for")
    receipt_type = serializers.ChoiceField(
        choices=["SALE", "REFUND", "VOID"],
        default="SALE",
    )
    template = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text="Template UUID (uses default if omitted)",
    )
    auto_print = serializers.BooleanField(default=False)


class ReceiptPrintSerializer(serializers.Serializer):
    """Request schema for printing a receipt."""

    printer_ip = serializers.IPAddressField(
        required=False,
        help_text="Printer IP address (uses terminal default if omitted)",
    )
    printer_port = serializers.IntegerField(
        required=False,
        default=9100,
        min_value=1,
        max_value=65535,
    )
    paper_width = serializers.ChoiceField(
        choices=["80mm", "58mm"],
        default="80mm",
    )
    copies = serializers.IntegerField(default=1, min_value=1, max_value=5)
    open_drawer = serializers.BooleanField(default=False)


class ReceiptEmailSerializer(serializers.Serializer):
    """Request schema for emailing a receipt."""

    email = serializers.EmailField(help_text="Recipient email address")
    subject = serializers.CharField(
        max_length=200,
        required=False,
        allow_blank=True,
    )
    message = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        help_text="Custom message to include in the email body",
    )
    attach_pdf = serializers.BooleanField(default=True)
    cc = serializers.ListField(
        child=serializers.EmailField(),
        required=False,
        max_length=5,
    )


class ReceiptDuplicateSerializer(serializers.Serializer):
    """Request schema for creating a duplicate receipt."""

    reason = serializers.CharField(
        max_length=200,
        required=False,
        allow_blank=True,
        help_text="Reason for reprinting",
    )


class ReceiptSearchSerializer(serializers.Serializer):
    """Request schema for receipt search."""

    query = serializers.CharField(
        max_length=200,
        required=False,
        allow_blank=True,
    )
    receipt_type = serializers.ChoiceField(
        choices=["SALE", "REFUND", "VOID", "DUPLICATE"],
        required=False,
    )
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    cart = serializers.UUIDField(required=False)
    min_total = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        min_value=Decimal("0"),
    )
    max_total = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        min_value=Decimal("0"),
    )


class ReceiptExportSerializer(serializers.Serializer):
    """Request schema for receipt export."""

    format = serializers.ChoiceField(
        choices=["csv", "json"],
        default="csv",
    )
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    receipt_type = serializers.ChoiceField(
        choices=["SALE", "REFUND", "VOID", "DUPLICATE"],
        required=False,
    )
