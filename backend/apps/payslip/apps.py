from django.apps import AppConfig


class PayslipConfig(AppConfig):
    """Configuration for the Payslip Generation app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.payslip"
    verbose_name = "Payslip Generation"
