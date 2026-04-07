"""Customers application configuration."""

from django.apps import AppConfig


class CustomersConfig(AppConfig):
    """Configuration for the Customers application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.customers"
    label = "customers"
    verbose_name = "Customer Management"
