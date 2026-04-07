from django.apps import AppConfig


class AttendanceConfig(AppConfig):
    """Configuration for the Attendance management app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.attendance"
    verbose_name = "Attendance Management"

    def ready(self):
        import apps.attendance.signals  # noqa: F401
