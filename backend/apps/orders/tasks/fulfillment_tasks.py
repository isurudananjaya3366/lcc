"""
Order notification and fulfillment Celery tasks (Task 66).
"""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_order_notification_async(self, order_id, notification_type):
    """
    Send an order notification asynchronously.

    notification_type: 'confirmed', 'shipped', 'delivered', etc.
    """
    try:
        from apps.orders.models import Order

        order = Order.objects.get(id=order_id)
        logger.info(
            "Sending %s notification for order %s",
            notification_type,
            order.order_number,
        )
        # TODO: Integrate with actual notification service (email/SMS)
    except Exception as exc:
        logger.exception("Failed to send %s notification for order %s", notification_type, order_id)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def update_tracking_status_async(self, fulfillment_id):
    """
    Poll carrier API and update fulfillment tracking status.
    """
    try:
        from apps.orders.models.fulfillment import Fulfillment

        fulfillment = Fulfillment.objects.get(id=fulfillment_id)
        logger.info(
            "Updating tracking for fulfillment %s (carrier: %s, tracking: %s)",
            fulfillment.fulfillment_number,
            fulfillment.carrier,
            fulfillment.tracking_number,
        )
        # TODO: Integrate with carrier tracking APIs
    except Exception as exc:
        logger.exception("Failed to update tracking for fulfillment %s", fulfillment_id)
        raise self.retry(exc=exc)


@shared_task
def check_delivery_status_async():
    """
    Periodic task: check delivery status for all shipped fulfillments.
    """
    from apps.orders.models.fulfillment import Fulfillment, FulfillmentStatus

    shipped = Fulfillment.objects.filter(
        status=FulfillmentStatus.SHIPPED,
        tracking_number__gt="",
    )
    for fulfillment in shipped:
        update_tracking_status_async.delay(str(fulfillment.id))

    logger.info("Queued tracking updates for %d shipped fulfillments", shipped.count())


@shared_task
def send_batch_shipping_notifications():
    """
    Periodic task: send notifications for recently shipped orders.
    """
    from django.utils import timezone
    from datetime import timedelta

    from apps.orders.models.fulfillment import Fulfillment, FulfillmentStatus

    recent = timezone.now() - timedelta(hours=1)
    fulfillments = Fulfillment.objects.filter(
        status=FulfillmentStatus.SHIPPED,
        shipped_at__gte=recent,
    ).select_related("order")

    for fulfillment in fulfillments:
        send_order_notification_async.delay(
            str(fulfillment.order_id), "shipped"
        )

    logger.info("Queued %d shipping notifications", fulfillments.count())
