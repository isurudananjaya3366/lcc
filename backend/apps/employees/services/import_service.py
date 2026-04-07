"""
Employee Import Service.

Handles bulk import of employee data from CSV files.
"""

import csv
import io
import logging

from django.core.exceptions import ValidationError
from django.db import transaction

logger = logging.getLogger(__name__)


class EmployeeImportService:
    """Service class for importing employee data from CSV files."""

    REQUIRED_COLUMNS = [
        "first_name",
        "last_name",
        "nic_number",
    ]

    OPTIONAL_COLUMNS = [
        "middle_name",
        "email",
        "personal_email",
        "mobile",
        "phone",
        "date_of_birth",
        "gender",
        "marital_status",
        "employment_type",
        "department",
        "designation",
        "hire_date",
    ]

    @classmethod
    def import_from_csv(cls, file_obj, user=None):
        """
        Import employees from a CSV file.

        Args:
            file_obj: File-like object (CSV).
            user: User performing the import.

        Returns:
            dict with created, errors, and total counts.
        """
        from apps.employees.services.employee_service import EmployeeService

        results = {"created": 0, "errors": [], "total": 0}

        try:
            if hasattr(file_obj, "read"):
                content = file_obj.read()
                if isinstance(content, bytes):
                    content = content.decode("utf-8-sig")
            else:
                content = str(file_obj)

            reader = csv.DictReader(io.StringIO(content))
            rows = list(reader)
        except Exception as e:
            results["errors"].append({"row": 0, "error": f"Failed to parse CSV: {e}"})
            return results

        results["total"] = len(rows)

        # Validate headers
        if rows:
            headers = set(rows[0].keys())
            missing = set(cls.REQUIRED_COLUMNS) - headers
            if missing:
                results["errors"].append({
                    "row": 0,
                    "error": f"Missing required columns: {', '.join(missing)}",
                })
                return results

        for row_num, row in enumerate(rows, start=2):
            try:
                data = cls._clean_row(row)
                cls._validate_row(data, row_num)

                with transaction.atomic():
                    EmployeeService.create_employee(data, user=user)
                    results["created"] += 1

            except Exception as e:
                results["errors"].append({"row": row_num, "error": str(e)})

        logger.info(
            "Import completed: %d created, %d errors out of %d total",
            results["created"], len(results["errors"]), results["total"],
        )
        return results

    @classmethod
    def _clean_row(cls, row):
        """Clean and prepare a CSV row for employee creation."""
        data = {}
        for key, value in row.items():
            key = key.strip().lower().replace(" ", "_")
            value = value.strip() if value else ""
            if value:
                data[key] = value
        return data

    @classmethod
    def _validate_row(cls, data, row_num):
        """Validate a single import row."""
        missing = [col for col in cls.REQUIRED_COLUMNS if not data.get(col)]
        if missing:
            raise ValidationError(
                f"Row {row_num}: Missing required fields: {', '.join(missing)}"
            )

    @classmethod
    def get_template_headers(cls):
        """Return CSV template headers."""
        return cls.REQUIRED_COLUMNS + cls.OPTIONAL_COLUMNS

    @classmethod
    def validate_import_file(cls, file_obj):
        """
        Validate an import file without saving.

        Args:
            file_obj: File-like object (CSV).

        Returns:
            dict with 'valid', 'errors', 'row_count', 'columns' keys.
        """
        errors = []
        try:
            if hasattr(file_obj, "read"):
                content = file_obj.read()
                if isinstance(content, bytes):
                    content = content.decode("utf-8-sig")
                # Reset file pointer for future reads
                if hasattr(file_obj, "seek"):
                    file_obj.seek(0)
            else:
                content = str(file_obj)

            reader = csv.DictReader(io.StringIO(content))
            columns = reader.fieldnames or []

            missing = [col for col in cls.REQUIRED_COLUMNS if col not in columns]
            if missing:
                errors.append(f"Missing required columns: {', '.join(missing)}")

            rows = list(reader)
            if not rows:
                errors.append("File contains no data rows.")

            for i, row in enumerate(rows, start=2):
                for col in cls.REQUIRED_COLUMNS:
                    if not row.get(col, "").strip():
                        errors.append(f"Row {i}: '{col}' is required.")

            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "row_count": len(rows),
                "columns": list(columns),
            }

        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Failed to parse file: {str(e)}"],
                "row_count": 0,
                "columns": [],
            }

    @classmethod
    def preview_import(cls, file_obj, max_rows=10):
        """
        Preview import data without saving.

        Args:
            file_obj: File-like object (CSV).
            max_rows: Maximum number of rows to return.

        Returns:
            dict with 'rows', 'total_count', 'columns' keys.
        """
        try:
            if hasattr(file_obj, "read"):
                content = file_obj.read()
                if isinstance(content, bytes):
                    content = content.decode("utf-8-sig")
                if hasattr(file_obj, "seek"):
                    file_obj.seek(0)
            else:
                content = str(file_obj)

            reader = csv.DictReader(io.StringIO(content))
            columns = reader.fieldnames or []
            rows = []

            all_rows = list(reader)
            for row in all_rows[:max_rows]:
                rows.append(dict(row))

            return {
                "rows": rows,
                "total_count": len(all_rows),
                "columns": list(columns),
            }

        except Exception as e:
            return {
                "rows": [],
                "total_count": 0,
                "columns": [],
                "error": str(e),
            }
