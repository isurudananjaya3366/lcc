"""PayrollPeriod model for managing monthly payroll periods."""

import calendar
from datetime import date, timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.mixins import TimestampMixin, UUIDMixin
from apps.payroll.constants import PayrollStatus


class PayrollPeriodManager(models.Manager):
    """Custom manager for PayrollPeriod."""

    def unlocked(self):
        """Return only unlocked periods."""
        return self.filter(is_locked=False)

    def locked(self):
        """Return only locked periods."""
        return self.filter(is_locked=True)


class PayrollPeriod(UUIDMixin, TimestampMixin, models.Model):
    """Represents a monthly payroll period with status tracking and locking.

    Each period covers a specific month/year, tracks its processing status,
    and can be locked to prevent modifications. Supports status transitions
    from DRAFT through FINALIZED or REVERSED.
    """

    # ── Period Identification ────────────────────────────────
    period_month = models.PositiveSmallIntegerField(
        help_text="Month of the payroll period (1-12).",
    )
    period_year = models.PositiveSmallIntegerField(
        help_text="Year of the payroll period (e.g. 2025).",
    )
    name = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        help_text="Auto-generated period name (e.g. 'January 2025').",
    )

    # ── Date Boundaries ──────────────────────────────────────
    start_date = models.DateField(
        help_text="First day of the payroll period.",
    )
    end_date = models.DateField(
        help_text="Last day of the payroll period.",
    )
    pay_date = models.DateField(
        help_text="Scheduled payment date for this period.",
    )

    # ── Status & Workflow ────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=PayrollStatus.choices,
        default=PayrollStatus.DRAFT,
        help_text="Current processing status of this period.",
    )

    # ── Working Days ─────────────────────────────────────────
    total_working_days = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Total working days in this period (excludes weekends and public holidays).",
    )

    # ── Locking ──────────────────────────────────────────────
    is_locked = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether this period is locked for modifications.",
    )
    locked_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the period was locked.",
    )
    locked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="locked_payroll_periods",
        help_text="User who locked this period.",
    )

    # ── Notes ────────────────────────────────────────────────
    notes = models.TextField(
        blank=True,
        default="",
        help_text="Optional notes for this payroll period.",
    )

    objects = PayrollPeriodManager()

    class Meta:
        ordering = ["-period_year", "-period_month"]
        unique_together = [("period_month", "period_year")]
        indexes = [
            models.Index(fields=["status"], name="idx_payperiod_status"),
            models.Index(fields=["period_year", "period_month"], name="idx_payperiod_ym"),
        ]
        verbose_name = "Payroll Period"
        verbose_name_plural = "Payroll Periods"

    def __str__(self):
        return self.name or self.generate_name()

    # ── Auto-generation ──────────────────────────────────────

    def generate_name(self):
        """Generate a human-readable period name like 'January 2025'."""
        try:
            return f"{calendar.month_name[self.period_month]} {self.period_year}"
        except (IndexError, TypeError):
            return f"{self.period_month}/{self.period_year}"

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.generate_name()
        if self.total_working_days == 0 and self.start_date and self.end_date:
            self.total_working_days = self.calculate_working_days()
        # Lock enforcement: prevent changes to locked periods (except lock/unlock fields)
        if self.pk and self.is_locked:
            update_fields = kwargs.get("update_fields")
            lock_fields = {"is_locked", "locked_at", "locked_by", "updated_on", "status"}
            if update_fields and not set(update_fields).issubset(lock_fields):
                raise ValidationError("Cannot modify a locked payroll period.")
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        errors = {}

        # Validate month range
        if self.period_month and (self.period_month < 1 or self.period_month > 12):
            errors["period_month"] = "Month must be between 1 and 12."

        # Validate year range
        if self.period_year and self.period_year < 2000:
            errors["period_year"] = "Year must be 2000 or later."

        # Validate date ordering
        if self.start_date and self.end_date and self.start_date > self.end_date:
            errors["end_date"] = "End date must be on or after start date."

        # Validate pay_date is not before start_date
        if self.start_date and self.pay_date and self.pay_date < self.start_date:
            errors["pay_date"] = "Pay date must not be before the period start date."

        if errors:
            raise ValidationError(errors)

    # ── Status Transitions ───────────────────────────────────

    VALID_TRANSITIONS = {
        PayrollStatus.DRAFT: [PayrollStatus.PROCESSING],
        PayrollStatus.PROCESSING: [PayrollStatus.PROCESSED, PayrollStatus.DRAFT],
        PayrollStatus.PROCESSED: [PayrollStatus.PENDING_APPROVAL, PayrollStatus.APPROVED, PayrollStatus.DRAFT],
        PayrollStatus.PENDING_APPROVAL: [PayrollStatus.APPROVED, PayrollStatus.REJECTED],
        PayrollStatus.APPROVED: [PayrollStatus.FINALIZED, PayrollStatus.PROCESSED],
        PayrollStatus.REJECTED: [PayrollStatus.PROCESSED],
        PayrollStatus.FINALIZED: [PayrollStatus.REVERSED],
        PayrollStatus.REVERSED: [PayrollStatus.DRAFT],
    }

    def _transition_to(self, new_status):
        """Transition to a new status if valid, otherwise raise ValidationError."""
        allowed = self.VALID_TRANSITIONS.get(self.status, [])
        if new_status not in allowed:
            raise ValidationError(
                f"Cannot transition from {self.status} to {new_status}. "
                f"Allowed transitions: {allowed}"
            )
        self.status = new_status
        self.save(update_fields=["status", "updated_on"])

    def start_processing(self):
        """Transition from DRAFT to PROCESSING."""
        self._transition_to(PayrollStatus.PROCESSING)

    def mark_processed(self):
        """Transition from PROCESSING to PROCESSED."""
        self._transition_to(PayrollStatus.PROCESSED)

    def approve(self):
        """Transition from PROCESSED to APPROVED."""
        self._transition_to(PayrollStatus.APPROVED)

    def finalize(self):
        """Transition from APPROVED to FINALIZED."""
        self._transition_to(PayrollStatus.FINALIZED)

    def reverse(self):
        """Transition from FINALIZED to REVERSED."""
        self._transition_to(PayrollStatus.REVERSED)

    def reset_to_draft(self):
        """Reset from PROCESSING or PROCESSED back to DRAFT."""
        self._transition_to(PayrollStatus.DRAFT)

    # ── Status Query Properties ──────────────────────────────

    @property
    def is_draft(self):
        return self.status == PayrollStatus.DRAFT

    @property
    def is_processing(self):
        return self.status == PayrollStatus.PROCESSING

    @property
    def is_processed(self):
        return self.status == PayrollStatus.PROCESSED

    @property
    def is_approved(self):
        return self.status == PayrollStatus.APPROVED

    @property
    def is_finalized(self):
        return self.status == PayrollStatus.FINALIZED

    @property
    def is_reversed(self):
        return self.status == PayrollStatus.REVERSED

    # ── Workflow Readiness Checks ────────────────────────────

    def can_process(self):
        """Check if this period can be processed."""
        return self.status == PayrollStatus.DRAFT and not self.is_locked

    def can_approve(self):
        """Check if this period can be approved."""
        return self.status in (PayrollStatus.PROCESSED, PayrollStatus.PENDING_APPROVAL)

    def can_finalize(self):
        """Check if this period can be finalized."""
        return self.status == PayrollStatus.APPROVED

    def can_reverse(self):
        """Check if this period can be reversed."""
        return self.status == PayrollStatus.FINALIZED

    @property
    def is_reversible(self):
        """Whether this period's payroll can be reversed."""
        return self.can_reverse()

    @property
    def can_unlock(self):
        """Whether this period can be unlocked."""
        return self.is_locked and self.status not in (
            PayrollStatus.FINALIZED,
        )

    # ── Locking Methods ──────────────────────────────────────

    def lock(self, user=None, reason=""):
        """Lock this period to prevent modifications."""
        from django.utils import timezone

        self.is_locked = True
        self.locked_at = timezone.now()
        self.locked_by = user
        if reason and not self.notes:
            self.notes = f"Locked: {reason}"
        self.save(update_fields=["is_locked", "locked_at", "locked_by", "notes", "updated_on"])

    def unlock(self, user=None, reason=""):
        """Unlock this period to allow modifications."""
        self.is_locked = False
        self.locked_at = None
        self.locked_by = None
        self.save(update_fields=["is_locked", "locked_at", "locked_by", "updated_on"])

    # ── Working Days Calculation ─────────────────────────────

    def calculate_working_days(self):
        """Calculate working days between start_date and end_date (excludes weekends)."""
        if not self.start_date or not self.end_date:
            return 0

        working_days = 0
        current = self.start_date
        one_day = timedelta(days=1)
        while current <= self.end_date:
            if current.weekday() < 5:  # Monday=0 to Friday=4
                working_days += 1
            current += one_day
        return working_days

    def recalculate_working_days(self):
        """Recalculate and save working days, optionally excluding public holidays."""
        working_days = self.calculate_working_days()
        public_holidays = self.get_public_holidays()
        working_days -= len(public_holidays)
        self.total_working_days = max(working_days, 0)
        self.save(update_fields=["total_working_days", "updated_on"])
        return self.total_working_days

    def get_public_holidays(self):
        """Return public holidays within this period's date range.

        Attempts to fetch from a PublicHoliday model; returns empty list
        if the model is not available.
        """
        if not self.start_date or not self.end_date:
            return []
        try:
            from apps.hr.models import PublicHoliday
            return list(
                PublicHoliday.objects.filter(
                    date__gte=self.start_date,
                    date__lte=self.end_date,
                ).values_list("date", flat=True)
            )
        except (ImportError, Exception):
            return []

    @property
    def average_days_per_week(self):
        """Average working days per week in this period."""
        if not self.start_date or not self.end_date:
            return 0
        total_weeks = max(((self.end_date - self.start_date).days + 1) / 7, 1)
        return float(self.total_working_days) / total_weeks

    @property
    def working_days_ratio(self):
        """Ratio of working days to standard 30-day month."""
        if not self.total_working_days:
            return 0
        return float(self.total_working_days) / 30
