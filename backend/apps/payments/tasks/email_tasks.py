"""Celery tasks for payment email notifications."""

import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def send_payment_confirmation_task(self, payment_id):
    """Send payment confirmation email asynchronously."""
    try:
        from apps.payments.models import Payment
        from apps.payments.services.email_service import PaymentEmailService

        payment = Payment.objects.select_related("customer", "invoice").get(
            id=payment_id
        )
        result = PaymentEmailService.send_payment_confirmation(payment)
        if not result["success"]:
            logger.warning(
                "Payment confirmation email failed for %s: %s",
                payment_id,
                result.get("error"),
            )
        return result
    except Exception as exc:
        logger.exception("Error sending payment confirmation for %s", payment_id)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def send_receipt_email_task(self, receipt_id):
    """Send receipt email with PDF attachment asynchronously."""
    try:
        from apps.payments.models import PaymentReceipt
        from apps.payments.services.email_service import PaymentEmailService
        from apps.payments.services.receipt_pdf_service import ReceiptPDFService

        receipt = PaymentReceipt.objects.select_related(
            "payment", "customer"
        ).get(id=receipt_id)

        # Ensure PDF is generated
        if not receipt.has_pdf():
            ReceiptPDFService.generate_receipt_pdf(receipt)
            receipt.refresh_from_db()

        result = PaymentEmailService.send_receipt_email(receipt)
        if not result["success"]:
            logger.warning(
                "Receipt email failed for %s: %s",
                receipt_id,
                result.get("error"),
            )
        return result
    except Exception as exc:
        logger.exception("Error sending receipt email for %s", receipt_id)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def send_refund_notification_task(self, refund_id):
    """Send refund notification email asynchronously."""
    try:
        from apps.payments.models import Refund
        from apps.payments.services.email_service import PaymentEmailService

        refund = Refund.objects.select_related(
            "original_payment", "original_payment__customer"
        ).get(id=refund_id)
        result = PaymentEmailService.send_refund_notification(refund)
        if not result["success"]:
            logger.warning(
                "Refund notification email failed for %s: %s",
                refund_id,
                result.get("error"),
            )
        return result
    except Exception as exc:
        logger.exception("Error sending refund notification for %s", refund_id)
        raise self.retry(exc=exc)


@shared_task
def send_payment_reminder_task(invoice_id, days_overdue=0):
    """Send payment reminder for a specific invoice."""
    try:
        from apps.invoices.models import Invoice
        from apps.payments.services.email_service import PaymentEmailService

        invoice = Invoice.objects.select_related("customer").get(id=invoice_id)
        result = PaymentEmailService.send_payment_reminder(invoice, days_overdue)
        if not result["success"]:
            logger.warning(
                "Payment reminder failed for invoice %s: %s",
                invoice_id,
                result.get("error"),
            )
        return result
    except Exception as exc:
        logger.exception("Error sending payment reminder for invoice %s", invoice_id)
        return {"success": False, "error": str(exc)}


@shared_task
def send_bulk_payment_reminders():
    """
    Daily scheduled task: find overdue invoices and send reminders.
    Runs at 9:00 AM via Celery Beat.
    """
    try:
        from apps.invoices.models import Invoice

        today = timezone.now().date()

        overdue_invoices = Invoice.objects.filter(
            status__in=["UNPAID", "PARTIAL", "OVERDUE"],
            due_date__lt=today,
        ).select_related("customer")

        sent_count = 0
        for invoice in overdue_invoices:
            days_overdue = (today - invoice.due_date).days
            send_payment_reminder_task.delay(str(invoice.id), days_overdue)
            sent_count += 1

        logger.info("Queued %d payment reminder emails.", sent_count)
        return {"queued": sent_count}
    except Exception:
        logger.exception("Error in bulk payment reminders.")
        return {"queued": 0}
