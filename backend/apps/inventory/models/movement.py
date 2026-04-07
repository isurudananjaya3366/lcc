"""
StockMovement model for the inventory application.

Defines the StockMovement model which records every stock change
for a complete audit trail. Each movement captures what happened
(type), how much (quantity), where (product/location), and why
(reference). Stock quantities should only be modified through
movement records to maintain full traceability.
"""

from django.conf import settings
from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin
from apps.inventory.constants import MOVEMENT_TYPE_CHOICES, MOVEMENT_TYPE_IN


class StockMovement(UUIDMixin, TimestampMixin, models.Model):
    """
    Stock movement audit record.

    Every change to stock quantity is recorded as a movement for
    complete traceability. Movements are immutable once created —
    corrections should be made via new adjustment or return movements,
    never by editing existing records.

    Fields:
        product: FK to Product — which product is being moved.
        location: FK to StockLocation — where the movement occurs.
            For transfers, this is the source location; the
            destination is captured in destination_location.
        destination_location: FK to StockLocation (optional) —
            only used for transfer movements to record where stock
            is being transferred to.
        movement_type: Type of movement controlling business logic.
            One of: in, out, transfer, adjustment, return.
        quantity: Amount moved (always positive — direction is
            inferred from the movement_type).
        reference: Free-text reference linking to the source document
            (e.g. order number, invoice ID, adjustment reason).
        notes: Optional additional notes about the movement.
        performed_by: FK to user who performed this movement.
    """

    # ── Foreign Keys ────────────────────────────────────────────────
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="stock_movements",
        verbose_name="Product",
        help_text="The product being moved.",
    )
    location = models.ForeignKey(
        "inventory.StockLocation",
        on_delete=models.CASCADE,
        related_name="movements_from",
        verbose_name="Location",
        help_text=(
            "The location where the movement occurs. For transfers, "
            "this is the source location."
        ),
    )
    destination_location = models.ForeignKey(
        "inventory.StockLocation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movements_to",
        verbose_name="Destination Location",
        help_text=(
            "Destination location for transfer movements. "
            "Null for non-transfer movements."
        ),
    )

    # ── Movement Type ───────────────────────────────────────────────
    movement_type = models.CharField(
        max_length=20,
        choices=MOVEMENT_TYPE_CHOICES,
        default=MOVEMENT_TYPE_IN,
        db_index=True,
        verbose_name="Movement Type",
        help_text="Type of stock movement: in, out, transfer, adjustment, or return.",
    )

    # ── Quantity ────────────────────────────────────────────────────
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        verbose_name="Quantity",
        help_text=(
            "Amount moved (always positive). Direction is inferred "
            "from the movement_type."
        ),
    )

    # ── Reference & Notes ───────────────────────────────────────────
    reference = models.CharField(
        max_length=255,
        blank=True,
        default="",
        db_index=True,
        verbose_name="Reference",
        help_text=(
            "Reference linking to the source document — order number, "
            "invoice ID, purchase order, or adjustment reason."
        ),
    )
    notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Notes",
        help_text="Optional additional notes about this movement.",
    )

    # ── Audit ───────────────────────────────────────────────────────
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movements",
        verbose_name="Performed By",
        help_text="The user who performed this stock movement.",
    )

    class Meta:
        db_table = "inventory_stock_movement"
        verbose_name = "Stock Movement"
        verbose_name_plural = "Stock Movements"
        ordering = ["-created_on"]
        indexes = [
            models.Index(
                fields=["product", "movement_type"],
                name="idx_movement_product_type",
            ),
            models.Index(
                fields=["location", "movement_type"],
                name="idx_movement_location_type",
            ),
            models.Index(
                fields=["-created_on"],
                name="idx_movement_created",
            ),
        ]

    def __str__(self):
        return (
            f"{self.get_movement_type_display()} — "
            f"{self.product} × {self.quantity} @ {self.location}"
        )

    @property
    def is_inbound(self):
        """Return True if this movement increases stock (in, return)."""
        return self.movement_type in ("in", "return")

    @property
    def is_outbound(self):
        """Return True if this movement decreases stock (out)."""
        return self.movement_type == "out"

    @property
    def is_transfer(self):
        """Return True if this is a transfer between locations."""
        return self.movement_type == "transfer"
