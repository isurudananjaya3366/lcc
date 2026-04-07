"""
Stock model for the inventory application.

Defines the Stock model which tracks per-product, per-location
stock levels. Each record represents the current quantity of a
specific product at a specific stock location. The combination
of product and location is unique — there is exactly one stock
record for each product at each location within a tenant schema.
"""

from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin


class Stock(UUIDMixin, TimestampMixin, models.Model):
    """
    Stock level per product per location.

    Tracks on-hand quantity for each product at each stock location.
    Quantity changes are applied through StockMovement records to
    maintain a full audit trail. The reorder_level field enables
    low-stock alerts when quantity drops below the threshold.

    Fields:
        product: FK to Product — which product this stock is for.
        location: FK to StockLocation — where this stock is held.
        quantity: Current on-hand quantity (can be negative for
            backorder scenarios, but typically ≥ 0).
        reorder_level: Threshold below which a low-stock alert
            should be triggered. Default 0 disables alerts.
        last_counted: Optional datetime of the last physical
            stock count at this location.

    Constraints:
        uq_stock_product_location: Unique on (product, location).
            Ensures only one stock record per product per location.
    """

    # ── Foreign Keys ────────────────────────────────────────────────
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="stock_levels",
        verbose_name="Product",
        help_text="The product this stock record is for.",
    )
    location = models.ForeignKey(
        "inventory.StockLocation",
        on_delete=models.CASCADE,
        related_name="stock_levels",
        verbose_name="Stock Location",
        help_text="The location where this stock is held.",
    )

    # ── Quantity Fields ─────────────────────────────────────────────
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=0,
        verbose_name="Quantity",
        help_text=(
            "Current on-hand quantity. Adjusted via stock movements "
            "for full audit trail. Supports fractional units (e.g. kg)."
        ),
    )
    reorder_level = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=0,
        verbose_name="Reorder Level",
        help_text=(
            "Low-stock threshold. A reorder alert is triggered when "
            "quantity drops below this value. Set to 0 to disable."
        ),
    )

    # ── Audit Fields ────────────────────────────────────────────────
    last_counted = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Last Counted",
        help_text="Date/time of the last physical stock count.",
    )

    class Meta:
        db_table = "inventory_stock"
        verbose_name = "Stock"
        verbose_name_plural = "Stock"
        ordering = ["product", "location"]
        constraints = [
            models.UniqueConstraint(
                fields=["product", "location"],
                name="uq_stock_product_location",
            ),
        ]
        indexes = [
            models.Index(
                fields=["product", "location"],
                name="idx_stock_product_location",
            ),
        ]

    def __str__(self):
        return f"{self.product} @ {self.location} — qty: {self.quantity}"

    @property
    def is_low_stock(self):
        """Return True if current quantity is below the reorder level."""
        if self.reorder_level <= 0:
            return False
        return self.quantity < self.reorder_level

    @property
    def needs_reorder(self):
        """Alias for is_low_stock for semantic clarity in business logic."""
        return self.is_low_stock
