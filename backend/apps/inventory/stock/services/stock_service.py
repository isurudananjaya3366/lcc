"""
StockService — core service for all stock operations.

Provides transaction-safe stock_in, stock_out, transfer, reserve,
release, and commit_reserved operations. Each operation locks the
relevant StockLevel row with select_for_update(), creates a
StockMovement record, and returns an OperationResult.
"""

import logging
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.inventory.stock.constants import (
    MOVEMENT_TYPE_ADJUSTMENT,
    MOVEMENT_TYPE_RELEASED,
    MOVEMENT_TYPE_RESERVED,
    MOVEMENT_TYPE_STOCK_IN,
    MOVEMENT_TYPE_STOCK_OUT,
    MOVEMENT_TYPE_TRANSFER,
    REASON_CORRECTION,
    REASON_ORDER_CANCELLED,
    REASON_ORDER_TIMEOUT,
    REASON_PURCHASE,
    REASON_SALE,
    REASON_TRANSFER,
    REFERENCE_TYPE_ORDER,
    REFERENCE_TYPE_PO,
    REFERENCE_TYPE_TRANSFER,
    TRANSIT_DISPATCHED,
    TRANSIT_PENDING,
    TRANSIT_RECEIVED,
)
from apps.inventory.stock.exceptions import (
    InactiveWarehouseError,
    InsufficientStockError,
    InvalidProductError,
    StockOperationError,
)
from apps.inventory.stock.results import OperationResult

logger = logging.getLogger("inventory.stock.operations")


class StockService:
    """Service for all core stock operations."""

    def __init__(self, user=None, notes=""):
        self.user = user
        self.notes = notes

    # ── Helpers ─────────────────────────────────────────────────────

    def _get_stock_level(self, product, variant, warehouse, location=None, lock=True):
        """Get or create a StockLevel row, optionally locked for update."""
        from apps.inventory.stock.models.stock_level import StockLevel

        lookup = {
            "product": product,
            "variant": variant,
            "warehouse": warehouse,
            "location": location,
        }
        qs = StockLevel.objects.filter(**lookup)
        if lock:
            qs = qs.select_for_update()

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

    def _create_movement(self, **kwargs):
        """Create and return a StockMovement record."""
        from apps.inventory.stock.models.stock_movement import StockMovement

        kwargs.setdefault("created_by", self.user)
        return StockMovement.objects.create(**kwargs)

    def _validate_quantity(self, quantity):
        if quantity is None or quantity <= 0:
            raise StockOperationError("Quantity must be greater than zero.")

    def _validate_product(self, product, variant=None):
        if product is None:
            raise InvalidProductError("Product is required.")
        if variant is not None and variant.product_id != product.pk:
            raise InvalidProductError("Variant does not belong to the given product.")

    def _validate_warehouse(self, warehouse):
        if warehouse is None:
            raise StockOperationError("Warehouse is required.")
        if hasattr(warehouse, "is_active") and not warehouse.is_active:
            raise InactiveWarehouseError(
                f"Warehouse '{warehouse}' is inactive."
            )

    # ── Stock In (Task 38) ──────────────────────────────────────────

    @transaction.atomic
    def stock_in(
        self,
        product,
        quantity,
        warehouse,
        variant=None,
        location=None,
        cost_per_unit=None,
        reason=REASON_PURCHASE,
        reference_type=None,
        reference_id=None,
        notes=None,
    ):
        """Receive stock into a warehouse."""
        self._validate_product(product, variant)
        self._validate_quantity(quantity)
        self._validate_warehouse(warehouse)

        quantity = Decimal(str(quantity))

        sl = self._get_stock_level(product, variant, warehouse, location)

        # Weighted average cost update
        if cost_per_unit is not None:
            cost_per_unit = Decimal(str(cost_per_unit))
            old_total = sl.quantity * sl.cost_per_unit
            new_total = quantity * cost_per_unit
            new_qty = sl.quantity + quantity
            sl.cost_per_unit = (
                (old_total + new_total) / new_qty if new_qty > 0 else cost_per_unit
            )

        sl.quantity += quantity
        if reference_type == REFERENCE_TYPE_PO and sl.incoming_quantity >= quantity:
            sl.incoming_quantity -= quantity
        sl.last_stock_update = timezone.now()
        sl.save()

        movement = self._create_movement(
            product=product,
            variant=variant,
            to_warehouse=warehouse,
            to_location=location,
            movement_type=MOVEMENT_TYPE_STOCK_IN,
            quantity=quantity,
            reason=reason,
            cost_per_unit=cost_per_unit or sl.cost_per_unit,
            reference_type=reference_type or "",
            reference_id=reference_id or "",
            notes=notes or self.notes,
        )

        logger.info(
            "STOCK_IN product=%s qty=%s warehouse=%s movement=%s",
            product.pk, quantity, warehouse.pk, movement.pk,
        )
        return OperationResult.ok(
            "stock_in",
            data={
                "movement_id": str(movement.pk),
                "new_quantity": str(sl.quantity),
                "cost_per_unit": str(sl.cost_per_unit),
            },
        )

    # ── Stock Out (Task 39) ─────────────────────────────────────────

    @transaction.atomic
    def stock_out(
        self,
        product,
        quantity,
        warehouse,
        variant=None,
        location=None,
        reason=REASON_SALE,
        reference_type=None,
        reference_id=None,
        notes=None,
    ):
        """Remove stock from a warehouse."""
        self._validate_product(product, variant)
        self._validate_quantity(quantity)
        self._validate_warehouse(warehouse)

        quantity = Decimal(str(quantity))

        sl = self._get_stock_level(product, variant, warehouse, location)
        available = sl.available_quantity

        if available < quantity:
            raise InsufficientStockError(
                available=available, requested=quantity,
            )

        sl.quantity -= quantity
        sl.last_stock_update = timezone.now()
        sl.save()

        movement = self._create_movement(
            product=product,
            variant=variant,
            from_warehouse=warehouse,
            from_location=location,
            movement_type=MOVEMENT_TYPE_STOCK_OUT,
            quantity=quantity,
            reason=reason,
            cost_per_unit=sl.cost_per_unit,
            reference_type=reference_type or "",
            reference_id=reference_id or "",
            notes=notes or self.notes,
        )

        logger.info(
            "STOCK_OUT product=%s qty=%s warehouse=%s movement=%s",
            product.pk, quantity, warehouse.pk, movement.pk,
        )
        return OperationResult.ok(
            "stock_out",
            data={
                "movement_id": str(movement.pk),
                "remaining_quantity": str(sl.quantity),
                "cost_per_unit": str(sl.cost_per_unit),
            },
        )

    # ── Stock Availability (Task 40) ────────────────────────────────

    def check_availability(self, product, quantity, warehouse, variant=None, location=None):
        """Read-only availability check (no locks)."""
        from apps.inventory.stock.models.stock_level import StockLevel

        quantity = Decimal(str(quantity))
        try:
            sl = StockLevel.objects.get(
                product=product,
                variant=variant,
                warehouse=warehouse,
                location=location,
            )
        except StockLevel.DoesNotExist:
            return {
                "is_available": False,
                "total_quantity": Decimal("0"),
                "reserved_quantity": Decimal("0"),
                "available_quantity": Decimal("0"),
                "requested_quantity": quantity,
                "shortage": quantity,
            }

        available = sl.available_quantity
        return {
            "is_available": available >= quantity,
            "total_quantity": sl.quantity,
            "reserved_quantity": sl.reserved_quantity,
            "available_quantity": available,
            "requested_quantity": quantity,
            "shortage": max(Decimal("0"), quantity - available),
        }

    def validate_availability_or_raise(self, product, quantity, warehouse, variant=None, location=None):
        """Raise InsufficientStockError if stock is insufficient."""
        result = self.check_availability(product, quantity, warehouse, variant, location)
        if not result["is_available"]:
            raise InsufficientStockError(
                available=result["available_quantity"],
                requested=result["requested_quantity"],
            )
        return result

    # ── Transfer (Tasks 41-42) ──────────────────────────────────────

    @transaction.atomic
    def transfer(
        self,
        product,
        quantity,
        from_warehouse,
        to_warehouse,
        variant=None,
        from_location=None,
        to_location=None,
        reason=REASON_TRANSFER,
        reference_type=None,
        reference_id=None,
        notes=None,
    ):
        """Transfer stock between warehouses atomically."""
        self._validate_product(product, variant)
        self._validate_quantity(quantity)
        self._validate_warehouse(from_warehouse)
        self._validate_warehouse(to_warehouse)

        if from_warehouse.pk == to_warehouse.pk:
            raise StockOperationError("Cannot transfer to the same warehouse.")

        quantity = Decimal(str(quantity))

        # Lock in consistent ID order to prevent deadlocks
        first, second = sorted(
            [
                (from_warehouse, from_location, "source"),
                (to_warehouse, to_location, "dest"),
            ],
            key=lambda x: str(x[0].pk),
        )

        sl_first = self._get_stock_level(product, variant, first[0], first[1])
        sl_second = self._get_stock_level(product, variant, second[0], second[1])

        if first[2] == "source":
            src_sl, dst_sl = sl_first, sl_second
        else:
            src_sl, dst_sl = sl_second, sl_first

        if src_sl.available_quantity < quantity:
            raise InsufficientStockError(
                available=src_sl.available_quantity, requested=quantity,
            )

        # Update source
        src_sl.quantity -= quantity
        src_sl.last_stock_update = timezone.now()
        src_sl.save()

        # Update destination (carry over cost)
        old_total = dst_sl.quantity * dst_sl.cost_per_unit
        new_total = quantity * src_sl.cost_per_unit
        new_qty = dst_sl.quantity + quantity
        dst_sl.cost_per_unit = (
            (old_total + new_total) / new_qty if new_qty > 0 else src_sl.cost_per_unit
        )
        dst_sl.quantity += quantity
        dst_sl.last_stock_update = timezone.now()
        dst_sl.save()

        movement = self._create_movement(
            product=product,
            variant=variant,
            from_warehouse=from_warehouse,
            to_warehouse=to_warehouse,
            from_location=from_location,
            to_location=to_location,
            movement_type=MOVEMENT_TYPE_TRANSFER,
            quantity=quantity,
            reason=reason,
            cost_per_unit=src_sl.cost_per_unit,
            reference_type=reference_type or REFERENCE_TYPE_TRANSFER,
            reference_id=reference_id or "",
            notes=notes or self.notes,
        )

        logger.info(
            "TRANSFER product=%s qty=%s from=%s to=%s movement=%s",
            product.pk, quantity, from_warehouse.pk, to_warehouse.pk, movement.pk,
        )
        return OperationResult.ok(
            "transfer",
            data={
                "movement_id": str(movement.pk),
                "source_quantity": str(src_sl.quantity),
                "destination_quantity": str(dst_sl.quantity),
            },
        )

    # ── Reserve (Task 44) ───────────────────────────────────────────

    @transaction.atomic
    def reserve_stock(
        self,
        product,
        quantity,
        warehouse,
        variant=None,
        location=None,
        reference_id=None,
        notes=None,
    ):
        """Reserve stock for a pending order."""
        self._validate_product(product, variant)
        self._validate_quantity(quantity)
        self._validate_warehouse(warehouse)

        quantity = Decimal(str(quantity))

        sl = self._get_stock_level(product, variant, warehouse, location)
        available = sl.available_quantity

        if available < quantity:
            raise InsufficientStockError(available=available, requested=quantity)

        sl.reserved_quantity += quantity
        sl.last_stock_update = timezone.now()
        sl.save()

        movement = self._create_movement(
            product=product,
            variant=variant,
            from_warehouse=warehouse,
            from_location=location,
            movement_type=MOVEMENT_TYPE_RESERVED,
            quantity=quantity,
            reason=REASON_SALE,
            reference_type=REFERENCE_TYPE_ORDER,
            reference_id=reference_id or "",
            notes=notes or self.notes,
        )

        logger.info(
            "RESERVE product=%s qty=%s warehouse=%s movement=%s",
            product.pk, quantity, warehouse.pk, movement.pk,
        )
        return OperationResult.ok(
            "reserve",
            data={
                "movement_id": str(movement.pk),
                "reserved_quantity": str(sl.reserved_quantity),
                "available_quantity": str(sl.available_quantity),
            },
        )

    # ── Release (Task 45) ───────────────────────────────────────────

    @transaction.atomic
    def release_stock(
        self,
        product,
        quantity,
        warehouse,
        variant=None,
        location=None,
        reference_id=None,
        reason=REASON_CORRECTION,
        notes=None,
    ):
        """Release previously reserved stock back to available."""
        self._validate_product(product, variant)
        self._validate_quantity(quantity)
        self._validate_warehouse(warehouse)

        quantity = Decimal(str(quantity))

        sl = self._get_stock_level(product, variant, warehouse, location)

        if sl.reserved_quantity < quantity:
            raise StockOperationError(
                f"Cannot release {quantity}: only {sl.reserved_quantity} reserved."
            )

        sl.reserved_quantity -= quantity
        sl.last_stock_update = timezone.now()
        sl.save()

        movement = self._create_movement(
            product=product,
            variant=variant,
            to_warehouse=warehouse,
            to_location=location,
            movement_type=MOVEMENT_TYPE_RELEASED,
            quantity=quantity,
            reason=reason,
            reference_type=REFERENCE_TYPE_ORDER,
            reference_id=reference_id or "",
            notes=notes or self.notes,
        )

        logger.info(
            "RELEASE product=%s qty=%s warehouse=%s movement=%s",
            product.pk, quantity, warehouse.pk, movement.pk,
        )
        return OperationResult.ok(
            "release",
            data={
                "movement_id": str(movement.pk),
                "reserved_quantity": str(sl.reserved_quantity),
                "available_quantity": str(sl.available_quantity),
            },
        )

    # ── Commit Reserved (Task 46) ───────────────────────────────────

    @transaction.atomic
    def commit_reserved(
        self,
        product,
        quantity,
        warehouse,
        variant=None,
        location=None,
        reference_id=None,
        notes=None,
    ):
        """Convert reserved stock to sold — reduces both quantity and reserved."""
        self._validate_product(product, variant)
        self._validate_quantity(quantity)
        self._validate_warehouse(warehouse)

        quantity = Decimal(str(quantity))

        sl = self._get_stock_level(product, variant, warehouse, location)

        if sl.reserved_quantity < quantity:
            raise StockOperationError(
                f"Cannot commit {quantity}: only {sl.reserved_quantity} reserved."
            )

        sl.quantity -= quantity
        sl.reserved_quantity -= quantity
        sl.last_stock_update = timezone.now()
        sl.save()

        movement = self._create_movement(
            product=product,
            variant=variant,
            from_warehouse=warehouse,
            from_location=location,
            movement_type=MOVEMENT_TYPE_STOCK_OUT,
            quantity=quantity,
            reason=REASON_SALE,
            cost_per_unit=sl.cost_per_unit,
            reference_type=REFERENCE_TYPE_ORDER,
            reference_id=reference_id or "",
            notes=notes or f"Committed reserved stock. {self.notes}",
        )

        logger.info(
            "COMMIT_RESERVED product=%s qty=%s warehouse=%s movement=%s",
            product.pk, quantity, warehouse.pk, movement.pk,
        )
        return OperationResult.ok(
            "commit_reserved",
            data={
                "movement_id": str(movement.pk),
                "remaining_quantity": str(sl.quantity),
                "reserved_quantity": str(sl.reserved_quantity),
                "cost_per_unit": str(sl.cost_per_unit),
            },
        )

    # ── In-Transit Tracking (Task 43) ───────────────────────────────

    @transaction.atomic
    def mark_as_dispatched(self, movement_id, user=None):
        """Mark a transfer movement as dispatched and track in-transit qty."""
        from apps.inventory.stock.models.stock_movement import StockMovement

        movement = StockMovement.objects.select_for_update().get(pk=movement_id)
        if movement.movement_type != MOVEMENT_TYPE_TRANSFER:
            raise StockOperationError("Only transfer movements can be dispatched.")
        if movement.transit_status == TRANSIT_DISPATCHED:
            raise StockOperationError("Movement is already dispatched.")

        movement.transit_status = TRANSIT_DISPATCHED
        movement.dispatched_at = timezone.now()
        movement.dispatched_by = user or self.user
        movement.save(update_fields=[
            "transit_status", "dispatched_at", "dispatched_by", "updated_on",
        ])

        # Update in_transit_quantity on destination stock level
        dst_sl = self._get_stock_level(
            movement.product, movement.variant, movement.to_warehouse,
        )
        dst_sl.in_transit_quantity += movement.quantity
        dst_sl.save(update_fields=["in_transit_quantity", "updated_on"])

        logger.info(
            "DISPATCHED movement=%s product=%s qty=%s",
            movement.pk, movement.product.pk, movement.quantity,
        )
        return OperationResult.ok(
            "mark_as_dispatched",
            data={
                "movement_id": str(movement.pk),
                "transit_status": TRANSIT_DISPATCHED,
                "in_transit_quantity": str(dst_sl.in_transit_quantity),
            },
        )

    @transaction.atomic
    def mark_as_received(self, movement_id, user=None):
        """Mark a dispatched transfer as received and clear in-transit qty."""
        from apps.inventory.stock.models.stock_movement import StockMovement

        movement = StockMovement.objects.select_for_update().get(pk=movement_id)
        if movement.movement_type != MOVEMENT_TYPE_TRANSFER:
            raise StockOperationError("Only transfer movements can be received.")
        if movement.transit_status != TRANSIT_DISPATCHED:
            raise StockOperationError("Movement must be dispatched before receiving.")

        movement.transit_status = TRANSIT_RECEIVED
        movement.received_at = timezone.now()
        movement.received_by = user or self.user
        movement.save(update_fields=[
            "transit_status", "received_at", "received_by", "updated_on",
        ])

        # Clear in_transit_quantity on destination stock level
        dst_sl = self._get_stock_level(
            movement.product, movement.variant, movement.to_warehouse,
        )
        dst_sl.in_transit_quantity = max(
            Decimal("0"), dst_sl.in_transit_quantity - movement.quantity
        )
        dst_sl.save(update_fields=["in_transit_quantity", "updated_on"])

        logger.info(
            "RECEIVED movement=%s product=%s qty=%s",
            movement.pk, movement.product.pk, movement.quantity,
        )
        return OperationResult.ok(
            "mark_as_received",
            data={
                "movement_id": str(movement.pk),
                "transit_status": TRANSIT_RECEIVED,
                "in_transit_quantity": str(dst_sl.in_transit_quantity),
            },
        )

    def get_in_transit_quantity(self, product, warehouse, variant=None):
        """Get total in-transit quantity for a product at a warehouse."""
        from apps.inventory.stock.models.stock_movement import StockMovement
        from django.db.models import Sum
        from django.db.models.functions import Coalesce

        total = StockMovement.objects.filter(
            product=product,
            to_warehouse=warehouse,
            movement_type=MOVEMENT_TYPE_TRANSFER,
            transit_status=TRANSIT_DISPATCHED,
            is_reversed=False,
        )
        if variant is not None:
            total = total.filter(variant=variant)
        result = total.aggregate(
            in_transit=Coalesce(Sum("quantity"), Decimal("0")),
        )
        return result["in_transit"]

    # ── Movement-ID Based Release/Commit (Tasks 45-46) ──────────────

    @transaction.atomic
    def release_by_movement(self, movement_id, reason=REASON_ORDER_CANCELLED, notes=None):
        """Release reserved stock by the original reservation movement ID."""
        from apps.inventory.stock.models.stock_movement import StockMovement

        original = StockMovement.objects.get(pk=movement_id)
        if original.movement_type != MOVEMENT_TYPE_RESERVED:
            raise StockOperationError("Can only release reservation movements.")
        if original.is_reversed:
            raise StockOperationError("This reservation has already been released.")

        return self.release_stock(
            product=original.product,
            quantity=original.quantity,
            warehouse=original.from_warehouse,
            variant=original.variant,
            reference_id=original.reference_id,
            reason=reason,
            notes=notes or f"Released via movement {movement_id}",
        )

    @transaction.atomic
    def commit_by_movement(self, movement_id, notes=None):
        """Commit reserved stock by the original reservation movement ID."""
        from apps.inventory.stock.models.stock_movement import StockMovement

        original = StockMovement.objects.get(pk=movement_id)
        if original.movement_type != MOVEMENT_TYPE_RESERVED:
            raise StockOperationError("Can only commit reservation movements.")
        if original.is_reversed:
            raise StockOperationError("This reservation has already been released.")

        return self.commit_reserved(
            product=original.product,
            quantity=original.quantity,
            warehouse=original.from_warehouse,
            variant=original.variant,
            reference_id=original.reference_id,
            notes=notes or f"Committed via movement {movement_id}",
        )

    @transaction.atomic
    def release_all_for_order(self, reference_id, reason=REASON_ORDER_CANCELLED, notes=None):
        """Release all reservations associated with an order reference_id."""
        from apps.inventory.stock.models.stock_movement import StockMovement

        reservations = StockMovement.objects.filter(
            movement_type=MOVEMENT_TYPE_RESERVED,
            reference_id=reference_id,
            is_reversed=False,
        )
        results = []
        for reservation in reservations:
            result = self.release_stock(
                product=reservation.product,
                quantity=reservation.quantity,
                warehouse=reservation.from_warehouse,
                variant=reservation.variant,
                reference_id=reference_id,
                reason=reason,
                notes=notes or f"Order {reference_id} cancelled/released.",
            )
            results.append(result)
        return OperationResult.ok(
            "release_all_for_order",
            data={
                "reference_id": reference_id,
                "released_count": len(results),
            },
        )

    @transaction.atomic
    def commit_all_for_order(self, reference_id, notes=None):
        """Commit all reservations associated with an order reference_id."""
        from apps.inventory.stock.models.stock_movement import StockMovement

        reservations = StockMovement.objects.filter(
            movement_type=MOVEMENT_TYPE_RESERVED,
            reference_id=reference_id,
            is_reversed=False,
        )
        results = []
        for reservation in reservations:
            result = self.commit_reserved(
                product=reservation.product,
                quantity=reservation.quantity,
                warehouse=reservation.from_warehouse,
                variant=reservation.variant,
                reference_id=reference_id,
                notes=notes or f"Order {reference_id} fulfilled.",
            )
            results.append(result)
        return OperationResult.ok(
            "commit_all_for_order",
            data={
                "reference_id": reference_id,
                "committed_count": len(results),
            },
        )

    # ── Expired Reservation Cleanup ─────────────────────────────────

    @transaction.atomic
    def release_expired_reservations(self):
        """Release all reservations past their reserved_until time."""
        from apps.inventory.stock.models.stock_movement import StockMovement

        now = timezone.now()
        expired = StockMovement.objects.filter(
            movement_type=MOVEMENT_TYPE_RESERVED,
            reserved_until__isnull=False,
            reserved_until__lt=now,
            is_reversed=False,
        )
        results = []
        for reservation in expired:
            result = self.release_stock(
                product=reservation.product,
                quantity=reservation.quantity,
                warehouse=reservation.from_warehouse,
                variant=reservation.variant,
                reference_id=reservation.reference_id,
                reason=REASON_ORDER_TIMEOUT,
                notes="Reservation expired automatically.",
            )
            results.append(result)

        logger.info("Released %d expired reservations.", len(results))
        return OperationResult.ok(
            "release_expired_reservations",
            data={"released_count": len(results)},
        )
