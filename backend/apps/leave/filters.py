"""Django Filter classes for the Leave Management application."""

import django_filters

from apps.leave.models import Holiday, LeaveBalance, LeaveRequest, LeaveType


class LeaveTypeFilter(django_filters.FilterSet):
    """Filter set for LeaveType model."""

    category = django_filters.CharFilter(field_name="category")
    is_active = django_filters.BooleanFilter(field_name="is_active")
    applicable_gender = django_filters.CharFilter(field_name="applicable_gender")
    is_paid = django_filters.BooleanFilter(field_name="is_paid")

    class Meta:
        model = LeaveType
        fields = ["category", "is_active", "applicable_gender", "is_paid"]


class LeaveBalanceFilter(django_filters.FilterSet):
    """Filter set for LeaveBalance model."""

    employee = django_filters.UUIDFilter(field_name="employee__id")
    leave_type = django_filters.UUIDFilter(field_name="leave_type__id")
    year = django_filters.NumberFilter(field_name="year")
    is_active = django_filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = LeaveBalance
        fields = ["employee", "leave_type", "year", "is_active"]


class LeaveRequestFilter(django_filters.FilterSet):
    """Filter set for LeaveRequest model."""

    employee = django_filters.UUIDFilter(field_name="employee__id")
    leave_type = django_filters.UUIDFilter(field_name="leave_type__id")
    status = django_filters.CharFilter(field_name="status")
    start_date_from = django_filters.DateFilter(
        field_name="start_date", lookup_expr="gte",
    )
    start_date_to = django_filters.DateFilter(
        field_name="start_date", lookup_expr="lte",
    )
    end_date_from = django_filters.DateFilter(
        field_name="end_date", lookup_expr="gte",
    )
    end_date_to = django_filters.DateFilter(
        field_name="end_date", lookup_expr="lte",
    )
    is_half_day = django_filters.BooleanFilter(field_name="is_half_day")
    department = django_filters.UUIDFilter(
        field_name="employee__department__id",
    )

    class Meta:
        model = LeaveRequest
        fields = ["employee", "leave_type", "status"]


class HolidayFilter(django_filters.FilterSet):
    """Filter set for Holiday model."""

    holiday_type = django_filters.CharFilter(field_name="holiday_type")
    applies_to = django_filters.CharFilter(field_name="applies_to")
    is_active = django_filters.BooleanFilter(field_name="is_active")
    year = django_filters.NumberFilter(field_name="year")
    is_recurring = django_filters.BooleanFilter(field_name="is_recurring")
    date_from = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    date_to = django_filters.DateFilter(field_name="date", lookup_expr="lte")
    department = django_filters.UUIDFilter(field_name="department__id")

    class Meta:
        model = Holiday
        fields = ["holiday_type", "applies_to", "is_active", "year"]
