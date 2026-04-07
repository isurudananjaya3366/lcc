"""Employees application configuration."""

from django.apps import AppConfig


class EmployeesConfig(AppConfig):
    """Configuration for the Employees application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.employees"
    label = "employees"
    verbose_name = "Employee Management"

    def ready(self):
        import apps.employees.signals  # noqa: F401
