"""
AccountingPeriod model for the accounting application.

Manages fiscal periods with date ranges and open/closed/locked
status, controlling which dates accept new journal entries and
enforcing proper period-end closing procedures.
"""

import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.accounting.models.enums import PeriodStatus
from apps.core.mixins import UUIDMixin


class AccountingPeriod(UUIDMixin, models.Model):
    """
    Fiscal period for accounting transaction control.

    Each period defines a date range (typically one calendar month)
    and a status that controls entry creation:

        OPEN   → regular entries accepted
        CLOSED → adjusting entries only
        LOCKED → read-only (post-audit)

    Lifecycle: OPEN → CLOSED → LOCKED
    """

    # ── Date Range ──────────────────────────────────────────────────
    start_date = models.DateField(
        verbose_name="Start Date",
        help_text="First day of the accounting period.",
    )

    end_date = models.DateField(
        verbose_name="End Date",
        help_text="Last day of the accounting period.",
    )

    # ── Period Status ───────────────────────────────────────────────
    status = models.CharField(
        max_length=10,
        choices=PeriodStatus.choices,
        default=PeriodStatus.OPEN,
        db_index=True,
        verbose_name="Status",
        help_text="Period lifecycle status (Open/Closed/Locked).",
    )

    # ── Fiscal Year & Period Number ─────────────────────────────────
    fiscal_year = models.PositiveIntegerField(
        verbose_name="Fiscal Year",
        help_text="Fiscal year this period belongs to (e.g. 2026).",
    )

    period_number = models.PositiveSmallIntegerField(
        verbose_name="Period Number",
        help_text="Period number within the fiscal year (1-12).",
    )

    name = models.CharField(
        max_length=50,
        blank=True,
        default="",
        verbose_name="Period Name",
        help_text="Display name (e.g. 'April 2026', 'Q1 2026').",
    )

    # ── Timestamps ──────────────────────────────────────────────────
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At",
    )

    class Meta:
        db_table = "accounting_period"
        verbose_name = "Accounting Period"
        verbose_name_plural = "Accounting Periods"
        ordering = ["-start_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["fiscal_year", "period_number"],
                name="uq_accounting_period_year_number",
            ),
        ]
        indexes = [
            models.Index(
                fields=["fiscal_year", "period_number"],
                name="idx_ap_year_period",
            ),
            models.Index(
                fields=["start_date", "end_date"],
                name="idx_ap_date_range",
            ),
        ]

    def __str__(self):
        return self.name or f"FY{self.fiscal_year} P{self.period_number}"

    def clean(self):
        """Validate that start_date is before end_date."""
        super().clean()
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError(
                {"end_date": "End date must be on or after start date."}
            )

    @property
    def is_open(self):
        return self.status == PeriodStatus.OPEN

    @property
    def is_closed(self):
        return self.status == PeriodStatus.CLOSED

    @property
    def is_locked(self):
        return self.status == PeriodStatus.LOCKED

    @property
    def is_current_period(self):
        """Check if today falls within this period."""
        today = datetime.date.today()
        return self.start_date <= today <= self.end_date

    def get_period_display(self):
        """Format period for display, e.g. 'Period 1 - January 2026'."""
        if self.name:
            return self.name
        month_name = self.start_date.strftime("%B") if self.start_date else ""
        return f"Period {self.period_number} - {month_name} {self.fiscal_year}"

    def close_period(self, closed_by=None):
        """Transition period from OPEN to CLOSED."""
        if not self.is_open:
            raise ValidationError("Only OPEN periods can be closed.")
        self.status = PeriodStatus.CLOSED
        self.save(update_fields=["status", "updated_at"])

    def lock_period(self, locked_by=None):
        """Transition period from CLOSED to LOCKED."""
        if not self.is_closed:
            raise ValidationError("Only CLOSED periods can be locked.")
        self.status = PeriodStatus.LOCKED
        self.save(update_fields=["status", "updated_at"])

    def reopen_period(self):
        """Re-open a CLOSED period (cannot re-open LOCKED periods)."""
        if self.is_locked:
            raise ValidationError("LOCKED periods cannot be re-opened.")
        if not self.is_closed:
            raise ValidationError("Only CLOSED periods can be re-opened.")
        self.status = PeriodStatus.OPEN
        self.save(update_fields=["status", "updated_at"])

    def can_post_entry(self, entry_type=None):
        """
        Check if this period accepts entries of the given type.

        OPEN periods accept all entries.
        CLOSED periods accept only ADJUSTING entries.
        LOCKED periods accept no entries.
        """
        if self.is_locked:
            return False
        if self.is_closed:
            return entry_type == "ADJUSTING"
        return True

    def get_next_period(self):
        """Return the next accounting period, or None."""
        return AccountingPeriod.objects.filter(
            start_date__gt=self.end_date,
        ).order_by("start_date").first()

    def get_previous_period(self):
        """Return the previous accounting period, or None."""
        return AccountingPeriod.objects.filter(
            end_date__lt=self.start_date,
        ).order_by("-start_date").first()
