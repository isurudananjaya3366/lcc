"""HR application configuration."""

from django.apps import AppConfig


class HrConfig(AppConfig):
    """Configuration for the HR application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.hr"
    label = "hr"
    verbose_name = "Human Resources"
