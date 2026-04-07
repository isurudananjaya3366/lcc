"""PayslipBatch model for tracking bulk generation runs."""

from django.conf import settings
from django.db import models

from apps.core.mixins import TimestampMixin, UUIDMixin


class BatchStatus(models.TextChoices):
    """Status choices for batch operations."""

    PENDING = "PENDING", "Pending"
    PROCESSING = "PROCESSING", "Processing"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"
    PARTIAL = "PARTIAL", "Partially Completed"


class PayslipBatch(UUIDMixin, TimestampMixin, models.Model):
    """Tracks a bulk payslip generation or email distribution run.

    Records total/success/failed counts and timing for audit and
    progress tracking purposes.
    """

    # ── Relationships ────────────────────────────────────────
    payroll_period = models.ForeignKey(
        "payroll.PayrollPeriod",
        on_delete=models.CASCADE,
        related_name="payslip_batches",
        help_text="Payroll period for this batch.",
    )
    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payslip_batches",
        help_text="User who initiated this batch.",
    )

    # ── Batch Type ───────────────────────────────────────────
    batch_type = models.CharField(
        max_length=20,
        choices=[
            ("GENERATION", "PDF Generation"),
            ("EMAIL", "Email Distribution"),
        ],
        help_text="Type of batch operation.",
    )

    # ── Status & Counts ──────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=BatchStatus.choices,
        default=BatchStatus.PENDING,
        db_index=True,
        help_text="Current batch status.",
    )
    total_count = models.PositiveIntegerField(
        default=0,
        help_text="Total payslips in this batch.",
    )
    success_count = models.PositiveIntegerField(
        default=0,
        help_text="Successfully processed payslips.",
    )
    failed_count = models.PositiveIntegerField(
        default=0,
        help_text="Failed payslips in this batch.",
    )
    error_log = models.TextField(
        blank=True,
        null=True,
        help_text="Error details for failed items.",
    )

    # ── Timing ───────────────────────────────────────────────
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When batch processing started.",
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When batch processing completed.",
    )

    class Meta:
        app_label = "payslip"
        verbose_name = "Payslip Batch"
        verbose_name_plural = "Payslip Batches"
        ordering = ["-created_on"]

    def __str__(self):
        return (
            f"{self.get_batch_type_display()} - "
            f"{self.payroll_period} ({self.status})"
        )

    @property
    def duration_seconds(self):
        """Return batch processing duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @property
    def progress_percent(self):
        """Return progress as a percentage."""
        if self.total_count == 0:
            return 0
        return round(
            (self.success_count + self.failed_count) / self.total_count * 100
        )
