"""
Tenants application configuration.

Provides multi-tenancy support via django-tenants,
including tenant models, domain management, and
tenant provisioning for the LankaCommerce Cloud platform.
"""

from django.apps import AppConfig


class TenantsConfig(AppConfig):
    """Configuration for the Tenants application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.tenants"
    label = "tenants"
    verbose_name = "Multi-Tenancy"

    def ready(self):
        """Import signal handlers when the app is ready."""
        import apps.tenants.signals  # noqa: F401
