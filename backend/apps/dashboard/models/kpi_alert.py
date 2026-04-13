"""KPIAlert model — alert configuration for KPI thresholds."""

from django.db import models


class KPIAlert(models.Model):
    """Configures alert thresholds and notification settings for a KPI."""

    kpi = models.ForeignKey(
        "dashboard.KPIDefinition",
        on_delete=models.CASCADE,
        related_name="alerts",
        verbose_name="KPI",
    )
    name = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Alert Name",
        help_text="Short name for this alert rule",
    )
    warning_threshold = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Warning Threshold",
        help_text="Value that triggers a warning alert",
    )
    critical_threshold = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Critical Threshold",
        help_text="Value that triggers a critical alert",
    )
    comparison = models.CharField(
        max_length=10,
        choices=[
            ("lt", "Less Than"),
            ("gt", "Greater Than"),
            ("lte", "Less Than or Equal"),
            ("gte", "Greater Than or Equal"),
        ],
        default="lt",
        verbose_name="Comparison Operator",
        help_text="How to compare the KPI value against thresholds",
    )
    notify_email = models.BooleanField(
        default=False,
        verbose_name="Email Notification",
        help_text="Send email when threshold is breached",
    )
    notify_dashboard = models.BooleanField(
        default=True,
        verbose_name="Dashboard Notification",
        help_text="Show notification on dashboard when threshold is breached",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
        help_text="Whether this alert is currently active",
    )
    consecutive_breaches = models.PositiveIntegerField(
        default=0,
        verbose_name="Consecutive Breaches",
        help_text="Number of consecutive times the threshold was breached",
    )
    cooldown_period_minutes = models.PositiveIntegerField(
        default=1440,
        verbose_name="Cooldown (minutes)",
        help_text="Minimum minutes between repeated notifications (default 24h)",
    )
    last_triggered = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Last Triggered",
        help_text="When this alert was last triggered",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "dashboard_kpi_alert"
        verbose_name = "KPI Alert"
        verbose_name_plural = "KPI Alerts"

    def __str__(self):
        return f"Alert for {self.kpi.name} (warn: {self.warning_threshold}, crit: {self.critical_threshold})"
