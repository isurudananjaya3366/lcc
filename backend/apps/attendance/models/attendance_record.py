import logging

from django.conf import settings
from django.db import models

from apps.attendance.constants import (
    ATTENDANCE_STATUS_CHOICES,
    CHECKIN_METHOD_CHOICES,
    CHECKIN_METHOD_WEB,
    DEFAULT_ATTENDANCE_STATUS,
)
from apps.core.mixins import SoftDeleteMixin, TimestampMixin, UUIDMixin

logger = logging.getLogger(__name__)


class AttendanceRecord(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """Tracks daily attendance for each employee with clock in/out and computed hours."""

    # ── Employee & Date ──────────────────────────────────────
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="attendance_records",
        help_text="Employee this record belongs to.",
    )
    date = models.DateField(
        db_index=True,
        help_text="Date of attendance (one record per employee per day).",
    )

    # ── Clock In/Out ─────────────────────────────────────────
    clock_in = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Clock-in timestamp.",
    )
    clock_out = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Clock-out timestamp.",
    )

    # ── Check-In Method ──────────────────────────────────────
    clock_in_method = models.CharField(
        max_length=20,
        choices=CHECKIN_METHOD_CHOICES,
        default=CHECKIN_METHOD_WEB,
        blank=True,
        help_text="Method used for clock-in.",
    )
    clock_out_method = models.CharField(
        max_length=20,
        choices=CHECKIN_METHOD_CHOICES,
        default=CHECKIN_METHOD_WEB,
        blank=True,
        help_text="Method used for clock-out.",
    )

    # ── Status ───────────────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=ATTENDANCE_STATUS_CHOICES,
        default=DEFAULT_ATTENDANCE_STATUS,
        db_index=True,
        help_text="Attendance status for the day.",
    )

    # ── Shift Reference ──────────────────────────────────────
    shift = models.ForeignKey(
        "attendance.Shift",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attendance_records",
        help_text="The shift this record is associated with.",
    )

    # ── Work Hours Fields ────────────────────────────────────
    work_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Total work hours including overtime.",
    )
    break_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0,
        help_text="Total break hours taken.",
    )
    effective_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Effective work hours (work_hours - break_hours).",
    )

    # ── Late / Early Departure ───────────────────────────────
    late_minutes = models.PositiveIntegerField(
        default=0,
        help_text="Minutes late beyond grace period.",
    )
    early_departure_minutes = models.PositiveIntegerField(
        default=0,
        help_text="Minutes of early departure beyond grace period.",
    )

    # ── Overtime ─────────────────────────────────────────────
    overtime_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0,
        help_text="Overtime hours worked.",
    )
    overtime_approved = models.BooleanField(
        null=True,
        default=None,
        help_text="Overtime approval status: None=pending, True=approved, False=rejected.",
    )

    # ── Location (GPS) ───────────────────────────────────────
    clock_in_location = models.JSONField(
        null=True,
        blank=True,
        help_text="GPS location data for clock-in.",
    )
    clock_out_location = models.JSONField(
        null=True,
        blank=True,
        help_text="GPS location data for clock-out.",
    )

    # ── IP Address ───────────────────────────────────────────
    clock_in_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address for web-based clock-in.",
    )
    clock_out_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address for web-based clock-out.",
    )

    # ── Notes & Regularization ───────────────────────────────
    notes = models.TextField(
        blank=True,
        default="",
        help_text="Additional notes for the attendance record.",
    )
    is_regularized = models.BooleanField(
        default=False,
        help_text="Whether this record has been regularized.",
    )
    regularized_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="regularized_attendance",
        help_text="User who approved the regularization.",
    )

    class Meta:
        ordering = ["-date", "employee"]
        unique_together = [("employee", "date")]
        indexes = [
            models.Index(fields=["employee", "date"], name="idx_att_emp_date"),
            models.Index(fields=["date"], name="idx_att_date"),
            models.Index(fields=["status"], name="idx_att_status"),
            models.Index(fields=["employee", "status"], name="idx_att_emp_status"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(work_hours__gte=0) & models.Q(work_hours__lte=24),
                name="check_work_hours_range",
            ),
            models.CheckConstraint(
                condition=models.Q(break_hours__gte=0),
                name="check_break_hours_range",
            ),
            models.CheckConstraint(
                condition=models.Q(effective_hours__gte=0),
                name="check_effective_hours_nonneg",
            ),
            models.CheckConstraint(
                condition=models.Q(overtime_hours__gte=0),
                name="check_overtime_hours_nonneg",
            ),
        ]

    def __str__(self):
        return f"{self.employee} - {self.date} ({self.status})"

    @property
    def is_clocked_in(self):
        """Whether the employee has clocked in but not out."""
        return self.clock_in is not None and self.clock_out is None

    @property
    def is_complete(self):
        """Whether both clock-in and clock-out are recorded."""
        return self.clock_in is not None and self.clock_out is not None
