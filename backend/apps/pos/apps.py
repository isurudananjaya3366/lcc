from django.apps import AppConfig


class PosConfig(AppConfig):
    """Configuration for the Point of Sale application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.pos"
    label = "pos"
    verbose_name = "Point of Sale"
