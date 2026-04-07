"""Sales application configuration."""

from django.apps import AppConfig


class SalesConfig(AppConfig):
    """Configuration for the Sales application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.sales"
    label = "sales"
    verbose_name = "Sales Management"
