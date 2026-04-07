"""Django Filter classes for the Employees application."""

import django_filters
from django.utils import timezone

from apps.employees.models import Employee, EmployeeDocument


class EmployeeFilter(django_filters.FilterSet):
    """Filter set for Employee model."""

    hired_after = django_filters.DateFilter(field_name="hire_date", lookup_expr="gte")
    hired_before = django_filters.DateFilter(field_name="hire_date", lookup_expr="lte")
    has_user_account = django_filters.BooleanFilter(method="filter_has_user")
    is_on_probation = django_filters.BooleanFilter(method="filter_on_probation")
    manager = django_filters.UUIDFilter(field_name="manager__id")
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Employee
        fields = [
            "status",
            "employment_type",
            "gender",
            "department",
            "designation",
            "work_location",
            "work_from_home_eligible",
        ]

    def filter_search(self, queryset, name, value):
        from apps.employees.services.search_service import EmployeeSearchService
        return EmployeeSearchService.search(queryset, value)

    def filter_has_user(self, queryset, name, value):
        if value:
            return queryset.filter(user__isnull=False)
        return queryset.filter(user__isnull=True)

    def filter_on_probation(self, queryset, name, value):
        today = timezone.now().date()
        if value:
            return queryset.filter(
                probation_end_date__isnull=False,
                probation_end_date__gte=today,
                confirmation_date__isnull=True,
            )
        return queryset.exclude(
            probation_end_date__isnull=False,
            probation_end_date__gte=today,
            confirmation_date__isnull=True,
        )


class EmployeeDocumentFilter(django_filters.FilterSet):
    """Filter set for EmployeeDocument model."""

    expiring_within_days = django_filters.NumberFilter(method="filter_expiring")

    class Meta:
        model = EmployeeDocument
        fields = [
            "employee",
            "document_type",
            "is_sensitive",
            "visible_to_employee",
        ]

    def filter_expiring(self, queryset, name, value):
        from datetime import date, timedelta
        expiry_threshold = date.today() + timedelta(days=int(value))
        return queryset.filter(
            expiry_date__lte=expiry_threshold,
            expiry_date__gte=date.today(),
        )
