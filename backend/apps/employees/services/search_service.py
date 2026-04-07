"""
Employee Search Service.

Provides search, filtering, and query capabilities for employee records.
"""

from django.db.models import Q


class EmployeeSearchService:
    """Service class for searching and filtering employees."""

    @classmethod
    def search(cls, queryset, query):
        """
        Full-text search across employee fields.

        Args:
            queryset: Base Employee queryset.
            query: Search string.

        Returns:
            Filtered queryset.
        """
        if not query:
            return queryset

        return queryset.filter(
            Q(employee_id__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(middle_name__icontains=query)
            | Q(nic_number__icontains=query)
            | Q(email__icontains=query)
            | Q(mobile__icontains=query)
            | Q(department__name__icontains=query)
            | Q(designation__title__icontains=query)
        )

    @classmethod
    def filter_by_status(cls, queryset, status):
        """Filter employees by status."""
        if not status:
            return queryset
        if isinstance(status, (list, tuple)):
            return queryset.filter(status__in=status)
        return queryset.filter(status=status)

    @classmethod
    def filter_by_department(cls, queryset, department):
        """Filter employees by department."""
        if not department:
            return queryset
        return queryset.filter(department__name__icontains=department)

    @classmethod
    def filter_by_employment_type(cls, queryset, employment_type):
        """Filter employees by employment type."""
        if not employment_type:
            return queryset
        return queryset.filter(employment_type=employment_type)

    @classmethod
    def filter_active(cls, queryset):
        """Return only active employees."""
        from apps.employees.constants import EMPLOYEE_STATUS_ACTIVE
        return queryset.filter(status=EMPLOYEE_STATUS_ACTIVE)

    @classmethod
    def get_reporting_to(cls, manager_id):
        """Get all employees reporting to a manager."""
        from apps.employees.models import Employee
        return Employee.objects.filter(manager_id=manager_id)

    @classmethod
    def get_employees_with_expiring_documents(cls, days=30):
        """Get employees with documents expiring within given days."""
        from datetime import date, timedelta
        from apps.employees.models import EmployeeDocument

        expiry_threshold = date.today() + timedelta(days=days)
        return EmployeeDocument.objects.filter(
            expiry_date__lte=expiry_threshold,
            expiry_date__gte=date.today(),
        ).select_related("employee")
