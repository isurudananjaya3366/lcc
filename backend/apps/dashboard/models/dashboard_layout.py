"""DashboardLayout model — user dashboard customization."""

from django.conf import settings
from django.db import models


def _default_widgets():
    """Default widget layout for new dashboards."""
    return {"widgets": []}


class DashboardLayout(models.Model):
    """Stores per-user dashboard layout with widget positions and configuration."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dashboard_layouts",
        verbose_name="User",
    )
    name = models.CharField(
        max_length=100,
        default="Default Dashboard",
        verbose_name="Layout Name",
        help_text="Name for this dashboard layout",
    )
    widgets = models.JSONField(
        default=_default_widgets,
        verbose_name="Widget Configuration",
        help_text="JSON configuration of widget positions and settings",
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name="Default Layout",
        help_text="Whether this is the user's default dashboard layout",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "dashboard_layout"
        verbose_name = "Dashboard Layout"
        verbose_name_plural = "Dashboard Layouts"

    def __str__(self):
        return f"{self.name} ({self.user})"
