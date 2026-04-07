from django.apps import AppConfig


class LeaveConfig(AppConfig):
    """Configuration for the Leave Management app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.leave"
    verbose_name = "Leave Management"
