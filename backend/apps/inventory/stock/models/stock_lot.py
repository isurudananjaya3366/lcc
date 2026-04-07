"""
StockLot model for FIFO/LIFO inventory costing (Task 55).

Tracks individual lot batches with their receipt dates, costs, and
remaining quantities. Used by the costing module to allocate stock
using First-In-First-Out or Last-In-First-Out methods.
"""

from decimal import Decimal

from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

from apps.core.mixins import UUIDMixin, TimestampMixin

from apps.inventory.stock.constants import (
    LOT_STATUS_ACTIVE,
    LOT_STATUS_CHOICES,
    LOT_STATUS_DEPLETED,
    LOT_STATUS_EXPIRED,
)


class StockLotManager(models.Manager):
    """Custom manager for StockLot queries."""

    def active(self):
        """Return active (non-depleted, non-expired) lots."""
        return self.get_queryset().filter(status=LOT_STATUS_ACTIVE)

    def for_product(self, product, warehouse, variant=None):
        """Return lots for a product at a warehouse, ordered by received date (FIFO)."""
        qs = self.get_queryset().filter(
            product=product,
            warehouse=warehouse,
            status=LOT_STATUS_ACTIVE,
        )
        if variant is not None:
            qs = qs.filter(variant=variant)
        return qs.order_by("received_date")

    def expiring_soon(self, days=30):
        """Return lots that expire within the given number of days."""
        cutoff = timezone.now().date() + timezone.timedelta(days=days)
        return (
            self.get_queryset()
            .filter(
                status=LOT_STATUS_ACTIVE,
                expiry_date__isnull=False,
                expiry_date__lte=cutoff,
            )
            .order_by("expiry_date")
        )


class StockLot(UUIDMixin, TimestampMixin, models.Model):
    """
    Individual lot/batch of stock for FIFO/LIFO costing.

    Each lot represents a batch of product received at a specific cost.
    When stock is consumed (stock_out), lots are allocated in FIFO or
    LIFO order to determine the cost of goods sold.
    """

    lot_number = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name="Lot Number",
        help_text="Unique identifier for this lot/batch.",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="stock_lots",
        db_index=True,
        verbose_name="Product",
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="stock_lots",
        verbose_name="Variant",
    )
    warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.PROTECT,
        related_name="stock_lots",
        db_index=True,
        verbose_name="Warehouse",
    )

    # ── Quantity Fields ─────────────────────────────────────────────
    original_quantity = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        validators=[MinValueValidator(Decimal("0.001"))],
        verbose_name="Original Quantity",
        help_text="Quantity originally received in this lot.",
    )
    remaining_quantity = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name="Remaining Quantity",
        help_text="Quantity remaining in this lot.",
    )
    cost_per_unit = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        default=0,
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name="Cost Per Unit",
        help_text="Cost per unit for this lot.",
    )

    # ── Dates ───────────────────────────────────────────────────────
    received_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="Received Date",
        help_text="Date this lot was received.",
    )
    expiry_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Expiry Date",
        help_text="Expiry date for this lot (if perishable).",
    )

    # ── Status ──────────────────────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=LOT_STATUS_CHOICES,
        default=LOT_STATUS_ACTIVE,
        db_index=True,
        verbose_name="Status",
    )

    # ── Reference to source movement ────────────────────────────────
    source_movement = models.ForeignKey(
        "inventory.StockMovement",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_lots",
        verbose_name="Source Movement",
        help_text="The stock-in movement that created this lot.",
    )

    objects = StockLotManager()

    class Meta:
        verbose_name = "Stock Lot"
        verbose_name_plural = "Stock Lots"
        db_table = "inventory_stock_lot"
        ordering = ["received_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["lot_number", "product", "warehouse"],
                name="uq_stock_lot_number_product_wh",
            ),
        ]
        indexes = [
            models.Index(
                fields=["product", "warehouse", "status"],
                name="idx_lot_product_wh_status",
            ),
            models.Index(
                fields=["expiry_date"],
                name="idx_lot_expiry_date",
            ),
        ]

    def __str__(self):
        return f"Lot {self.lot_number} - {self.product}: {self.remaining_quantity}"

    @property
    def is_depleted(self):
        return self.remaining_quantity <= 0

    @property
    def is_expired(self):
        if self.expiry_date is None:
            return False
        return self.expiry_date <= timezone.now().date()

    @property
    def lot_value(self):
        return self.remaining_quantity * self.cost_per_unit

    def consume(self, quantity):
        """Consume quantity from this lot. Returns the actual quantity consumed."""
        quantity = Decimal(str(quantity))
        consumed = min(quantity, self.remaining_quantity)
        self.remaining_quantity -= consumed
        if self.remaining_quantity <= 0:
            self.status = LOT_STATUS_DEPLETED
        self.save(update_fields=["remaining_quantity", "status", "updated_on"])
        return consumed

    def mark_expired(self):
        """Mark this lot as expired."""
        self.status = LOT_STATUS_EXPIRED
        self.save(update_fields=["status", "updated_on"])
