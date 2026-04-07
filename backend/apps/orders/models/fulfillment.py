"""
Fulfillment model for tracking order shipment fulfillment (Task 51-53).
"""

from decimal import Decimal

from django.conf import settings
from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin


class FulfillmentStatus(models.TextChoices):
    """Fulfillment lifecycle status."""

    PENDING = "pending", "Pending"
    CONFIRMED = "confirmed", "Confirmed"
    PROCESSING = "processing", "Processing"
    PICKING = "picking", "Picking"
    PICKED = "picked", "Picked"
    PACKING = "packing", "Packing"
    PACKED = "packed", "Packed"
    SHIPPED = "shipped", "Shipped"
    DELIVERED = "delivered", "Delivered"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"


# Carrier tracking URL templates
CARRIER_TRACKING_URLS = {
    "dhl": "https://www.dhl.com/en/express/tracking.html?AWB={tracking}",
    "fedex": "https://www.fedex.com/fedextrack/?trknbr={tracking}",
    "ups": "https://www.ups.com/track?tracknum={tracking}",
    "aramex": "https://www.aramex.com/track/results?ShipmentNumber={tracking}",
    "sri_lanka_post": "https://tracking.slpost.lk/?trackid={tracking}",
}


class Fulfillment(UUIDMixin, TimestampMixin, models.Model):
    """
    Represents a fulfillment/shipment for an order.

    A single order can have multiple fulfillments (partial fulfillment).
    """

    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="fulfillments",
    )
    fulfillment_number = models.CharField(
        max_length=50, unique=True, db_index=True
    )
    status = models.CharField(
        max_length=20,
        choices=FulfillmentStatus.choices,
        default=FulfillmentStatus.PENDING,
        db_index=True,
    )

    # ── Warehouse / Location ────────────────────────────────────────
    warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fulfillments",
    )
    notes = models.TextField(blank=True, default="")

    # ── Tracking (Task 52) ──────────────────────────────────────────
    carrier = models.CharField(max_length=50, blank=True, default="")
    tracking_number = models.CharField(
        max_length=100, blank=True, default="", db_index=True
    )
    tracking_url = models.URLField(max_length=500, blank=True, default="")
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    delivery_attempts = models.IntegerField(default=0)
    delivery_confirmed = models.BooleanField(default=False)
    delivery_recipient = models.CharField(max_length=200, blank=True, default="")
    delivery_signature = models.TextField(blank=True, default="")
    delivery_photo_url = models.URLField(max_length=500, blank=True, default="")
    delivery_status = models.CharField(
        max_length=50, blank=True, default="",
        help_text="Last known delivery status from carrier",
    )
    delivery_failure_reason = models.TextField(blank=True, default="")
    last_tracking_update = models.DateTimeField(null=True, blank=True)

    # ── Package (Task 53) ───────────────────────────────────────────
    weight = models.DecimalField(
        max_digits=8, decimal_places=3, null=True, blank=True,
        help_text="Weight in kg",
    )
    dimensions = models.JSONField(
        default=dict, blank=True,
        help_text='{"length": cm, "width": cm, "height": cm}',
    )
    volumetric_weight = models.DecimalField(
        max_digits=8, decimal_places=3, null=True, blank=True
    )
    shipping_cost = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    insurance_cost = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    requires_special_handling = models.BooleanField(default=False)
    special_handling_notes = models.TextField(blank=True, default="")

    # ── Shipping Options ─────────────────────────────────────────────
    carrier_service = models.CharField(
        max_length=100, blank=True, default="",
        help_text="Specific carrier service level (e.g. Express, Standard)",
    )
    estimated_delivery_date = models.DateTimeField(null=True, blank=True)
    number_of_packages = models.PositiveIntegerField(default=1)
    weight_unit = models.CharField(
        max_length=5, default="kg",
        choices=[("kg", "Kilograms"), ("lb", "Pounds")],
    )
    package_type = models.CharField(
        max_length=50, blank=True, default="",
        help_text="e.g. box, envelope, pallet",
    )
    requires_signature = models.BooleanField(default=False)
    is_fragile = models.BooleanField(default=False)

    # ── International / Customs ─────────────────────────────────────
    is_international = models.BooleanField(default=False)
    customs_value = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
    )
    customs_description = models.TextField(blank=True, default="")

    # ── Processing Timestamps ───────────────────────────────────────
    processing_started_at = models.DateTimeField(null=True, blank=True)
    packed_at = models.DateTimeField(null=True, blank=True)

    # ── Notes ───────────────────────────────────────────────────────
    internal_notes = models.TextField(blank=True, default="")
    customer_notes = models.TextField(blank=True, default="")

    # ── Users ───────────────────────────────────────────────────────
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_fulfillments",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_fulfillments",
    )
    shipped_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="shipped_fulfillments",
    )

    class Meta:
        db_table = "orders_fulfillment"
        verbose_name = "Fulfillment"
        verbose_name_plural = "Fulfillments"
        ordering = ["-created_on"]
        indexes = [
            models.Index(
                fields=["order", "status"], name="idx_fulfillment_order_status"
            ),
        ]

    def __str__(self):
        return f"Fulfillment {self.fulfillment_number}"

    def generate_tracking_url(self):
        """Auto-generate tracking URL from carrier and tracking number."""
        if not self.carrier or not self.tracking_number:
            return ""
        template = CARRIER_TRACKING_URLS.get(self.carrier.lower(), "")
        if template:
            self.tracking_url = template.format(tracking=self.tracking_number)
        return self.tracking_url

    def calculate_volumetric_weight(self, divisor=5000):
        """Calculate volumetric weight from dimensions."""
        dims = self.dimensions or {}
        length = Decimal(str(dims.get("length", 0)))
        width = Decimal(str(dims.get("width", 0)))
        height = Decimal(str(dims.get("height", 0)))
        if length and width and height:
            self.volumetric_weight = (
                length * width * height / Decimal(str(divisor))
            )
        return self.volumetric_weight

    @property
    def chargeable_weight(self):
        """The greater of actual vs volumetric weight."""
        actual = self.weight or Decimal("0")
        volumetric = self.volumetric_weight or Decimal("0")
        return max(actual, volumetric)

    def get_total_quantity(self):
        """Return total quantity across all line items in this fulfillment."""
        from django.db.models import Sum
        return (
            self.line_items.aggregate(total=Sum("quantity"))["total"]
            or Decimal("0")
        )

    def get_fulfillment_percentage(self):
        """Percentage of order fulfilled by this fulfillment."""
        from django.db.models import Sum
        total_ordered = (
            self.order.line_items.aggregate(total=Sum("quantity_ordered"))["total"]
            or Decimal("1")
        )
        return (self.get_total_quantity() / total_ordered * 100).quantize(Decimal("0.01"))

    def can_cancel(self):
        """Whether this fulfillment can still be cancelled."""
        from apps.orders.models.fulfillment import FulfillmentStatus
        return self.status not in (
            FulfillmentStatus.SHIPPED,
            FulfillmentStatus.DELIVERED,
            FulfillmentStatus.CANCELLED,
        )

    def get_transit_time(self):
        """Return transit time in days between shipped and delivered, or None."""
        if self.shipped_at and self.delivered_at:
            delta = self.delivered_at - self.shipped_at
            return delta.days
        return None

    def update_tracking_status(self, status, details=""):
        """Update delivery tracking status with timestamp."""
        from django.utils import timezone
        self.last_tracking_update = timezone.now()
        if details:
            self.notes = f"{self.notes}\n[{self.last_tracking_update:%Y-%m-%d %H:%M}] {details}".strip()
        self.save(update_fields=["last_tracking_update", "notes", "updated_on"])
