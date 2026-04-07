"""
Notification service for order-related notifications (Task 65).

Handles sending emails, SMS, and in-app notifications for order events.
Integrates with Celery for async delivery.
"""

import logging

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Centralized notification dispatcher for order lifecycle events.

    All methods are safe to call synchronously — they queue async
    tasks for actual delivery via Celery.
    """

    # ── Order Lifecycle Notifications ────────────────────────────

    @classmethod
    def notify_order_confirmed(cls, order, user=None):
        """Send order confirmation notification to customer."""
        cls._dispatch(order, "confirmed", context={
            "order_number": order.order_number,
            "total": str(order.total_amount),
        })

    @classmethod
    def notify_order_processing(cls, order, user=None):
        """Notify customer that order is being processed."""
        cls._dispatch(order, "processing", context={
            "order_number": order.order_number,
        })

    @classmethod
    def notify_order_shipped(cls, order, fulfillment=None, user=None):
        """Send shipping notification with tracking details."""
        context = {"order_number": order.order_number}
        if fulfillment:
            context.update({
                "carrier": fulfillment.carrier,
                "tracking_number": fulfillment.tracking_number,
                "tracking_url": fulfillment.tracking_url,
                "estimated_delivery": str(fulfillment.estimated_delivery_date or ""),
            })
        cls._dispatch(order, "shipped", context=context)

    @classmethod
    def notify_order_delivered(cls, order, fulfillment=None, user=None):
        """Send delivery confirmation notification."""
        cls._dispatch(order, "delivered", context={
            "order_number": order.order_number,
            "delivered_at": str(fulfillment.delivered_at) if fulfillment else "",
        })

    @classmethod
    def notify_order_completed(cls, order, user=None):
        """Send order completion notification."""
        cls._dispatch(order, "completed", context={
            "order_number": order.order_number,
        })

    @classmethod
    def notify_order_cancelled(cls, order, reason="", user=None):
        """Send cancellation notification."""
        cls._dispatch(order, "cancelled", context={
            "order_number": order.order_number,
            "reason": reason,
        })

    # ── Fulfillment Notifications ────────────────────────────────

    @classmethod
    def notify_partial_fulfillment(cls, order, fulfillment, user=None):
        """Notify customer about partial shipment."""
        cls._dispatch(order, "partial_shipment", context={
            "order_number": order.order_number,
            "fulfillment_number": fulfillment.fulfillment_number,
            "carrier": fulfillment.carrier,
            "tracking_number": fulfillment.tracking_number,
        })

    @classmethod
    def notify_warehouse_team(cls, order, fulfillment=None, action="pick"):
        """Send internal notification to warehouse team."""
        logger.info(
            "Warehouse notification: %s for order %s (fulfillment %s)",
            action,
            order.order_number,
            fulfillment.fulfillment_number if fulfillment else "N/A",
        )
        # Internal notifications — no customer email needed
        # TODO: Integrate with internal messaging / dashboard alerts

    # ── Stock Notifications ──────────────────────────────────────

    @classmethod
    def notify_insufficient_stock(cls, order, item_name, available, requested):
        """Alert staff about insufficient stock."""
        logger.warning(
            "Insufficient stock for order %s: %s — need %s, have %s",
            order.order_number,
            item_name,
            requested,
            available,
        )
        # TODO: Integrate with staff notification channel

    @classmethod
    def notify_low_stock(cls, product_name, current_quantity, threshold):
        """Alert when stock falls below threshold."""
        logger.warning(
            "Low stock alert: %s — current: %s, threshold: %s",
            product_name,
            current_quantity,
            threshold,
        )
        # TODO: Integrate with inventory alerts

    # ── Dispatch Engine ──────────────────────────────────────────

    @classmethod
    def _dispatch(cls, order, notification_type, context=None):
        """
        Queue a notification for async delivery.

        Uses Celery task if available, falls back to synchronous logging.
        """
        from apps.orders.tasks.fulfillment_tasks import send_order_notification_async

        logger.info(
            "Dispatching '%s' notification for order %s",
            notification_type,
            order.order_number,
        )

        try:
            send_order_notification_async.delay(
                str(order.id), notification_type
            )
        except Exception:
            logger.exception(
                "Failed to queue '%s' notification for order %s",
                notification_type,
                order.order_number,
            )
