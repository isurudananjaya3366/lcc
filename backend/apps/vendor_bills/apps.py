"""Vendor Bills application configuration."""

from django.apps import AppConfig


class VendorBillsConfig(AppConfig):
    """Configuration for the Vendor Bills application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.vendor_bills"
    label = "vendor_bills"
    verbose_name = "Vendor Bills & Payments"

    def ready(self):
        import apps.vendor_bills.signals  # noqa: F401
