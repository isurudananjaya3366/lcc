"""Invoices application configuration."""

from django.apps import AppConfig


class InvoicesConfig(AppConfig):
    """Configuration for the Invoices application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.invoices"
    label = "invoices"
    verbose_name = "Invoice Management"

    def ready(self):
        from apps.invoices.signals import recalculation  # noqa: F401
