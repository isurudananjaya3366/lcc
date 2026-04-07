"""Credit & Loyalty application configuration."""

from django.apps import AppConfig


class CreditConfig(AppConfig):
    """Configuration for the Credit & Loyalty application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.credit"
    label = "credit"
    verbose_name = "Customer Credit & Loyalty"

    def ready(self):
        import apps.credit.signals  # noqa: F401
