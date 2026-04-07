"""
HR models package.

Exports all models from the HR application for convenient
importing. Models can be imported directly from apps.hr.models:

    from apps.hr.models import Employee
"""

from apps.hr.models.employee import Employee

__all__ = [
    "Employee",
]
