"""Django admin configuration for the analytics application."""

from django.contrib import admin

from apps.analytics.models import (
    ReportDefinition,
    ReportInstance,
    SavedReport,
    ScheduledReport,
    ScheduleHistory,
)


@admin.register(ReportDefinition)
class ReportDefinitionAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "category", "is_active", "created_on")
    list_filter = ("category", "is_active", "created_on")
    search_fields = ("code", "name", "description")
    ordering = ("category", "name")


@admin.register(ReportInstance)
class ReportInstanceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "report_name",
        "output_format",
        "status",
        "user",
        "generated_at",
    )
    list_filter = ("status", "output_format", "generated_at")
    search_fields = ("report_definition__name",)
    ordering = ("-created_on",)

    def report_name(self, obj):
        return obj.report_definition.name if obj.report_definition else "-"

    report_name.short_description = "Report"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(SavedReport)
class SavedReportAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "report_definition",
        "owner",
        "is_public",
        "created_on",
    )
    list_filter = ("is_public", "created_on")
    search_fields = ("name",)
    list_select_related = ("report_definition", "owner")


@admin.register(ScheduledReport)
class ScheduledReportAdmin(admin.ModelAdmin):
    list_display = (
        "saved_report",
        "frequency",
        "is_active",
        "next_run",
        "last_status",
        "created_by",
    )
    list_filter = ("frequency", "is_active", "last_status")
    list_select_related = ("saved_report", "created_by")
    actions = ["activate_schedules", "deactivate_schedules"]

    @admin.action(description="Activate selected schedules")
    def activate_schedules(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="Deactivate selected schedules")
    def deactivate_schedules(self, request, queryset):
        queryset.update(is_active=False)


@admin.register(ScheduleHistory)
class ScheduleHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "scheduled_report",
        "status",
        "run_at",
        "email_sent",
        "execution_time_seconds",
    )
    list_filter = ("status", "email_sent")
    ordering = ("-run_at",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
