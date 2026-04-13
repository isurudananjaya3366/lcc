"""Dashboard admin configuration."""

from django.contrib import admin

from apps.dashboard.models import DashboardLayout, KPIAlert, KPIDefinition


@admin.register(KPIDefinition)
class KPIDefinitionAdmin(admin.ModelAdmin):
    """Admin for KPI definitions."""

    list_display = ("name", "code", "category", "default_widget_type", "is_active")
    list_filter = ("category", "default_widget_type", "is_active")
    search_fields = ("name", "code", "description")
    ordering = ("category", "name")


@admin.register(KPIAlert)
class KPIAlertAdmin(admin.ModelAdmin):
    """Admin for KPI alerts."""

    list_display = ("kpi", "warning_threshold", "critical_threshold", "is_active")
    list_filter = ("is_active", "notify_email", "notify_dashboard")
    search_fields = ("kpi__name",)


@admin.register(DashboardLayout)
class DashboardLayoutAdmin(admin.ModelAdmin):
    """Admin for dashboard layouts."""

    list_display = ("user", "name", "is_default", "created_at")
    list_filter = ("is_default",)
    search_fields = ("user__email", "name")
