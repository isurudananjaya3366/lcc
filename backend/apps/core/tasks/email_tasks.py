"""
LankaCommerce Cloud - Email Celery Tasks.

Asynchronous email sending with automatic retry on transient SMTP errors.
All tasks are tenant-aware — they activate the correct schema before
accessing any tenant-scoped data (e.g. email templates, contact records).
"""

import logging
from smtplib import SMTPException

from celery import shared_task
from django.core.mail import send_mail, send_mass_mail

from apps.core.tasks.base import TenantAwareTask

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    base=TenantAwareTask,
    name="apps.core.tasks.email_tasks.send_email_task",
    max_retries=3,
    retry_backoff=True,
    retry_jitter=True,
)
def send_email_task(
    self,
    *,
    tenant_id: int,
    subject: str,
    message: str,
    from_email: str | None = None,
    recipient_list: list[str],
    html_message: str | None = None,
):
    """Send a single email asynchronously.

    Args:
        tenant_id: PK of the target :class:`~apps.tenants.models.Tenant`.
        subject: Email subject line.
        message: Plain-text body.
        from_email: Sender address (``None`` → Django DEFAULT_FROM_EMAIL).
        recipient_list: List of recipient email addresses.
        html_message: Optional HTML body.
    """
    try:
        logger.info(
            "Sending email to %s (subject='%s')", recipient_list, subject
        )
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False,
        )
        logger.info("Email sent successfully to %s", recipient_list)
    except SMTPException as exc:
        logger.warning("SMTP error sending email: %s — retrying", exc)
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    base=TenantAwareTask,
    name="apps.core.tasks.email_tasks.send_bulk_email_task",
    max_retries=3,
    retry_backoff=True,
    retry_jitter=True,
)
def send_bulk_email_task(
    self,
    *,
    tenant_id: int,
    messages: list[tuple[str, str, str, list[str]]],
):
    """Send multiple emails in a single connection.

    Args:
        tenant_id: PK of the target :class:`~apps.tenants.models.Tenant`.
        messages: Iterable of ``(subject, message, from_email, recipient_list)`` tuples
                  compatible with :func:`django.core.mail.send_mass_mail`.
    """
    try:
        count = len(messages)
        logger.info("Sending bulk email batch of %d messages", count)
        send_mass_mail(
            datatuple=tuple(messages),
            fail_silently=False,
        )
        logger.info("Bulk email batch of %d messages sent successfully", count)
    except SMTPException as exc:
        logger.warning("SMTP error in bulk email: %s — retrying", exc)
        raise self.retry(exc=exc)
