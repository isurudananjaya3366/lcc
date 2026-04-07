"""
StockLevel model for tracking product inventory quantities.

Tracks stock quantities by product, variant, warehouse, and optionally
storage location. Supports reserved and incoming quantity tracking with
dynamic availability calculations and stock status determination.
"""

import logging
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import DecimalField, F, Q, Sum, Value
from django.db.models.functions import Coalesce
from django.dispatch import Signal
from django.utils import timezone

from apps.core.mixins import UUIDMixin, TimestampMixin

from apps.inventory.stock.constants import (
    DEFAULT_REORDER_POINT,
    IN_STOCK,
    LOW_STOCK,
    OUT_OF_STOCK,
    STOCK_STATUS_CHOICES,
    STOCK_STATUS_COLORS,
    STOCK_STATUS_ICONS,
)

logger = logging.getLogger(__name__)

# Custom signal emitted when stock level quantity changes
stock_level_changed = Signal()


class StockLevelManager(models.Manager):
    """Custom manager for StockLevel queries."""

    def get_for_product(self, product, variant=None):
        """Return stock levels for a product, optionally filtered by variant."""
        qs = self.get_queryset().filter(product=product)
        if variant is not None:
            qs = qs.filter(variant=variant)
        else:
            qs = qs.filter(variant__isnull=True)
        return qs

    def get_total_stock(self, product, variant=None):
        """Return total quantity across all warehouses for a product."""
        qs = self.get_queryset().filter(product=product)
        if variant is not None:
            qs = qs.filter(variant=variant)
        result = qs.aggregate(
            total=Coalesce(Sum("quantity"), Value(Decimal("0")), output_field=DecimalField())
        )
        return result["total"]

    def get_by_warehouse(self, warehouse):
        """Return all stock levels for a given warehouse."""
        return self.get_queryset().filter(warehouse=warehouse)

    def low_stock_items(self):
        """Return items where available quantity is at or below reorder point."""
        return (
            self.get_queryset()
            .filter(quantity__gt=0)
            .annotate(
                _available=F("quantity") - F("reserved_quantity"),
            )
            .filter(_available__lte=F("reorder_point"))
        )

    def out_of_stock_items(self):
        """Return items with zero or negative quantity."""
        return self.get_queryset().filter(quantity__lte=0)

    def annotate_available_quantity(self):
        """Return queryset annotated with calculated available_quantity."""
        return self.get_queryset().annotate(
            calculated_available=F("quantity") - F("reserved_quantity"),
        )

    def get_available_by_warehouse(self, product, variant=None):
        """Return dict mapping warehouse to available quantity for a product."""
        qs = self.get_queryset().filter(product=product).select_related("warehouse")
        if variant is not None:
            qs = qs.filter(variant=variant)
        qs = qs.annotate(
            _available=F("quantity") - F("reserved_quantity"),
        ).order_by("warehouse__name")
        result = {}
        for sl in qs:
            avail = sl._available if sl._available >= 0 else Decimal("0")
            result[sl.warehouse] = avail
        return result

    def get_available_by_warehouse_id(self, product, variant=None):
        """Return dict mapping warehouse ID to available quantity."""
        by_wh = self.get_available_by_warehouse(product, variant)
        return {wh.id: qty for wh, qty in by_wh.items()}

    # ── Aggregation Methods (Task 15) ───────────────────────────────

    def get_total_available(self, product, variant=None):
        """Return sum of available quantity across all warehouses."""
        qs = self.get_queryset().filter(product=product)
        if variant is not None:
            qs = qs.filter(variant=variant)
        result = qs.aggregate(
            total_qty=Coalesce(Sum("quantity"), Value(Decimal("0")), output_field=DecimalField()),
            total_reserved=Coalesce(Sum("reserved_quantity"), Value(Decimal("0")), output_field=DecimalField()),
        )
        available = result["total_qty"] - result["total_reserved"]
        return max(available, Decimal("0"))

    def get_total_reserved(self, product, variant=None):
        """Return sum of reserved quantity across all warehouses."""
        qs = self.get_queryset().filter(product=product)
        if variant is not None:
            qs = qs.filter(variant=variant)
        result = qs.aggregate(
            total=Coalesce(Sum("reserved_quantity"), Value(Decimal("0")), output_field=DecimalField()),
        )
        return result["total"]

    def get_warehouse_summary(self, warehouse):
        """Return aggregated stock summary for a warehouse."""
        qs = self.get_queryset().filter(warehouse=warehouse)
        agg = qs.aggregate(
            total_items=models.Count("product", distinct=True),
            total_quantity=Coalesce(Sum("quantity"), Value(Decimal("0")), output_field=DecimalField()),
            total_reserved=Coalesce(Sum("reserved_quantity"), Value(Decimal("0")), output_field=DecimalField()),
        )
        total_available = agg["total_quantity"] - agg["total_reserved"]
        low_stock_count = (
            qs.filter(quantity__gt=0)
            .annotate(_avail=F("quantity") - F("reserved_quantity"))
            .filter(_avail__lte=F("reorder_point"))
            .count()
        )
        out_of_stock_count = qs.filter(quantity__lte=0).count()
        return {
            "warehouse": warehouse,
            "total_items": agg["total_items"],
            "total_quantity": agg["total_quantity"],
            "total_reserved": agg["total_reserved"],
            "total_available": max(total_available, Decimal("0")),
            "low_stock_count": low_stock_count,
            "out_of_stock_count": out_of_stock_count,
        }

    def get_product_summary(self, product, variant=None):
        """Return comprehensive stock data for a product."""
        qs = self.get_queryset().filter(product=product)
        if variant is not None:
            qs = qs.filter(variant=variant)
        agg = qs.aggregate(
            total_quantity=Coalesce(Sum("quantity"), Value(Decimal("0")), output_field=DecimalField()),
            total_reserved=Coalesce(Sum("reserved_quantity"), Value(Decimal("0")), output_field=DecimalField()),
            total_incoming=Coalesce(Sum("incoming_quantity"), Value(Decimal("0")), output_field=DecimalField()),
        )
        total_available = agg["total_quantity"] - agg["total_reserved"]
        projected = agg["total_quantity"] + agg["total_incoming"] - agg["total_reserved"]
        warehouses_count = qs.values("warehouse").distinct().count()

        if agg["total_quantity"] <= 0 or total_available <= 0:
            status = OUT_OF_STOCK
        elif total_available <= DEFAULT_REORDER_POINT:
            status = LOW_STOCK
        else:
            status = IN_STOCK

        return {
            "product": product,
            "variant": variant,
            "total_quantity": agg["total_quantity"],
            "total_reserved": agg["total_reserved"],
            "total_available": max(total_available, Decimal("0")),
            "total_incoming": agg["total_incoming"],
            "projected_available": max(projected, Decimal("0")),
            "warehouses_with_stock": warehouses_count,
            "status": status,
        }

    def get_low_stock_report(self):
        """Return low stock items annotated with shortage info, ordered by urgency."""
        return (
            self.get_queryset()
            .filter(quantity__gt=0)
            .annotate(
                _available=F("quantity") - F("reserved_quantity"),
            )
            .filter(_available__lte=F("reorder_point"))
            .annotate(
                shortage=F("reorder_point") - F("_available"),
            )
            .select_related("product", "warehouse", "variant")
            .order_by("-shortage")
        )

    def calculate_stock_value(self, warehouse=None):
        """Calculate total inventory value (quantity * cost_per_unit)."""
        qs = self.get_queryset()
        if warehouse is not None:
            qs = qs.filter(warehouse=warehouse)
        result = qs.aggregate(
            total_value=Coalesce(
                Sum(F("quantity") * F("cost_per_unit")),
                Value(Decimal("0")),
                output_field=DecimalField(),
            ),
        )
        return result["total_value"]


class StockLevel(UUIDMixin, TimestampMixin, models.Model):
    """
    Stock level per product/variant per warehouse/location.

    Tracks on-hand, reserved, and incoming quantities for each
    product (or variant) at each warehouse (and optionally at a
    specific storage location). The combination of product, variant,
    warehouse, and location must be unique.

    Managers:
        objects (StockLevelManager): Custom manager with convenience
            query methods for stock operations and reporting.
    """

    # ── Foreign Keys ────────────────────────────────────────────────
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="inventory_stock_levels",
        db_index=True,
        verbose_name="Product",
        help_text="Product being tracked.",
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="inventory_stock_levels",
        db_index=True,
        verbose_name="Variant",
        help_text=(
            "Optional. If the product has variants, specify which "
            "variant this stock level tracks. NULL means product-level tracking."
        ),
    )
    warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.PROTECT,
        related_name="stock_levels",
        db_index=True,
        verbose_name="Warehouse",
        help_text="Warehouse where the stock is held.",
    )
    location = models.ForeignKey(
        "inventory.StorageLocation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_levels",
        db_index=True,
        verbose_name="Storage Location",
        help_text=(
            "Optional. Specific location within the warehouse. "
            "NULL means stock tracked at warehouse level only."
        ),
    )

    # ── Quantity Fields ─────────────────────────────────────────────
    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        default=0,
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name="Quantity",
        help_text="Current physical stock on hand.",
    )
    reserved_quantity = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        default=0,
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name="Reserved Quantity",
        help_text="Quantity reserved for pending orders but not yet fulfilled.",
    )
    incoming_quantity = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        default=0,
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name="Incoming Quantity",
        help_text="Expected quantity from pending purchase orders.",
    )
    in_transit_quantity = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        default=0,
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name="In Transit Quantity",
        help_text="Quantity currently in transit from inter-warehouse transfers.",
    )
    last_counted_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Last Counted Date",
        help_text="Last time this stock level was physically counted.",
    )
    abc_classification = models.CharField(
        max_length=1,
        blank=True,
        default="",
        verbose_name="ABC Classification",
        help_text="ABC classification for cycle counting priority (A/B/C).",
    )
    reorder_point = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        default=DEFAULT_REORDER_POINT,
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name="Reorder Point",
        help_text="Low stock threshold. Alerts trigger when available falls below this.",
    )

    # ── Cost Tracking (Task 17) ─────────────────────────────────────
    cost_per_unit = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        default=0,
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name="Cost Per Unit",
        help_text="Weighted average cost per unit at this stock level.",
    )

    # ── Timestamps ──────────────────────────────────────────────────
    last_stock_update = models.DateTimeField(
        auto_now=True,
        verbose_name="Last Stock Update",
        help_text="Last time stock quantity was modified.",
    )

    # ── Manager ─────────────────────────────────────────────────────
    objects = StockLevelManager()

    class Meta:
        verbose_name = "Stock Level"
        verbose_name_plural = "Stock Levels"
        db_table = "inventory_stock_level"
        ordering = ["product__name", "warehouse__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["product", "variant", "warehouse", "location"],
                name="uq_stock_level_product_variant_wh_loc",
            ),
        ]
        indexes = [
            models.Index(
                fields=["product", "warehouse"],
                name="idx_stock_level_product_wh",
            ),
            models.Index(
                fields=["warehouse", "location"],
                name="idx_stock_level_wh_loc",
            ),
            models.Index(
                fields=["last_stock_update"],
                name="idx_stock_level_last_update",
            ),
        ]
        permissions = [
            ("can_adjust_stock", "Can adjust stock levels"),
            ("can_view_stock_levels", "Can view stock levels"),
            ("can_approve_adjustments", "Can approve stock adjustments"),
        ]

    def __str__(self):
        base = f"{self.product} - {self.warehouse}: {self.quantity}"
        if self.location:
            base = f"{self.product} - {self.warehouse} [{self.location}]: {self.quantity}"
        return base

    # ── Calculated Properties ───────────────────────────────────────

    @property
    def available_quantity(self):
        """
        Calculate available quantity for new orders.

        Formula: max(0, quantity - reserved_quantity)
        """
        result = self.quantity - self.reserved_quantity
        if result < 0:
            logger.warning(
                "Negative available_quantity detected for StockLevel pk=%s "
                "(quantity=%s, reserved=%s). Returning 0.",
                self.pk, self.quantity, self.reserved_quantity,
            )
            return Decimal("0")
        return result

    @property
    def projected_quantity(self):
        """
        Calculate projected availability after pending receipts.

        Formula: quantity + incoming_quantity - reserved_quantity
        """
        result = self.quantity + self.incoming_quantity - self.reserved_quantity
        return max(result, Decimal("0"))

    @property
    def stock_status(self):
        """Determine current stock status based on availability."""
        if self.quantity <= 0:
            return OUT_OF_STOCK
        available = self.available_quantity
        if available <= 0:
            return OUT_OF_STOCK
        elif available <= self.reorder_point:
            return LOW_STOCK
        return IN_STOCK

    def get_stock_status_display(self):
        """Get human-readable stock status."""
        status = self.stock_status
        for value, label in STOCK_STATUS_CHOICES:
            if value == status:
                return label
        return status

    def get_stock_status_color(self):
        """Get CSS color for stock status display."""
        return STOCK_STATUS_COLORS.get(self.stock_status, "grey")

    def get_stock_status_icon(self):
        """Get icon for stock status display."""
        return STOCK_STATUS_ICONS.get(self.stock_status, "?")

    @property
    def days_since_last_change(self):
        """Calculate days since last stock update. None if never updated."""
        if self.last_stock_update is None:
            return None
        delta = timezone.now() - self.last_stock_update
        return delta.days

    @property
    def stock_value(self):
        """Calculate total value of stock at this level."""
        return self.quantity * self.cost_per_unit

    def update_average_cost(self, new_quantity, new_cost_per_unit):
        """
        Update cost_per_unit using weighted average cost (WAC) formula.

        WAC = (existing_value + new_value) / total_quantity
        """
        new_quantity = Decimal(str(new_quantity))
        new_cost_per_unit = Decimal(str(new_cost_per_unit))

        existing_value = self.quantity * self.cost_per_unit
        new_value = new_quantity * new_cost_per_unit
        total_quantity = self.quantity + new_quantity

        if total_quantity > 0:
            self.cost_per_unit = (existing_value + new_value) / total_quantity
        else:
            self.cost_per_unit = new_cost_per_unit

    # ── Validation ──────────────────────────────────────────────────

    def clean(self):
        """Validate stock level data integrity."""
        super().clean()
        errors = {}
        if self.quantity < 0:
            errors["quantity"] = "Quantity cannot be negative."
        if self.reserved_quantity < 0:
            errors["reserved_quantity"] = "Reserved quantity cannot be negative."
        if self.incoming_quantity < 0:
            errors["incoming_quantity"] = "Incoming quantity cannot be negative."
        if self.reserved_quantity > self.quantity:
            errors["reserved_quantity"] = (
                "Reserved quantity cannot exceed available quantity."
            )
        if self.location and self.warehouse:
            # Validate location belongs to warehouse (if both set)
            if hasattr(self.location, "warehouse_id") and self.location.warehouse_id != self.warehouse_id:
                errors["location"] = (
                    "Storage location must belong to the specified warehouse."
                )
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Override save to validate and emit stock_level_changed signal."""
        if not kwargs.get("update_fields"):
            self.full_clean()
        old_quantity = None
        if self.pk:
            try:
                old = StockLevel.objects.get(pk=self.pk)
                old_quantity = old.quantity
            except StockLevel.DoesNotExist:
                pass
        super().save(*args, **kwargs)
        if old_quantity is not None and old_quantity != self.quantity:
            stock_level_changed.send(
                sender=self.__class__,
                instance=self,
                old_quantity=old_quantity,
                new_quantity=self.quantity,
            )
