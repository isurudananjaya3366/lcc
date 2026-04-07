"""
Celery tasks for sending quote emails asynchronously.
"""

import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, retry_backoff=True, retry_backoff_max=600)
def send_quote_email_task(self, quote_id, to_email=None, cc=None, subject=None, message=None):
    """Send a quote email asynchronously via Celery with exponential backoff."""
    try:
        from apps.quotes.models import Quote
        from apps.quotes.services.email_service import QuoteEmailService

        quote = Quote.objects.get(pk=quote_id)
        QuoteEmailService.send_quote_email(
            quote,
            to_email=to_email,
            cc=cc,
            subject=subject,
            message=message,
        )
    except Exception as exc:
        logger.exception("send_quote_email_task failed for %s", quote_id)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, retry_backoff=True, retry_backoff_max=600)
def send_expiry_reminder_task(self, quote_id, to_email=None):
    """Send an expiry reminder email for a quote about to expire."""
    try:
        from apps.quotes.models import Quote
        from apps.quotes.services.email_service import QuoteEmailService

        quote = Quote.objects.get(pk=quote_id)
        QuoteEmailService.send_expiry_reminder(quote, to_email=to_email)
    except Exception as exc:
        logger.exception("send_expiry_reminder_task failed for %s", quote_id)
        raise self.retry(exc=exc)


@shared_task
def send_expiry_reminders_task(days_before=3):
    """
    Periodic task: find quotes expiring within *days_before* days
    and send reminder emails.  Intended for Celery Beat scheduling.
    """
    from apps.quotes.models import Quote

    now = timezone.now().date()
    threshold = now + timezone.timedelta(days=days_before)

    expiring = Quote.objects.filter(
        status="SENT",
        valid_until__isnull=False,
        valid_until__lte=threshold,
        valid_until__gt=now,
    )

    sent = 0
    for quote in expiring:
        try:
            send_expiry_reminder_task.delay(str(quote.pk))
            sent += 1
        except Exception:
            logger.exception("Failed to queue expiry reminder for %s", quote.quote_number)

    logger.info("Queued %d expiry reminders (threshold=%s)", sent, threshold)
    return sent
