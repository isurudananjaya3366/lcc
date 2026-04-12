"""
Report result model.

Stores generated financial report data and metadata for caching
and retrieval.
"""

from django.conf import settings
from django.db import models

from apps.core.mixins import UUIDMixin

from ..reports.enums import ReportType


class ReportResult(UUIDMixin, models.Model):
    """
    Stores a generated financial report with data and metadata.

    Acts as a cache for generated reports. Linked to the config
    that produced it.
    """

    config = models.ForeignKey(
        "accounting.ReportConfig",
        on_delete=models.CASCADE,
        related_name="results",
    )
    report_type = models.CharField(
        max_length=20,
        choices=ReportType.choices,
    )

    # ── Report Data ─────────────────────────────────────────────────
    report_data = models.JSONField(default=dict)
    report_metadata = models.JSONField(default=dict)

    # ── Generation Tracking ─────────────────────────────────────────
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_reports",
    )
    generation_time_ms = models.PositiveIntegerField(
        default=0,
        help_text="Time taken to generate the report in milliseconds.",
    )
    is_cached = models.BooleanField(default=False)

    # ── Status ──────────────────────────────────────────────────────
    is_success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, default="")

    class Meta:
        db_table = "accounting_report_result"
        verbose_name = "Report Result"
        verbose_name_plural = "Report Results"
        ordering = ["-generated_at"]
        indexes = [
            models.Index(
                fields=["config", "report_type", "generated_at"],
                name="idx_rptresult_config_type",
            ),
        ]

    def __str__(self):
        generated = (
            self.generated_at.strftime("%Y-%m-%d %H:%M")
            if self.generated_at
            else "pending"
        )
        return f"{self.get_report_type_display()} - {generated}"
