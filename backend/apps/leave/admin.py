from django.contrib import admin

from apps.leave.models import Holiday, LeaveBalance, LeavePolicy, LeaveRequest, LeaveType


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "category", "default_days_per_year", "is_paid", "is_active"]
    list_filter = ["category", "is_active", "is_paid", "applicable_gender"]
    search_fields = ["name", "code"]
    readonly_fields = ["id", "created_on", "updated_on"]


@admin.register(LeavePolicy)
class LeavePolicyAdmin(admin.ModelAdmin):
    list_display = ["leave_type", "applies_to", "effective_from", "effective_to", "is_active"]
    list_filter = ["applies_to", "is_active"]
    search_fields = ["leave_type__name"]
    readonly_fields = ["id", "created_on", "updated_on"]


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ["employee", "leave_type", "year", "opening_balance", "used_days", "pending_days", "is_active"]
    list_filter = ["year", "is_active", "leave_type"]
    search_fields = ["employee__first_name", "employee__last_name", "employee__employee_id"]
    readonly_fields = ["id", "created_on", "updated_on"]


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ["employee", "leave_type", "start_date", "end_date", "total_days", "status", "submitted_at"]
    list_filter = ["status", "leave_type", "is_half_day"]
    search_fields = ["employee__first_name", "employee__last_name", "employee__employee_id"]
    readonly_fields = ["id", "created_on", "updated_on"]
    date_hierarchy = "start_date"


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ["name", "date", "holiday_type", "applies_to", "is_active", "is_recurring"]
    list_filter = ["holiday_type", "applies_to", "is_active", "is_recurring"]
    search_fields = ["name"]
    readonly_fields = ["id", "created_on", "updated_on"]
    date_hierarchy = "date"
