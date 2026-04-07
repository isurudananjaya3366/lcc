"""PayrollSettings model for configuring tenant-level payroll parameters."""

import calendar
from datetime import date, timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.core.mixins import TimestampMixin, UUIDMixin


class PayrollSettings(UUIDMixin, TimestampMixin, models.Model):
    """Tenant-level payroll configuration settings.

    Controls pay day, cutoff periods, approval workflows,
    and automatic period creation behavior.
    """

    # ── Effective Date ───────────────────────────────────────
    effective_from = models.DateField(
        default=date.today,
        help_text="Date from which these settings are effective.",
    )
    notification_email = models.EmailField(
        blank=True,
        default="",
        help_text="Email address for payroll notifications.",
    )

    # ── Pay Day Configuration ────────────────────────────────
    default_pay_day = models.PositiveSmallIntegerField(
        default=25,
        validators=[MinValueValidator(1), MaxValueValidator(28)],
        help_text="Default day of the month for salary payments (1-28).",
    )
    adjust_for_weekends = models.BooleanField(
        default=True,
        help_text="If True, adjust pay date when it falls on a weekend.",
    )

    # ── Attendance Cutoff ────────────────────────────────────
    attendance_cutoff_day = models.PositiveSmallIntegerField(
        default=20,
        validators=[MinValueValidator(1), MaxValueValidator(28)],
        help_text="Day of month for attendance data cutoff (1-28).",
    )
    use_cutoff_period = models.BooleanField(
        default=False,
        help_text="If True, use cutoff-based periods instead of calendar months.",
    )

    # ── Approval Configuration ───────────────────────────────
    require_approval = models.BooleanField(
        default=True,
        help_text="Whether payroll requires approval before finalization.",
    )
    approvers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="payroll_approver_for",
        help_text="Users authorized to approve payroll.",
    )
    min_approvals = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Minimum number of approvals required.",
    )

    # ── Auto-Create Configuration ────────────────────────────
    auto_create_period = models.BooleanField(
        default=False,
        help_text="Automatically create payroll periods each month.",
    )
    auto_create_day = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(28)],
        help_text="Day of month to auto-create the next period (1-28).",
    )
    create_months_ahead = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(3)],
        help_text="How many months ahead to auto-create periods (0-3).",
    )

    class Meta:
        verbose_name = "Payroll Settings"
        verbose_name_plural = "Payroll Settings"

    def __str__(self):
        return f"Payroll Settings (effective {self.effective_from})"

    def clean(self):
        super().clean()
        errors = {}

        if self.attendance_cutoff_day and self.default_pay_day:
            if self.attendance_cutoff_day > self.default_pay_day:
                errors["attendance_cutoff_day"] = (
                    "Attendance cutoff day should not be after the pay day."
                )

        self._validate_cutoff_settings(errors)
        self._validate_auto_create_settings(errors)

        if errors:
            raise ValidationError(errors)

    def _validate_cutoff_settings(self, errors):
        """Validate cutoff-related settings consistency."""
        if self.default_pay_day and self.attendance_cutoff_day:
            gap = self.default_pay_day - self.attendance_cutoff_day
            if gap < 3 and gap >= 0:
                errors["attendance_cutoff_day"] = (
                    "There must be at least 3 days between cutoff day and pay day "
                    "for processing time."
                )

    def _validate_auto_create_settings(self, errors):
        """Validate auto-create period settings."""
        if self.auto_create_period and not self.auto_create_day:
            errors["auto_create_day"] = (
                "Auto-create day must be set when auto-create period is enabled."
            )

    # ── Pay Date Calculation ─────────────────────────────────

    def calculate_pay_date(self, month, year):
        """Calculate the pay date for a given month/year based on settings.

        Returns a date object for the pay day, clamped to the last day
        of the month if default_pay_day exceeds the month's length.
        Adjusts for weekends if configured.
        """
        last_day = calendar.monthrange(year, month)[1]
        pay_day = min(self.default_pay_day, last_day)
        pay_date = date(year, month, pay_day)

        if self.adjust_for_weekends:
            pay_date = self.adjust_to_working_day(pay_date)

        return pay_date

    def adjust_to_working_day(self, dt):
        """Adjust a date to the nearest prior working day if it falls on a weekend."""
        # Saturday -> Friday, Sunday -> Friday
        if dt.weekday() == 5:  # Saturday
            return dt - timedelta(days=1)
        elif dt.weekday() == 6:  # Sunday
            return dt - timedelta(days=2)
        return dt

    # ── Cutoff Date Calculation ──────────────────────────────

    def calculate_cutoff_dates(self, month, year):
        """Calculate the cutoff start and end dates for a given month/year.

        If use_cutoff_period is True, the period runs from
        cutoff_day+1 of the previous month to cutoff_day of the current month.
        Otherwise, returns the calendar month boundaries.
        """
        if not self.use_cutoff_period:
            last_day = calendar.monthrange(year, month)[1]
            return date(year, month, 1), date(year, month, last_day)

        # Cutoff period: previous month cutoff_day+1 to this month cutoff_day
        if month == 1:
            prev_month, prev_year = 12, year - 1
        else:
            prev_month, prev_year = month - 1, year

        prev_last_day = calendar.monthrange(prev_year, prev_month)[1]
        cutoff_start_day = min(self.attendance_cutoff_day + 1, prev_last_day)
        start_date = date(prev_year, prev_month, cutoff_start_day)

        current_last_day = calendar.monthrange(year, month)[1]
        cutoff_end_day = min(self.attendance_cutoff_day, current_last_day)
        end_date = date(year, month, cutoff_end_day)

        return start_date, end_date

    # ── Approval Helpers ─────────────────────────────────────

    def can_user_approve(self, user):
        """Check if a given user is authorized to approve payroll."""
        if not self.require_approval:
            return True
        return self.approvers.filter(pk=user.pk).exists()

    def needs_approval(self, period=None):
        """Check if payroll approval is required.

        Args:
            period: Optional PayrollPeriod. If given, can apply period-specific logic.
        """
        return self.require_approval

    @staticmethod
    def is_weekend(dt):
        """Check if a date falls on a weekend (Saturday or Sunday)."""
        return dt.weekday() >= 5

    # ── Auto-Create Helpers ──────────────────────────────────

    def should_auto_create_period(self, check_date=None):
        """Check if a period should be auto-created on the given date."""
        if not self.auto_create_period:
            return False
        check_date = check_date or date.today()
        return check_date.day == self.auto_create_day

    def get_approver_emails(self):
        """Return list of active approver email addresses."""
        emails = list(
            self.approvers.filter(is_active=True).values_list("email", flat=True)
        )
        if self.notification_email and self.notification_email not in emails:
            emails.append(self.notification_email)
        return emails
