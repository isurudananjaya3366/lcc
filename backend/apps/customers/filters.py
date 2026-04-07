"""
Customer filtering with django-filter.

Provides comprehensive filtering for the customer list API
including status, type, tags, date ranges, and financial fields.
"""

import django_filters

from apps.customers.models import Customer


class CustomerFilter(django_filters.FilterSet):
    """Filter set for Customer list view."""

    # Exact / choice filters
    status = django_filters.CharFilter(field_name="status", lookup_expr="exact")
    status__in = django_filters.BaseInFilter(field_name="status", lookup_expr="in")
    customer_type = django_filters.CharFilter(
        field_name="customer_type", lookup_expr="exact"
    )
    customer_type__in = django_filters.BaseInFilter(
        field_name="customer_type", lookup_expr="in"
    )
    source = django_filters.CharFilter(field_name="source", lookup_expr="exact")

    # Tags
    tags = django_filters.CharFilter(method="filter_by_tag_name")
    tags__in = django_filters.CharFilter(method="filter_by_tag_names")

    # Date range
    created_from = django_filters.DateFilter(
        field_name="created_on", lookup_expr="gte"
    )
    created_to = django_filters.DateFilter(
        field_name="created_on", lookup_expr="lte"
    )

    # Financial ranges
    total_purchases_min = django_filters.NumberFilter(
        field_name="total_purchases", lookup_expr="gte"
    )
    total_purchases_max = django_filters.NumberFilter(
        field_name="total_purchases", lookup_expr="lte"
    )
    outstanding_balance_min = django_filters.NumberFilter(
        field_name="outstanding_balance", lookup_expr="gte"
    )
    outstanding_balance_max = django_filters.NumberFilter(
        field_name="outstanding_balance", lookup_expr="lte"
    )

    # Boolean convenience
    has_outstanding = django_filters.BooleanFilter(method="filter_has_outstanding")
    is_active = django_filters.BooleanFilter(field_name="is_active")

    # Geography
    province = django_filters.CharFilter(
        field_name="billing_state_province", lookup_expr="iexact"
    )
    district = django_filters.CharFilter(
        field_name="billing_city", lookup_expr="iexact"
    )

    # Text search
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Customer
        fields: list[str] = []

    # ── Custom filter methods ────────────────────────────────────────

    def filter_by_tag_name(self, queryset, name, value):
        """Filter by a single tag name."""
        return queryset.filter(
            tag_assignments__tag__name__iexact=value,
            tag_assignments__tag__is_active=True,
        ).distinct()

    def filter_by_tag_names(self, queryset, name, value):
        """Filter by comma-separated tag names (OR logic)."""
        tag_names = [t.strip() for t in value.split(",") if t.strip()]
        if not tag_names:
            return queryset
        return queryset.filter(
            tag_assignments__tag__name__in=tag_names,
            tag_assignments__tag__is_active=True,
        ).distinct()

    def filter_has_outstanding(self, queryset, name, value):
        """Filter customers with (or without) outstanding balance."""
        if value:
            return queryset.filter(outstanding_balance__gt=0)
        return queryset.filter(outstanding_balance__lte=0)

    def filter_search(self, queryset, name, value):
        """Quick text search across key fields."""
        from django.db.models import Q

        term = value.strip()
        if not term:
            return queryset
        return queryset.filter(
            Q(first_name__icontains=term)
            | Q(last_name__icontains=term)
            | Q(display_name__icontains=term)
            | Q(business_name__icontains=term)
            | Q(email__icontains=term)
            | Q(customer_code__icontains=term)
        ).distinct()
