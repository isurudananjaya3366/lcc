"""Reports application configuration."""

from django.apps import AppConfig


class ReportsConfig(AppConfig):
    """Configuration for the Reports application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.reports"
    label = "reports"
    verbose_name = "Reports & Analytics"
