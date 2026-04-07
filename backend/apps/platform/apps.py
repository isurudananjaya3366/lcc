"""
Platform application configuration.

Provides public schema models for platform-wide settings,
subscription plans, feature flags, audit logging, and billing
for the LankaCommerce Cloud platform.
"""

from django.apps import AppConfig


class PlatformConfig(AppConfig):
    """Configuration for the Platform application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.platform"
    label = "platform"
    verbose_name = "Platform Services"
