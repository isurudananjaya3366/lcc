"""
StockAlert model for tracking stock alert occurrences.

Covers Tasks 19-28: model definition, warehouse FK, threshold fields,
stock snapshot, lifecycle timestamps, acknowledgment, snooze,
Meta/indexes, custom manager, and deduplication logic.
"""

from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.html import format_html

from apps.core.mixins import UUIDMixin
from apps.inventory.alerts.constants import (
    ALERT_STATUS_ACTIVE,
    ALERT_STATUS_ACKNOWLEDGED,
    ALERT_STATUS_CHOICES,
    ALERT_STATUS_RESOLVED,
    ALERT_STATUS_SNOOZED,
    ALERT_TYPE_BACK_IN_STOCK,
    ALERT_TYPE_CHOICES,
    ALERT_TYPE_COLORS,
    ALERT_TYPE_CRITICAL_STOCK,
    ALERT_TYPE_LOW_STOCK,
    ALERT_TYPE_OUT_OF_STOCK,
    ALERT_TYPE_PRIORITY,
    THRESHOLD_TYPE_CHOICES,
)


class StockAlertManager(models.Manager):
    """Custom manager for StockAlert with convenience query methods."""

    def get_active(self):
        return self.filter(status=ALERT_STATUS_ACTIVE)

    def get_acknowledged(self):
        return self.filter(status=ALERT_STATUS_ACKNOWLEDGED)

    def get_resolved(self):
        return self.filter(status=ALERT_STATUS_RESOLVED)

    def get_unacknowledged(self):
        return self.filter(
            status=ALERT_STATUS_ACTIVE,
            acknowledged_at__isnull=True,
        )

    def get_by_product(self, product, include_resolved=False):
        qs = self.filter(product=product)
        if not include_resolved:
            qs = qs.exclude(status=ALERT_STATUS_RESOLVED)
        return qs

    def get_by_warehouse(self, warehouse, include_resolved=False):
        qs = self.filter(warehouse=warehouse)
        if not include_resolved:
            qs = qs.exclude(status=ALERT_STATUS_RESOLVED)
        return qs

    def get_by_type(self, alert_type):
        return self.filter(alert_type=alert_type)

    def get_critical(self):
        return self.filter(
            alert_type__in=[ALERT_TYPE_OUT_OF_STOCK, ALERT_TYPE_CRITICAL_STOCK],
            status=ALERT_STATUS_ACTIVE,
        )

    def get_snoozed_expired(self):
        return self.filter(
            status=ALERT_STATUS_SNOOZED,
            snoozed_until__lte=timezone.now(),
        )

    def get_by_date_range(self, start_date, end_date):
        return self.filter(created_at__range=(start_date, end_date))

    def count_by_status(self):
        from django.db.models import Count
        return dict(
            self.values_list("status").annotate(count=Count("id")).values_list("status", "count")
        )

    def count_by_type(self):
        from django.db.models import Count
        return dict(
            self.values_list("alert_type").annotate(count=Count("id")).values_list("alert_type", "count")
        )

    def average_resolution_time(self):
        from django.db.models import Avg, ExpressionWrapper, F, DurationField
        return self.filter(resolved_at__isnull=False).aggregate(
            avg_time=Avg(
                ExpressionWrapper(
                    F("resolved_at") - F("created_at"),
                    output_field=DurationField(),
                )
            )
        )["avg_time"]

    # ── Dashboard Aggregation (Task 49) ─────────────────────────

    def get_dashboard_summary(self):
        """Get summary data for the dashboard."""
        from django.db.models import Count, Q

        active_alerts = self.get_active()

        return {
            "total_active": active_alerts.count(),
            "by_type": list(
                active_alerts.values("alert_type").annotate(count=Count("id"))
            ),
            "by_priority": list(
                active_alerts.values("priority").annotate(count=Count("id"))
            ),
            "critical_count": active_alerts.filter(priority__gte=3).count(),
            "needs_attention": active_alerts.filter(
                Q(status=ALERT_STATUS_ACTIVE) & Q(acknowledged_at__isnull=True)
            ).count(),
        }

    def get_top_alerts(self, limit=10):
        """Get highest priority active alerts."""
        return self.get_active().order_by("-priority", "-created_at")[:limit]

    def get_alert_trends(self, days=7):
        """Get daily alert counts over a period."""
        from django.db.models import Count
        from django.db.models.functions import TruncDate

        cutoff = timezone.now() - timedelta(days=days)

        return list(
            self.filter(created_at__gte=cutoff)
            .annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        )

    def get_warehouse_summary(self):
        """Get active alert counts grouped by warehouse."""
        from django.db.models import Count

        return list(
            self.get_active()
            .values("warehouse__name")
            .annotate(alert_count=Count("id"))
            .order_by("-alert_count")
        )


class StockAlert(UUIDMixin, models.Model):
    """
    Tracks stock alert occurrences with lifecycle management.

    Alerts are created when stock thresholds are breached and support
    acknowledgment, snoozing, and resolution workflows.
    """

    # ── Core relationships ──────────────────────────────────────
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="stock_alerts",
        help_text="Product that triggered this alert",
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="stock_alerts",
        help_text="Optional specific variant",
    )
    warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="stock_alerts",
        help_text="Warehouse where alert occurred (None = all warehouses)",
    )

    # ── Alert type & status ─────────────────────────────────────
    alert_type = models.CharField(
        max_length=30,
        choices=ALERT_TYPE_CHOICES,
        help_text="Type of stock alert",
    )
    status = models.CharField(
        max_length=30,
        choices=ALERT_STATUS_CHOICES,
        default=ALERT_STATUS_ACTIVE,
        help_text="Current status of alert",
    )
    priority = models.PositiveSmallIntegerField(
        default=2,
        help_text="Priority level (1=Info, 4=Critical)",
    )
    message = models.TextField(
        blank=True,
        help_text="Auto-generated alert message",
    )

    # ── Threshold context ───────────────────────────────────────
    threshold_value = models.PositiveIntegerField(
        default=0,
        help_text="Threshold that was breached to trigger alert",
    )
    threshold_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Type of threshold (low_stock_threshold, reorder_point, etc.)",
    )
    threshold_source = models.CharField(
        max_length=50,
        choices=THRESHOLD_TYPE_CHOICES,
        blank=True,
        help_text="Where the threshold came from in config chain",
    )
    expected_restock_date = models.DateField(
        null=True,
        blank=True,
        help_text="Expected date when stock will be replenished",
    )
    reorder_suggested = models.BooleanField(
        default=False,
        help_text="Whether reorder suggestion was created",
    )
    days_until_critical = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Estimated days until stock becomes critical",
    )
    velocity_at_alert = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Daily sales velocity when alert created",
    )

    # ── Stock snapshot ──────────────────────────────────────────
    current_stock = models.IntegerField(
        default=0,
        help_text="Stock level when alert was created",
    )
    available_quantity = models.IntegerField(
        default=0,
        help_text="Available quantity (stock - reserved) when alert created",
    )
    reserved_quantity = models.PositiveIntegerField(
        default=0,
        help_text="Quantity reserved in orders when alert created",
    )
    incoming_quantity = models.PositiveIntegerField(
        default=0,
        help_text="Quantity in open purchase orders when alert created",
    )
    stock_change_since_alert = models.IntegerField(
        default=0,
        editable=False,
        help_text="Stock change since alert created (calculated)",
    )
    last_stock_check = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time stock level was checked for this alert",
    )

    # ── Lifecycle timestamps ────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    # ── User tracking ──────────────────────────────────────────
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="acknowledged_alerts",
    )
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_alerts",
    )

    # ── Snooze ──────────────────────────────────────────────────
    snoozed_until = models.DateTimeField(null=True, blank=True)
    snoozed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="snoozed_alerts",
    )
    snooze_reason = models.CharField(max_length=200, blank=True)
    snooze_count = models.PositiveIntegerField(default=0)

    objects = StockAlertManager()

    class Meta:
        verbose_name = "Stock Alert"
        verbose_name_plural = "Stock Alerts"
        db_table = "inventory_stock_alert"
        ordering = ["-priority", "-created_at"]
        get_latest_by = "created_at"
        indexes = [
            models.Index(fields=["product"]),
            models.Index(fields=["warehouse"]),
            models.Index(fields=["status"]),
            models.Index(fields=["alert_type"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["resolved_at"]),
            models.Index(fields=["snoozed_until"]),
            models.Index(fields=["product", "warehouse", "alert_type", "status"]),
            models.Index(fields=["-priority", "-created_at"]),
        ]
        permissions = [
            ("view_alert_dashboard", "Can view alert dashboard"),
            ("acknowledge_alerts", "Can acknowledge alerts"),
            ("resolve_alerts", "Can resolve alerts"),
            ("snooze_alerts", "Can snooze alerts"),
        ]

    # ── String / display ────────────────────────────────────────

    def __str__(self):
        wh = self.warehouse_name
        return f"{self.get_alert_type_display()} - {self.product} @ {wh} ({self.get_status_display()})"

    @property
    def warehouse_name(self):
        return self.warehouse.name if self.warehouse_id else "All Warehouses"

    @property
    def stock_status_emoji(self):
        emojis = {
            ALERT_TYPE_OUT_OF_STOCK: "\U0001f534",
            ALERT_TYPE_CRITICAL_STOCK: "\U0001f7e0",
            ALERT_TYPE_LOW_STOCK: "\U0001f7e1",
            ALERT_TYPE_BACK_IN_STOCK: "\U0001f7e2",
        }
        return emojis.get(self.alert_type, "\u26aa")

    @property
    def deduplication_key(self):
        wh_id = str(self.warehouse_id) if self.warehouse_id else "all"
        return f"{self.product_id}:{self.alert_type}:{wh_id}"

    # ── Save overrides ──────────────────────────────────────────

    def save(self, *args, **kwargs):
        if not self.priority or self.priority == 2:
            self.priority = ALERT_TYPE_PRIORITY.get(self.alert_type, 2)
        if not self.message:
            self.message = self._generate_message()
        super().save(*args, **kwargs)

    def _generate_message(self):
        wh = f" at {self.warehouse.name}" if self.warehouse_id else ""
        templates = {
            ALERT_TYPE_LOW_STOCK: f"{self.product}{wh} is running low ({self.current_stock} units remaining)",
            ALERT_TYPE_CRITICAL_STOCK: f"CRITICAL: {self.product}{wh} stock critically low ({self.current_stock} units)",
            ALERT_TYPE_OUT_OF_STOCK: f"OUT OF STOCK: {self.product}{wh} is unavailable",
            ALERT_TYPE_BACK_IN_STOCK: f"{self.product}{wh} is back in stock ({self.current_stock} units)",
        }
        return templates.get(self.alert_type, "Stock alert")

    # ── Lifecycle properties ────────────────────────────────────

    @property
    def is_resolved(self):
        return self.resolved_at is not None

    @property
    def is_acknowledged(self):
        return self.acknowledged_at is not None

    @property
    def time_to_acknowledge(self):
        if not self.acknowledged_at:
            return None
        return self.acknowledged_at - self.created_at

    @property
    def time_to_resolve(self):
        if not self.resolved_at:
            return None
        return self.resolved_at - self.created_at

    @property
    def days_active(self):
        if self.is_resolved:
            return (self.resolved_at - self.created_at).days
        return (timezone.now() - self.created_at).days

    # ── Acknowledgment ──────────────────────────────────────────

    def acknowledge(self, user):
        self.status = ALERT_STATUS_ACKNOWLEDGED
        self.acknowledged_at = timezone.now()
        self.acknowledged_by = user
        self.save(update_fields=["status", "acknowledged_at", "acknowledged_by", "updated_at"])

    def get_acknowledger_name(self):
        if self.acknowledged_by:
            return self.acknowledged_by.get_full_name() or self.acknowledged_by.username
        return "Not Acknowledged"

    # ── Resolution ──────────────────────────────────────────────

    def resolve(self, user=None, auto=False):
        self.status = ALERT_STATUS_RESOLVED
        self.resolved_at = timezone.now()
        if user:
            self.resolved_by = user
        self.save(update_fields=["status", "resolved_at", "resolved_by", "updated_at"])

    def auto_resolve(self):
        if self.has_stock_improved and self.status == ALERT_STATUS_ACTIVE:
            self.resolve(auto=True)
            return True
        return False

    def get_resolver_name(self):
        if self.resolved_by:
            return self.resolved_by.get_full_name() or self.resolved_by.username
        elif self.resolved_at:
            return "Auto-resolved"
        return "Unresolved"

    # ── Snooze ──────────────────────────────────────────────────

    def snooze(self, until_datetime, user, reason=""):
        if until_datetime <= timezone.now():
            raise ValueError("Snooze time must be in the future")
        self.status = ALERT_STATUS_SNOOZED
        self.snoozed_until = until_datetime
        self.snoozed_by = user
        self.snooze_reason = reason
        self.snooze_count += 1
        self.save()

    def unsnooze(self):
        self.status = ALERT_STATUS_ACTIVE
        self.snoozed_until = None
        self.save(update_fields=["status", "snoozed_until", "updated_at"])

    def snooze_for_hours(self, hours, user, reason=""):
        until = timezone.now() + timedelta(hours=hours)
        self.snooze(until, user, reason)

    def snooze_for_days(self, days, user, reason=""):
        until = timezone.now() + timedelta(days=days)
        self.snooze(until, user, reason)

    @property
    def is_snoozed(self):
        if self.status == ALERT_STATUS_SNOOZED and self.snoozed_until:
            return self.snoozed_until > timezone.now()
        return False

    @property
    def snooze_expired(self):
        if self.status == ALERT_STATUS_SNOOZED and self.snoozed_until:
            return self.snoozed_until <= timezone.now()
        return False

    def get_snooze_info(self):
        return {
            "is_snoozed": self.is_snoozed,
            "until": self.snoozed_until,
            "by": self.get_snoozer_name(),
            "reason": self.snooze_reason,
            "count": self.snooze_count,
        }

    def get_snoozer_name(self):
        if self.snoozed_by:
            return self.snoozed_by.get_full_name() or self.snoozed_by.username
        return ""

    # ── Stock tracking ──────────────────────────────────────────

    @property
    def has_stock_improved(self):
        if self.alert_type == ALERT_TYPE_OUT_OF_STOCK:
            return self.stock_change_since_alert > 0
        elif self.alert_type == ALERT_TYPE_CRITICAL_STOCK:
            return self.current_stock + self.stock_change_since_alert > self.threshold_value * 0.5
        elif self.alert_type == ALERT_TYPE_LOW_STOCK:
            return self.current_stock + self.stock_change_since_alert > self.threshold_value
        return False

    def update_stock_change(self):
        from apps.inventory.stock.models.stock_level import StockLevel

        level = StockLevel.objects.filter(
            product=self.product,
            warehouse=self.warehouse,
        ).first()
        if level:
            self.stock_change_since_alert = level.quantity - self.current_stock
            self.last_stock_check = timezone.now()
            self.save(update_fields=["stock_change_since_alert", "last_stock_check"])

    def get_current_stock_level(self):
        from apps.inventory.stock.models.stock_level import StockLevel

        level = StockLevel.objects.filter(
            product=self.product,
            warehouse=self.warehouse,
        ).first()
        current = level.quantity if level else 0
        return {
            "current": current,
            "at_alert": self.current_stock,
            "change": current - self.current_stock,
        }

    def get_warehouse_stock_level(self):
        from apps.inventory.stock.models.stock_level import StockLevel

        level = StockLevel.objects.filter(
            product=self.product,
            warehouse=self.warehouse,
        ).first()
        return level.quantity if level else 0

    # ── Threshold helpers ───────────────────────────────────────

    def calculate_days_until_critical(self):
        if not self.velocity_at_alert or self.velocity_at_alert <= 0:
            return None
        critical_threshold = self.threshold_value * 0.5
        stock_to_critical = self.current_stock - critical_threshold
        if stock_to_critical <= 0:
            return 0
        return max(0, int(stock_to_critical / float(self.velocity_at_alert)))

    def get_threshold_info(self):
        return {
            "value": self.threshold_value,
            "type": self.threshold_type,
            "source": self.threshold_source,
            "velocity": float(self.velocity_at_alert) if self.velocity_at_alert else None,
            "days_until_critical": self.days_until_critical,
        }

    # ── Deduplication ───────────────────────────────────────────

    @classmethod
    def get_existing_alert(cls, product, alert_type, warehouse=None):
        return cls.objects.filter(
            product=product,
            alert_type=alert_type,
            warehouse=warehouse,
            status=ALERT_STATUS_ACTIVE,
        ).first()

    @classmethod
    def check_cooldown(cls, product, alert_type, warehouse=None, cooldown_hours=24):
        cutoff = timezone.now() - timedelta(hours=cooldown_hours)
        return cls.objects.filter(
            product=product,
            alert_type=alert_type,
            warehouse=warehouse,
            status=ALERT_STATUS_RESOLVED,
            resolved_at__gte=cutoff,
        ).exists()

    @classmethod
    def create_or_update(cls, product, alert_type, warehouse=None,
                         current_stock=0, threshold_value=0, **kwargs):
        """Create new alert or update existing. Returns (alert, created)."""
        existing = cls.get_existing_alert(product, alert_type, warehouse)
        if existing:
            stock_change = abs(existing.current_stock - current_stock)
            if stock_change >= 5:
                existing.current_stock = current_stock
                existing.threshold_value = threshold_value
                existing.update_stock_change()
                existing.save()
            return (existing, False)

        if cls.check_cooldown(product, alert_type, warehouse):
            return (None, False)

        alert = cls.objects.create(
            product=product,
            alert_type=alert_type,
            warehouse=warehouse,
            current_stock=current_stock,
            threshold_value=threshold_value,
            **kwargs,
        )
        return (alert, True)

    def is_duplicate_of(self, other):
        return self.deduplication_key == other.deduplication_key
