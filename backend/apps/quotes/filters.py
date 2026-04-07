"""
Quote Filters – django-filter FilterSet for quote list endpoints.
"""

import django_filters

from apps.quotes.constants import CurrencyChoice, QuoteStatus
from apps.quotes.models import Quote


class QuoteFilter(django_filters.FilterSet):
    """FilterSet for the Quote model."""

    status = django_filters.ChoiceFilter(choices=QuoteStatus.choices)
    currency = django_filters.ChoiceFilter(choices=CurrencyChoice.choices)
    customer = django_filters.UUIDFilter(field_name="customer_id")
    created_by = django_filters.UUIDFilter(field_name="created_by_id")

    issue_date_from = django_filters.DateFilter(
        field_name="issue_date", lookup_expr="gte"
    )
    issue_date_to = django_filters.DateFilter(
        field_name="issue_date", lookup_expr="lte"
    )
    valid_until_from = django_filters.DateFilter(
        field_name="valid_until", lookup_expr="gte"
    )
    valid_until_to = django_filters.DateFilter(
        field_name="valid_until", lookup_expr="lte"
    )

    total_min = django_filters.NumberFilter(field_name="total", lookup_expr="gte")
    total_max = django_filters.NumberFilter(field_name="total", lookup_expr="lte")

    is_latest_revision = django_filters.BooleanFilter()

    class Meta:
        model = Quote
        fields = [
            "status",
            "currency",
            "customer",
            "created_by",
            "issue_date_from",
            "issue_date_to",
            "valid_until_from",
            "valid_until_to",
            "total_min",
            "total_max",
            "is_latest_revision",
        ]
