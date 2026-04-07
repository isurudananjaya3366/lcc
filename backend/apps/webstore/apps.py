"""Webstore application configuration."""

from django.apps import AppConfig


class WebstoreConfig(AppConfig):
    """Configuration for the Webstore application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.webstore"
    label = "webstore"
    verbose_name = "E-commerce Webstore"
