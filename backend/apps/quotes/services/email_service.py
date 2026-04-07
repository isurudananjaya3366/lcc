"""
Quote Email Service.

Handles sending quote emails with PDF attachments to customers.
"""

import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)


class QuoteEmailService:
    """Send quote-related emails."""

    @staticmethod
    def send_quote_email(quote, to_email=None, cc=None, subject=None, message=None):
        """
        Send the quote PDF to the customer via email.

        Parameters
        ----------
        quote : Quote
            The quote to send.
        to_email : str | None
            Override recipient. Falls back to customer email.
        cc : list[str] | None
            Optional CC addresses.
        subject : str | None
            Override subject line.
        message : str | None
            Optional personal message included in the email body.
        """
        recipient = to_email or quote.customer_email_address
        if not recipient:
            raise ValueError("No email address available for this quote.")

        if not subject:
            subject = f"Quotation {quote.quote_number}"
            if quote.title:
                subject += f" — {quote.title}"

        context = {
            "quote": quote,
            "personal_message": message or "",
            "public_url": quote.get_public_url(),
        }

        text_body = render_to_string("quotes/emails/quote_email.txt", context)
        html_body = render_to_string("quotes/emails/quote_email.html", context)

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
            cc=cc or [],
        )
        email.attach_alternative(html_body, "text/html")

        # Attach PDF if available
        if quote.pdf_file:
            try:
                pdf_data = quote.pdf_file.read()
                email.attach(
                    f"{quote.quote_number}.pdf",
                    pdf_data,
                    "application/pdf",
                )
            except Exception:
                logger.warning(
                    "Could not attach PDF for %s", quote.quote_number
                )

        try:
            email.send(fail_silently=False)
        except Exception as exc:
            quote.email_last_error = str(exc)[:500]
            quote.save(update_fields=["email_last_error"])
            logger.exception("Failed to send email for %s", quote.quote_number)
            raise

        # Update tracking fields
        quote.email_sent_to = recipient
        quote.email_sent_at = timezone.now()
        quote.email_sent_count = (quote.email_sent_count or 0) + 1
        quote.email_last_error = None
        quote.save(
            update_fields=[
                "email_sent_to",
                "email_sent_at",
                "email_sent_count",
                "email_last_error",
            ]
        )

        logger.info("Quote email sent: %s → %s", quote.quote_number, recipient)
        return True

    @staticmethod
    def send_expiry_reminder(quote, to_email=None):
        """
        Send an expiry reminder email for a quote about to expire.

        Parameters
        ----------
        quote : Quote
            The quote expiring soon.
        to_email : str | None
            Override recipient. Falls back to customer email.
        """
        recipient = to_email or quote.customer_email_address
        if not recipient:
            raise ValueError("No email address available for this quote.")

        days_left = quote.days_until_expiry
        subject = f"Reminder: Quotation {quote.quote_number} expires soon"

        context = {
            "quote": quote,
            "days_until_expiry": days_left,
            "public_url": quote.get_public_url(),
        }

        text_body = render_to_string("quotes/emails/expiry_reminder.txt", context)
        html_body = render_to_string("quotes/emails/expiry_reminder.html", context)

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
        )
        email.attach_alternative(html_body, "text/html")

        try:
            email.send(fail_silently=False)
        except Exception as exc:
            logger.exception("Failed to send expiry reminder for %s", quote.quote_number)
            raise

        logger.info("Expiry reminder sent: %s → %s", quote.quote_number, recipient)
        return True
