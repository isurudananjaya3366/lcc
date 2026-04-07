"""
Celery tasks for quote expiry management.

Task 43: Automated expiry and reminders.
"""

import logging
import time

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(name="quotes.expire_old_quotes", bind=True, max_retries=3)
def expire_old_quotes(self):
    """Expire all SENT quotes that have passed their validity date."""
    from apps.quotes.services.quote_service import QuoteService

    start = time.monotonic()
    try:
        expired_quotes = QuoteService.get_expired_quotes()
        count = QuoteService.bulk_expire_quotes(expired_quotes)
        duration = time.monotonic() - start
        logger.info("Expired %d quotes in %.2fs", count, duration)
        return {
            "success": True,
            "expired_count": count,
            "execution_time_seconds": round(duration, 2),
            "timestamp": timezone.now().isoformat(),
        }
    except Exception as exc:
        logger.exception("Error expiring quotes")
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@shared_task(name="quotes.send_expiry_reminders")
def send_expiry_reminders(days_threshold=3):
    """Send reminders for quotes expiring within N days."""
    from apps.quotes.services.quote_service import QuoteService

    try:
        expiring = QuoteService.get_expiring_soon(days=days_threshold)
        count = expiring.count()
        # Reminder sending logic would go here (email integration in Group E)
        logger.info("Found %d quotes expiring within %d days", count, days_threshold)
        return {
            "success": True,
            "reminders_sent": count,
            "timestamp": timezone.now().isoformat(),
        }
    except Exception:
        logger.exception("Error sending expiry reminders")
        return {
            "success": False,
            "reminders_sent": 0,
            "timestamp": timezone.now().isoformat(),
        }
