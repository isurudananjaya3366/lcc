"""
StockTakeItem model — individual counted item within a stock take.

Each item records expected vs counted quantity, with automatic variance
calculation on save.
"""

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.mixins import UUIDMixin, TimestampMixin

from apps.inventory.stock.constants import (
    APPROVAL_NOT_REQUIRED,
    APPROVAL_STATUS_CHOICES,
    ITEM_APPROVAL_THRESHOLD_CRITICAL,
    ITEM_APPROVAL_THRESHOLD_MAJOR,
    ITEM_APPROVAL_THRESHOLD_MINOR,
    STOCK_TAKE_ITEM_COUNTED,
    STOCK_TAKE_ITEM_PENDING,
    STOCK_TAKE_ITEM_STATUS_CHOICES,
    VARIANCE_MINOR_THRESHOLD,
    VARIANCE_MODERATE_THRESHOLD,
    VARIANCE_SIGNIFICANT_THRESHOLD,
)


class StockTakeItemManager(models.Manager):
    """Custom manager for StockTakeItem queries."""

    def with_variance(self):
        return self.get_queryset().exclude(variance_quantity=Decimal("0"))

    def over_threshold(self, threshold):
        return self.get_queryset().filter(
            models.Q(variance_quantity__gt=threshold)
            | models.Q(variance_quantity__lt=-threshold)
        )

    def negative_variance(self):
        return self.get_queryset().filter(variance_quantity__lt=0)

    def positive_variance(self):
        return self.get_queryset().filter(variance_quantity__gt=0)

    def pending(self):
        return self.get_queryset().filter(status=STOCK_TAKE_ITEM_PENDING)

    def counted(self):
        return self.get_queryset().exclude(status=STOCK_TAKE_ITEM_PENDING)


class StockTakeItem(UUIDMixin, TimestampMixin, models.Model):
    """Individual item within a stock take."""

    # ── Foreign Keys ────────────────────────────────────────────────
    stock_take = models.ForeignKey(
        "inventory.StockTake",
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Stock Take",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="stock_take_items",
        verbose_name="Product",
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="stock_take_items",
        verbose_name="Variant",
    )
    location = models.ForeignKey(
        "inventory.StorageLocation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_take_items",
        verbose_name="Storage Location",
    )

    # ── Quantities ──────────────────────────────────────────────────
    expected_quantity = models.DecimalField(
        max_digits=15, decimal_places=3, default=Decimal("0"),
        verbose_name="Expected Quantity",
    )
    counted_quantity = models.DecimalField(
        max_digits=15, decimal_places=3, null=True, blank=True,
        verbose_name="Counted Quantity",
    )
    system_quantity = models.DecimalField(
        max_digits=15, decimal_places=3, default=Decimal("0"),
        verbose_name="System Quantity",
        help_text="System quantity snapshot at count time.",
    )
    variance_quantity = models.DecimalField(
        max_digits=15, decimal_places=3, default=Decimal("0"),
        verbose_name="Variance Quantity",
    )
    variance_percentage = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        verbose_name="Variance %",
    )

    # ── Cost & Value ────────────────────────────────────────────────
    cost_per_unit = models.DecimalField(
        max_digits=15, decimal_places=3, default=Decimal("0"),
        verbose_name="Cost Per Unit",
    )
    expected_value = models.DecimalField(
        max_digits=15, decimal_places=3, default=Decimal("0"),
        verbose_name="Expected Value",
    )
    counted_value = models.DecimalField(
        max_digits=15, decimal_places=3, default=Decimal("0"),
        verbose_name="Counted Value",
    )
    variance_value = models.DecimalField(
        max_digits=15, decimal_places=3, default=Decimal("0"),
        verbose_name="Variance Value",
    )

    # ── Status & Tracking ───────────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=STOCK_TAKE_ITEM_STATUS_CHOICES,
        default=STOCK_TAKE_ITEM_PENDING,
        verbose_name="Status",
    )
    count_sequence = models.PositiveIntegerField(
        default=0,
        verbose_name="Count Sequence",
    )
    is_locked = models.BooleanField(default=False, verbose_name="Locked")
    requires_recount = models.BooleanField(default=False, verbose_name="Requires Recount")
    notes = models.TextField(blank=True, default="", verbose_name="Notes")
    discrepancy_reason = models.CharField(
        max_length=200, blank=True, default="",
        verbose_name="Discrepancy Reason",
    )

    # ── Counter Info ────────────────────────────────────────────────
    counted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="counted_stock_items",
        verbose_name="Counted By",
    )
    counted_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Counted At",
    )

    # ── Per-Item Approval (Task 69) ─────────────────────────────────
    item_approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default=APPROVAL_NOT_REQUIRED,
        verbose_name="Item Approval Status",
        help_text="Approval status for this specific item's variance.",
    )
    item_approval_level = models.CharField(
        max_length=20,
        blank=True,
        default="",
        verbose_name="Required Approval Level",
        help_text="Level of approval required (auto/manager/director).",
    )
    item_approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_stock_take_items",
        verbose_name="Approved By",
    )
    item_approved_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Item Approved At",
    )
    item_rejection_reason = models.CharField(
        max_length=255, blank=True, default="",
        verbose_name="Item Rejection Reason",
    )

    objects = StockTakeItemManager()

    class Meta:
        verbose_name = "Stock Take Item"
        verbose_name_plural = "Stock Take Items"
        db_table = "inventory_stock_take_item"
        ordering = ["count_sequence", "product__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["stock_take", "product", "variant", "location"],
                name="uq_stock_take_product_variant_loc",
            ),
        ]
        indexes = [
            models.Index(fields=["stock_take", "status"], name="idx_sti_take_status"),
        ]

    def __str__(self):
        return f"{self.stock_take.reference} — {self.product}"

    # ── Variance Calculation ────────────────────────────────────────

    def calculate_variance(self):
        """Calculate variance fields based on counted vs expected."""
        if self.counted_quantity is None:
            return

        self.variance_quantity = self.counted_quantity - self.expected_quantity

        if self.expected_quantity and self.expected_quantity != 0:
            self.variance_percentage = (
                (self.variance_quantity / self.expected_quantity) * 100
            ).quantize(Decimal("0.01"))
        else:
            self.variance_percentage = None

        self.expected_value = self.expected_quantity * self.cost_per_unit
        self.counted_value = self.counted_quantity * self.cost_per_unit
        self.variance_value = self.variance_quantity * self.cost_per_unit

    def get_variance_classification(self):
        """Return NONE, MINOR, MODERATE, or SIGNIFICANT."""
        if self.variance_percentage is None or self.variance_quantity == 0:
            return "NONE"
        pct = abs(self.variance_percentage)
        if pct <= VARIANCE_MINOR_THRESHOLD:
            return "MINOR"
        if pct <= VARIANCE_MODERATE_THRESHOLD:
            return "MODERATE"
        return "SIGNIFICANT"

    def determine_approval_level(self):
        """Determine the required approval level based on variance percentage."""
        if self.variance_percentage is None or self.variance_quantity == 0:
            return "auto"
        pct = abs(float(self.variance_percentage))
        if pct <= ITEM_APPROVAL_THRESHOLD_MINOR:
            return "auto"
        if pct <= ITEM_APPROVAL_THRESHOLD_MAJOR:
            return "manager"
        return "director"

    def save(self, *args, **kwargs):
        if self.counted_quantity is not None:
            self.calculate_variance()
        super().save(*args, **kwargs)
