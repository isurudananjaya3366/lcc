"""
SMS receipt service (stub).

Task 67: SMS gateway integration for receipt delivery.
"""

import logging
import re

from django.conf import settings

logger = logging.getLogger(__name__)


class ReceiptSMSService:
    """
    Sends short SMS receipt notifications.

    This is a stub implementation. A real deployment would integrate
    with Twilio, MessageBird, or a local Sri Lankan gateway.
    """

    MAX_LENGTH = 160
    # Sri Lankan phone number patterns: +94XXXXXXXXX or 0XXXXXXXXX
    _SL_PHONE_RE = re.compile(r"^(?:\+94|0)?[0-9]{9,10}$")

    def __init__(self, receipt_data: dict | None = None):
        self.data = receipt_data or {}

    @classmethod
    def normalize_phone(cls, phone: str) -> str:
        """Normalize a Sri Lankan phone number to +94 format."""
        cleaned = re.sub(r"[\s\-()]", "", phone)
        if cleaned.startswith("0"):
            cleaned = "+94" + cleaned[1:]
        elif not cleaned.startswith("+"):
            cleaned = "+94" + cleaned
        return cleaned

    @classmethod
    def validate_phone(cls, phone: str) -> bool:
        """Validate phone number format."""
        cleaned = re.sub(r"[\s\-()]", "", phone)
        return bool(cls._SL_PHONE_RE.match(cleaned))

    def send_sms(self, phone_number: str, short_url: str | None = None) -> bool:
        """
        Send an SMS receipt notification.

        Returns True if successfully queued.
        """
        biz_name = self.data.get("header", {}).get("business_name", "Store")
        grand = self.data.get("totals", {}).get("grand_total_display", "")
        receipt_num = self.data.get("transaction", {}).get("receipt_number", "")

        url = short_url or receipt_num
        message = f"Your receipt from {biz_name}: Total {grand}. View: {url}"

        if len(message) > self.MAX_LENGTH:
            message = message[: self.MAX_LENGTH - 3] + "..."

        return self._dispatch(phone_number, message)

    @staticmethod
    def _dispatch(phone_number: str, message: str) -> bool:
        """
        Send via configured SMS gateway.

        Override or extend this method with actual gateway logic.
        """
        gateway = getattr(settings, "SMS_GATEWAY_BACKEND", None)

        if not gateway:
            logger.warning(
                "SMS gateway not configured — message to %s not sent",
                phone_number,
            )
            return False

        logger.info("SMS queued to %s (%d chars)", phone_number, len(message))
        return True
