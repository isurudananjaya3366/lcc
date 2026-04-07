from django.apps import AppConfig


class PayrollConfig(AppConfig):
    """Configuration for the Payroll Management app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.payroll"
    verbose_name = "Payroll Management"

    def ready(self):
        import apps.payroll.signals  # noqa: F401
