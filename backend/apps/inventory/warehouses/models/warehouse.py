"""
Warehouse model for the inventory application.

Defines the Warehouse model representing physical warehouse locations
within the multi-tenant system. Each tenant has its own independent
set of warehouses. Tenant scoping is enforced at the database level
via django-tenants schema isolation.
"""

import re

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.utils.text import slugify

from apps.core.mixins import AuditMixin, SoftDeleteMixin, StatusMixin, UUIDMixin
from apps.core.managers import AliveManager
from apps.inventory.warehouses.constants import (
    SRI_LANKA_DISTRICTS,
    WAREHOUSE_STATUS_ACTIVE,
    WAREHOUSE_STATUS_CHOICES,
    WAREHOUSE_TYPE_CHOICES,
    WAREHOUSE_TYPE_MAIN,
)
from apps.inventory.warehouses.managers import WarehouseManager


class Warehouse(UUIDMixin, AuditMixin, StatusMixin, SoftDeleteMixin, models.Model):
    """
    Physical warehouse location within a tenant.

    Represents a warehouse that stores inventory. Each tenant uses
    its own PostgreSQL schema so no explicit tenant FK is needed.
    Only one warehouse per tenant can be marked ``is_default=True``
    (enforced by a partial unique index).

    Managers:
        objects (WarehouseManager): Custom manager with convenience
            query methods (active, by_type, get_default, etc.).
        all_with_deleted (Manager): Unfiltered access including
            soft-deleted records.
    """

    # ── Identity ────────────────────────────────────────────────────
    name = models.CharField(
        max_length=200,
        verbose_name="Warehouse Name",
        help_text='e.g., "Colombo Main Warehouse"',
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Warehouse Code",
        help_text='Unique code like "WH-CMB-01". Stored uppercase.',
    )
    warehouse_type = models.CharField(
        max_length=20,
        choices=WAREHOUSE_TYPE_CHOICES,
        default=WAREHOUSE_TYPE_MAIN,
        db_index=True,
        verbose_name="Warehouse Type",
    )

    # ── Address ─────────────────────────────────────────────────────
    address_line_1 = models.CharField(
        max_length=255,
        verbose_name="Address Line 1",
        help_text="Street address or P.O. Box",
    )
    address_line_2 = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Address Line 2",
        help_text="Apartment, suite, building, floor, etc.",
    )
    city = models.CharField(
        max_length=100,
        verbose_name="City",
        help_text="e.g., Colombo, Kandy, Galle",
    )
    district = models.CharField(
        max_length=50,
        choices=SRI_LANKA_DISTRICTS,
        db_index=True,
        verbose_name="District",
    )
    postal_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Postal Code",
        help_text="Sri Lankan postal code (5 digits)",
    )

    # ── Contact ─────────────────────────────────────────────────────
    phone = models.CharField(
        max_length=20,
        verbose_name="Phone Number",
        help_text="Format: +94 XX XXX XXXX",
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Email Address",
        help_text="Warehouse contact email",
    )
    manager_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Manager Name",
        help_text="Warehouse manager or supervisor",
    )

    # ── Status ──────────────────────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=WAREHOUSE_STATUS_CHOICES,
        default=WAREHOUSE_STATUS_ACTIVE,
        db_index=True,
        verbose_name="Status",
    )
    is_default = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Default Warehouse",
        help_text="Default warehouse for POS and automatic operations",
    )

    # ── Operating Hours ─────────────────────────────────────────────
    is_24_hours = models.BooleanField(
        default=False,
        verbose_name="24-Hour Operation",
    )
    opens_at = models.TimeField(
        blank=True,
        null=True,
        verbose_name="Opens At",
        help_text="Warehouse opening time (Asia/Colombo)",
    )
    closes_at = models.TimeField(
        blank=True,
        null=True,
        verbose_name="Closes At",
        help_text="Warehouse closing time (Asia/Colombo)",
    )
    breaks_start = models.TimeField(
        blank=True,
        null=True,
        verbose_name="Break Start",
    )
    breaks_end = models.TimeField(
        blank=True,
        null=True,
        verbose_name="Break End",
    )

    # ── GPS Coordinates ─────────────────────────────────────────────
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        blank=True,
        null=True,
        verbose_name="Latitude",
        help_text="GPS latitude coordinate",
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        blank=True,
        null=True,
        verbose_name="Longitude",
        help_text="GPS longitude coordinate",
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )

    # ── Managers ────────────────────────────────────────────────────
    objects = WarehouseManager()
    all_with_deleted = models.Manager()

    class Meta:
        verbose_name = "Warehouse"
        verbose_name_plural = "Warehouses"
        db_table = "inventory_warehouses"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["status"], name="idx_wh_status"),
            models.Index(fields=["warehouse_type"], name="idx_wh_type"),
            models.Index(fields=["district"], name="idx_wh_district"),
            models.Index(fields=["is_default"], name="idx_wh_default"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["is_default"],
                condition=models.Q(is_default=True),
                name="unique_default_warehouse_per_tenant",
            ),
        ]
        permissions = [
            ("can_set_default_warehouse", "Can set a warehouse as default"),
            ("can_deactivate_warehouse", "Can deactivate a warehouse"),
        ]

    # ── String Representations ──────────────────────────────────────

    def __str__(self):
        return f"{self.name} ({self.code})"

    def __repr__(self):
        return f"<Warehouse id={self.pk} code={self.code!r}>"

    # ── Helper Methods ──────────────────────────────────────────────

    def is_open_at(self, dt):
        """
        Return True if the warehouse is open at the given datetime.

        Checks ``is_24_hours`` first. Then compares the time component
        of *dt* against ``opens_at`` / ``closes_at``, accounting for
        any configured break period.
        """
        if self.is_24_hours:
            return True
        if not self.opens_at or not self.closes_at:
            return True  # No hours configured → assumed open
        t = dt.time() if hasattr(dt, "time") else dt
        if t < self.opens_at or t > self.closes_at:
            return False
        if self.breaks_start and self.breaks_end:
            if self.breaks_start <= t <= self.breaks_end:
                return False
        return True

    def get_coordinates(self):
        """Return ``(latitude, longitude)`` tuple, or ``None``."""
        if self.latitude is not None and self.longitude is not None:
            return (self.latitude, self.longitude)
        return None

    def get_maps_url(self):
        """Return a Google Maps URL for this warehouse, or ``None``."""
        coords = self.get_coordinates()
        if coords:
            return f"https://maps.google.com/?q={coords[0]},{coords[1]}"
        return None

    def is_status_active(self):
        """Return True if the warehouse status is ACTIVE."""
        return self.status == WAREHOUSE_STATUS_ACTIVE

    @transaction.atomic
    def set_as_default(self):
        """
        Set this warehouse as the default for its tenant.

        Automatically unsets the previous default warehouse within
        an atomic transaction.

        Raises:
            ValidationError: If the warehouse is not active.
        """
        if self.status != WAREHOUSE_STATUS_ACTIVE:
            raise ValidationError(
                "Only active warehouses can be set as default."
            )
        if self.is_default:
            return True  # Already default

        # Unset old default (if any) via queryset update to avoid signals
        Warehouse.objects.filter(is_default=True).exclude(pk=self.pk).update(
            is_default=False
        )
        self.is_default = True
        self.save(update_fields=["is_default"])
        return True

    # ── Validation ──────────────────────────────────────────────────

    def clean(self):
        """
        Cross-field validation for warehouse data.

        Validates operating hours consistency, coordinate pairing,
        phone format, postal code format, break periods, and
        business rules.
        """
        super().clean()
        errors = {}

        # -- Code: uppercase -------------------------------------------------
        if self.code:
            self.code = self.code.upper()

        # -- Operating hours --------------------------------------------------
        if not self.is_24_hours:
            if self.opens_at and not self.closes_at:
                errors["closes_at"] = (
                    "Closing time is required when opening time is set."
                )
            elif self.closes_at and not self.opens_at:
                errors["opens_at"] = (
                    "Opening time is required when closing time is set."
                )
            elif self.opens_at and self.closes_at:
                if self.closes_at <= self.opens_at:
                    errors["closes_at"] = "Must be after opening time."

        # -- Breaks -----------------------------------------------------------
        if self.breaks_start and not self.breaks_end:
            errors["breaks_end"] = (
                "Break end time is required when break start is set."
            )
        elif self.breaks_end and not self.breaks_start:
            errors["breaks_start"] = (
                "Break start time is required when break end is set."
            )
        elif self.breaks_start and self.breaks_end:
            if self.breaks_end <= self.breaks_start:
                errors["breaks_end"] = "Must be after break start time."
            if self.opens_at and self.breaks_start < self.opens_at:
                errors["breaks_start"] = (
                    "Break start must be within operating hours."
                )
            if self.closes_at and self.breaks_end > self.closes_at:
                errors["breaks_end"] = (
                    "Break end must be within operating hours."
                )

        # -- Coordinates ------------------------------------------------------
        if bool(self.latitude) != bool(self.longitude):
            field = "longitude" if self.latitude else "latitude"
            errors[field] = (
                "Both latitude and longitude must be provided together."
            )

        # -- Phone format (+94 XX XXX XXXX) -----------------------------------
        if self.phone:
            cleaned = re.sub(r"[\s\-]", "", self.phone)
            if not re.match(r"^\+94\d{9}$", cleaned):
                errors["phone"] = (
                    "Invalid format. Use: +94 XX XXX XXXX (12 chars total)."
                )

        # -- Postal code (5 digits) -------------------------------------------
        if self.postal_code:
            if not re.match(r"^\d{5}$", self.postal_code):
                errors["postal_code"] = "Must be exactly 5 digits."

        # -- Business rules ---------------------------------------------------
        if self.is_default and self.status != WAREHOUSE_STATUS_ACTIVE:
            errors["is_default"] = (
                "Only active warehouses can be set as default."
            )

        if errors:
            raise ValidationError(errors)
