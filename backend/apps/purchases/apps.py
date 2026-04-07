"""Purchases application configuration."""

from django.apps import AppConfig


class PurchasesConfig(AppConfig):
    """Configuration for the Purchases application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.purchases"
    label = "purchases"
    verbose_name = "Purchase Orders"

    def ready(self):
        import apps.purchases.signals  # noqa: F401
