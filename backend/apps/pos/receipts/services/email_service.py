"""
Email receipt service.

Tasks 60-64: Email template rendering, styling, email sending,
PDF attachment, and receipt lookup support.
"""

import logging
import os

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


class ReceiptEmailService:
    """
    Sends receipt emails with optional PDF attachment.
    """

    def __init__(self, receipt=None, receipt_data: dict | None = None):
        self.receipt = receipt
        self.data = receipt_data or (receipt.receipt_data if receipt else {})

    # ── Validation ────────────────────────────────────────

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate an email address using Django's validator."""
        from django.core.validators import validate_email as django_validate

        try:
            django_validate(email)
            return True
        except Exception:
            return False

    # ── Public API ────────────────────────────────────────

    def send_email(
        self,
        recipient_email: str,
        custom_message: str | None = None,
        attach_pdf: bool = True,
        cc_emails: list[str] | None = None,
        subject: str | None = None,
    ) -> bool:
        """
        Send an email receipt.

        Returns True if the email was sent successfully.
        """
        biz_name = self.data.get("header", {}).get("business_name", "Business")

        email_subject = subject or f"Your Receipt from {biz_name}"
        context = self._build_email_context(custom_message)

        html_body = render_to_string(
            "receipts/email/receipt_email.html", context
        )
        text_body = render_to_string(
            "receipts/email/receipt_email.txt", context
        )

        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com")

        msg = EmailMultiAlternatives(
            subject=email_subject,
            body=text_body,
            from_email=from_email,
            to=[recipient_email],
            cc=cc_emails or [],
        )
        msg.attach_alternative(html_body, "text/html")

        # PDF attachment
        if attach_pdf:
            self._attach_pdf(msg)

        try:
            msg.send()
            logger.info(
                "Email receipt sent to %s (receipt=%s)",
                recipient_email,
                self.data.get("transaction", {}).get("receipt_number", "?"),
            )

            # Update receipt timestamps
            if self.receipt and hasattr(self.receipt, "mark_as_emailed"):
                self.receipt.mark_as_emailed()

            return True
        except Exception:
            logger.exception("Failed to send receipt email to %s", recipient_email)
            return False

    # ── Context building ──────────────────────────────────

    def _build_email_context(self, custom_message: str | None = None) -> dict:
        ctx = {
            "header": self.data.get("header", {}),
            "transaction": self.data.get("transaction", {}),
            "items": self.data.get("items", []),
            "totals": self.data.get("totals", {}),
            "payments": self.data.get("payments", {}),
            "footer": self.data.get("footer", {}),
            "qr_code": self.data.get("qr_code", {}),
            "is_duplicate": self.data.get("is_duplicate", False),
            "custom_message": custom_message,
            "primary_color": "#2c3e50",
            "accent_color": "#3498db",
            "logo_url": None,
        }
        return ctx

    # ── PDF attachment ────────────────────────────────────

    def _attach_pdf(self, msg: EmailMultiAlternatives):
        """Generate and attach PDF to email message."""
        try:
            from apps.pos.receipts.services.pdf_generator import PDFGeneratorService

            generator = PDFGeneratorService(
                receipt=self.receipt,
                receipt_data=self.data,
            )
            pdf_bytes = generator.generate_pdf()

            biz_name = self.data.get("header", {}).get(
                "business_name", "Receipt"
            ).replace(" ", "_")
            receipt_num = self.data.get("transaction", {}).get(
                "receipt_number", "receipt"
            )
            filename = f"{biz_name}_Receipt_{receipt_num}.pdf"

            msg.attach(filename, pdf_bytes, "application/pdf")
        except Exception:
            logger.warning("PDF attachment failed — sending without PDF", exc_info=True)
