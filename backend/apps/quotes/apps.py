from django.apps import AppConfig


class QuotesConfig(AppConfig):
    """Configuration for the Quote Management application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.quotes"
    label = "quotes"
    verbose_name = "Quote Management"

    def ready(self):
        from apps.quotes.signals.recalculation import connect_signals

        connect_signals()
