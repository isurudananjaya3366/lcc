"""
WarehouseCapacity model — tracks warehouse utilisation and capacity limits.

One-to-one link with Warehouse; provides capacity tracking, utilisation
percentage, and alert thresholds.
"""

import logging
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from apps.core.mixins import TimestampMixin, UUIDMixin
from apps.inventory.warehouses.constants import (
    CAPACITY_THRESHOLD_GREEN,
    CAPACITY_THRESHOLD_ORANGE,
    CAPACITY_THRESHOLD_RED,
    CAPACITY_THRESHOLD_YELLOW,
)

logger = logging.getLogger(__name__)


class WarehouseCapacity(UUIDMixin, TimestampMixin, models.Model):
    """Capacity tracker for a single warehouse."""

    warehouse = models.OneToOneField(
        "inventory.Warehouse",
        on_delete=models.CASCADE,
        related_name="capacity",
    )

    # Limits
    max_item_capacity = models.PositiveIntegerField(default=0)
    max_weight_capacity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Maximum weight in kg",
    )
    max_volume_capacity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Maximum volume in m³",
    )

    # Current usage (updated periodically)
    current_item_count = models.PositiveIntegerField(default=0)
    current_weight = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0"),
    )
    current_volume = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0"),
    )

    last_calculated = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "inventory"
        db_table = "inventory_warehouse_capacities"
        verbose_name = "Warehouse Capacity"
        verbose_name_plural = "Warehouse Capacities"

    def __str__(self):
        return f"Capacity: {self.warehouse.code} ({self.utilization_percentage:.0f}%)"

    # ── utilisation ───────────────────────────────────────────────────

    @property
    def utilization_percentage(self):
        """Item-based utilisation as a percentage (0–100+)."""
        if not self.max_item_capacity:
            return 0.0
        return (self.current_item_count / self.max_item_capacity) * 100

    @property
    def alert_level(self):
        """
        Return string alert level:
        green / yellow / orange / red / critical.
        """
        pct = self.utilization_percentage
        if pct >= CAPACITY_THRESHOLD_RED:
            return "critical"
        if pct >= CAPACITY_THRESHOLD_ORANGE:
            return "red"
        if pct >= CAPACITY_THRESHOLD_YELLOW:
            return "orange"
        if pct >= CAPACITY_THRESHOLD_GREEN:
            return "yellow"
        return "green"

    # ── calculation ───────────────────────────────────────────────────

    def calculate_capacity(self):
        """
        Recalculate current usage from stock data.

        Safely handles the case where the Stock / StockLevel model is
        not yet available.
        """
        try:
            from apps.inventory.models import Stock

            stock_qs = Stock.objects.filter(
                location__warehouse=self.warehouse,
            )
            self.current_item_count = stock_qs.count()
        except Exception:
            logger.debug("Stock model not ready – skipping capacity calculation")

        self.last_calculated = timezone.now()
        self.save(update_fields=[
            "current_item_count",
            "current_weight",
            "current_volume",
            "last_calculated",
        ])

    # ── alerts ────────────────────────────────────────────────────────

    def check_capacity_alerts(self):
        """
        Return a list of alert dicts if any thresholds are breached.
        """
        alerts = []
        pct = self.utilization_percentage

        if pct >= CAPACITY_THRESHOLD_RED:
            alerts.append({
                "level": "critical",
                "message": (
                    f"Warehouse {self.warehouse.code} is at {pct:.0f}% capacity – "
                    "new receipts should be blocked."
                ),
            })
        elif pct >= CAPACITY_THRESHOLD_ORANGE:
            alerts.append({
                "level": "red",
                "message": (
                    f"Warehouse {self.warehouse.code} is at {pct:.0f}% capacity."
                ),
            })
        elif pct >= CAPACITY_THRESHOLD_YELLOW:
            alerts.append({
                "level": "orange",
                "message": (
                    f"Warehouse {self.warehouse.code} approaching capacity ({pct:.0f}%)."
                ),
            })

        return alerts
