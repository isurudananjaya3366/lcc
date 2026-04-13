"""
Analytics report instance model.

Tracks individual generated reports with their filter parameters,
output file, generation status, and metadata.
"""

from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.analytics.enums import ReportFormat, ReportStatus
from apps.core.mixins import TimestampMixin, UUIDMixin


def _default_filter_params():
    return {}


class ReportInstance(UUIDMixin, TimestampMixin, models.Model):
    """
    Tracks an individual generated report.

    Each instance represents a specific report generation with its
    filter parameters, output file, generation status, and timing.
    """

    # Relationships
    report_definition = models.ForeignKey(
        "analytics.ReportDefinition",
        on_delete=models.CASCADE,
        related_name="instances",
        verbose_name="Report Definition",
        help_text="The report definition that was generated.",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="report_instances",
        verbose_name="Requested By",
        help_text="User who requested this report.",
    )

    # Filter data
    filter_parameters = models.JSONField(
        default=_default_filter_params,
        blank=True,
        verbose_name="Filter Parameters",
        help_text="Filter values used for this report generation.",
    )

    # Output
    output_format = models.CharField(
        max_length=10,
        choices=ReportFormat.choices,
        default=ReportFormat.PDF,
        verbose_name="Output Format",
        help_text="Format of the generated report file.",
    )
    output_file = models.FileField(
        upload_to="reports/%Y/%m/",
        null=True,
        blank=True,
        verbose_name="Output File",
        help_text="Generated report file.",
    )
    file_size = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="File Size (bytes)",
        help_text="Size of the generated file in bytes.",
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=ReportStatus.choices,
        default=ReportStatus.PENDING,
        db_index=True,
        verbose_name="Status",
        help_text="Current status of report generation.",
    )

    # Timing
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Started At",
        help_text="When generation started.",
    )
    generated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Generated At",
        help_text="When generation completed.",
    )
    generation_time_seconds = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Generation Time (seconds)",
        help_text="Time taken to generate the report in seconds.",
    )

    # Error tracking
    error_message = models.TextField(
        blank=True,
        verbose_name="Error Message",
        help_text="Error details if generation failed.",
    )

    # Additional tracking (Task 14)
    title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Title",
        help_text="User-friendly report title.",
    )
    celery_task_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Celery Task ID",
        help_text="ID of the Celery task for cancellation.",
    )
    is_scheduled = models.BooleanField(
        default=False,
        verbose_name="Is Scheduled",
        help_text="Indicates if this report was triggered by a schedule.",
    )
    accessed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Last Accessed",
        help_text="When the report was last downloaded.",
    )
    access_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Access Count",
        help_text="Number of times the report has been downloaded.",
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Expires At",
        help_text="When the report file will be eligible for deletion.",
    )

    class Meta:
        verbose_name = "Report Instance"
        verbose_name_plural = "Report Instances"
        ordering = ["-created_on"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["report_definition", "-created_on"]),
            models.Index(fields=["celery_task_id"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return self.title or f"{self.report_definition.name} ({self.status})"

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = self._generate_title()
        if not self.expires_at and self.status == ReportStatus.COMPLETED:
            days = 90 if self.is_scheduled else 30
            self.expires_at = timezone.now() + timedelta(days=days)
        super().save(*args, **kwargs)

    def _generate_title(self) -> str:
        """Auto-generate a title from definition and filters."""
        name = self.report_definition.name if self.report_definition_id else "Report"
        date_range = (self.filter_parameters or {}).get("date_range", {})
        start = date_range.get("start_date", "")
        end = date_range.get("end_date", "")
        if start and end:
            return f"{name} - {start} to {end}"
        return name

    def mark_generating(self):
        """Mark this instance as currently generating."""
        self.status = ReportStatus.GENERATING
        self.started_at = timezone.now()
        self.save(update_fields=["status", "started_at", "updated_on"])

    def mark_completed(self, file_path=None, file_size=None):
        """Mark this instance as completed."""
        now = timezone.now()
        self.status = ReportStatus.COMPLETED
        self.generated_at = now
        if self.started_at:
            self.generation_time_seconds = int(
                (now - self.started_at).total_seconds()
            )
        if file_path:
            self.output_file = file_path
        if file_size is not None:
            self.file_size = file_size
        # Set expiry
        days = 90 if self.is_scheduled else 30
        self.expires_at = now + timedelta(days=days)
        self.save(update_fields=[
            "status", "generated_at", "generation_time_seconds",
            "output_file", "file_size", "expires_at", "updated_on",
        ])

    def mark_failed(self, error: str):
        """Mark this instance as failed with an error message."""
        self.status = ReportStatus.FAILED
        self.error_message = error
        self.generated_at = timezone.now()
        if self.started_at:
            self.generation_time_seconds = int(
                (self.generated_at - self.started_at).total_seconds()
            )
        self.save(update_fields=[
            "status", "error_message", "generated_at",
            "generation_time_seconds", "updated_on",
        ])

    def can_cancel(self) -> bool:
        """Check if this report generation can be cancelled."""
        return self.status in (ReportStatus.PENDING, ReportStatus.GENERATING)

    def is_expired(self) -> bool:
        """Check if this report has expired."""
        if not self.expires_at:
            return False
        return self.expires_at < timezone.now()

    def increment_access(self) -> None:
        """Record a download access and extend expiry."""
        self.access_count += 1
        self.accessed_at = timezone.now()
        if self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=30)
        self.save(update_fields=[
            "access_count", "accessed_at", "expires_at", "updated_on",
        ])

    def delete_file(self) -> None:
        """Delete the physical report file."""
        if self.output_file:
            self.output_file.delete(save=False)
            self.output_file = None
            self.save(update_fields=["output_file", "updated_on"])

    def get_file_size_display(self) -> str:
        """Return human-readable file size."""
        if self.file_size is None:
            return "N/A"
        size = self.file_size
        for unit in ("B", "KB", "MB", "GB"):
            if abs(size) < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def get_generation_time_display(self) -> str:
        """Return human-readable generation time."""
        if self.generation_time_seconds is None:
            return "N/A"
        secs = self.generation_time_seconds
        if secs < 60:
            return f"{secs} second{'s' if secs != 1 else ''}"
        minutes = secs // 60
        remaining = secs % 60
        if remaining:
            return f"{minutes} minute{'s' if minutes != 1 else ''} {remaining} seconds"
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
