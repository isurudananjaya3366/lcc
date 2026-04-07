"""
PO Email Service.

Handles sending purchase order emails to vendors, including
PO delivery, acknowledgment reminders, and delivery reminders.
"""

import logging

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from apps.purchases.constants import PO_STATUS_SENT

logger = logging.getLogger(__name__)


class POEmailService:
    """Service for sending PO-related emails."""

    @classmethod
    def send_po_email(cls, po_id, recipient_email, cc=None):
        """
        Send PO PDF to the vendor via email.

        Updates PO status to SENT and logs to POHistory.

        Args:
            po_id: UUID of the PurchaseOrder.
            recipient_email: Vendor email address.
            cc: Optional list of CC email addresses.

        Returns:
            bool: True if sent successfully.
        """
        from apps.purchases.models.purchase_order import PurchaseOrder
        from apps.purchases.models.po_history import POHistory
        from apps.purchases.services.pdf_generator import POPDFGenerator
        from apps.purchases.constants import CHANGE_TYPE_SENT

        po = PurchaseOrder.objects.select_related("vendor").get(pk=po_id)
        pdf_content = POPDFGenerator.generate_pdf(po)

        subject = f"Purchase Order {po.po_number}"
        context = {
            "po": po,
            "vendor": po.vendor,
        }

        # Try HTML template, fall back to plain text
        text_body = (
            f"Dear {po.vendor.company_name},\n\n"
            f"Please find attached Purchase Order {po.po_number} "
            f"dated {po.order_date}.\n\n"
            f"Total: {po.currency} {po.total}\n\n"
            f"Please acknowledge receipt of this order.\n\n"
            f"Regards"
        )
        html_body = cls._render_template("purchases/emails/po_send.html", context)

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            to=[recipient_email],
            cc=cc or [],
        )
        if html_body:
            email.attach_alternative(html_body, "text/html")

        email.attach(
            f"{po.po_number}.pdf",
            pdf_content,
            "application/pdf",
        )

        sent = bool(email.send())
        if sent:
            # Update PO status to SENT
            po.status = PO_STATUS_SENT
            po.save(update_fields=["status", "updated_on"])

            # Log to history
            POHistory.objects.create(
                purchase_order=po,
                change_type=CHANGE_TYPE_SENT,
                changed_by=po.created_by,
                description=f"PO emailed to {recipient_email}",
            )
            logger.info("PO %s sent to %s", po.po_number, recipient_email)

        return sent

    @classmethod
    def send_acknowledgment_reminder(cls, po_id, recipient_email):
        """
        Send an acknowledgment reminder for an unacknowledged PO.

        Args:
            po_id: UUID of the PurchaseOrder.
            recipient_email: Vendor email address.

        Returns:
            bool: True if sent successfully.
        """
        from apps.purchases.models.purchase_order import PurchaseOrder

        po = PurchaseOrder.objects.select_related("vendor").get(pk=po_id)
        subject = f"Reminder: Please acknowledge PO {po.po_number}"

        text_body = (
            f"Dear {po.vendor.company_name},\n\n"
            f"This is a reminder to acknowledge receipt of "
            f"Purchase Order {po.po_number} dated {po.order_date}.\n\n"
            f"Total: {po.currency} {po.total}\n\n"
            f"Please acknowledge at your earliest convenience.\n\n"
            f"Regards"
        )
        context = {"po": po, "vendor": po.vendor}
        html_body = cls._render_template(
            "purchases/emails/acknowledgment_reminder.html", context
        )

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            to=[recipient_email],
        )
        if html_body:
            email.attach_alternative(html_body, "text/html")

        sent = bool(email.send())
        if sent:
            logger.info(
                "Acknowledgment reminder sent for PO %s to %s",
                po.po_number,
                recipient_email,
            )
        return sent

    @classmethod
    def send_delivery_reminder(cls, po_id, recipient_email):
        """
        Send a delivery reminder for an overdue PO.

        Args:
            po_id: UUID of the PurchaseOrder.
            recipient_email: Vendor email address.

        Returns:
            bool: True if sent successfully.
        """
        from apps.purchases.models.purchase_order import PurchaseOrder

        po = PurchaseOrder.objects.select_related("vendor").get(pk=po_id)
        subject = f"Delivery Reminder: PO {po.po_number} - Expected {po.expected_delivery_date}"

        text_body = (
            f"Dear {po.vendor.company_name},\n\n"
            f"This is a reminder that Purchase Order {po.po_number} "
            f"was expected for delivery on {po.expected_delivery_date}.\n\n"
            f"Please provide an updated delivery schedule.\n\n"
            f"Regards"
        )
        context = {"po": po, "vendor": po.vendor}
        html_body = cls._render_template(
            "purchases/emails/delivery_reminder.html", context
        )

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            to=[recipient_email],
        )
        if html_body:
            email.attach_alternative(html_body, "text/html")

        sent = bool(email.send())
        if sent:
            logger.info(
                "Delivery reminder sent for PO %s to %s",
                po.po_number,
                recipient_email,
            )
        return sent

    @classmethod
    def _render_template(cls, template_name, context):
        """
        Safely render an HTML email template.

        Returns None if template doesn't exist.
        """
        try:
            return render_to_string(template_name, context)
        except Exception:
            return None
