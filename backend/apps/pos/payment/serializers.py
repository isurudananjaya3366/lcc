"""
POS Payment serializers.

Provides serialization for POSPayment model and
request/response payloads for payment operations.
"""

from decimal import Decimal

from rest_framework import serializers

from apps.pos.constants import PAYMENT_METHOD_CHOICES, PAYMENT_STATUS_COMPLETED
from apps.pos.payment.models import POSPayment


class POSPaymentSerializer(serializers.ModelSerializer):
    """Full payment representation."""

    processed_by_email = serializers.EmailField(
        source="processed_by.email", read_only=True, default=None
    )
    is_successful = serializers.SerializerMethodField()
    can_refund = serializers.SerializerMethodField()
    payment_method_display = serializers.CharField(
        source="get_method_display", read_only=True
    )
    processing_duration = serializers.SerializerMethodField()

    class Meta:
        model = POSPayment
        fields = [
            "id",
            "cart",
            "processed_by",
            "processed_by_email",
            "method",
            "payment_method_display",
            "amount",
            "status",
            "amount_tendered",
            "change_due",
            "reference_number",
            "authorization_code",
            "transaction_id",
            "paid_at",
            "voided_at",
            "failed_at",
            "refunded_at",
            "notes",
            "is_successful",
            "can_refund",
            "processing_duration",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "status",
            "change_due",
            "paid_at",
            "voided_at",
            "failed_at",
            "refunded_at",
            "created_on",
            "updated_on",
        ]

    def get_is_successful(self, obj):
        return obj.status == PAYMENT_STATUS_COMPLETED

    def get_can_refund(self, obj):
        return obj.status == PAYMENT_STATUS_COMPLETED

    def get_processing_duration(self, obj):
        duration = obj.processing_duration
        if duration:
            return duration.total_seconds()
        return None


class PaymentRequestSerializer(serializers.Serializer):
    """Validates an incoming single-payment request."""

    cart = serializers.UUIDField()
    payment_method = serializers.ChoiceField(choices=PAYMENT_METHOD_CHOICES)
    amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=Decimal("0.01")
    )
    tendered_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        allow_null=True,
    )
    reference_number = serializers.CharField(
        max_length=100, required=False, allow_blank=True
    )
    authorization_code = serializers.CharField(
        max_length=50, required=False, allow_blank=True
    )


class SplitPaymentItemSerializer(serializers.Serializer):
    """One leg of a split payment."""

    payment_method = serializers.ChoiceField(choices=PAYMENT_METHOD_CHOICES)
    amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=Decimal("0.01")
    )
    tendered_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        allow_null=True,
    )
    reference_number = serializers.CharField(
        max_length=100, required=False, allow_blank=True
    )
    authorization_code = serializers.CharField(
        max_length=50, required=False, allow_blank=True
    )


class SplitPaymentRequestSerializer(serializers.Serializer):
    """Validates split-payment requests."""

    cart = serializers.UUIDField()
    payments = SplitPaymentItemSerializer(many=True, min_length=2)

    def validate_payments(self, value):
        if len(value) < 2:
            raise serializers.ValidationError(
                "Split payment requires at least two payment methods."
            )
        return value


class PaymentRefundRequestSerializer(serializers.Serializer):
    """Validates refund requests."""

    refund_amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=Decimal("0.01")
    )
    reason = serializers.CharField(max_length=500, required=False)


class PaymentCompleteRequestSerializer(serializers.Serializer):
    """Request to finalize a pending payment / transaction."""

    payment_id = serializers.UUIDField()
