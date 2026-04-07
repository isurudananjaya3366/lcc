from django.contrib import admin

from apps.attendance.models import (
    AttendanceRecord,
    AttendanceRegularization,
    AttendanceSettings,
    OvertimeRequest,
    Shift,
    ShiftSchedule,
)


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "shift_type", "status", "start_time", "end_time", "work_hours"]
    list_filter = ["shift_type", "status", "is_default"]
    search_fields = ["name", "code"]
    readonly_fields = ["id", "created_on", "updated_on"]


@admin.register(ShiftSchedule)
class ShiftScheduleAdmin(admin.ModelAdmin):
    list_display = ["name", "shift", "employee", "department", "effective_from", "effective_to", "is_active"]
    list_filter = ["is_active", "is_recurring"]
    search_fields = ["name"]
    readonly_fields = ["id", "created_on", "updated_on"]


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ["employee", "date", "status", "clock_in", "clock_out", "effective_hours", "late_minutes"]
    list_filter = ["status", "clock_in_method", "date"]
    search_fields = ["employee__first_name", "employee__last_name", "employee__employee_id"]
    readonly_fields = ["id", "created_on", "updated_on"]
    date_hierarchy = "date"


@admin.register(AttendanceRegularization)
class AttendanceRegularizationAdmin(admin.ModelAdmin):
    list_display = ["employee", "attendance_record", "status", "created_on", "approved_by"]
    list_filter = ["status"]
    search_fields = ["employee__first_name", "employee__last_name"]
    readonly_fields = ["id", "created_on", "updated_on"]


@admin.register(OvertimeRequest)
class OvertimeRequestAdmin(admin.ModelAdmin):
    list_display = ["employee", "date", "planned_hours", "actual_hours", "status", "approved_by"]
    list_filter = ["status", "date"]
    search_fields = ["employee__first_name", "employee__last_name"]
    readonly_fields = ["id", "created_on", "updated_on"]
    date_hierarchy = "date"


@admin.register(AttendanceSettings)
class AttendanceSettingsAdmin(admin.ModelAdmin):
    list_display = ["tenant", "default_late_grace_minutes", "require_overtime_approval", "enable_geofencing"]
    readonly_fields = ["id", "created_on", "updated_on"]
