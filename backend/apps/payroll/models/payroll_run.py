"""PayrollRun model for tracking payroll processing executions."""

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.mixins import TimestampMixin, UUIDMixin
from apps.payroll.constants import PayrollStatus


class PayrollRun(UUIDMixin, TimestampMixin, models.Model):
    """Represents a single payroll processing execution for a specific period.

    Tracks processing status, stores summary financial totals, captures
    approval information, and logs errors. Multiple runs can exist per
    period to handle corrections and reprocessing.
    """

    # ── Period & Run Identification ──────────────────────────
    payroll_period = models.ForeignKey(
        "payroll.PayrollPeriod",
        on_delete=models.CASCADE,
        related_name="payroll_runs",
        help_text="The payroll period this run processes.",
    )
    run_number = models.PositiveIntegerField(
        default=1,
        help_text="Processing sequence number (increments for correction runs).",
    )

    # ── Status & Timestamps ──────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=PayrollStatus.choices,
        default=PayrollStatus.DRAFT,
        db_index=True,
        help_text="Current processing status of this run.",
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when processing began.",
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when processing completed.",
    )

    # ── Financial Summary ────────────────────────────────────
    total_employees = models.PositiveIntegerField(
        default=0,
        help_text="Number of employees processed in this run.",
    )
    total_gross = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Sum of all employee gross salaries.",
    )
    total_deductions = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Sum of all employee deductions.",
    )
    total_net = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Sum of all employee net salaries.",
    )
    total_epf_employee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Sum of employee EPF contributions (8%).",
    )
    total_epf_employer = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Sum of employer EPF contributions (12%).",
    )
    total_etf = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Sum of employer ETF contributions (3%).",
    )
    total_paye = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Sum of PAYE tax deductions.",
    )

    # ── User Tracking ────────────────────────────────────────
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="processed_payroll_runs",
        help_text="User who initiated the processing.",
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="submitted_payroll_runs",
        help_text="User who submitted the run for approval.",
    )
    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the run was submitted for approval.",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="approved_payroll_runs",
        help_text="User who approved the payroll run.",
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the run was approved.",
    )
    rejected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="rejected_payroll_runs",
        help_text="User who rejected the payroll run.",
    )
    rejected_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the run was rejected.",
    )
    finalized_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="finalized_payroll_runs",
        help_text="User who finalized the payroll run.",
    )
    finalized_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the run was finalized.",
    )
    reversed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="reversed_payroll_runs",
        help_text="User who reversed the payroll run.",
    )
    reversed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the run was reversed.",
    )

    # ── Bank / Payment ───────────────────────────────────────
    bank_file_generated = models.BooleanField(
        default=False,
        help_text="Whether bank file has been generated for this run.",
    )
    payment_reference = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Bank transaction reference for payment.",
    )
    payment_date = models.DateField(
        null=True,
        blank=True,
        help_text="Actual date payment was made.",
    )
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when payment was recorded.",
    )

    # ── Error Tracking ───────────────────────────────────────
    error_count = models.PositiveIntegerField(
        default=0,
        help_text="Count of employees that failed processing.",
    )
    errors = models.JSONField(
        default=list,
        blank=True,
        help_text="Error details for failed employee processing.",
    )

    # ── Notes ────────────────────────────────────────────────
    notes = models.TextField(
        blank=True,
        default="",
        help_text="Optional notes about this run.",
    )

    class Meta:
        ordering = ["-created_on"]
        unique_together = [("payroll_period", "run_number")]
        indexes = [
            models.Index(fields=["status"], name="idx_payrun_status"),
        ]
        verbose_name = "Payroll Run"
        verbose_name_plural = "Payroll Runs"

    def __str__(self):
        return f"Run #{self.run_number} - {self.payroll_period}"

    # ── Computed Properties ──────────────────────────────────

    @property
    def duration(self):
        """Time elapsed between started_at and completed_at."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None

    @property
    def has_errors(self):
        return self.error_count > 0

    @property
    def is_approved(self):
        return self.approved_by is not None

    # ── Validation ───────────────────────────────────────────

    def validate_totals(self):
        """Verify financial totals are consistent."""
        expected_net = self.total_gross - self.total_deductions
        if self.total_net != expected_net:
            raise ValidationError(
                f"Net total ({self.total_net}) does not match "
                f"gross ({self.total_gross}) - deductions ({self.total_deductions}) "
                f"= {expected_net}"
            )

    def can_approve(self):
        """Check if this run is in a state that can be approved."""
        return (
            self.status in (PayrollStatus.PROCESSED, PayrollStatus.PENDING_APPROVAL)
            and self.error_count == 0
            and self.total_employees > 0
        )
