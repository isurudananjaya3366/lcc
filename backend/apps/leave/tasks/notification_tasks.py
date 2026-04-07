"""Celery tasks for leave notifications.

Handles async notification sending, daily expiry reminders,
and upcoming leave reminders.
"""

import logging
from datetime import timedelta

from django.utils import timezone

logger = logging.getLogger(__name__)

try:
    from celery import shared_task
except ImportError:

    def shared_task(*args, **kwargs):
        def decorator(func):
            return func
        if args and callable(args[0]):
            return args[0]
        return decorator


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def send_leave_notification_async(self, notification_type, leave_request_id, tenant_id=None):
    """Send a leave notification asynchronously.

    Args:
        notification_type: One of 'submission', 'approval', 'rejection',
                          'cancellation'.
        leave_request_id: UUID of the leave request.
        tenant_id: Optional tenant ID for schema context.
    """
    try:
        from apps.leave.models.leave_request import LeaveRequest
        from apps.leave.services.notification_service import LeaveNotificationService

        leave_request = LeaveRequest.objects.select_related(
            "employee__user", "employee__department", "leave_type", "approved_by"
        ).get(id=leave_request_id)

        service = LeaveNotificationService()

        dispatch = {
            "submission": service.notify_request_submitted,
            "approval": service.notify_approval,
            "rejection": service.notify_rejection,
            "cancellation": service.notify_cancellation,
        }

        handler = dispatch.get(notification_type)
        if handler:
            handler(leave_request)
            logger.info(
                "Sent %s notification for leave %s",
                notification_type,
                leave_request_id,
            )
        else:
            logger.warning("Unknown notification type: %s", notification_type)

    except Exception as exc:
        logger.error(
            "Failed to send %s notification for leave %s: %s",
            notification_type,
            leave_request_id,
            str(exc),
        )
        raise self.retry(exc=exc)


@shared_task
def send_expiry_reminders_batch():
    """Daily cron: find expiring balances and send notifications.

    Searches for balances with carry_forward_expiry within 30 days
    across all tenants.
    """
    try:
        from apps.leave.models.leave_balance import LeaveBalance
        from apps.leave.services.notification_service import LeaveNotificationService

        today = timezone.now().date()
        threshold = today + timedelta(days=30)

        expiring = LeaveBalance.objects.filter(
            carry_forward_expiry__isnull=False,
            carry_forward_expiry__lte=threshold,
            carry_forward_expiry__gte=today,
            is_active=True,
        ).select_related("employee__user", "leave_type")

        service = LeaveNotificationService()
        targets = []
        for bal in expiring:
            days_left = (bal.carry_forward_expiry - today).days
            targets.append((bal, days_left))

        if targets:
            result = service.send_bulk_expiry_notifications(targets)
            logger.info(
                "Expiry reminders sent: %d success, %d failed",
                result["success"],
                result["failed"],
            )

    except Exception as exc:
        logger.error("Failed to send expiry reminders: %s", str(exc))


@shared_task
def send_upcoming_leave_reminders():
    """Daily cron: find leaves starting in 3 days and send reminders."""
    try:
        from apps.leave.constants import LeaveRequestStatus
        from apps.leave.models.leave_request import LeaveRequest
        from apps.leave.services.notification_service import LeaveNotificationService

        today = timezone.now().date()
        target_date = today + timedelta(days=3)

        upcoming = LeaveRequest.objects.filter(
            start_date=target_date,
            status=LeaveRequestStatus.APPROVED,
            is_deleted=False,
        ).select_related("employee__user", "leave_type")

        service = LeaveNotificationService()
        targets = [(lr, 3) for lr in upcoming]

        if targets:
            result = service.send_bulk_upcoming_reminders(targets)
            logger.info(
                "Upcoming reminders sent: %d success, %d failed",
                result["success"],
                result["failed"],
            )

    except Exception as exc:
        logger.error("Failed to send upcoming reminders: %s", str(exc))
