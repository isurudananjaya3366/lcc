"""
CustomerImport model for tracking CSV import progress.
"""

from django.conf import settings
from django.db import models

from apps.core.mixins import UUIDMixin


class CustomerImport(UUIDMixin, models.Model):
    """
    Tracks a customer CSV import operation.
    """

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PROCESSING", "Processing"),
        ("COMPLETED", "Completed"),
        ("COMPLETED_WITH_ERRORS", "Completed with Errors"),
        ("FAILED", "Failed"),
        ("CANCELLED", "Cancelled"),
    ]

    filename = models.CharField(max_length=255, verbose_name="Filename")
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="PENDING",
        verbose_name="Status",
    )
    total_rows = models.IntegerField(default=0, verbose_name="Total Rows")
    processed_rows = models.IntegerField(default=0, verbose_name="Processed Rows")
    successful_rows = models.IntegerField(default=0, verbose_name="Successful Rows")
    failed_rows = models.IntegerField(default=0, verbose_name="Failed Rows")
    skipped_rows = models.IntegerField(default=0, verbose_name="Skipped Rows")
    error_log = models.JSONField(default=list, blank=True, verbose_name="Error Log")
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Started At")
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Completed At",
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customer_imports",
        verbose_name="Uploaded By",
    )

    class Meta:
        db_table = "customers_customer_import"
        verbose_name = "Customer Import"
        verbose_name_plural = "Customer Imports"
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["status"], name="idx_import_status"),
            models.Index(fields=["-started_at"], name="idx_import_started"),
        ]

    def __str__(self):
        return f"{self.filename} ({self.status})"

    @property
    def progress_percent(self) -> float:
        if self.total_rows == 0:
            return 0.0
        return round((self.processed_rows / self.total_rows) * 100, 2)
