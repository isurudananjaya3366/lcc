"""Integrations application configuration."""

from django.apps import AppConfig


class IntegrationsConfig(AppConfig):
    """Configuration for the Integrations application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.integrations"
    label = "integrations"
    verbose_name = "Third-Party Integrations"
