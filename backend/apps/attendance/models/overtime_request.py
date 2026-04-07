import logging

from django.conf import settings
from django.db import models
from django.utils import timezone as tz

from apps.attendance.constants import (
    DEFAULT_OVERTIME_STATUS,
    OVERTIME_STATUS_CHOICES,
)
from apps.core.mixins import SoftDeleteMixin, TimestampMixin, UUIDMixin

logger = logging.getLogger(__name__)


class OvertimeRequest(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """Employee request for overtime work (pre-approval or post-approval)."""

    # ── References ───────────────────────────────────────────
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="overtime_requests",
    )
    attendance_record = models.ForeignKey(
        "attendance.AttendanceRecord",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="overtime_requests",
    )

    # ── Tracking Number ──────────────────────────────────────
    request_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        help_text="Auto-generated request number (OT-YYYYMMDD-NNNN).",
    )

    # ── Details ──────────────────────────────────────────────
    date = models.DateField(
        db_index=True,
        help_text="Date of overtime work.",
    )
    planned_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        help_text="Planned overtime hours.",
    )
    actual_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Actual overtime hours worked.",
    )
    reason = models.TextField(
        help_text="Reason for the overtime request.",
    )

    # ── Status & Approval ────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=OVERTIME_STATUS_CHOICES,
        default=DEFAULT_OVERTIME_STATUS,
        db_index=True,
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_overtime_requests",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["employee", "date"], name="idx_ot_emp_date"),
            models.Index(fields=["status"], name="idx_ot_status"),
        ]

    def __str__(self):
        return f"OT Request: {self.employee} - {self.date} ({self.planned_hours}h)"

    def save(self, *args, **kwargs):
        if not self.request_number:
            today = tz.localdate()
            prefix = f"OT-{today:%Y%m%d}-"
            last = (
                OvertimeRequest.objects.filter(request_number__startswith=prefix)
                .order_by("-request_number")
                .values_list("request_number", flat=True)
                .first()
            )
            seq = int(last.split("-")[-1]) + 1 if last else 1
            self.request_number = f"{prefix}{seq:04d}"
        super().save(*args, **kwargs)
