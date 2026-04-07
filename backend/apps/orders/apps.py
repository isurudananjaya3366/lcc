"""Orders application configuration."""

from django.apps import AppConfig


class OrdersConfig(AppConfig):
    """Configuration for the Orders application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.orders"
    label = "orders"
    verbose_name = "Order Management"

    def ready(self):
        from apps.orders.signals.recalculation import connect_signals

        connect_signals()
