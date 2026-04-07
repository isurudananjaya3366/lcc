"""Payment serializers."""

from rest_framework import serializers

from apps.payments.constants import PaymentMethod, PaymentStatus
from apps.payments.models import (
    Payment,
    PaymentAllocation,
    PaymentHistory,
    PaymentReceipt,
    Refund,
)


# ─── Payment Serializers ───────────────────────────────────────────


class PaymentListSerializer(serializers.ModelSerializer):
    """Compact serializer for list views."""

    status_display = serializers.SerializerMethodField()
    method_display = serializers.SerializerMethodField()
    customer_display = serializers.SerializerMethodField()
    has_receipt = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            "id",
            "payment_number",
            "method",
            "method_display",
            "status",
            "status_display",
            "amount",
            "currency",
            "customer",
            "customer_display",
            "invoice",
            "payment_date",
            "reference_number",
            "has_receipt",
            "created_on",
        ]
        read_only_fields = fields

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_method_display(self, obj):
        return obj.get_method_display()

    def get_customer_display(self, obj):
        if obj.customer:
            return str(obj.customer)
        return ""

    def get_has_receipt(self, obj):
        return hasattr(obj, "receipt") and obj.receipt is not None


class PaymentSerializer(serializers.ModelSerializer):
    """Full serializer for detail views."""

    status_display = serializers.SerializerMethodField()
    method_display = serializers.SerializerMethodField()
    customer_display = serializers.SerializerMethodField()
    has_receipt = serializers.SerializerMethodField()
    receipt_number = serializers.SerializerMethodField()
    total_refunded = serializers.SerializerMethodField()
    is_pending = serializers.BooleanField(read_only=True)
    is_processed = serializers.BooleanField(read_only=True)
    is_cancelled = serializers.BooleanField(read_only=True)
    is_refunded = serializers.BooleanField(read_only=True)
    is_terminal = serializers.BooleanField(read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "payment_number",
            "method",
            "method_display",
            "status",
            "status_display",
            "amount",
            "currency",
            "exchange_rate",
            "amount_in_base_currency",
            "customer",
            "customer_display",
            "invoice",
            "order",
            "payment_date",
            "processed_at",
            "cancelled_at",
            "reference_number",
            "transaction_id",
            "method_details",
            "received_by",
            "approved_by",
            "notes",
            "internal_notes",
            # Computed
            "has_receipt",
            "receipt_number",
            "total_refunded",
            "is_pending",
            "is_processed",
            "is_cancelled",
            "is_refunded",
            "is_terminal",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "payment_number",
            "status",
            "processed_at",
            "cancelled_at",
            "amount_in_base_currency",
            "created_on",
            "updated_on",
        ]

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_method_display(self, obj):
        return obj.get_method_display()

    def get_customer_display(self, obj):
        if obj.customer:
            return str(obj.customer)
        return ""

    def get_has_receipt(self, obj):
        return hasattr(obj, "receipt") and obj.receipt is not None

    def get_receipt_number(self, obj):
        try:
            return obj.receipt.receipt_number if obj.receipt else None
        except PaymentReceipt.DoesNotExist:
            return None

    def get_total_refunded(self, obj):
        from django.db.models import Sum

        total = obj.refunds.aggregate(total=Sum("amount"))["total"]
        return str(total) if total else "0.00"


class PaymentCreateSerializer(serializers.Serializer):
    """Serializer for creating a payment."""

    method = serializers.ChoiceField(choices=PaymentMethod.choices)
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    invoice_id = serializers.UUIDField(required=False)
    order_id = serializers.UUIDField(required=False)
    customer_id = serializers.UUIDField(required=False)
    payment_date = serializers.DateField(required=False)
    reference_number = serializers.CharField(
        required=False, default="", allow_blank=True
    )
    transaction_id = serializers.CharField(
        required=False, default="", allow_blank=True
    )
    currency = serializers.CharField(required=False, default="LKR")
    exchange_rate = serializers.DecimalField(
        max_digits=12, decimal_places=6, required=False
    )
    method_details = serializers.JSONField(required=False)
    notes = serializers.CharField(required=False, default="", allow_blank=True)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value


class PaymentDetailSerializer(PaymentSerializer):
    """Extended serializer including history and allocations."""

    history = serializers.SerializerMethodField()
    allocations = serializers.SerializerMethodField()

    class Meta(PaymentSerializer.Meta):
        fields = PaymentSerializer.Meta.fields + ["history", "allocations"]

    def get_history(self, obj):
        entries = obj.history.order_by("-changed_at")[:20]
        return PaymentHistorySerializer(entries, many=True).data

    def get_allocations(self, obj):
        allocs = obj.allocations.select_related("invoice")
        return PaymentAllocationSerializer(allocs, many=True).data


# ─── Supporting Serializers ─────────────────────────────────────────


class PaymentHistorySerializer(serializers.ModelSerializer):
    """Read-only serializer for payment audit history."""

    changed_by_display = serializers.SerializerMethodField()

    class Meta:
        model = PaymentHistory
        fields = [
            "id",
            "action",
            "old_value",
            "new_value",
            "changed_by",
            "changed_by_display",
            "changed_at",
            "description",
        ]
        read_only_fields = fields

    def get_changed_by_display(self, obj):
        if obj.changed_by:
            return str(obj.changed_by)
        return "System"


class PaymentAllocationSerializer(serializers.ModelSerializer):
    """Read-only serializer for payment allocations."""

    invoice_number = serializers.SerializerMethodField()

    class Meta:
        model = PaymentAllocation
        fields = [
            "id",
            "invoice",
            "invoice_number",
            "amount",
            "notes",
            "created_on",
        ]
        read_only_fields = fields

    def get_invoice_number(self, obj):
        if obj.invoice:
            return getattr(obj.invoice, "invoice_number", str(obj.invoice))
        return None


# ─── Refund Serializers ─────────────────────────────────────────────


class RefundListSerializer(serializers.ModelSerializer):
    """Compact refund serializer for list views."""

    status_display = serializers.SerializerMethodField()
    reason_display = serializers.SerializerMethodField()
    original_payment_number = serializers.SerializerMethodField()

    class Meta:
        model = Refund
        fields = [
            "id",
            "refund_number",
            "original_payment",
            "original_payment_number",
            "amount",
            "reason",
            "reason_display",
            "refund_method",
            "status",
            "status_display",
            "created_on",
        ]
        read_only_fields = fields

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_reason_display(self, obj):
        return obj.get_reason_display()

    def get_original_payment_number(self, obj):
        return obj.original_payment.payment_number if obj.original_payment else None


class RefundSerializer(serializers.ModelSerializer):
    """Full refund serializer."""

    status_display = serializers.SerializerMethodField()
    reason_display = serializers.SerializerMethodField()
    original_payment_number = serializers.SerializerMethodField()

    class Meta:
        model = Refund
        fields = [
            "id",
            "refund_number",
            "original_payment",
            "original_payment_number",
            "amount",
            "reason",
            "reason_display",
            "reason_notes",
            "refund_method",
            "status",
            "status_display",
            "requested_by",
            "approved_by",
            "processed_by",
            "approved_at",
            "processed_at",
            "notes",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "refund_number",
            "status",
            "requested_by",
            "approved_by",
            "processed_by",
            "approved_at",
            "processed_at",
            "created_on",
            "updated_on",
        ]

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_reason_display(self, obj):
        return obj.get_reason_display()

    def get_original_payment_number(self, obj):
        return obj.original_payment.payment_number if obj.original_payment else None


class RefundCreateSerializer(serializers.Serializer):
    """Serializer for requesting a refund."""

    payment_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    reason = serializers.CharField(max_length=30)
    reason_notes = serializers.CharField(required=False, default="", allow_blank=True)
    refund_method = serializers.CharField(required=False, default="ORIGINAL")
    notes = serializers.CharField(required=False, default="", allow_blank=True)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Refund amount must be greater than zero.")
        return value


class RefundApproveSerializer(serializers.Serializer):
    """Serializer for approving a refund."""

    notes = serializers.CharField(required=False, default="", allow_blank=True)


class RefundRejectSerializer(serializers.Serializer):
    """Serializer for rejecting a refund."""

    notes = serializers.CharField(required=False, default="", allow_blank=True)


# ─── Receipt Serializers ────────────────────────────────────────────


class PaymentReceiptSerializer(serializers.ModelSerializer):
    """Full serializer for payment receipts."""

    payment_number = serializers.SerializerMethodField()
    customer_display = serializers.SerializerMethodField()
    has_pdf = serializers.SerializerMethodField()
    pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = PaymentReceipt
        fields = [
            "id",
            "receipt_number",
            "payment",
            "payment_number",
            "invoice",
            "customer",
            "customer_display",
            "receipt_date",
            "receipt_amount",
            "payment_method",
            "reference_number",
            "currency",
            "exchange_rate",
            "has_pdf",
            "pdf_url",
            "pdf_generated_at",
            "is_sent",
            "sent_at",
            "sent_to",
            "notes",
            "created_on",
        ]
        read_only_fields = fields

    def get_payment_number(self, obj):
        return obj.payment.payment_number if obj.payment else None

    def get_customer_display(self, obj):
        return str(obj.customer) if obj.customer else ""

    def get_has_pdf(self, obj):
        return obj.has_pdf()

    def get_pdf_url(self, obj):
        return obj.get_pdf_url()
