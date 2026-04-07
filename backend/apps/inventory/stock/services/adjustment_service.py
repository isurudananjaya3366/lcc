"""
StockAdjustmentService — manual stock corrections with authorization.

Handles positive and negative adjustments with optional approval
workflow based on value thresholds.
"""

import logging
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.inventory.stock.constants import (
    ADJUSTMENT_AUTHORIZATION_THRESHOLD,
    MOVEMENT_TYPE_ADJUSTMENT,
    REFERENCE_TYPE_ADJUSTMENT,
)
from apps.inventory.stock.exceptions import (
    InsufficientStockError,
    StockOperationError,
)
from apps.inventory.stock.results import OperationResult

logger = logging.getLogger("inventory.stock.operations")


class StockAdjustmentService:
    """Service for manual stock adjustments with authorization."""

    def __init__(self, user=None, notes=""):
        self.user = user
        self.notes = notes

    def _get_stock_level(self, product, variant, warehouse, location=None):
        from apps.inventory.stock.models.stock_level import StockLevel

        lookup = {
            "product": product,
            "variant": variant,
            "warehouse": warehouse,
            "location": location,
        }
        qs = StockLevel.objects.select_for_update().filter(**lookup)
        try:
            return qs.get()
        except StockLevel.DoesNotExist:
            return StockLevel.objects.create(
                **lookup,
                quantity=Decimal("0"),
                reserved_quantity=Decimal("0"),
                incoming_quantity=Decimal("0"),
                reorder_point=0,
                cost_per_unit=Decimal("0"),
            )

    def requires_authorization(self, quantity, cost_per_unit=None):
        """Check if an adjustment value exceeds the authorization threshold."""
        value = abs(Decimal(str(quantity))) * (
            Decimal(str(cost_per_unit)) if cost_per_unit else Decimal("1")
        )
        return value > ADJUSTMENT_AUTHORIZATION_THRESHOLD

    # ── Positive Adjustment (Task 48) ───────────────────────────────

    @transaction.atomic
    def adjust_up(
        self,
        product,
        quantity,
        warehouse,
        reason,
        variant=None,
        location=None,
        cost_per_unit=None,
        reference_id=None,
        notes=None,
    ):
        """Increase stock quantity (physical > system)."""
        from apps.inventory.stock.models.stock_movement import StockMovement

        if quantity is None or Decimal(str(quantity)) <= 0:
            raise StockOperationError("Adjustment quantity must be positive.")

        quantity = Decimal(str(quantity))

        sl = self._get_stock_level(product, variant, warehouse, location)

        # Update weighted average cost if cost provided
        if cost_per_unit is not None:
            cost_per_unit = Decimal(str(cost_per_unit))
            old_total = sl.quantity * sl.cost_per_unit
            new_total = quantity * cost_per_unit
            new_qty = sl.quantity + quantity
            sl.cost_per_unit = (
                (old_total + new_total) / new_qty if new_qty > 0 else cost_per_unit
            )

        sl.quantity += quantity
        sl.last_stock_update = timezone.now()
        sl.save()

        movement = StockMovement.objects.create(
            product=product,
            variant=variant,
            to_warehouse=warehouse,
            to_location=location,
            movement_type=MOVEMENT_TYPE_ADJUSTMENT,
            quantity=quantity,
            reason=reason,
            cost_per_unit=cost_per_unit or sl.cost_per_unit,
            reference_type=REFERENCE_TYPE_ADJUSTMENT,
            reference_id=reference_id or "",
            notes=notes or self.notes,
            created_by=self.user,
        )

        logger.info(
            "ADJUST_UP product=%s qty=+%s warehouse=%s movement=%s user=%s reason=%s",
            product.pk, quantity, warehouse.pk, movement.pk,
            getattr(self.user, "pk", None), reason,
        )
        return OperationResult.ok(
            "adjust_up",
            data={
                "movement_id": str(movement.pk),
                "new_quantity": str(sl.quantity),
                "cost_per_unit": str(sl.cost_per_unit),
                "requires_authorization": self.requires_authorization(
                    quantity, cost_per_unit,
                ),
            },
        )

    # ── Negative Adjustment (Task 49) ───────────────────────────────

    @transaction.atomic
    def adjust_down(
        self,
        product,
        quantity,
        warehouse,
        reason,
        variant=None,
        location=None,
        reference_id=None,
        notes=None,
    ):
        """Decrease stock quantity (system > physical)."""
        from apps.inventory.stock.models.stock_movement import StockMovement

        if quantity is None or Decimal(str(quantity)) <= 0:
            raise StockOperationError("Adjustment quantity must be positive.")

        quantity = Decimal(str(quantity))

        sl = self._get_stock_level(product, variant, warehouse, location)

        if sl.available_quantity < quantity:
            raise InsufficientStockError(
                available=sl.available_quantity, requested=quantity,
            )

        sl.quantity -= quantity
        sl.last_stock_update = timezone.now()
        sl.save()

        movement = StockMovement.objects.create(
            product=product,
            variant=variant,
            from_warehouse=warehouse,
            from_location=location,
            movement_type=MOVEMENT_TYPE_ADJUSTMENT,
            quantity=quantity,
            reason=reason,
            cost_per_unit=sl.cost_per_unit,
            reference_type=REFERENCE_TYPE_ADJUSTMENT,
            reference_id=reference_id or "",
            notes=notes or self.notes,
            created_by=self.user,
        )

        logger.info(
            "ADJUST_DOWN product=%s qty=-%s warehouse=%s movement=%s user=%s reason=%s",
            product.pk, quantity, warehouse.pk, movement.pk,
            getattr(self.user, "pk", None), reason,
        )
        return OperationResult.ok(
            "adjust_down",
            data={
                "movement_id": str(movement.pk),
                "new_quantity": str(sl.quantity),
                "requires_authorization": self.requires_authorization(
                    quantity, sl.cost_per_unit,
                ),
            },
        )
