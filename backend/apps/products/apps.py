"""Products application configuration."""

from django.apps import AppConfig


class ProductsConfig(AppConfig):
    """Configuration for the Products application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.products"
    label = "products"
    verbose_name = "Product Management"

    def ready(self):
        """Register signal handlers when the app is ready."""
        import apps.products.signals  # noqa: F401
        import apps.products.media.signals  # noqa: F401
