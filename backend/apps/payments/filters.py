"""Payment filters for API views."""

import django_filters
from django.db.models import Q

from apps.payments.constants import PaymentMethod, PaymentStatus
from apps.payments.models import Payment, Refund
from apps.payments.models.refund import RefundStatus


class PaymentFilter(django_filters.FilterSet):
    """Filter set for Payment list views."""

    method = django_filters.MultipleChoiceFilter(choices=PaymentMethod.choices)
    status = django_filters.MultipleChoiceFilter(choices=PaymentStatus.choices)
    customer = django_filters.UUIDFilter(field_name="customer__id")
    customer_name = django_filters.CharFilter(method="filter_customer_name")
    invoice = django_filters.UUIDFilter(field_name="invoice__id")
    invoice_number = django_filters.CharFilter(
        field_name="invoice__invoice_number", lookup_expr="icontains"
    )
    order = django_filters.UUIDFilter(field_name="order__id")
    currency = django_filters.CharFilter(field_name="currency")
    has_receipt = django_filters.BooleanFilter(method="filter_has_receipt")
    refund_status = django_filters.ChoiceFilter(
        field_name="refund_status",
        choices=[
            ("NONE", "No Refunds"),
            ("PARTIAL", "Partially Refunded"),
            ("FULL", "Fully Refunded"),
        ],
    )

    # Date range
    payment_date_from = django_filters.DateFilter(
        field_name="payment_date", lookup_expr="gte"
    )
    payment_date_to = django_filters.DateFilter(
        field_name="payment_date", lookup_expr="lte"
    )
    created_from = django_filters.DateFilter(
        field_name="created_on", lookup_expr="gte"
    )
    created_to = django_filters.DateFilter(
        field_name="created_on", lookup_expr="lte"
    )

    # Amount range
    amount_min = django_filters.NumberFilter(field_name="amount", lookup_expr="gte")
    amount_max = django_filters.NumberFilter(field_name="amount", lookup_expr="lte")

    class Meta:
        model = Payment
        fields = [
            "method",
            "status",
            "customer",
            "customer_name",
            "invoice",
            "invoice_number",
            "order",
            "currency",
            "has_receipt",
            "refund_status",
            "payment_date_from",
            "payment_date_to",
            "created_from",
            "created_to",
            "amount_min",
            "amount_max",
        ]

    def filter_customer_name(self, queryset, name, value):
        return queryset.filter(
            Q(customer__first_name__icontains=value)
            | Q(customer__last_name__icontains=value)
            | Q(customer__business_name__icontains=value)
        )

    def filter_has_receipt(self, queryset, name, value):
        if value:
            return queryset.filter(receipt__isnull=False)
        return queryset.filter(receipt__isnull=True)


class RefundFilter(django_filters.FilterSet):
    """Filter set for Refund list views."""

    status = django_filters.MultipleChoiceFilter(choices=RefundStatus.choices)
    reason = django_filters.CharFilter(field_name="reason")
    payment = django_filters.UUIDFilter(field_name="original_payment__id")
    customer = django_filters.UUIDFilter(field_name="customer__id")
    refund_method = django_filters.CharFilter(field_name="refund_method")
    created_from = django_filters.DateFilter(
        field_name="created_on", lookup_expr="gte"
    )
    created_to = django_filters.DateFilter(
        field_name="created_on", lookup_expr="lte"
    )
    amount_min = django_filters.NumberFilter(field_name="amount", lookup_expr="gte")
    amount_max = django_filters.NumberFilter(field_name="amount", lookup_expr="lte")

    class Meta:
        model = Refund
        fields = [
            "status",
            "reason",
            "payment",
            "customer",
            "refund_method",
            "created_from",
            "created_to",
            "amount_min",
            "amount_max",
        ]
