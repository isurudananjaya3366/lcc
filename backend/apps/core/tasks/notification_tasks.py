"""
LankaCommerce Cloud - Notification Celery Tasks.

Stub implementations for in-app and push notification delivery.
Actual notification service integration will be added in later phases.
"""

import logging

from celery import shared_task

from apps.core.tasks.base import TenantAwareTask

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    base=TenantAwareTask,
    name="apps.core.tasks.notification_tasks.send_notification_task",
    max_retries=3,
    retry_backoff=True,
)
def send_notification_task(
    self,
    *,
    tenant_id: int,
    user_id: int,
    title: str,
    message: str,
    notification_type: str = "info",
    data: dict | None = None,
):
    """Send an in-app notification to a user.

    This is a **stub** — the actual notification service is not yet wired.

    Args:
        tenant_id: PK of the target :class:`~apps.tenants.models.Tenant`.
        user_id: PK of the recipient user.
        title: Notification title / headline.
        message: Notification body text.
        notification_type: Category (``"info"``, ``"warning"``, ``"error"``, ``"success"``).
        data: Optional extra payload for the client.
    """
    logger.info(
        "Sending notification to user %s (tenant %s): [%s] %s",
        user_id,
        tenant_id,
        notification_type,
        title,
    )

    # TODO: Persist notification record and broadcast via WebSocket / SSE.
    logger.info("Notification sent (stub) — user=%s, title='%s'", user_id, title)
    return {
        "status": "sent",
        "user_id": user_id,
        "title": title,
        "notification_type": notification_type,
    }


@shared_task(
    bind=True,
    base=TenantAwareTask,
    name="apps.core.tasks.notification_tasks.send_push_notification_task",
    max_retries=3,
    retry_backoff=True,
)
def send_push_notification_task(
    self,
    *,
    tenant_id: int,
    user_id: int,
    title: str,
    body: str,
    data: dict | None = None,
):
    """Send a push notification to a user's device.

    This is a **stub** — push provider (FCM / APNs) is not yet integrated.

    Args:
        tenant_id: PK of the target :class:`~apps.tenants.models.Tenant`.
        user_id: PK of the recipient user.
        title: Push notification title.
        body: Push notification body.
        data: Optional payload for the client app.
    """
    logger.info(
        "Sending push notification to user %s (tenant %s): '%s'",
        user_id,
        tenant_id,
        title,
    )

    # TODO: Integrate FCM / APNs push provider.
    logger.info(
        "Push notification sent (stub) — user=%s, title='%s'", user_id, title
    )
    return {
        "status": "sent",
        "user_id": user_id,
        "title": title,
    }
