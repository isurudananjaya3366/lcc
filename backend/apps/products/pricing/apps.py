from django.apps import AppConfig


class PricingConfig(AppConfig):
    name = "apps.products.pricing"
    default_auto_field = "django.db.models.BigAutoField"
    verbose_name = "Product Pricing"

    def ready(self):
        import apps.products.pricing.signals  # noqa: F401
