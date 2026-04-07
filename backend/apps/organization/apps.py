from django.apps import AppConfig


class OrganizationConfig(AppConfig):
    """Configuration for the Organization application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.organization"
    label = "organization"
    verbose_name = "Organization Management"

    def ready(self):
        import apps.organization.signals  # noqa: F401
