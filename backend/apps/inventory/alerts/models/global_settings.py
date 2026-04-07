"""
Global stock settings model for tenant-wide default thresholds and alert configuration.
"""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin


class GlobalStockSettings(UUIDMixin, TimestampMixin, models.Model):
    """
    Tenant-wide default stock thresholds and alert settings.

    Provides fallback configuration when products don't have specific
    threshold settings. Each tenant schema has exactly one instance.
    This is the bottom of the inheritance chain:
        ProductStockConfig → CategoryStockConfig → GlobalStockSettings
    """

    # ── Threshold Fields (Task 05) ──────────────────────────────
    default_low_threshold = models.PositiveIntegerField(
        default=10,
        validators=[MinValueValidator(0)],
        help_text="Default threshold for low stock alerts.",
    )
    default_reorder_point = models.PositiveIntegerField(
        default=15,
        validators=[MinValueValidator(0)],
        help_text="Default stock level to trigger reorder suggestions.",
    )
    default_reorder_qty = models.PositiveIntegerField(
        default=50,
        validators=[MinValueValidator(1)],
        help_text="Default quantity to suggest when reordering.",
    )
    enable_auto_reorder = models.BooleanField(
        default=True,
        help_text="Automatically generate reorder suggestions.",
    )
    critical_threshold_multiplier = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal("0.50"),
        validators=[MinValueValidator(Decimal("0.10")), MaxValueValidator(Decimal("1.00"))],
        help_text="Critical threshold = low_threshold × this value.",
    )
    days_of_history_for_velocity = models.PositiveIntegerField(
        default=30,
        validators=[MinValueValidator(7), MaxValueValidator(365)],
        help_text="Number of days to analyze for sales velocity.",
    )
    default_lead_time_days = models.PositiveIntegerField(
        default=7,
        validators=[MinValueValidator(1), MaxValueValidator(180)],
        help_text="Default time from order to delivery (days).",
    )

    # ── Alert Channel Settings (Task 06) ────────────────────────
    email_alerts_enabled = models.BooleanField(
        default=True,
        help_text="Send email notifications when alerts trigger.",
    )
    email_recipients = models.TextField(
        blank=True,
        default="",
        help_text="Comma-separated email addresses for alert notifications.",
    )
    dashboard_alerts_enabled = models.BooleanField(
        default=True,
        help_text="Show alerts in admin dashboard.",
    )
    sms_alerts_enabled = models.BooleanField(
        default=False,
        help_text="Send SMS for critical alerts (requires SMS gateway).",
    )
    sms_recipients = models.CharField(
        max_length=500,
        blank=True,
        default="",
        help_text="Comma-separated phone numbers (+94 format).",
    )

    # ── Alert Type Toggles ──────────────────────────────────────
    alert_on_low_stock = models.BooleanField(
        default=True,
        help_text="Send alerts for LOW_STOCK status.",
    )
    alert_on_critical_stock = models.BooleanField(
        default=True,
        help_text="Send alerts for CRITICAL_STOCK status.",
    )
    alert_on_out_of_stock = models.BooleanField(
        default=True,
        help_text="Send alerts for OUT_OF_STOCK status.",
    )
    alert_on_back_in_stock = models.BooleanField(
        default=False,
        help_text="Send notification when stock replenished.",
    )

    # ── Webhook & Throttle ──────────────────────────────────────
    webhook_enabled = models.BooleanField(
        default=False,
        help_text="Enable webhook notifications.",
    )
    webhook_url = models.URLField(
        blank=True,
        default="",
        help_text="POST alerts to external system (optional).",
    )
    webhook_secret = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Webhook authentication secret for HMAC signing.",
    )
    webhook_events = models.JSONField(
        default=list,
        blank=True,
        help_text="List of event types to trigger webhooks.",
    )
    webhook_retry_attempts = models.PositiveIntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Number of retry attempts for failed webhooks.",
    )
    webhook_timeout_seconds = models.PositiveIntegerField(
        default=10,
        validators=[MinValueValidator(1), MaxValueValidator(60)],
        help_text="Webhook request timeout in seconds.",
    )
    alert_throttle_hours = models.PositiveIntegerField(
        default=24,
        validators=[MinValueValidator(1), MaxValueValidator(168)],
        help_text="Minimum hours between repeat alerts for the same product (1-168).",
    )

    # ── Per-Type Throttle (Task 48) ─────────────────────────────
    throttle_low_stock_hours = models.PositiveIntegerField(
        default=24,
        help_text="Hours between LOW_STOCK alerts for same product.",
    )
    throttle_critical_stock_hours = models.PositiveIntegerField(
        default=12,
        help_text="Hours between CRITICAL_STOCK alerts for same product.",
    )
    throttle_oos_hours = models.PositiveIntegerField(
        default=6,
        help_text="Hours between OUT_OF_STOCK alerts for same product.",
    )
    throttle_bypass_threshold = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("50.00"),
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
        help_text="Percentage stock drop to bypass throttle.",
    )

    # ── Monitoring Frequency (Task 44) ──────────────────────────
    monitoring_frequency = models.CharField(
        max_length=20,
        choices=[
            ("hourly", "Every Hour"),
            ("every_2_hours", "Every 2 Hours"),
            ("every_4_hours", "Every 4 Hours"),
            ("twice_daily", "8 AM and 6 PM"),
            ("daily", "Daily at 1 AM"),
        ],
        default="hourly",
        help_text="How often to run the stock monitoring check.",
    )
    monitoring_start_hour = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(23)],
        help_text="Start monitoring at this hour (0-23).",
    )
    monitoring_end_hour = models.PositiveIntegerField(
        default=23,
        validators=[MinValueValidator(0), MaxValueValidator(23)],
        help_text="Stop monitoring at this hour (0-23).",
    )

    # ── EOQ Configuration (Task 59) ─────────────────────────────
    use_eoq_calculation = models.BooleanField(
        default=True,
        help_text="Use Economic Order Quantity formula for suggestions.",
    )
    ordering_cost_lkr = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("5000.00"),
        help_text="Cost per purchase order in LKR.",
    )
    holding_cost_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("25.00"),
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
        help_text="Annual holding cost as % of unit cost.",
    )

    # ── Safety Stock (Task 60) ──────────────────────────────────
    target_service_level = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("95.00"),
        validators=[MinValueValidator(Decimal("50")), MaxValueValidator(Decimal("99.99"))],
        help_text="Target in-stock probability (%).",
    )
    safety_stock_days = models.PositiveIntegerField(
        default=7,
        help_text="Safety stock buffer (days) for simplified calculation.",
    )

    # ── Reorder Suggestions (Task 62) ──────────────────────────
    reorder_suggestions_enabled = models.BooleanField(
        default=True,
        help_text="Enable automated reorder suggestion generation.",
    )

    # ── Auto-Reorder (Task 64) ─────────────────────────────────
    auto_reorder_enabled = models.BooleanField(
        default=False,
        help_text="Enable automatic purchase order creation.",
    )
    auto_reorder_min_urgency = models.CharField(
        max_length=20,
        choices=[
            ("critical", "Critical Only"),
            ("high", "High and Critical"),
            ("medium", "Medium and above"),
        ],
        default="high",
        help_text="Minimum urgency level for auto-reorder.",
    )
    auto_reorder_max_value_lkr = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("100000.00"),
        help_text="Maximum LKR value per auto-generated PO.",
    )
    auto_reorder_require_approval = models.BooleanField(
        default=True,
        help_text="Require approval before sending auto-generated POs.",
    )

    class Meta:
        verbose_name = "Global Stock Settings"
        verbose_name_plural = "Global Stock Settings"
        db_table = "inventory_global_stock_settings"

    def __str__(self):
        return "Global Stock Settings"

    def clean(self):
        super().clean()
        errors = {}
        if (
            self.default_reorder_point is not None
            and self.default_low_threshold is not None
            and self.default_reorder_point < self.default_low_threshold
        ):
            errors["default_reorder_point"] = (
                "Reorder point must be greater than or equal to the low stock threshold."
            )
        if errors:
            raise ValidationError(errors)

    @classmethod
    def get_settings(cls):
        """Return the singleton settings instance, creating it if needed."""
        obj, _ = cls.objects.get_or_create(pk=cls.objects.first().pk if cls.objects.exists() else None)
        return obj

    def get_throttle_period(self, alert_type):
        """Get throttle period in hours for an alert type."""
        from apps.inventory.alerts.constants import (
            ALERT_TYPE_CRITICAL_STOCK,
            ALERT_TYPE_LOW_STOCK,
            ALERT_TYPE_OUT_OF_STOCK,
        )

        throttle_map = {
            ALERT_TYPE_LOW_STOCK: self.throttle_low_stock_hours,
            ALERT_TYPE_CRITICAL_STOCK: self.throttle_critical_stock_hours,
            ALERT_TYPE_OUT_OF_STOCK: self.throttle_oos_hours,
        }
        return throttle_map.get(alert_type, self.alert_throttle_hours)

    def is_within_monitoring_window(self):
        """Check if current time is within the monitoring window."""
        from django.utils import timezone as tz

        current_hour = tz.now().hour
        if self.monitoring_start_hour <= self.monitoring_end_hour:
            return self.monitoring_start_hour <= current_hour <= self.monitoring_end_hour
        # Wraps midnight (e.g., 22 to 6)
        return current_hour >= self.monitoring_start_hour or current_hour <= self.monitoring_end_hour

    def get_monitoring_schedule(self):
        """
        Return a Celery crontab object matching the configured monitoring frequency.

        Used to dynamically update Celery Beat schedules per-tenant.
        """
        from celery.schedules import crontab

        schedules = {
            "hourly": crontab(minute=0),
            "every_2_hours": crontab(minute=0, hour="*/2"),
            "every_4_hours": crontab(minute=0, hour="*/4"),
            "twice_daily": crontab(minute=0, hour="8,18"),
            "daily": crontab(minute=0, hour=1),
        }
        return schedules.get(self.monitoring_frequency, crontab(minute=0))
