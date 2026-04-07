"""
Credit serializers.

Provides CreditTransactionSerializer, CustomerCreditSerializer (detail),
and CreditListSerializer (lightweight list view).
"""

from rest_framework import serializers

from apps.credit.models import CreditTransaction, CustomerCredit


class CreditTransactionSerializer(serializers.ModelSerializer):
    """Serializer for credit transaction history."""

    transaction_type_display = serializers.CharField(
        source="get_transaction_type_display", read_only=True
    )

    class Meta:
        model = CreditTransaction
        fields = [
            "id",
            "transaction_number",
            "transaction_type",
            "transaction_type_display",
            "amount",
            "balance_after",
            "transaction_date",
            "reference_type",
            "reference_id",
            "notes",
            "status",
            "is_reversed",
        ]
        read_only_fields = ["id", "transaction_number", "transaction_date", "balance_after"]


class CustomerCreditSerializer(serializers.ModelSerializer):
    """Full serializer for customer credit accounts (detail view)."""

    customer_name = serializers.SerializerMethodField()
    customer_email = serializers.SerializerMethodField()
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    recent_transactions = serializers.SerializerMethodField()

    class Meta:
        model = CustomerCredit
        fields = [
            "id",
            "customer",
            "customer_name",
            "customer_email",
            "credit_limit",
            "available_credit",
            "outstanding_balance",
            "status",
            "status_display",
            "payment_terms_days",
            "interest_rate_annual",
            "risk_score",
            "last_payment_date",
            "next_payment_due",
            "account_opened_date",
            "notes",
            "recent_transactions",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "available_credit",
            "outstanding_balance",
            "last_payment_date",
            "account_opened_date",
            "created_on",
            "updated_on",
        ]

    def get_customer_name(self, obj):
        customer = obj.customer
        first = getattr(customer, "first_name", "")
        last = getattr(customer, "last_name", "")
        return f"{first} {last}".strip() or str(customer)

    def get_customer_email(self, obj):
        return getattr(obj.customer, "email", "")

    def get_recent_transactions(self, obj):
        txns = obj.transactions.order_by("-transaction_date")[:5]
        return CreditTransactionSerializer(txns, many=True).data


class CreditListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for credit list views."""

    customer_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )

    class Meta:
        model = CustomerCredit
        fields = [
            "id",
            "customer",
            "customer_name",
            "credit_limit",
            "available_credit",
            "outstanding_balance",
            "status",
            "status_display",
            "updated_on",
        ]

    def get_customer_name(self, obj):
        customer = obj.customer
        first = getattr(customer, "first_name", "")
        last = getattr(customer, "last_name", "")
        return f"{first} {last}".strip() or str(customer)
