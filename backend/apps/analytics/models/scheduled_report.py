"""
Scheduled report and schedule history models.

Supports recurring report generation with email distribution.
"""

import re
from datetime import datetime, time, timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from apps.analytics.enums import ReportFormat, ScheduleFrequency
from apps.core.mixins import TimestampMixin, UUIDMixin


def _default_recipients():
    return []


def validate_email_list(value):
    """Validate that value is a list of valid email addresses."""
    if not isinstance(value, list):
        raise ValidationError("Recipients must be a list.")
    email_re = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    for addr in value:
        if not isinstance(addr, str) or not email_re.match(addr):
            raise ValidationError(f"Invalid email address: {addr}")


class ScheduledReport(UUIDMixin, TimestampMixin, models.Model):
    """Recurring report schedule with email delivery configuration."""

    LAST_STATUS_CHOICES = [
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
        ("PENDING", "Pending"),
    ]

    saved_report = models.ForeignKey(
        "analytics.SavedReport",
        on_delete=models.CASCADE,
        related_name="schedules",
    )
    frequency = models.CharField(
        max_length=10,
        choices=ScheduleFrequency.choices,
        default=ScheduleFrequency.WEEKLY,
    )
    time_of_day = models.TimeField(
        default=time(9, 0),
        help_text="Time to run the report (tenant timezone).",
    )
    day_of_week = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(6)],
        help_text="0=Monday .. 6=Sunday. Required for WEEKLY.",
    )
    day_of_month = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        help_text="Day of month (1-31). Required for MONTHLY.",
    )
    next_run = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
    )
    last_run = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="scheduled_reports",
    )
    last_status = models.CharField(
        max_length=20,
        choices=LAST_STATUS_CHOICES,
        null=True,
        blank=True,
    )
    error_message = models.TextField(blank=True, null=True)

    # ── Email configuration ───────────────────────────────────────
    recipients = models.JSONField(
        default=_default_recipients,
        blank=True,
        validators=[validate_email_list],
        help_text="List of email addresses.",
    )
    email_subject = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Supports {report_name}, {date}.",
    )
    email_body = models.TextField(blank=True, null=True)
    attach_pdf = models.BooleanField(default=True)
    include_csv = models.BooleanField(default=False)
    include_excel = models.BooleanField(default=False)
    cc_emails = models.JSONField(
        default=_default_recipients,
        blank=True,
        validators=[validate_email_list],
    )
    bcc_emails = models.JSONField(
        default=_default_recipients,
        blank=True,
        validators=[validate_email_list],
    )
    last_report_instance = models.ForeignKey(
        "analytics.ReportInstance",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    class Meta:
        db_table = "analytics_scheduled_report"
        ordering = ["next_run"]
        indexes = [
            models.Index(
                fields=["is_active", "next_run"],
                name="idx_sched_active_next",
            ),
        ]
        verbose_name = "Scheduled Report"
        verbose_name_plural = "Scheduled Reports"

    def __str__(self) -> str:
        return (
            f"{self.saved_report.name} – "
            f"{self.get_frequency_display()} @ {self.time_of_day}"
        )

    # ── Schedule logic ────────────────────────────────────────────

    def calculate_next_run(self, after: datetime | None = None) -> datetime:
        """Calculate the next run datetime (UTC) based on frequency."""
        now = after or timezone.now()
        run_time = self.time_of_day or time(9, 0)

        if self.frequency == ScheduleFrequency.DAILY:
            candidate = now.replace(
                hour=run_time.hour,
                minute=run_time.minute,
                second=0,
                microsecond=0,
            )
            if candidate <= now:
                candidate += timedelta(days=1)
            return candidate

        if self.frequency == ScheduleFrequency.WEEKLY:
            dow = self.day_of_week if self.day_of_week is not None else 0
            # Python weekday: 0=Mon
            days_ahead = dow - now.weekday()
            if days_ahead < 0:
                days_ahead += 7
            candidate = (now + timedelta(days=days_ahead)).replace(
                hour=run_time.hour,
                minute=run_time.minute,
                second=0,
                microsecond=0,
            )
            if candidate <= now:
                candidate += timedelta(weeks=1)
            return candidate

        if self.frequency == ScheduleFrequency.MONTHLY:
            dom = self.day_of_month if self.day_of_month else 1
            import calendar

            year, month = now.year, now.month
            max_day = calendar.monthrange(year, month)[1]
            day = min(dom, max_day)
            candidate = now.replace(
                day=day,
                hour=run_time.hour,
                minute=run_time.minute,
                second=0,
                microsecond=0,
            )
            if candidate <= now:
                # Next month
                if month == 12:
                    year += 1
                    month = 1
                else:
                    month += 1
                max_day = calendar.monthrange(year, month)[1]
                day = min(dom, max_day)
                candidate = candidate.replace(year=year, month=month, day=day)
            return candidate

        return now + timedelta(days=1)

    def update_next_run(self) -> None:
        """Recalculate and persist next_run."""
        self.next_run = self.calculate_next_run()
        self.save(update_fields=["next_run"])

    def save(self, **kwargs):
        if not self.next_run and self.is_active:
            self.next_run = self.calculate_next_run()
        super().save(**kwargs)

    def clean(self):
        super().clean()
        if (
            self.frequency == ScheduleFrequency.WEEKLY
            and self.day_of_week is None
        ):
            raise ValidationError(
                {"day_of_week": "Required for weekly schedules."}
            )
        if (
            self.frequency == ScheduleFrequency.MONTHLY
            and self.day_of_month is None
        ):
            raise ValidationError(
                {"day_of_month": "Required for monthly schedules."}
            )


class ScheduleHistory(UUIDMixin, TimestampMixin, models.Model):
    """Audit log of scheduled report executions."""

    STATUS_CHOICES = [
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
        ("PARTIAL", "Partial"),
    ]

    scheduled_report = models.ForeignKey(
        ScheduledReport,
        on_delete=models.CASCADE,
        related_name="history",
    )
    run_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    report_instance = models.ForeignKey(
        "analytics.ReportInstance",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    error_message = models.TextField(blank=True, null=True)
    recipients_count = models.IntegerField(default=0)
    email_sent = models.BooleanField(default=False)
    execution_time_seconds = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    file_size_bytes = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "analytics_schedule_history"
        ordering = ["-run_at"]
        indexes = [
            models.Index(fields=["scheduled_report", "run_at"]),
            models.Index(fields=["status"]),
        ]
        verbose_name = "Schedule History"
        verbose_name_plural = "Schedule Histories"

    def __str__(self) -> str:
        return f"{self.scheduled_report} – {self.status} @ {self.run_at}"

    @classmethod
    def create_history(
        cls,
        scheduled_report,
        status: str,
        report_instance=None,
        error_message: str | None = None,
        recipients_count: int = 0,
        email_sent: bool = False,
        execution_time_seconds=None,
        file_size_bytes: int | None = None,
    ):
        """Create a history record for a schedule run."""
        return cls.objects.create(
            scheduled_report=scheduled_report,
            status=status,
            report_instance=report_instance,
            error_message=error_message,
            recipients_count=recipients_count,
            email_sent=email_sent,
            execution_time_seconds=execution_time_seconds,
            file_size_bytes=file_size_bytes,
        )
