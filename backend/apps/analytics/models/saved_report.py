"""
Saved report model.

Allows users to persist report configurations (definition + filters)
for quick re-generation.
"""

from django.conf import settings
from django.core.validators import MinLengthValidator
from django.db import models

from apps.analytics.enums import ReportFormat
from apps.core.mixins import TimestampMixin, UUIDMixin


class SavedReport(UUIDMixin, TimestampMixin, models.Model):
    """A user-saved report configuration for quick re-use."""

    name = models.CharField(
        max_length=150,
        db_index=True,
        validators=[MinLengthValidator(3)],
        help_text="User-assigned name for this saved report.",
    )
    description = models.TextField(
        max_length=1000,
        blank=True,
        null=True,
    )
    report_definition = models.ForeignKey(
        "analytics.ReportDefinition",
        on_delete=models.PROTECT,
        related_name="saved_reports",
        help_text="The base report definition.",
    )
    filters_config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Saved filter parameters (date_range, category, etc).",
    )
    output_format = models.CharField(
        max_length=20,
        choices=ReportFormat.choices,
        default=ReportFormat.PDF,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_reports",
    )
    is_public = models.BooleanField(
        default=False,
        help_text="If True, other users can view/use this saved report.",
    )

    class Meta:
        db_table = "analytics_saved_report"
        ordering = ["-created_on", "name"]
        unique_together = [("owner", "name")]
        verbose_name = "Saved Report"
        verbose_name_plural = "Saved Reports"

    def __str__(self) -> str:
        return f"{self.name} ({self.report_definition})"

    # ── Helpers ───────────────────────────────────────────────────

    def get_filters_display(self) -> str:
        """Return a human-readable summary of saved filters."""
        if not self.filters_config:
            return "No filters"
        parts: list[str] = []
        date_range = self.filters_config.get("date_range")
        if date_range:
            start = date_range.get("start_date", "")
            end = date_range.get("end_date", "")
            if start and end:
                parts.append(f"{start} to {end}")
        for key, value in self.filters_config.items():
            if key == "date_range":
                continue
            parts.append(f"{key}={value}")
        return ", ".join(parts) if parts else "No filters"

    def validate_filters_config(self) -> tuple[bool, dict]:
        """Validate saved filters against the report definition schema."""
        if self.report_definition:
            return self.report_definition.validate_filter_parameters(
                self.filters_config or {}
            )
        return (True, {})

    def can_access(self, user) -> bool:
        """Check if user can access this saved report."""
        if self.is_public:
            return True
        return self.owner_id == user.pk

    def make_public(self) -> None:
        """Make this saved report publicly visible."""
        self.is_public = True
        self.save(update_fields=["is_public", "updated_on"])

    def make_private(self) -> None:
        """Make this saved report private (owner only)."""
        self.is_public = False
        self.save(update_fields=["is_public", "updated_on"])
