"""Vendor filter set for list views."""

import django_filters
from django.db.models import Q

from apps.vendors.models import Vendor


class VendorFilter(django_filters.FilterSet):
    """Filter set for Vendor list view."""

    status = django_filters.CharFilter(field_name="status", lookup_expr="exact")
    status__in = django_filters.BaseInFilter(field_name="status", lookup_expr="in")
    vendor_type = django_filters.CharFilter(field_name="vendor_type", lookup_expr="exact")
    vendor_type__in = django_filters.BaseInFilter(field_name="vendor_type", lookup_expr="in")
    province = django_filters.CharFilter(field_name="province", lookup_expr="iexact")
    district = django_filters.CharFilter(field_name="district", lookup_expr="iexact")
    is_preferred_vendor = django_filters.BooleanFilter(field_name="is_preferred_vendor")
    is_local_vendor = django_filters.BooleanFilter(field_name="is_local_vendor")

    rating_min = django_filters.NumberFilter(field_name="rating", lookup_expr="gte")
    rating_max = django_filters.NumberFilter(field_name="rating", lookup_expr="lte")

    created_from = django_filters.DateFilter(field_name="created_on", lookup_expr="gte")
    created_to = django_filters.DateFilter(field_name="created_on", lookup_expr="lte")
    created_after = django_filters.DateFilter(field_name="created_on", lookup_expr="gte")
    created_before = django_filters.DateFilter(field_name="created_on", lookup_expr="lte")

    total_spend_min = django_filters.NumberFilter(field_name="total_spend", lookup_expr="gte")
    total_spend_max = django_filters.NumberFilter(field_name="total_spend", lookup_expr="lte")

    tags = django_filters.CharFilter(method="filter_tags")
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Vendor
        fields: list[str] = []

    def filter_tags(self, queryset, name, value):
        """Filter by tag contained in JSON tags field."""
        return queryset.filter(tags__icontains=value)

    def filter_search(self, queryset, name, value):
        """Quick search across key fields."""
        return queryset.filter(
            Q(vendor_code__icontains=value)
            | Q(company_name__icontains=value)
            | Q(display_name__icontains=value)
            | Q(primary_email__icontains=value)
            | Q(primary_phone__icontains=value)
            | Q(tax_id__icontains=value)
        )
