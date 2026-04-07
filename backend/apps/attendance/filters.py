"""Django Filter classes for the Attendance application."""

import django_filters

from apps.attendance.models import (
    AttendanceRecord,
    AttendanceRegularization,
    OvertimeRequest,
    Shift,
)


class ShiftFilter(django_filters.FilterSet):
    """Filter set for Shift model."""

    shift_type = django_filters.CharFilter(field_name="shift_type")
    status = django_filters.CharFilter(field_name="status")
    is_default = django_filters.BooleanFilter(field_name="is_default")
    start_time_gte = django_filters.TimeFilter(
        field_name="start_time", lookup_expr="gte",
    )
    start_time_lte = django_filters.TimeFilter(
        field_name="start_time", lookup_expr="lte",
    )
    work_hours_gte = django_filters.NumberFilter(
        field_name="work_hours", lookup_expr="gte",
    )
    work_hours_lte = django_filters.NumberFilter(
        field_name="work_hours", lookup_expr="lte",
    )

    class Meta:
        model = Shift
        fields = ["shift_type", "status", "is_default"]


class AttendanceRecordFilter(django_filters.FilterSet):
    """Filter set for AttendanceRecord model."""

    employee = django_filters.UUIDFilter(field_name="employee__id")
    shift = django_filters.UUIDFilter(field_name="shift__id")
    status = django_filters.CharFilter(field_name="status")
    date = django_filters.DateFilter(field_name="date")
    date_from = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    date_to = django_filters.DateFilter(field_name="date", lookup_expr="lte")
    is_late = django_filters.BooleanFilter(method="filter_is_late")
    is_early_leave = django_filters.BooleanFilter(method="filter_is_early_leave")
    has_overtime = django_filters.BooleanFilter(method="filter_has_overtime")
    department = django_filters.UUIDFilter(
        field_name="employee__department__id",
    )

    class Meta:
        model = AttendanceRecord
        fields = ["employee", "shift", "status", "date"]

    def filter_is_late(self, queryset, name, value):
        if value:
            return queryset.filter(late_minutes__gt=0)
        return queryset.filter(late_minutes=0)

    def filter_is_early_leave(self, queryset, name, value):
        if value:
            return queryset.filter(early_departure_minutes__gt=0)
        return queryset.filter(early_departure_minutes=0)

    def filter_has_overtime(self, queryset, name, value):
        if value:
            return queryset.filter(overtime_hours__gt=0)
        return queryset.filter(overtime_hours=0)


class RegularizationFilter(django_filters.FilterSet):
    """Filter set for AttendanceRegularization model."""

    employee = django_filters.UUIDFilter(field_name="employee__id")
    status = django_filters.CharFilter(field_name="status")
    date_from = django_filters.DateFilter(
        field_name="attendance_record__date", lookup_expr="gte",
    )
    date_to = django_filters.DateFilter(
        field_name="attendance_record__date", lookup_expr="lte",
    )

    class Meta:
        model = AttendanceRegularization
        fields = ["employee", "status"]


class OvertimeRequestFilter(django_filters.FilterSet):
    """Filter set for OvertimeRequest model."""

    employee = django_filters.UUIDFilter(field_name="employee__id")
    status = django_filters.CharFilter(field_name="status")
    date = django_filters.DateFilter(field_name="date")
    date_from = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    date_to = django_filters.DateFilter(field_name="date", lookup_expr="lte")

    class Meta:
        model = OvertimeRequest
        fields = ["employee", "status", "date"]
