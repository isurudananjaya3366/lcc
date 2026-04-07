"""
StockMovement model for tracking all stock changes with full audit trail.

Every stock change is recorded as a movement for complete traceability.
Movements are immutable once created — corrections are made via reversal
movements, not by editing existing records.
"""

import logging
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import Count, DecimalField, F, Q, Sum, Value
from django.db.models.functions import Coalesce, TruncDate
from django.utils import timezone

from apps.core.mixins import UUIDMixin, TimestampMixin

from apps.inventory.stock.constants import (
    MOVEMENT_REASON_CHOICES,
    MOVEMENT_TYPE_CHOICES,
    MOVEMENT_TYPE_ADJUSTMENT,
    MOVEMENT_TYPE_RELEASED,
    MOVEMENT_TYPE_RESERVED,
    MOVEMENT_TYPE_STOCK_IN,
    MOVEMENT_TYPE_STOCK_OUT,
    MOVEMENT_TYPE_TRANSFER,
    REASON_CORRECTION,
    REFERENCE_TYPE_CHOICES,
    TRANSIT_PENDING,
    TRANSIT_STATUS_CHOICES,
    VALID_REASON_COMBINATIONS,
)

logger = logging.getLogger(__name__)


class StockMovementManager(models.Manager):
    """Custom manager for StockMovement queries."""

    def by_type(self, movement_type):
        """Filter movements by type."""
        return self.get_queryset().filter(movement_type=movement_type)

    def by_date_range(self, start_date, end_date=None):
        """Filter movements within a date range."""
        qs = self.get_queryset().filter(movement_date__gte=start_date)
        if end_date is not None:
            qs = qs.filter(movement_date__lte=end_date)
        return qs

    def for_product(self, product, variant=None):
        """Filter movements for a specific product and optional variant."""
        qs = self.get_queryset().filter(product=product)
        if variant is not None:
            qs = qs.filter(variant=variant)
        return qs

    def for_warehouse(self, warehouse, direction="both"):
        """Filter movements involving a warehouse (source, destination, or both)."""
        if direction == "incoming":
            return self.get_queryset().filter(to_warehouse=warehouse)
        elif direction == "outgoing":
            return self.get_queryset().filter(from_warehouse=warehouse)
        return self.get_queryset().filter(
            Q(from_warehouse=warehouse) | Q(to_warehouse=warehouse)
        )

    def by_reference(self, reference_type, reference_id):
        """Filter movements by reference type and ID."""
        return self.get_queryset().filter(
            reference_type=reference_type,
            reference_id=reference_id,
        )

    def recent(self, days=7):
        """Return movements from the last N days."""
        cutoff = timezone.now() - timedelta(days=days)
        return self.get_queryset().filter(movement_date__gte=cutoff).order_by("-movement_date")

    def with_relations(self):
        """Return queryset with all related objects prefetched."""
        return self.get_queryset().select_related(
            "product",
            "variant",
            "from_warehouse",
            "to_warehouse",
            "from_location",
            "to_location",
            "created_by",
        )

    # ── Summary Methods (Task 35) ───────────────────────────────────

    def summary_by_product(self, start_date=None, end_date=None):
        """Aggregate movement quantities by product."""
        qs = self.get_queryset()
        if start_date:
            qs = qs.filter(movement_date__gte=start_date)
        if end_date:
            qs = qs.filter(movement_date__lte=end_date)
        return (
            qs.values("product__id", "product__name", "movement_type")
            .annotate(
                total_quantity=Coalesce(Sum("quantity"), Value(Decimal("0")), output_field=DecimalField()),
                movement_count=Count("id"),
            )
            .order_by("product__name", "movement_type")
        )

    def summary_by_warehouse(self, start_date=None, end_date=None):
        """Aggregate movement quantities by warehouse."""
        qs = self.get_queryset()
        if start_date:
            qs = qs.filter(movement_date__gte=start_date)
        if end_date:
            qs = qs.filter(movement_date__lte=end_date)
        return (
            qs.values("from_warehouse__id", "from_warehouse__name", "movement_type")
            .annotate(
                total_quantity=Coalesce(Sum("quantity"), Value(Decimal("0")), output_field=DecimalField()),
                movement_count=Count("id"),
            )
            .order_by("from_warehouse__name", "movement_type")
        )

    def cost_summary(self, start_date=None, end_date=None):
        """Calculate total cost of movements by type."""
        qs = self.get_queryset()
        if start_date:
            qs = qs.filter(movement_date__gte=start_date)
        if end_date:
            qs = qs.filter(movement_date__lte=end_date)
        return (
            qs.values("movement_type")
            .annotate(
                total_cost=Coalesce(
                    Sum(F("quantity") * F("cost_per_unit")),
                    Value(Decimal("0")),
                    output_field=DecimalField(),
                ),
                total_quantity=Coalesce(Sum("quantity"), Value(Decimal("0")), output_field=DecimalField()),
                movement_count=Count("id"),
            )
            .order_by("movement_type")
        )

    def daily_summary(self, start_date=None, end_date=None):
        """Aggregate movements by date."""
        qs = self.get_queryset()
        if start_date:
            qs = qs.filter(movement_date__gte=start_date)
        if end_date:
            qs = qs.filter(movement_date__lte=end_date)
        return (
            qs.annotate(date=TruncDate("movement_date"))
            .values("date")
            .annotate(
                total_quantity=Coalesce(Sum("quantity"), Value(Decimal("0")), output_field=DecimalField()),
                movement_count=Count("id"),
            )
            .order_by("date")
        )

    def user_activity(self, user, start_date=None, end_date=None):
        """Get movement activity for a specific user."""
        qs = self.get_queryset().filter(created_by=user)
        if start_date:
            qs = qs.filter(movement_date__gte=start_date)
        if end_date:
            qs = qs.filter(movement_date__lte=end_date)
        return (
            qs.values("movement_type")
            .annotate(
                total_quantity=Coalesce(Sum("quantity"), Value(Decimal("0")), output_field=DecimalField()),
                movement_count=Count("id"),
            )
            .order_by("movement_type")
        )

    def summary_by_reference(self, start_date=None, end_date=None):
        """Aggregate movement quantities by reference type."""
        qs = self.get_queryset()
        if start_date:
            qs = qs.filter(movement_date__gte=start_date)
        if end_date:
            qs = qs.filter(movement_date__lte=end_date)
        return (
            qs.values("reference_type")
            .annotate(
                total_quantity=Coalesce(Sum("quantity"), Value(Decimal("0")), output_field=DecimalField()),
                movement_count=Count("id"),
            )
            .order_by("reference_type")
        )


class StockMovement(UUIDMixin, TimestampMixin, models.Model):
    """
    Stock movement audit record.

    Every change to stock quantity is recorded as a movement for
    complete traceability. Movements are immutable once created —
    corrections are made via reversal movements.

    Managers:
        objects (StockMovementManager): Custom manager with filter,
            summary, and aggregation methods.
    """

    # ── Foreign Keys ────────────────────────────────────────────────
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="inventory_movements",
        db_index=True,
        verbose_name="Product",
        help_text="Product being moved.",
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="inventory_movements",
        db_index=True,
        verbose_name="Variant",
        help_text="Optional variant for variant-level movement tracking.",
    )
    from_warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="movements_out",
        db_index=True,
        verbose_name="Source Warehouse",
        help_text="Source warehouse. Required for STOCK_OUT, TRANSFER, RESERVED.",
    )
    to_warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="movements_in",
        db_index=True,
        verbose_name="Destination Warehouse",
        help_text="Destination warehouse. Required for STOCK_IN, TRANSFER, RELEASED.",
    )
    from_location = models.ForeignKey(
        "inventory.StorageLocation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movements_out",
        verbose_name="Source Location",
        help_text="Source storage location within the warehouse.",
    )
    to_location = models.ForeignKey(
        "inventory.StorageLocation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movements_in",
        verbose_name="Destination Location",
        help_text="Destination storage location within the warehouse.",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movements",
        verbose_name="Created By",
        help_text="User who performed this movement.",
    )

    # ── Movement Details ────────────────────────────────────────────
    movement_type = models.CharField(
        max_length=20,
        choices=MOVEMENT_TYPE_CHOICES,
        db_index=True,
        verbose_name="Movement Type",
        help_text="Type of stock movement.",
    )
    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        validators=[MinValueValidator(Decimal("0.001"))],
        verbose_name="Quantity",
        help_text="Amount moved (always positive — direction from movement_type).",
    )
    reason = models.CharField(
        max_length=30,
        choices=MOVEMENT_REASON_CHOICES,
        blank=True,
        default="",
        verbose_name="Reason",
        help_text="Reason for this movement.",
    )
    movement_date = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Movement Date",
        help_text="When the movement occurred.",
    )

    # ── Reference Fields ────────────────────────────────────────────
    reference_type = models.CharField(
        max_length=30,
        choices=REFERENCE_TYPE_CHOICES,
        blank=True,
        default="",
        verbose_name="Reference Type",
        help_text="Type of the source document (order, PO, adjustment, etc.).",
    )
    reference_id = models.CharField(
        max_length=100,
        blank=True,
        default="",
        db_index=True,
        verbose_name="Reference ID",
        help_text="ID of the source document.",
    )
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Reference Number",
        help_text="Human-readable reference number for display.",
    )
    notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Notes",
        help_text="Additional context or notes about this movement.",
    )

    # ── Cost Tracking ───────────────────────────────────────────────
    cost_per_unit = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        default=0,
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name="Cost Per Unit",
        help_text="Cost per unit at the time of movement (for COGS).",
    )

    # ── Reversal Support (Task 34) ──────────────────────────────────
    is_reversed = models.BooleanField(
        default=False,
        verbose_name="Is Reversed",
        help_text="Whether this movement has been reversed.",
    )
    reversed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movements_reversed",
        verbose_name="Reversed By",
        help_text="User who reversed this movement.",
    )
    reversed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Reversed At",
        help_text="When this movement was reversed.",
    )
    reversal_reason = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Reversal Reason",
        help_text="Reason for reversing this movement.",
    )
    original_movement = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reversals",
        verbose_name="Original Movement",
        help_text="If this is a reversal, points to the original movement.",
    )

    # ── Transit Tracking (Task 43) ──────────────────────────────────
    transit_status = models.CharField(
        max_length=20,
        choices=TRANSIT_STATUS_CHOICES,
        blank=True,
        default="",
        db_index=True,
        verbose_name="Transit Status",
        help_text="Tracking status for transfer movements in transit.",
    )
    dispatched_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Dispatched At",
        help_text="When the transfer was physically dispatched.",
    )
    received_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Received At",
        help_text="When the transfer was physically received.",
    )
    dispatched_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movements_dispatched",
        verbose_name="Dispatched By",
        help_text="User who dispatched this transfer.",
    )
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movements_received",
        verbose_name="Received By",
        help_text="User who confirmed receipt of this transfer.",
    )

    # ── Reservation Expiry (Task 44) ────────────────────────────────
    reserved_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Reserved Until",
        help_text="Expiry time for reservation movements. After this time, "
                  "reservation can be automatically released.",
    )

    # ── Manager ─────────────────────────────────────────────────────
    objects = StockMovementManager()

    class Meta:
        verbose_name = "Stock Movement"
        verbose_name_plural = "Stock Movements"
        db_table = "inventory_stock_movement"
        ordering = ["-movement_date", "-created_on"]
        get_latest_by = "movement_date"
        indexes = [
            models.Index(
                fields=["product", "movement_date"],
                name="idx_movement_product_date",
            ),
            models.Index(
                fields=["from_warehouse", "movement_date"],
                name="idx_movement_from_wh_date",
            ),
            models.Index(
                fields=["to_warehouse", "movement_date"],
                name="idx_movement_to_wh_date",
            ),
            models.Index(
                fields=["movement_type", "movement_date"],
                name="idx_movement_type_date",
            ),
            models.Index(
                fields=["reference_type", "reference_id"],
                name="idx_movement_reference",
            ),
        ]
        permissions = [
            ("can_create_movement", "Can create stock movements"),
            ("can_reverse_movement", "Can reverse stock movements"),
            ("can_approve_adjustment", "Can approve stock adjustments"),
            ("can_view_movement_history", "Can view movement history"),
        ]

    def __str__(self):
        return (
            f"{self.get_movement_type_display()} - "
            f"{self.product}: {self.quantity}"
        )

    @property
    def total_cost(self):
        """Calculate total cost for this movement."""
        return self.quantity * self.cost_per_unit

    # ── Validation ──────────────────────────────────────────────────

    def clean(self):
        """Validate movement data integrity."""
        super().clean()
        errors = {}

        # Quantity must be positive
        if self.quantity is not None and self.quantity <= 0:
            errors["quantity"] = "Quantity must be greater than zero."

        # Cost non-negative
        if self.cost_per_unit is not None and self.cost_per_unit < 0:
            errors["cost_per_unit"] = "Cost cannot be negative."

        # Warehouse validation based on movement type
        self._validate_warehouses(errors)

        # Location must belong to its warehouse
        self._validate_locations(errors)

        # Reason must match movement type
        self._validate_reason(errors)

        # Reference consistency: both or neither
        if self.reference_type and not self.reference_id:
            errors["reference_id"] = "Reference ID required when reference type is set."
        if self.reference_id and not self.reference_type:
            errors["reference_type"] = "Reference type required when reference ID is set."

        # Can't reverse an already reversed movement
        if self.is_reversed and self.original_movement:
            errors["is_reversed"] = (
                "A reversal movement cannot itself be marked as reversed."
            )

        if errors:
            raise ValidationError(errors)

    def _validate_warehouses(self, errors):
        """Validate warehouse requirements by movement type."""
        if self.movement_type == MOVEMENT_TYPE_STOCK_IN:
            if not self.to_warehouse_id:
                errors["to_warehouse"] = "Destination warehouse required for stock-in."
            if self.from_warehouse_id:
                errors["from_warehouse"] = "Source warehouse should be empty for stock-in."
        elif self.movement_type == MOVEMENT_TYPE_STOCK_OUT:
            if not self.from_warehouse_id:
                errors["from_warehouse"] = "Source warehouse required for stock-out."
            if self.to_warehouse_id:
                errors["to_warehouse"] = "Destination warehouse should be empty for stock-out."
        elif self.movement_type == MOVEMENT_TYPE_TRANSFER:
            if not self.from_warehouse_id:
                errors["from_warehouse"] = "Source warehouse required for transfer."
            if not self.to_warehouse_id:
                errors["to_warehouse"] = "Destination warehouse required for transfer."
            if (
                self.from_warehouse_id
                and self.to_warehouse_id
                and self.from_warehouse_id == self.to_warehouse_id
            ):
                errors["to_warehouse"] = "Cannot transfer to the same warehouse."
        elif self.movement_type == MOVEMENT_TYPE_ADJUSTMENT:
            if not self.from_warehouse_id and not self.to_warehouse_id:
                errors["from_warehouse"] = "At least one warehouse required for adjustment."
        elif self.movement_type == MOVEMENT_TYPE_RESERVED:
            if not self.from_warehouse_id:
                errors["from_warehouse"] = "Source warehouse required for reservation."
        elif self.movement_type == MOVEMENT_TYPE_RELEASED:
            if not self.to_warehouse_id:
                errors["to_warehouse"] = "Destination warehouse required for release."

    def _validate_locations(self, errors):
        """Validate that locations belong to their respective warehouses."""
        if self.from_location_id and self.from_warehouse_id:
            try:
                if self.from_location.warehouse_id != self.from_warehouse_id:
                    errors["from_location"] = (
                        "Source location must belong to the source warehouse."
                    )
            except Exception:
                pass
        if self.to_location_id and self.to_warehouse_id:
            try:
                if self.to_location.warehouse_id != self.to_warehouse_id:
                    errors["to_location"] = (
                        "Destination location must belong to the destination warehouse."
                    )
            except Exception:
                pass

    def _validate_reason(self, errors):
        """Validate that reason matches the movement type."""
        if self.reason and self.movement_type and self.movement_type in VALID_REASON_COMBINATIONS:
            valid_reasons = VALID_REASON_COMBINATIONS[self.movement_type]
            if self.reason not in valid_reasons:
                errors["reason"] = (
                    f"Reason '{self.reason}' is not valid for movement type "
                    f"'{self.movement_type}'."
                )

    # ── Reversal ────────────────────────────────────────────────────

    @transaction.atomic
    def reverse(self, reason="", user=None):
        """
        Create a reversal movement that undoes this movement.

        Returns the new reversal StockMovement instance.
        Raises ValidationError if already reversed.
        """
        if self.is_reversed:
            raise ValidationError("This movement has already been reversed.")

        # Determine the reversed movement type and swap warehouses
        reversal_type = self.movement_type
        from_wh = self.to_warehouse
        to_wh = self.from_warehouse
        from_loc = self.to_location
        to_loc = self.from_location

        # For stock in, the reversal is stock out (and vice versa)
        if self.movement_type == MOVEMENT_TYPE_STOCK_IN:
            reversal_type = MOVEMENT_TYPE_STOCK_OUT
            from_wh = self.to_warehouse
            to_wh = None
        elif self.movement_type == MOVEMENT_TYPE_STOCK_OUT:
            reversal_type = MOVEMENT_TYPE_STOCK_IN
            from_wh = None
            to_wh = self.from_warehouse

        reversal = StockMovement.objects.create(
            product=self.product,
            variant=self.variant,
            from_warehouse=from_wh,
            to_warehouse=to_wh,
            from_location=from_loc,
            to_location=to_loc,
            movement_type=reversal_type,
            quantity=self.quantity,
            reason=REASON_CORRECTION,
            cost_per_unit=self.cost_per_unit,
            reference_type=self.reference_type,
            reference_id=self.reference_id,
            reference_number=self.reference_number,
            notes=f"Reversal of movement {self.pk}: {reason}",
            created_by=user,
            original_movement=self,
        )

        self.is_reversed = True
        self.reversed_by = user
        self.reversed_at = timezone.now()
        self.reversal_reason = reason
        self.save(update_fields=["is_reversed", "reversed_by", "reversed_at", "reversal_reason"])

        return reversal
