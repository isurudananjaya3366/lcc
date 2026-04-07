"""Employees views package."""

from apps.employees.views.document_viewset import DocumentViewSet
from apps.employees.views.employee_viewset import EmployeeViewSet

__all__ = [
    "DocumentViewSet",
    "EmployeeViewSet",
]
