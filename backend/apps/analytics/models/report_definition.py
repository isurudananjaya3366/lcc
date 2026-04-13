"""
Analytics report definition model.

Defines available report types with their parameters, permissions,
and configuration.
"""

import re

from django.core.exceptions import ValidationError
from django.db import models

from apps.analytics.enums import ReportCategory, ReportFormat
from apps.core.mixins import TimestampMixin, UUIDMixin


def _default_filters():
    return {}


def _default_tags():
    return []


class ReportDefinition(UUIDMixin, TimestampMixin, models.Model):
    """
    Defines an available report type in the analytics system.

    Each definition specifies a report's name, category, available
    filters, required permissions, and default configuration.
    """

    # Identification
    name = models.CharField(
        max_length=200,
        verbose_name="Report Name",
        help_text="Human-readable name for this report.",
    )
    code = models.CharField(
        max_length=100,
        verbose_name="Report Code",
        help_text="Unique code identifier for this report type.",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description",
        help_text="Detailed report description.",
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Active",
        help_text="Whether this report type is currently available.",
    )

    # Classification
    category = models.CharField(
        max_length=20,
        choices=ReportCategory.choices,
        verbose_name="Category",
        help_text="Report category for organisation.",
    )
    default_format = models.CharField(
        max_length=10,
        choices=ReportFormat.choices,
        default=ReportFormat.PDF,
        verbose_name="Default Format",
        help_text="Default output format when generating this report.",
    )

    # Configuration
    available_filters = models.JSONField(
        default=_default_filters,
        blank=True,
        verbose_name="Available Filters",
        help_text="JSON schema defining available filter parameters.",
    )
    required_permission = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Required Permission",
        help_text="Permission codename required to generate this report.",
    )
    allows_scheduling = models.BooleanField(
        default=True,
        verbose_name="Allows Scheduling",
        help_text="Whether this report can be scheduled.",
    )
    allows_export = models.BooleanField(
        default=True,
        verbose_name="Allows Export",
        help_text="Whether this report can be exported.",
    )
    max_date_range_days = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Max Date Range (days)",
        help_text="Maximum allowed date range in days. Null for unlimited.",
    )

    # Display
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Display Order",
        help_text="Controls display order in UI. Lower numbers appear first.",
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Icon",
        help_text="Icon name for UI display (e.g. fa-chart-line).",
    )
    help_text_content = models.TextField(
        blank=True,
        verbose_name="Help Text",
        help_text="User-facing help text explaining report purpose.",
    )
    estimated_time_seconds = models.IntegerField(
        default=60,
        verbose_name="Estimated Time (seconds)",
        help_text="Estimated generation time in seconds.",
    )
    tags = models.JSONField(
        default=_default_tags,
        blank=True,
        verbose_name="Tags",
        help_text="Searchable tags for categorisation.",
    )
    sample_output_url = models.URLField(
        blank=True,
        verbose_name="Sample Output URL",
        help_text="Link to a sample report output for preview.",
    )

    class Meta:
        verbose_name = "Report Definition"
        verbose_name_plural = "Report Definitions"
        ordering = ["category", "order", "name"]
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["code"]),
        ]
        permissions = [
            ("view_sales_reports", "Can view sales reports"),
            ("view_inventory_reports", "Can view inventory reports"),
            ("view_purchase_reports", "Can view purchase reports"),
            ("view_customer_reports", "Can view customer reports"),
            ("view_staff_reports", "Can view staff reports"),
            ("view_financial_reports", "Can view financial reports"),
            ("view_tax_reports", "Can view tax reports"),
        ]

    def __str__(self):
        return f"{self.name} ({self.category})"

    def save(self, *args, **kwargs):
        if not self.code and self.name:
            self.code = re.sub(r"[^A-Z0-9]+", "_", self.name.upper()).strip("_")
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.max_date_range_days is not None and self.max_date_range_days <= 0:
            raise ValidationError(
                {"max_date_range_days": "Must be a positive integer."}
            )

    def has_permission(self, user) -> bool:
        """Check if user has the required permission for this report."""
        if not self.required_permission:
            return True
        return user.has_perm(self.required_permission)

    def get_estimated_time_display(self) -> str:
        """Return estimated generation time as a human-readable string."""
        seconds = self.estimated_time_seconds
        if seconds < 60:
            return f"{seconds} seconds"
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''}"

    def validate_filter_parameters(self, filter_params: dict) -> tuple[bool, dict]:
        """
        Validate user-provided filter parameters against the schema.

        Returns:
            (is_valid, errors_dict)
        """
        errors = {}
        available = self.available_filters or {}

        for filter_name, config in available.items():
            if config.get("required", False) and filter_name not in filter_params:
                errors[filter_name] = "This filter is required."

        for filter_name in filter_params:
            if filter_name not in available:
                errors[filter_name] = "Unknown filter."

        return (len(errors) == 0, errors)

    def get_filter_summary(self, filter_params: dict) -> str:
        """Create a human-readable summary of applied filters."""
        if not filter_params:
            return "No filters"
        parts: list[str] = []
        date_range = filter_params.get("date_range")
        if date_range:
            start = date_range.get("start_date", "")
            end = date_range.get("end_date", "")
            if start and end:
                parts.append(f"Date Range: {start} to {end}")
        for key, value in filter_params.items():
            if key == "date_range":
                continue
            parts.append(f"{key}: {value}")
        return " | ".join(parts) if parts else "No filters"
