"""
Tax period record model.

Tracks individual tax filing periods for each tax type,
including date ranges, due dates, and filing status.
"""

from django.core.exceptions import ValidationError
from django.db import models

from apps.core.mixins import UUIDMixin

from ..tax.enums import FilingStatus, TaxPeriod, TaxType


class TaxPeriodRecord(UUIDMixin, models.Model):
    """
    Tracks one tax period for one tax type.

    Multiple records per tenant — one per tax type per period
    (e.g., 12 monthly VAT + 12 monthly PAYE + 12 EPF + 12 ETF = 48/year).
    """

    # ── Period Identification ───────────────────────────────────────
    tax_configuration = models.ForeignKey(
        "accounting.TaxConfiguration",
        on_delete=models.CASCADE,
        related_name="period_records",
    )
    tax_type = models.CharField(
        max_length=10,
        choices=TaxType.choices,
        db_index=True,
    )
    period_type = models.CharField(
        max_length=20,
        choices=TaxPeriod.choices,
    )
    year = models.PositiveIntegerField(db_index=True)
    period_number = models.PositiveSmallIntegerField(
        help_text="Month (1-12) for monthly, quarter (1-4) for quarterly, 1 for annual.",
    )

    # ── Date Range ──────────────────────────────────────────────────
    start_date = models.DateField(verbose_name="Period Start Date")
    end_date = models.DateField(verbose_name="Period End Date")
    due_date = models.DateField(
        verbose_name="Filing Due Date",
        help_text="Deadline for filing the return with the tax authority.",
    )

    # ── Status Tracking ─────────────────────────────────────────────
    filing_status = models.CharField(
        max_length=20,
        choices=FilingStatus.choices,
        default=FilingStatus.PENDING,
        db_index=True,
    )
    filed_date = models.DateField(null=True, blank=True)
    accepted_date = models.DateField(null=True, blank=True)

    # ── Timestamps ──────────────────────────────────────────────────
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounting_tax_period_record"
        verbose_name = "Tax Period Record"
        verbose_name_plural = "Tax Period Records"
        ordering = ["year", "period_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["tax_configuration", "tax_type", "year", "period_number"],
                name="unique_tax_period",
            ),
        ]

    def __str__(self):
        period_label = (
            f"Q{self.period_number}" if self.period_type == TaxPeriod.QUARTERLY else str(self.period_number)
        )
        return f"{self.get_tax_type_display()} - {self.year} {period_label} - {self.get_filing_status_display()}"

    def clean(self):
        super().clean()
        if self.end_date and self.start_date and self.end_date <= self.start_date:
            raise ValidationError({"end_date": "Period end date must be after start date."})
        if self.due_date and self.end_date and self.due_date < self.end_date:
            raise ValidationError({"due_date": "Due date cannot be before period end date."})

    @property
    def is_overdue(self):
        """Return True if the period is past due and not yet filed."""
        from django.utils import timezone

        if self.filing_status in (FilingStatus.FILED, FilingStatus.ACCEPTED):
            return False
        return timezone.now().date() > self.due_date
