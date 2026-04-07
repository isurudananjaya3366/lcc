"""Payments application configuration."""

from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    """Configuration for the Payments application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.payments"
    label = "payments"
    verbose_name = "Payment Management"
