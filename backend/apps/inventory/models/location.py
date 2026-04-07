"""
StockLocation model for the inventory application.

Defines the StockLocation model which represents physical and
virtual storage locations — warehouses, retail stores, in-transit
points, and virtual/dropship locations. Each tenant has its own
independent set of stock locations within its schema.
"""

from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin
from apps.inventory.constants import (
    DEFAULT_LOCATION_TYPE,
    LOCATION_TYPE_CHOICES,
)


class StockLocation(UUIDMixin, TimestampMixin, models.Model):
    """
    Stock location for inventory tracking.

    Represents a physical or virtual location where stock can be
    stored or tracked. Supports multi-location inventory management
    with different location types for warehouses, stores, transit
    points, and virtual/dropship locations.

    Fields:
        name: Human-friendly name for the location (max 255 chars).
            Must be unique per tenant schema.
        location_type: Type of location controlling business logic
            behaviour. One of: warehouse, store, transit, virtual.
        address_line_1: Primary address line for the physical location.
        address_line_2: Secondary address line (optional).
        city: City where the location is situated.
        state_province: State or province of the location.
        postal_code: Postal / ZIP code.
        country: Country code or name (defaults to Sri Lanka).
        phone: Contact phone number for the location (optional).
        email: Contact email for the location (optional).
        is_active: Controls whether this location is available for
            stock operations. Inactive locations cannot receive new
            stock or be used as source/destination for transfers
            but retain their existing stock records for audit.
        notes: Optional internal notes about the location.
    """

    # ── Identity Fields ─────────────────────────────────────────────
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Location Name",
        help_text="Human-friendly name for the location (e.g. 'Main Warehouse').",
    )
    location_type = models.CharField(
        max_length=20,
        choices=LOCATION_TYPE_CHOICES,
        default=DEFAULT_LOCATION_TYPE,
        db_index=True,
        verbose_name="Location Type",
        help_text="Type of location: warehouse, store, transit, or virtual.",
    )

    # ── Address Fields ──────────────────────────────────────────────
    address_line_1 = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Address Line 1",
        help_text="Primary address line for physical locations.",
    )
    address_line_2 = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Address Line 2",
        help_text="Secondary address line (optional).",
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="City",
        help_text="City where the location is situated.",
    )
    state_province = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="State / Province",
        help_text="State or province of the location.",
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        default="",
        verbose_name="Postal Code",
        help_text="Postal / ZIP code.",
    )
    country = models.CharField(
        max_length=100,
        default="Sri Lanka",
        verbose_name="Country",
        help_text="Country where the location is situated.",
    )

    # ── Contact Fields ──────────────────────────────────────────────
    phone = models.CharField(
        max_length=30,
        blank=True,
        default="",
        verbose_name="Phone",
        help_text="Contact phone number for the location.",
    )
    email = models.EmailField(
        blank=True,
        default="",
        verbose_name="Email",
        help_text="Contact email for the location.",
    )

    # ── Status Fields ───────────────────────────────────────────────
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Active",
        help_text=(
            "Controls whether this location is available for stock "
            "operations. Inactive locations retain their existing stock "
            "records but cannot be used for new transactions."
        ),
    )

    # ── Notes ───────────────────────────────────────────────────────
    notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Notes",
        help_text="Optional internal notes about this location.",
    )

    class Meta:
        db_table = "inventory_stock_location"
        verbose_name = "Stock Location"
        verbose_name_plural = "Stock Locations"
        ordering = ["name"]
        indexes = [
            models.Index(
                fields=["location_type", "is_active"],
                name="idx_location_type_active",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_location_type_display()})"

    @property
    def is_physical(self):
        """Return True if this is a physical location (warehouse or store)."""
        return self.location_type in ("warehouse", "store")

    @property
    def full_address(self):
        """Return formatted multi-line address string."""
        parts = [
            self.address_line_1,
            self.address_line_2,
            self.city,
            self.state_province,
            self.postal_code,
            self.country,
        ]
        return ", ".join(part for part in parts if part)
