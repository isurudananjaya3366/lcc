"""Payment email notification service."""

import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


class PaymentEmailService:
    """Service for sending payment-related email notifications."""

    @staticmethod
    def send_payment_confirmation(payment):
        """
        Send payment confirmation email to customer.

        Args:
            payment: Payment instance.

        Returns:
            dict with 'success' bool and optional 'error'.
        """
        if not payment.customer:
            return {"success": False, "error": "No customer associated with payment."}

        email = getattr(payment.customer, "email", None)
        if not email:
            return {"success": False, "error": "Customer has no email address."}

        context = {
            "payment": payment,
            "customer": payment.customer,
            "invoice": payment.invoice,
        }

        return PaymentEmailService._send_email(
            subject=f"Payment Confirmation - {payment.payment_number}",
            template="emails/payments/payment_confirmation.html",
            context=context,
            to_email=email,
        )

    @staticmethod
    def send_receipt_email(receipt):
        """
        Send receipt email with PDF attachment.

        Args:
            receipt: PaymentReceipt instance.

        Returns:
            dict with 'success' bool and optional 'error'.
        """
        if not receipt.customer:
            return {"success": False, "error": "No customer on receipt."}

        email = getattr(receipt.customer, "email", None)
        if not email:
            return {"success": False, "error": "Customer has no email address."}

        context = {
            "receipt": receipt,
            "payment": receipt.payment,
            "customer": receipt.customer,
        }

        attachments = []
        if receipt.has_pdf() and receipt.pdf_file:
            try:
                receipt.pdf_file.open("rb")
                pdf_content = receipt.pdf_file.read()
                receipt.pdf_file.close()
                attachments.append(
                    (f"{receipt.receipt_number}.pdf", pdf_content, "application/pdf")
                )
            except Exception:
                logger.exception("Failed to read receipt PDF for attachment.")

        result = PaymentEmailService._send_email(
            subject=f"Payment Receipt - {receipt.receipt_number}",
            template="emails/payments/receipt_delivery.html",
            context=context,
            to_email=email,
            attachments=attachments,
        )

        if result["success"]:
            receipt.mark_as_sent(sent_to=email)

        return result

    @staticmethod
    def send_refund_notification(refund):
        """
        Send refund notification email.

        Args:
            refund: Refund instance.

        Returns:
            dict with 'success' bool and optional 'error'.
        """
        payment = refund.original_payment
        if not payment.customer:
            return {"success": False, "error": "No customer on original payment."}

        email = getattr(payment.customer, "email", None)
        if not email:
            return {"success": False, "error": "Customer has no email address."}

        context = {
            "refund": refund,
            "payment": payment,
            "customer": payment.customer,
        }

        return PaymentEmailService._send_email(
            subject=f"Refund Notification - {refund.refund_number}",
            template="emails/payments/refund_notification.html",
            context=context,
            to_email=email,
        )

    @staticmethod
    def send_payment_reminder(invoice, days_overdue=0):
        """
        Send payment reminder for an outstanding invoice.

        Args:
            invoice: Invoice instance.
            days_overdue: Number of days past due.

        Returns:
            dict with 'success' bool and optional 'error'.
        """
        customer = getattr(invoice, "customer", None)
        if not customer:
            return {"success": False, "error": "No customer on invoice."}

        email = getattr(customer, "email", None)
        if not email:
            return {"success": False, "error": "Customer has no email address."}

        if days_overdue > 30:
            urgency = "URGENT"
        elif days_overdue > 7:
            urgency = "Reminder"
        else:
            urgency = "Friendly Reminder"

        context = {
            "invoice": invoice,
            "customer": customer,
            "days_overdue": days_overdue,
            "urgency": urgency,
        }

        invoice_number = getattr(invoice, "invoice_number", str(invoice))
        return PaymentEmailService._send_email(
            subject=f"{urgency}: Payment Due - {invoice_number}",
            template="emails/payments/payment_reminder.html",
            context=context,
            to_email=email,
        )

    @staticmethod
    def send_payment_failed_notification(payment, failure_reason=""):
        """
        Send payment failure notification.

        Args:
            payment: Payment instance.
            failure_reason: Reason for failure.

        Returns:
            dict with 'success' bool and optional 'error'.
        """
        if not payment.customer:
            return {"success": False, "error": "No customer on payment."}

        email = getattr(payment.customer, "email", None)
        if not email:
            return {"success": False, "error": "Customer has no email address."}

        context = {
            "payment": payment,
            "customer": payment.customer,
            "failure_reason": failure_reason,
        }

        return PaymentEmailService._send_email(
            subject=f"Payment Failed - {payment.payment_number}",
            template="emails/payments/payment_failed.html",
            context=context,
            to_email=email,
        )

    @staticmethod
    def _send_email(subject, template, context, to_email, attachments=None):
        """
        Internal method to render template and send email.

        Returns:
            dict with 'success' bool and optional 'error'.
        """
        try:
            html_content = render_to_string(template, context)
            text_content = strip_tags(html_content)

            from_email = getattr(
                settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"
            )

            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=[to_email],
            )
            msg.attach_alternative(html_content, "text/html")

            if attachments:
                for filename, content, mime_type in attachments:
                    msg.attach(filename, content, mime_type)

            msg.send()
            return {"success": True}
        except Exception as e:
            logger.exception("Failed to send payment email: %s", str(e))
            return {"success": False, "error": str(e)}
