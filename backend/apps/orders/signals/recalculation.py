"""
Signals for order recalculation on line item changes (Task 34).

Auto-recalculates order totals when a line item is saved or deleted.
Uses a global flag to prevent infinite recursion.
"""

import logging
from contextlib import contextmanager

from django.db.models.signals import post_delete, post_save

logger = logging.getLogger(__name__)

_recalculating = False


def recalculate_on_line_save(sender, instance, created, **kwargs):
    """Recalculate order totals when a line item is saved."""
    global _recalculating
    if _recalculating:
        return

    from apps.orders.constants import EDITABLE_STATES
    from apps.orders.services.calculation_service import OrderCalculationService

    order = instance.order
    if order.status not in EDITABLE_STATES:
        return

    _recalculating = True
    try:
        OrderCalculationService(order).calculate_all(save=True)
    except Exception:
        logger.exception("Error recalculating order %s", order.order_number)
    finally:
        _recalculating = False


def recalculate_on_line_delete(sender, instance, **kwargs):
    """Recalculate order totals when a line item is deleted."""
    global _recalculating
    if _recalculating:
        return

    from apps.orders.constants import EDITABLE_STATES
    from apps.orders.services.calculation_service import OrderCalculationService

    order = instance.order
    if order.status not in EDITABLE_STATES:
        return

    _recalculating = True
    try:
        OrderCalculationService(order).calculate_all(save=True)
    except Exception:
        logger.exception(
            "Error recalculating order %s after line delete", order.order_number
        )
    finally:
        _recalculating = False


def connect_signals():
    """Connect all order recalculation signals."""
    from apps.orders.models.order_item import OrderLineItem

    post_save.connect(recalculate_on_line_save, sender=OrderLineItem)
    post_delete.connect(recalculate_on_line_delete, sender=OrderLineItem)


@contextmanager
def disable_order_signals():
    """
    Context manager to temporarily disable order recalculation signals.

    Useful during bulk operations to avoid redundant recalculations.

    Usage:
        with disable_order_signals():
            # bulk create/update line items
            ...
        # Then manually trigger recalculation once
    """
    from apps.orders.models.order_item import OrderLineItem

    post_save.disconnect(recalculate_on_line_save, sender=OrderLineItem)
    post_delete.disconnect(recalculate_on_line_delete, sender=OrderLineItem)
    try:
        yield
    finally:
        post_save.connect(recalculate_on_line_save, sender=OrderLineItem)
        post_delete.connect(recalculate_on_line_delete, sender=OrderLineItem)
