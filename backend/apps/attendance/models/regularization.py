import logging

from django.conf import settings
from django.db import models

from apps.attendance.constants import (
    DEFAULT_REGULARIZATION_STATUS,
    REGULARIZATION_STATUS_APPROVED,
    REGULARIZATION_STATUS_CHOICES,
    REGULARIZATION_STATUS_REJECTED,
)
from apps.core.mixins import SoftDeleteMixin, TimestampMixin, UUIDMixin

logger = logging.getLogger(__name__)


class AttendanceRegularization(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """Request to correct an attendance record (e.g., missed punch)."""

    # ── References ───────────────────────────────────────────
    attendance_record = models.ForeignKey(
        "attendance.AttendanceRecord",
        on_delete=models.CASCADE,
        related_name="regularizations",
        help_text="The attendance record to correct.",
    )
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="attendance_regularizations",
        help_text="Employee requesting the correction.",
    )

    # ── Original Values ──────────────────────────────────────
    original_clock_in = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Original clock-in time before correction.",
    )
    original_clock_out = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Original clock-out time before correction.",
    )

    # ── Corrected Values ─────────────────────────────────────
    corrected_clock_in = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Requested corrected clock-in time.",
    )
    corrected_clock_out = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Requested corrected clock-out time.",
    )

    # ── Reason & Status ──────────────────────────────────────
    reason = models.TextField(
        help_text="Reason for the regularization request.",
    )
    status = models.CharField(
        max_length=20,
        choices=REGULARIZATION_STATUS_CHOICES,
        default=DEFAULT_REGULARIZATION_STATUS,
        db_index=True,
    )

    # ── Approval ─────────────────────────────────────────────
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_regularizations",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-created_on"]
        indexes = [
            models.Index(fields=["employee", "status"], name="idx_reg_emp_status"),
            models.Index(fields=["status"], name="idx_reg_status"),
        ]

    def __str__(self):
        return f"Regularization: {self.employee} - {self.attendance_record.date} ({self.status})"

    @property
    def is_pending(self):
        return self.status == DEFAULT_REGULARIZATION_STATUS

    @property
    def is_approved(self):
        return self.status == REGULARIZATION_STATUS_APPROVED

    @property
    def is_rejected(self):
        return self.status == REGULARIZATION_STATUS_REJECTED
