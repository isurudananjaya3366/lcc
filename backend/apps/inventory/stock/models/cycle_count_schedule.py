"""
CycleCountSchedule model for automated cycle counting (Task 72).

Manages scheduled cycle counts based on ABC classification and
configurable intervals. Tracks when products are due for counting
and generates stock takes automatically.
"""

from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.mixins import UUIDMixin, TimestampMixin

from apps.inventory.stock.constants import (
    ABC_CLASS_A,
    ABC_CLASS_B,
    ABC_CLASS_C,
    ABC_CLASSIFICATION_CHOICES,
    CYCLE_COUNT_INTERVAL_A,
    CYCLE_COUNT_INTERVAL_B,
    CYCLE_COUNT_INTERVAL_C,
    SCHEDULE_ACTIVE,
    SCHEDULE_STATUS_CHOICES,
)


class CycleCountScheduleManager(models.Manager):
    """Manager for CycleCountSchedule queries."""

    def active(self):
        """Return active schedules."""
        return self.get_queryset().filter(status=SCHEDULE_ACTIVE)

    def due_for_count(self, as_of=None):
        """Return schedules that are due for counting."""
        if as_of is None:
            as_of = timezone.now().date()
        return self.active().filter(next_count_date__lte=as_of)

    def for_warehouse(self, warehouse):
        """Return schedules for a specific warehouse."""
        return self.get_queryset().filter(warehouse=warehouse)


class CycleCountSchedule(UUIDMixin, TimestampMixin, models.Model):
    """
    Schedule for automated cycle counting based on ABC classification.

    Each schedule defines a counting interval for a product-warehouse
    combination based on its ABC classification. The system uses the
    next_count_date to determine when a count is due.
    """

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="cycle_count_schedules",
        verbose_name="Product",
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="cycle_count_schedules",
        verbose_name="Variant",
    )
    warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.CASCADE,
        related_name="cycle_count_schedules",
        verbose_name="Warehouse",
    )

    # ── Classification & Interval ───────────────────────────────────
    abc_classification = models.CharField(
        max_length=1,
        choices=ABC_CLASSIFICATION_CHOICES,
        default=ABC_CLASS_C,
        verbose_name="ABC Classification",
        help_text="Priority classification for cycle counting frequency.",
    )
    count_interval_days = models.PositiveIntegerField(
        default=CYCLE_COUNT_INTERVAL_C,
        verbose_name="Count Interval (Days)",
        help_text="Number of days between cycle counts.",
    )

    # ── Schedule Tracking ───────────────────────────────────────────
    last_count_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Last Count Date",
        help_text="Date of the last completed cycle count.",
    )
    next_count_date = models.DateField(
        verbose_name="Next Count Date",
        help_text="Date when the next cycle count is due.",
    )

    # ── Status ──────────────────────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=SCHEDULE_STATUS_CHOICES,
        default=SCHEDULE_ACTIVE,
        verbose_name="Status",
    )

    # ── Reference to last stock take ────────────────────────────────
    last_stock_take = models.ForeignKey(
        "inventory.StockTake",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cycle_count_schedule",
        verbose_name="Last Stock Take",
    )

    objects = CycleCountScheduleManager()

    class Meta:
        verbose_name = "Cycle Count Schedule"
        verbose_name_plural = "Cycle Count Schedules"
        db_table = "inventory_cycle_count_schedule"
        ordering = ["next_count_date", "abc_classification"]
        constraints = [
            models.UniqueConstraint(
                fields=["product", "variant", "warehouse"],
                name="uq_cycle_schedule_product_variant_wh",
            ),
        ]
        indexes = [
            models.Index(
                fields=["next_count_date", "status"],
                name="idx_cycle_schedule_next_date",
            ),
            models.Index(
                fields=["warehouse", "abc_classification"],
                name="idx_cycle_schedule_wh_abc",
            ),
        ]

    def __str__(self):
        return (
            f"Cycle Count: {self.product} @ {self.warehouse} "
            f"(Class {self.abc_classification})"
        )

    @property
    def is_due(self):
        """Check if this schedule is due for counting."""
        return self.next_count_date <= timezone.now().date()

    @property
    def days_until_due(self):
        """Days until the next count is due (negative if overdue)."""
        return (self.next_count_date - timezone.now().date()).days

    def record_count_completed(self, stock_take=None):
        """Record that a cycle count was completed and calculate next date."""
        today = timezone.now().date()
        self.last_count_date = today
        self.next_count_date = today + timedelta(days=self.count_interval_days)
        if stock_take:
            self.last_stock_take = stock_take
        self.save(update_fields=[
            "last_count_date", "next_count_date", "last_stock_take", "updated_on",
        ])

    def update_classification(self, new_class):
        """Update ABC classification and adjust interval accordingly."""
        default_intervals = {
            ABC_CLASS_A: CYCLE_COUNT_INTERVAL_A,
            ABC_CLASS_B: CYCLE_COUNT_INTERVAL_B,
            ABC_CLASS_C: CYCLE_COUNT_INTERVAL_C,
        }
        self.abc_classification = new_class
        self.count_interval_days = default_intervals.get(
            new_class, CYCLE_COUNT_INTERVAL_C
        )
        # Recalculate next count date from last count
        if self.last_count_date:
            self.next_count_date = (
                self.last_count_date + timedelta(days=self.count_interval_days)
            )
        self.save(update_fields=[
            "abc_classification", "count_interval_days",
            "next_count_date", "updated_on",
        ])

    @classmethod
    def get_default_interval(cls, abc_class):
        """Get the default counting interval for an ABC classification."""
        return {
            ABC_CLASS_A: CYCLE_COUNT_INTERVAL_A,
            ABC_CLASS_B: CYCLE_COUNT_INTERVAL_B,
            ABC_CLASS_C: CYCLE_COUNT_INTERVAL_C,
        }.get(abc_class, CYCLE_COUNT_INTERVAL_C)
