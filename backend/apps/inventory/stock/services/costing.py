"""
Inventory costing utilities — WAC, FIFO, LIFO helpers.

The primary costing method is Weighted Average Cost (WAC) which is
handled inline by StockService.stock_in(). This module provides helper
functions for cost reconciliation and FIFO/LIFO lot-based allocation.
"""

from decimal import Decimal

from django.db.models import F, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone


def calculate_weighted_average_cost(
    current_qty, current_cost, incoming_qty, incoming_cost,
):
    """Calculate new WAC after receiving stock.

    Formula: (old_qty * old_cost + new_qty * new_cost) / total_qty
    """
    current_qty = Decimal(str(current_qty))
    current_cost = Decimal(str(current_cost))
    incoming_qty = Decimal(str(incoming_qty))
    incoming_cost = Decimal(str(incoming_cost))

    total_qty = current_qty + incoming_qty
    if total_qty <= 0:
        return incoming_cost

    return (current_qty * current_cost + incoming_qty * incoming_cost) / total_qty


def reconcile_stock_level_cost(stock_level):
    """Recalculate WAC from all STOCK_IN movements for a stock level.

    Returns a dict with the calculated cost and any discrepancy.
    """
    from apps.inventory.stock.constants import MOVEMENT_TYPE_STOCK_IN
    from apps.inventory.stock.models.stock_movement import StockMovement

    movements = StockMovement.objects.filter(
        product=stock_level.product,
        variant=stock_level.variant,
        to_warehouse=stock_level.warehouse,
        movement_type=MOVEMENT_TYPE_STOCK_IN,
        is_reversed=False,
    ).aggregate(
        total_cost=Coalesce(
            Sum(F("quantity") * F("cost_per_unit")),
            Decimal("0"),
        ),
        total_qty=Coalesce(Sum("quantity"), Decimal("0")),
    )

    total_qty = movements["total_qty"]
    if total_qty <= 0:
        return {
            "calculated_cost": Decimal("0"),
            "current_cost": stock_level.cost_per_unit,
            "discrepancy": Decimal("0"),
        }

    calculated = movements["total_cost"] / total_qty
    discrepancy = abs(calculated - stock_level.cost_per_unit)
    return {
        "calculated_cost": calculated,
        "current_cost": stock_level.cost_per_unit,
        "discrepancy": discrepancy,
    }


def calculate_stock_value(product, warehouse=None, variant=None):
    """Calculate total inventory value for a product."""
    from apps.inventory.stock.models.stock_level import StockLevel

    qs = StockLevel.objects.filter(product=product)
    if warehouse:
        qs = qs.filter(warehouse=warehouse)
    if variant:
        qs = qs.filter(variant=variant)

    result = qs.aggregate(
        total_value=Coalesce(
            Sum(F("quantity") * F("cost_per_unit")),
            Decimal("0"),
        ),
        total_quantity=Coalesce(Sum("quantity"), Decimal("0")),
    )
    return {
        "total_value": result["total_value"],
        "total_quantity": result["total_quantity"],
    }


def allocate_stock_fifo(product, warehouse, quantity, variant=None):
    """
    Allocate stock using FIFO (First-In, First-Out) from active lots.

    Consumes from the oldest lots first.
    Returns a list of dicts with lot info and the total weighted cost.
    """
    from apps.inventory.stock.models.stock_lot import StockLot

    quantity = Decimal(str(quantity))
    remaining = quantity
    allocations = []
    total_cost = Decimal("0")

    lots = StockLot.objects.active().filter(
        product=product,
        warehouse=warehouse,
    )
    if variant is not None:
        lots = lots.filter(variant=variant)
    lots = lots.order_by("received_date")  # FIFO: oldest first

    for lot in lots:
        if remaining <= 0:
            break
        consumed = min(remaining, lot.remaining_quantity)
        cost = consumed * lot.cost_per_unit
        allocations.append({
            "lot_id": str(lot.pk),
            "lot_number": lot.lot_number,
            "consumed": consumed,
            "cost_per_unit": lot.cost_per_unit,
            "cost": cost,
        })
        total_cost += cost
        remaining -= consumed

    if remaining > 0:
        return {
            "success": False,
            "allocated": quantity - remaining,
            "shortage": remaining,
            "allocations": allocations,
            "total_cost": total_cost,
            "weighted_average_cost": (
                total_cost / (quantity - remaining) if (quantity - remaining) > 0 else Decimal("0")
            ),
        }

    return {
        "success": True,
        "allocated": quantity,
        "shortage": Decimal("0"),
        "allocations": allocations,
        "total_cost": total_cost,
        "weighted_average_cost": total_cost / quantity if quantity > 0 else Decimal("0"),
    }


def allocate_stock_lifo(product, warehouse, quantity, variant=None):
    """
    Allocate stock using LIFO (Last-In, First-Out) from active lots.

    Consumes from the newest lots first.
    Returns a list of dicts with lot info and the total weighted cost.
    """
    from apps.inventory.stock.models.stock_lot import StockLot

    quantity = Decimal(str(quantity))
    remaining = quantity
    allocations = []
    total_cost = Decimal("0")

    lots = StockLot.objects.active().filter(
        product=product,
        warehouse=warehouse,
    )
    if variant is not None:
        lots = lots.filter(variant=variant)
    lots = lots.order_by("-received_date")  # LIFO: newest first

    for lot in lots:
        if remaining <= 0:
            break
        consumed = min(remaining, lot.remaining_quantity)
        cost = consumed * lot.cost_per_unit
        allocations.append({
            "lot_id": str(lot.pk),
            "lot_number": lot.lot_number,
            "consumed": consumed,
            "cost_per_unit": lot.cost_per_unit,
            "cost": cost,
        })
        total_cost += cost
        remaining -= consumed

    if remaining > 0:
        return {
            "success": False,
            "allocated": quantity - remaining,
            "shortage": remaining,
            "allocations": allocations,
            "total_cost": total_cost,
            "weighted_average_cost": (
                total_cost / (quantity - remaining) if (quantity - remaining) > 0 else Decimal("0")
            ),
        }

    return {
        "success": True,
        "allocated": quantity,
        "shortage": Decimal("0"),
        "allocations": allocations,
        "total_cost": total_cost,
        "weighted_average_cost": total_cost / quantity if quantity > 0 else Decimal("0"),
    }


def commit_fifo_allocation(allocations):
    """
    Consume lots based on a previous FIFO/LIFO allocation result.

    Takes the allocations list from allocate_stock_fifo/lifo and
    actually decrements remaining_quantity on each lot.
    """
    from apps.inventory.stock.models.stock_lot import StockLot

    for alloc in allocations:
        lot = StockLot.objects.get(pk=alloc["lot_id"])
        lot.consume(alloc["consumed"])


def get_expiring_lots(days=30, warehouse=None):
    """Return lots expiring within the given number of days."""
    from apps.inventory.stock.models.stock_lot import StockLot

    qs = StockLot.objects.expiring_soon(days=days)
    if warehouse is not None:
        qs = qs.filter(warehouse=warehouse)
    return qs
