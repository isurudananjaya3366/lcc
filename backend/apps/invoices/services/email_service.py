"""
Invoice email service.
"""

import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


class InvoiceEmailService:
    """Sends invoice-related emails with PDF attachments."""

    @classmethod
    def send_invoice_email(cls, invoice_id):
        """Send an invoice PDF to the customer."""
        from apps.invoices.models import Invoice
        from apps.invoices.services.pdf_generator import InvoicePDFGenerator

        invoice = Invoice.objects.get(id=invoice_id)

        if not invoice.customer_email:
            logger.warning("No customer email for invoice %s", invoice.invoice_number)
            return False

        # Generate PDF if not present
        if not invoice.pdf_file:
            InvoicePDFGenerator.generate_pdf(invoice_id)
            invoice.refresh_from_db()

        subject = f"Invoice {invoice.invoice_number} from {invoice.business_name}"
        html_body = render_to_string("invoices/email/invoice_email.html", {
            "invoice": invoice,
        })

        email = EmailMessage(
            subject=subject,
            body=html_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[invoice.customer_email],
        )
        email.content_subtype = "html"

        if invoice.pdf_file:
            invoice.pdf_file.seek(0)
            email.attach(
                f"{invoice.invoice_number}.pdf",
                invoice.pdf_file.read(),
                "application/pdf",
            )

        try:
            email.send(fail_silently=False)
        except Exception:
            logger.exception("Failed to send invoice email for %s", invoice.invoice_number)
            return False

        # Update sent_date on the invoice
        from django.utils import timezone
        invoice.sent_date = timezone.now().date()
        invoice.save(update_fields=["sent_date"])

        logger.info("Invoice email sent for %s", invoice.invoice_number)
        return True

    @classmethod
    def send_reminder_email(cls, invoice_id):
        """Send a payment reminder email."""
        from apps.invoices.models import Invoice

        invoice = Invoice.objects.get(id=invoice_id)
        if not invoice.customer_email:
            return False

        subject = f"Payment Reminder: Invoice {invoice.invoice_number}"
        html_body = render_to_string("invoices/email/reminder_email.html", {
            "invoice": invoice,
        })

        email = EmailMessage(
            subject=subject,
            body=html_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[invoice.customer_email],
        )
        email.content_subtype = "html"

        try:
            email.send(fail_silently=False)
        except Exception:
            logger.exception("Failed to send reminder email for %s", invoice.invoice_number)
            return False

        logger.info("Reminder sent for %s", invoice.invoice_number)
        return True

    @classmethod
    def send_overdue_email(cls, invoice_id):
        """Send an overdue notification email."""
        from apps.invoices.models import Invoice

        invoice = Invoice.objects.get(id=invoice_id)
        if not invoice.customer_email:
            return False

        subject = f"Overdue Notice: Invoice {invoice.invoice_number}"
        html_body = render_to_string("invoices/email/overdue_email.html", {
            "invoice": invoice,
        })

        email = EmailMessage(
            subject=subject,
            body=html_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[invoice.customer_email],
        )
        email.content_subtype = "html"

        try:
            email.send(fail_silently=False)
        except Exception:
            logger.exception("Failed to send overdue email for %s", invoice.invoice_number)
            return False

        logger.info("Overdue notice sent for %s", invoice.invoice_number)
        return True
