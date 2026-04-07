"""
Users application configuration.

Provides custom user model, authentication, and user management
for the LankaCommerce Cloud platform.
"""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Configuration for the Users application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"
    label = "users"
    verbose_name = "User Management"

    def ready(self):
        """Import signal handlers when the app is ready."""
        import apps.users.signals  # noqa: F401
