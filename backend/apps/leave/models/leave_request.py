"""Leave Request model for the Leave Management app.

Handles employee leave applications with status workflow,
half-day support, and approval tracking.
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.mixins import SoftDeleteMixin, TimestampMixin, UUIDMixin
from apps.leave.constants import HalfDayType, LeaveRequestStatus


class LeaveRequest(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """Employee leave request with approval workflow.

    Status transitions:
        DRAFT → PENDING → APPROVED → RECALLED
        PENDING → CANCELLED
        PENDING → REJECTED
    Terminal states: CANCELLED, REJECTED, RECALLED
    """

    # ── Core Fields ──────────────────────────────────────────
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.PROTECT,
        related_name="leave_requests",
    )
    leave_type = models.ForeignKey(
        "leave.LeaveType",
        on_delete=models.PROTECT,
        related_name="leave_requests",
    )

    # ── Date & Duration ──────────────────────────────────────
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Total leave days requested (auto-calculated or manual).",
    )

    # ── Half-Day Support ─────────────────────────────────────
    is_half_day = models.BooleanField(default=False)
    half_day_type = models.CharField(
        max_length=20,
        choices=HalfDayType.choices,
        null=True,
        blank=True,
        help_text="Required when is_half_day is True.",
    )

    # ── Request Details ──────────────────────────────────────
    reason = models.TextField(default="", blank=True)
    contact_during_leave = models.CharField(
        max_length=200,
        blank=True,
        default="",
    )

    # ── Status Workflow ──────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=LeaveRequestStatus.choices,
        default=LeaveRequestStatus.DRAFT,
        db_index=True,
    )
    submitted_at = models.DateTimeField(null=True, blank=True)

    # ── Attachment ───────────────────────────────────────────
    attachment = models.FileField(
        upload_to="leave_docs/",
        null=True,
        blank=True,
    )

    # ── Approval Fields ──────────────────────────────────────
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_leave_requests",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, default="")

    # ── Recall Fields ────────────────────────────────────────
    recalled_at = models.DateTimeField(null=True, blank=True)
    recalled_reason = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-created_on"]
        indexes = [
            models.Index(fields=["status"], name="idx_leavereq_status"),
            models.Index(
                fields=["employee", "status"],
                name="idx_leavereq_emp_status",
            ),
        ]

    def __str__(self):
        return (
            f"{self.employee} - {self.leave_type.name} "
            f"({self.start_date} to {self.end_date})"
        )

    def clean(self):
        super().clean()
        errors = {}

        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                errors["end_date"] = "End date cannot be before start date."

        if self.is_half_day:
            if not self.half_day_type:
                errors["half_day_type"] = (
                    "Half-day type is required when is_half_day is True."
                )
            if self.start_date and self.end_date and self.start_date != self.end_date:
                errors["is_half_day"] = (
                    "Half-day leave must have the same start and end date."
                )
        elif self.half_day_type:
            errors["half_day_type"] = (
                "Half-day type should be empty when is_half_day is False."
            )

        if errors:
            raise ValidationError(errors)
