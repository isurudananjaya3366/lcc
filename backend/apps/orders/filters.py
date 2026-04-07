"""
Order filters — django-filter FilterSets (Task 85).
"""

import django_filters

from apps.orders.constants import (
    CurrencyChoice,
    OrderSource,
    OrderStatus,
    PaymentStatus,
)
from apps.orders.models import Order


class OrderFilter(django_filters.FilterSet):
    """FilterSet for the Order model."""

    status = django_filters.MultipleChoiceFilter(choices=OrderStatus.choices)
    source = django_filters.ChoiceFilter(choices=OrderSource.choices)
    payment_status = django_filters.ChoiceFilter(choices=PaymentStatus.choices)
    currency = django_filters.ChoiceFilter(choices=CurrencyChoice.choices)
    customer = django_filters.UUIDFilter(field_name="customer_id")
    created_by = django_filters.UUIDFilter(field_name="created_by_id")

    created_from = django_filters.DateFilter(
        field_name="created_on", lookup_expr="gte"
    )
    created_to = django_filters.DateFilter(
        field_name="created_on", lookup_expr="lte"
    )

    total_min = django_filters.NumberFilter(
        field_name="total_amount", lookup_expr="gte"
    )
    total_max = django_filters.NumberFilter(
        field_name="total_amount", lookup_expr="lte"
    )

    is_draft = django_filters.BooleanFilter()
    is_locked = django_filters.BooleanFilter()

    class Meta:
        model = Order
        fields = [
            "status",
            "source",
            "payment_status",
            "currency",
            "customer",
            "created_by",
            "created_from",
            "created_to",
            "total_min",
            "total_max",
            "is_draft",
            "is_locked",
        ]
