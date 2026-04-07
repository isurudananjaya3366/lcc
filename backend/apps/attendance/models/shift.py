import logging
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models

from apps.attendance.constants import (
    DEFAULT_EARLY_LEAVE_GRACE_MINUTES,
    DEFAULT_LATE_GRACE_MINUTES,
    DEFAULT_MIN_HOURS_FULL_DAY,
    DEFAULT_MIN_HOURS_HALF_DAY,
    DEFAULT_OVERTIME_MULTIPLIER,
    DEFAULT_OVERTIME_START_AFTER,
    DEFAULT_SHIFT_STATUS,
    DEFAULT_SHIFT_TYPE,
    SHIFT_STATUS_CHOICES,
    SHIFT_TYPE_CHOICES,
)
from apps.core.mixins import SoftDeleteMixin, TimestampMixin, UUIDMixin

logger = logging.getLogger(__name__)


class Shift(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """Defines a work shift with time rules, grace periods, and overtime configuration."""

    # ── Core Fields ──────────────────────────────────────────
    name = models.CharField(
        max_length=100,
        help_text="Descriptive name (e.g., 'Regular Day Shift').",
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text="Unique shift code (e.g., 'SHF-0001').",
    )
    shift_type = models.CharField(
        max_length=20,
        choices=SHIFT_TYPE_CHOICES,
        default=DEFAULT_SHIFT_TYPE,
        db_index=True,
        help_text="Type of shift.",
    )
    status = models.CharField(
        max_length=20,
        choices=SHIFT_STATUS_CHOICES,
        default=DEFAULT_SHIFT_STATUS,
        db_index=True,
    )
    description = models.TextField(blank=True, default="")
    is_default = models.BooleanField(
        default=False,
        help_text="Whether this is the default shift for the tenant.",
    )

    # ── Time Fields ──────────────────────────────────────────
    start_time = models.TimeField(help_text="Shift start time.")
    end_time = models.TimeField(help_text="Shift end time.")
    break_start = models.TimeField(
        null=True, blank=True, help_text="Break start time."
    )
    break_end = models.TimeField(
        null=True, blank=True, help_text="Break end time."
    )

    # ── Duration Fields (calculated) ─────────────────────────
    work_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total work hours (auto-calculated if blank).",
    )
    break_duration_minutes = models.PositiveIntegerField(
        default=0,
        help_text="Break duration in minutes (auto-calculated if break times set).",
    )

    # ── Grace Period Fields ──────────────────────────────────
    late_grace_minutes = models.PositiveIntegerField(
        default=DEFAULT_LATE_GRACE_MINUTES,
        help_text="Minutes allowed before marking as late.",
    )
    early_leave_grace_minutes = models.PositiveIntegerField(
        default=DEFAULT_EARLY_LEAVE_GRACE_MINUTES,
        help_text="Minutes allowed before marking as early departure.",
    )

    # ── Overtime Rules ───────────────────────────────────────
    overtime_start_after = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=DEFAULT_OVERTIME_START_AFTER,
        help_text="Overtime begins after this many hours worked.",
    )
    overtime_multiplier = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=DEFAULT_OVERTIME_MULTIPLIER,
        help_text="Pay multiplier for overtime hours.",
    )

    # ── Half-Day Threshold ───────────────────────────────────
    min_hours_for_half_day = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=DEFAULT_MIN_HOURS_HALF_DAY,
        help_text="Minimum hours to count as half-day attendance.",
    )
    min_hours_for_full_day = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=DEFAULT_MIN_HOURS_FULL_DAY,
        help_text="Minimum hours to count as full-day attendance.",
    )

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["code"], name="idx_shift_code"),
            models.Index(fields=["shift_type"], name="idx_shift_type"),
            models.Index(fields=["status"], name="idx_shift_status"),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def spans_midnight(self):
        """Whether this shift crosses midnight."""
        return self.end_time < self.start_time

    @property
    def total_duration(self):
        """Total shift duration as timedelta (including break)."""
        from datetime import datetime

        start_dt = datetime.combine(datetime.min, self.start_time)
        end_dt = datetime.combine(datetime.min, self.end_time)
        if self.spans_midnight:
            end_dt += timedelta(days=1)
        return end_dt - start_dt

    @property
    def effective_work_duration(self):
        """Effective work duration (total minus break) as timedelta."""
        duration = self.total_duration
        if self.break_duration_minutes:
            duration -= timedelta(minutes=self.break_duration_minutes)
        return duration

    def clean(self):
        super().clean()
        # Validate break times
        if self.break_start and not self.break_end:
            raise ValidationError(
                {"break_end": "Break end time is required when break start is set."}
            )
        if self.break_end and not self.break_start:
            raise ValidationError(
                {"break_start": "Break start time is required when break end is set."}
            )
        # Auto-calculate break duration
        if self.break_start and self.break_end:
            from datetime import datetime

            bs = datetime.combine(datetime.min, self.break_start)
            be = datetime.combine(datetime.min, self.break_end)
            if be < bs:
                be += timedelta(days=1)
            self.break_duration_minutes = int((be - bs).total_seconds() / 60)
        # Auto-calculate work hours
        if self.start_time and self.end_time:
            total_minutes = self.total_duration.total_seconds() / 60
            work_minutes = total_minutes - (self.break_duration_minutes or 0)
            from decimal import Decimal

            self.work_hours = Decimal(str(round(work_minutes / 60, 2)))

    def save(self, *args, **kwargs):
        if self.start_time and self.end_time:
            self.full_clean()
        super().save(*args, **kwargs)
