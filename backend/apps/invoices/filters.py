"""Invoice filters — django-filter FilterSets."""

import django_filters

from apps.invoices.constants import (
    CurrencyChoice,
    InvoiceStatus,
    InvoiceType,
    TaxScheme,
)
from apps.invoices.models import Invoice


class InvoiceFilter(django_filters.FilterSet):
    """FilterSet for the Invoice model."""

    status = django_filters.MultipleChoiceFilter(choices=InvoiceStatus.choices)
    type = django_filters.MultipleChoiceFilter(choices=InvoiceType.choices)
    tax_scheme = django_filters.ChoiceFilter(choices=TaxScheme.choices)
    currency = django_filters.ChoiceFilter(choices=CurrencyChoice.choices)
    customer = django_filters.UUIDFilter(field_name="customer_id")
    order = django_filters.UUIDFilter(field_name="order_id")
    created_by = django_filters.UUIDFilter(field_name="created_by_id")

    issue_date_from = django_filters.DateFilter(
        field_name="issue_date", lookup_expr="gte"
    )
    issue_date_to = django_filters.DateFilter(
        field_name="issue_date", lookup_expr="lte"
    )
    due_date_from = django_filters.DateFilter(
        field_name="due_date", lookup_expr="gte"
    )
    due_date_to = django_filters.DateFilter(
        field_name="due_date", lookup_expr="lte"
    )
    created_from = django_filters.DateFilter(
        field_name="created_on", lookup_expr="gte"
    )
    created_to = django_filters.DateFilter(
        field_name="created_on", lookup_expr="lte"
    )

    total_min = django_filters.NumberFilter(
        field_name="total", lookup_expr="gte"
    )
    total_max = django_filters.NumberFilter(
        field_name="total", lookup_expr="lte"
    )
    balance_min = django_filters.NumberFilter(
        field_name="balance_due", lookup_expr="gte"
    )
    balance_max = django_filters.NumberFilter(
        field_name="balance_due", lookup_expr="lte"
    )

    is_overdue = django_filters.BooleanFilter(method="filter_overdue")

    class Meta:
        model = Invoice
        fields = [
            "status",
            "type",
            "tax_scheme",
            "currency",
            "customer",
            "order",
            "created_by",
            "issue_date_from",
            "issue_date_to",
            "due_date_from",
            "due_date_to",
            "created_from",
            "created_to",
            "total_min",
            "total_max",
            "balance_min",
            "balance_max",
            "is_overdue",
        ]

    def filter_overdue(self, queryset, name, value):
        if value:
            from django.utils import timezone
            return queryset.filter(
                due_date__lt=timezone.now().date(),
                balance_due__gt=0,
            ).exclude(status__in=["CANCELLED", "VOID", "PAID"])
        return queryset
