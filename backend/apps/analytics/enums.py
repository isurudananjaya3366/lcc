"""
Analytics & Reports enumerations.

Defines enumerations for report categories, output formats, and
generation status used across the analytics application.
"""

from django.db import models


class ReportCategory(models.TextChoices):
    """Categories for organizing business reports."""

    SALES = "SALES", "Sales"
    INVENTORY = "INVENTORY", "Inventory"
    PURCHASE = "PURCHASE", "Purchase"
    CUSTOMER = "CUSTOMER", "Customer"
    STAFF = "STAFF", "Staff"
    FINANCIAL = "FINANCIAL", "Financial"
    TAX = "TAX", "Tax & Compliance"


class ReportFormat(models.TextChoices):
    """Output formats for generated reports."""

    PDF = "PDF", "PDF"
    EXCEL = "EXCEL", "Excel"
    CSV = "CSV", "CSV"
    JSON = "JSON", "JSON"
    HTML = "HTML", "HTML"

    @classmethod
    def get_file_extension(cls, fmt: str) -> str:
        """Return the file extension for a given format."""
        extensions = {
            cls.PDF: ".pdf",
            cls.EXCEL: ".xlsx",
            cls.CSV: ".csv",
            cls.JSON: ".json",
            cls.HTML: ".html",
        }
        return extensions.get(fmt, ".dat")

    @classmethod
    def get_content_type(cls, fmt: str) -> str:
        """Return the MIME content type for a given format."""
        content_types = {
            cls.PDF: "application/pdf",
            cls.EXCEL: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            cls.CSV: "text/csv",
            cls.JSON: "application/json",
            cls.HTML: "text/html",
        }
        return content_types.get(fmt, "application/octet-stream")


class ReportStatus(models.TextChoices):
    """Status of a report generation process."""

    PENDING = "PENDING", "Pending"
    GENERATING = "GENERATING", "Generating"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"
    CANCELLED = "CANCELLED", "Cancelled"

    @classmethod
    def is_terminal(cls, status: str) -> bool:
        """Check if status is final (no further processing)."""
        return status in [cls.COMPLETED, cls.FAILED, cls.CANCELLED]

    @classmethod
    def is_successful(cls, status: str) -> bool:
        """Check if generation succeeded."""
        return status == cls.COMPLETED


class ScheduleFrequency(models.TextChoices):
    """Frequency options for scheduled reports."""

    DAILY = "DAILY", "Daily"
    WEEKLY = "WEEKLY", "Weekly"
    MONTHLY = "MONTHLY", "Monthly"
