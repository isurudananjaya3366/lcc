"""Vendors application configuration."""

from django.apps import AppConfig


class VendorsConfig(AppConfig):
    """Configuration for the Vendors application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.vendors"
    label = "vendors"
    verbose_name = "Vendor Management"

    def ready(self):
        import apps.vendors.signals  # noqa: F401
