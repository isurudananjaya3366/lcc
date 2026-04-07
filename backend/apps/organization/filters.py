"""Django Filter classes for the Organization application."""

import django_filters
from django.db.models import Q

from apps.organization.models import Department, Designation


class DepartmentFilter(django_filters.FilterSet):
    """Filter set for Department model."""

    status = django_filters.CharFilter(field_name="status")
    has_parent = django_filters.BooleanFilter(
        field_name="parent", lookup_expr="isnull", exclude=True,
    )
    has_manager = django_filters.BooleanFilter(
        field_name="manager", lookup_expr="isnull", exclude=True,
    )
    has_budget = django_filters.BooleanFilter(method="filter_has_budget")
    level_gte = django_filters.NumberFilter(field_name="level", lookup_expr="gte")
    level_lte = django_filters.NumberFilter(field_name="level", lookup_expr="lte")
    parent = django_filters.UUIDFilter(field_name="parent__id")

    class Meta:
        model = Department
        fields = ["status", "parent"]

    def filter_has_budget(self, queryset, name, value):
        if value:
            return queryset.filter(annual_budget__isnull=False, annual_budget__gt=0)
        return queryset.filter(Q(annual_budget__isnull=True) | Q(annual_budget=0))


class DesignationFilter(django_filters.FilterSet):
    """Filter set for Designation model."""

    status = django_filters.CharFilter(field_name="status")
    level = django_filters.CharFilter(field_name="level")
    department = django_filters.UUIDFilter(field_name="department__id")
    is_manager = django_filters.BooleanFilter(field_name="is_manager")
    has_salary_range = django_filters.BooleanFilter(method="filter_has_salary")

    class Meta:
        model = Designation
        fields = ["status", "level", "department", "is_manager"]

    def filter_has_salary(self, queryset, name, value):
        if value:
            return queryset.filter(
                min_salary__isnull=False, max_salary__isnull=False,
            )
        return queryset.filter(min_salary__isnull=True) | queryset.filter(
            max_salary__isnull=True,
        )
