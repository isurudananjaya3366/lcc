"""Accounting application configuration."""

from django.apps import AppConfig


class AccountingConfig(AppConfig):
    """Configuration for the Accounting application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounting"
    label = "accounting"
    verbose_name = "Accounting & Finance"
