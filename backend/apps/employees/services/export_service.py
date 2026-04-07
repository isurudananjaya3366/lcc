"""
Employee Export Service.

Handles exporting employee data to CSV format with filtering support.
"""

import csv
import io
import logging

logger = logging.getLogger(__name__)


class EmployeeExportService:
    """Service class for exporting employee data to CSV."""

    DEFAULT_FIELDS = [
        "employee_id",
        "first_name",
        "last_name",
        "middle_name",
        "nic_number",
        "email",
        "mobile",
        "gender",
        "date_of_birth",
        "employment_type",
        "status",
        "department",
        "designation",
        "hire_date",
    ]

    @classmethod
    def export_to_csv(cls, queryset=None, fields=None, filters=None):
        """
        Export employees to CSV format.

        Args:
            queryset: Employee queryset (defaults to all).
            fields: List of field names to export.
            filters: dict of filters to apply.

        Returns:
            StringIO object containing CSV data.
        """
        from apps.employees.models import Employee
        from apps.employees.services.search_service import EmployeeSearchService

        if queryset is None:
            queryset = Employee.objects.all()

        # Apply filters
        if filters:
            if filters.get("status"):
                queryset = EmployeeSearchService.filter_by_status(
                    queryset, filters["status"]
                )
            if filters.get("department"):
                queryset = EmployeeSearchService.filter_by_department(
                    queryset, filters["department"]
                )
            if filters.get("employment_type"):
                queryset = EmployeeSearchService.filter_by_employment_type(
                    queryset, filters["employment_type"]
                )

        fields = fields or cls.DEFAULT_FIELDS
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(fields)

        # Write data
        for employee in queryset.values_list(*fields):
            writer.writerow(employee)

        output.seek(0)

        logger.info("Exported %d employees to CSV", queryset.count())
        return output

    @classmethod
    def get_employee_summary(cls, queryset=None):
        """
        Generate employee summary statistics.

        Returns:
            dict with employee counts by status, department, etc.
        """
        from django.db.models import Count
        from apps.employees.models import Employee

        if queryset is None:
            queryset = Employee.objects.all()

        return {
            "total": queryset.count(),
            "by_status": dict(
                queryset.values_list("status")
                .annotate(count=Count("id"))
                .values_list("status", "count")
            ),
            "by_employment_type": dict(
                queryset.values_list("employment_type")
                .annotate(count=Count("id"))
                .values_list("employment_type", "count")
            ),
            "by_department": dict(
                queryset.values_list("department")
                .annotate(count=Count("id"))
                .values_list("department", "count")
            ),
        }
