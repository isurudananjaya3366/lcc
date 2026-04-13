"""Dashboard application configuration."""

from django.apps import AppConfig


class DashboardConfig(AppConfig):
    """Configuration for the Dashboard & KPIs application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.dashboard"
    label = "dashboard"
    verbose_name = "Dashboard & KPIs"

    def ready(self):
        from apps.dashboard.signals import register_cache_invalidation_signals

        register_cache_invalidation_signals()
