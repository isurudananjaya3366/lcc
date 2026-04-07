"""
Stock reservation Celery tasks (Task 42).

Async tasks for stock reservation, release, and bulk operations.
"""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    soft_time_limit=300,
    time_limit=330,
)
def reserve_stock_async(self, order_id, user_id=None):
    """
    Reserve stock for an order asynchronously.

    Args:
        order_id: Order UUID string.
        user_id: User UUID string (optional).

    Returns:
        dict: Success result with reservation details.
    """
    from apps.orders.exceptions import InsufficientStockError

    try:
        from apps.orders.models import Order
        from apps.orders.services.stock_service import StockService

        order = Order.objects.get(id=order_id)

        if order.status != "confirmed":
            logger.warning(
                "Skipping stock reservation for order %s (status: %s)",
                order.order_number,
                order.status,
            )
            return {
                "status": "SKIPPED",
                "order_id": str(order_id),
                "reason": f"Order status is {order.status}, expected confirmed",
            }

        user = None
        if user_id:
            from django.contrib.auth import get_user_model

            User = get_user_model()
            user = User.objects.filter(id=user_id).first()

        StockService.reserve_stock(order, user)

        return {
            "status": "SUCCESS",
            "order_id": str(order_id),
            "order_number": order.order_number,
            "reserved_items": order.line_items.count(),
            "reserved_at": str(order.stock_reserved_at),
        }

    except InsufficientStockError as exc:
        logger.warning(
            "Insufficient stock for order %s: %s", order_id, str(exc)
        )
        return {
            "status": "INSUFFICIENT_STOCK",
            "order_id": str(order_id),
            "error": str(exc),
        }
    except Exception as exc:
        logger.exception(
            "Failed to reserve stock for order %s", order_id
        )
        countdown = 30 * (self.request.retries + 1)
        raise self.retry(exc=exc, countdown=countdown)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    soft_time_limit=300,
    time_limit=330,
)
def release_stock_async(self, order_id, user_id=None):
    """
    Release stock for an order asynchronously.

    Args:
        order_id: Order UUID string.
        user_id: User UUID string (optional).

    Returns:
        dict: Success result with release details.
    """
    try:
        from apps.orders.models import Order
        from apps.orders.services.stock_service import StockService

        order = Order.objects.get(id=order_id)

        user = None
        if user_id:
            from django.contrib.auth import get_user_model

            User = get_user_model()
            user = User.objects.filter(id=user_id).first()

        StockService.release_stock(order, user)

        return {
            "status": "SUCCESS",
            "order_id": str(order_id),
            "order_number": order.order_number,
            "released_items": order.line_items.count(),
        }

    except Exception as exc:
        logger.exception(
            "Failed to release stock for order %s", order_id
        )
        countdown = 30 * (self.request.retries + 1)
        raise self.retry(exc=exc, countdown=countdown)


@shared_task(bind=True)
def reserve_stock_bulk(self, order_ids):
    """
    Reserve stock for multiple orders in bulk.

    Dispatches individual reservation tasks for parallel execution.

    Args:
        order_ids: List of Order UUID strings.

    Returns:
        dict: Summary of dispatched tasks.
    """
    dispatched = []
    for order_id in order_ids:
        reserve_stock_async.delay(order_id)
        dispatched.append(order_id)

    logger.info("Dispatched bulk stock reservation for %d orders", len(dispatched))
    return {
        "status": "DISPATCHED",
        "count": len(dispatched),
        "order_ids": dispatched,
    }
