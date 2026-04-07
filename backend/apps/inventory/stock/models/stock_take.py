"""
StockTake model for physical inventory counting sessions.

A StockTake represents a cycle where warehouse staff count physical
inventory and compare it against system records. Variances are calculated,
reviewed, and optionally approved before being committed as adjustments.
"""

import logging
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.mixins import UUIDMixin, TimestampMixin

from apps.inventory.stock.constants import (
    APPROVAL_NOT_REQUIRED,
    APPROVAL_STATUS_CHOICES,
    STOCK_TAKE_CANCELLED,
    STOCK_TAKE_COMPLETED,
    STOCK_TAKE_COUNTING,
    STOCK_TAKE_DRAFT,
    STOCK_TAKE_IN_PROGRESS,
    STOCK_TAKE_REVIEW,
    STOCK_TAKE_SCOPE_CHOICES,
    STOCK_TAKE_SCOPE_FULL,
    STOCK_TAKE_STATUS_CHOICES,
)

logger = logging.getLogger(__name__)


class StockTakeManager(models.Manager):
    """Custom manager for StockTake queries."""

    def active(self):
        """Stock takes that are not completed or cancelled."""
        return self.get_queryset().exclude(
            status__in=[STOCK_TAKE_COMPLETED, STOCK_TAKE_CANCELLED],
        )

    def for_warehouse(self, warehouse):
        return self.get_queryset().filter(warehouse=warehouse)


class StockTake(UUIDMixin, TimestampMixin, models.Model):
    """Physical inventory counting session."""

    # ── Identification ──────────────────────────────────────────────
    name = models.CharField(
        max_length=200,
        verbose_name="Name",
        help_text="Descriptive name for this stock take.",
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name="Description",
    )
    reference = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="Reference",
        help_text="Auto-generated reference (e.g. ST-2026-0001).",
    )
    warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.CASCADE,
        related_name="stock_takes",
        verbose_name="Warehouse",
    )

    # ── Status & Scope ──────────────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=STOCK_TAKE_STATUS_CHOICES,
        default=STOCK_TAKE_DRAFT,
        db_index=True,
        verbose_name="Status",
    )
    scope = models.CharField(
        max_length=20,
        choices=STOCK_TAKE_SCOPE_CHOICES,
        default=STOCK_TAKE_SCOPE_FULL,
        verbose_name="Scope",
    )
    is_blind_count = models.BooleanField(
        default=False,
        verbose_name="Blind Count",
        help_text="If True, counters cannot see expected quantities.",
    )

    # ── Dates ───────────────────────────────────────────────────────
    scheduled_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Scheduled Date",
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Started At",
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Completed At",
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Cancelled At",
    )

    # ── Users ───────────────────────────────────────────────────────
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_stock_takes",
        verbose_name="Created By",
    )
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="completed_stock_takes",
        verbose_name="Completed By",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_stock_takes",
        verbose_name="Approved By",
    )

    # ── Approval ────────────────────────────────────────────────────
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default=APPROVAL_NOT_REQUIRED,
        verbose_name="Approval Status",
    )

    # ── Statistics ──────────────────────────────────────────────────
    total_items = models.PositiveIntegerField(default=0, verbose_name="Total Items")
    counted_items = models.PositiveIntegerField(default=0, verbose_name="Counted Items")
    items_with_variance = models.PositiveIntegerField(default=0, verbose_name="Items with Variance")
    total_variance_value = models.DecimalField(
        max_digits=15, decimal_places=3, default=Decimal("0"),
        verbose_name="Total Variance Value",
    )

    objects = StockTakeManager()

    class Meta:
        verbose_name = "Stock Take"
        verbose_name_plural = "Stock Takes"
        db_table = "inventory_stock_take"
        ordering = ["-created_on"]
        indexes = [
            models.Index(fields=["warehouse", "status"], name="idx_st_warehouse_status"),
            models.Index(fields=["-created_on"], name="idx_st_created"),
        ]
        permissions = [
            ("can_view_stocktake", "Can view stock takes"),
            ("can_create_stocktake", "Can create stock takes"),
            ("can_finalize_stocktake", "Can finalize stock takes"),
        ]

    def __str__(self):
        return f"{self.reference} — {self.name}"

    # ── Status Helpers ──────────────────────────────────────────────

    @property
    def is_active(self):
        return self.status not in (STOCK_TAKE_COMPLETED, STOCK_TAKE_CANCELLED)

    @property
    def is_editable(self):
        return self.status in (STOCK_TAKE_DRAFT, STOCK_TAKE_IN_PROGRESS)

    @property
    def can_record_counts(self):
        return self.status == STOCK_TAKE_COUNTING

    @property
    def progress_percentage(self):
        if self.total_items == 0:
            return Decimal("0")
        return Decimal(str(self.counted_items * 100)) / Decimal(str(self.total_items))

    def start_counting(self):
        if self.status not in (STOCK_TAKE_DRAFT, STOCK_TAKE_IN_PROGRESS):
            raise ValueError(f"Cannot start counting from status '{self.status}'.")
        self.status = STOCK_TAKE_COUNTING
        self.started_at = timezone.now()
        self.save(update_fields=["status", "started_at", "updated_on"])

    def submit_for_review(self):
        if self.status != STOCK_TAKE_COUNTING:
            raise ValueError("Can only submit for review from COUNTING status.")
        self.status = STOCK_TAKE_REVIEW
        self.save(update_fields=["status", "updated_on"])

    def complete(self, user=None):
        if self.status != STOCK_TAKE_REVIEW:
            raise ValueError("Can only complete from REVIEW status.")
        self.status = STOCK_TAKE_COMPLETED
        self.completed_at = timezone.now()
        self.completed_by = user
        self.save(update_fields=["status", "completed_at", "completed_by", "updated_on"])

    def cancel(self, user=None):
        if self.status in (STOCK_TAKE_COMPLETED,):
            raise ValueError("Cannot cancel a completed stock take.")
        self.status = STOCK_TAKE_CANCELLED
        self.cancelled_at = timezone.now()
        self.save(update_fields=["status", "cancelled_at", "updated_on"])
