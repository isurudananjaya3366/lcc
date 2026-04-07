"""
Filters for Credit, Loyalty, and Store Credit APIs.

Provides CreditFilterSet, LoyaltyFilterSet, and StoreCreditFilterSet
for use with DjangoFilterBackend.
"""

from datetime import date, timedelta

import django_filters

from apps.credit.models import CustomerCredit, CustomerLoyalty, StoreCredit


class CreditFilterSet(django_filters.FilterSet):
    """Filter set for customer credit accounts."""

    status = django_filters.ChoiceFilter(
        choices=lambda: CustomerCredit._meta.get_field("status").choices,
    )
    min_balance = django_filters.NumberFilter(
        field_name="outstanding_balance", lookup_expr="gte"
    )
    max_balance = django_filters.NumberFilter(
        field_name="outstanding_balance", lookup_expr="lte"
    )
    min_credit_limit = django_filters.NumberFilter(
        field_name="credit_limit", lookup_expr="gte"
    )
    max_credit_limit = django_filters.NumberFilter(
        field_name="credit_limit", lookup_expr="lte"
    )
    customer = django_filters.UUIDFilter(field_name="customer__id")
    payment_terms_days = django_filters.NumberFilter(
        field_name="payment_terms_days"
    )
    overdue = django_filters.BooleanFilter(method="filter_overdue")

    class Meta:
        model = CustomerCredit
        fields = [
            "status",
            "customer",
            "payment_terms_days",
        ]

    def filter_overdue(self, queryset, name, value):
        """Filter accounts with overdue payments."""
        today = date.today()
        if value:
            return queryset.filter(
                next_payment_due__lt=today,
                outstanding_balance__gt=0,
            )
        return queryset.exclude(
            next_payment_due__lt=today,
            outstanding_balance__gt=0,
        )


class LoyaltyFilterSet(django_filters.FilterSet):
    """Filter set for customer loyalty accounts."""

    status = django_filters.CharFilter(field_name="status")
    program = django_filters.UUIDFilter(field_name="program__id")
    current_tier = django_filters.UUIDFilter(field_name="current_tier__id")
    min_points = django_filters.NumberFilter(
        field_name="points_balance", lookup_expr="gte"
    )
    max_points = django_filters.NumberFilter(
        field_name="points_balance", lookup_expr="lte"
    )
    enrolled_after = django_filters.DateFilter(
        field_name="enrolled_date", lookup_expr="gte"
    )
    enrolled_before = django_filters.DateFilter(
        field_name="enrolled_date", lookup_expr="lte"
    )

    class Meta:
        model = CustomerLoyalty
        fields = [
            "status",
            "program",
            "current_tier",
        ]


class StoreCreditFilterSet(django_filters.FilterSet):
    """Filter set for store credit accounts."""

    created_from = django_filters.ChoiceFilter(
        choices=lambda: StoreCredit._meta.get_field("created_from").choices,
    )
    min_balance = django_filters.NumberFilter(
        field_name="balance", lookup_expr="gte"
    )
    max_balance = django_filters.NumberFilter(
        field_name="balance", lookup_expr="lte"
    )
    is_expired = django_filters.BooleanFilter(method="filter_expired")
    expiring_soon = django_filters.BooleanFilter(method="filter_expiring_soon")
    customer = django_filters.UUIDFilter(field_name="customer__id")

    class Meta:
        model = StoreCredit
        fields = [
            "created_from",
            "currency",
            "customer",
        ]

    def filter_expired(self, queryset, name, value):
        """Filter expired store credits."""
        today = date.today()
        if value:
            return queryset.filter(expiry_date__lt=today)
        return queryset.exclude(expiry_date__lt=today)

    def filter_expiring_soon(self, queryset, name, value):
        """Filter credits expiring within the next 30 days."""
        today = date.today()
        threshold = today + timedelta(days=30)
        if value:
            return queryset.filter(
                expiry_date__gte=today,
                expiry_date__lte=threshold,
            )
        return queryset
