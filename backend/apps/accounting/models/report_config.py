"""
Report configuration model.

Stores financial report configuration parameters including report type,
period selection, comparison settings, and detail level.
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.mixins import UUIDMixin

from ..reports.enums import ComparisonType, DetailLevel, ReportPeriod, ReportType


class ReportConfig(UUIDMixin, models.Model):
    """
    Stores configuration parameters for financial report generation.

    Supports both date-range reports (P&L, Cash Flow, GL) and
    point-in-time snapshot reports (Trial Balance, Balance Sheet).
    """

    # ── Identification ──────────────────────────────────────────────
    name = models.CharField(max_length=200)
    report_type = models.CharField(
        max_length=20,
        choices=ReportType.choices,
    )
    period_type = models.CharField(
        max_length=15,
        choices=ReportPeriod.choices,
        default=ReportPeriod.MONTHLY,
    )
    is_active = models.BooleanField(default=True)

    # ── Date Configuration ──────────────────────────────────────────
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    as_of_date = models.DateField(null=True, blank=True)
    fiscal_year = models.IntegerField(null=True, blank=True)

    # ── Comparison Configuration ────────────────────────────────────
    include_comparison = models.BooleanField(default=False)
    comparison_period_type = models.CharField(
        max_length=20,
        choices=ComparisonType.choices,
        null=True,
        blank=True,
    )
    comparison_start_date = models.DateField(null=True, blank=True)
    comparison_end_date = models.DateField(null=True, blank=True)
    comparison_as_of_date = models.DateField(null=True, blank=True)

    # ── Detail Configuration ────────────────────────────────────────
    detail_level = models.CharField(
        max_length=15,
        choices=DetailLevel.choices,
        default=DetailLevel.SUMMARY,
    )
    include_zero_balances = models.BooleanField(default=False)

    # ── Audit ───────────────────────────────────────────────────────
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="report_configs_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounting_report_config"
        verbose_name = "Report Configuration"
        verbose_name_plural = "Report Configurations"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["report_type", "is_active"],
                name="idx_rptcfg_type_active",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_report_type_display()})"

    def clean(self):
        """Validate date fields based on report type."""
        super().clean()
        errors = {}

        snapshot_types = {ReportType.TRIAL_BALANCE, ReportType.BALANCE_SHEET}
        period_types = {
            ReportType.PROFIT_LOSS,
            ReportType.CASH_FLOW,
            ReportType.GENERAL_LEDGER,
        }

        if self.report_type in snapshot_types:
            if not self.as_of_date:
                errors["as_of_date"] = (
                    "As-of date is required for snapshot reports."
                )

        if self.report_type in period_types:
            if not self.start_date:
                errors["start_date"] = (
                    "Start date is required for period reports."
                )
            if not self.end_date:
                errors["end_date"] = (
                    "End date is required for period reports."
                )

        if self.start_date and self.end_date and self.end_date < self.start_date:
            errors["end_date"] = "End date must be on or after start date."

        if self.include_comparison:
            if (
                self.comparison_period_type == ComparisonType.CUSTOM
                and not self.comparison_start_date
            ):
                errors["comparison_start_date"] = (
                    "Comparison start date is required for custom comparison."
                )
            if (
                self.comparison_period_type == ComparisonType.CUSTOM
                and not self.comparison_end_date
            ):
                errors["comparison_end_date"] = (
                    "Comparison end date is required for custom comparison."
                )

        if (
            self.comparison_start_date
            and self.comparison_end_date
            and self.comparison_end_date < self.comparison_start_date
        ):
            errors["comparison_end_date"] = (
                "Comparison end date must be on or after comparison start date."
            )

        if errors:
            raise ValidationError(errors)
