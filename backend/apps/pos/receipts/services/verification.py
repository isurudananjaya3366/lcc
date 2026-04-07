"""
Receipt verification service.

Task 65: Hash-based receipt verification for authenticity checks.
"""

import hashlib
import hmac
import logging
import secrets

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class ReceiptVerificationService:
    """
    Generates and verifies HMAC-based receipt integrity hashes.
    """

    @staticmethod
    def _get_secret() -> bytes:
        secret = getattr(settings, "RECEIPT_VERIFICATION_SECRET", settings.SECRET_KEY)
        return secret.encode("utf-8") if isinstance(secret, str) else secret

    @classmethod
    def generate_hash(cls, receipt) -> str:
        """Generate a 64-char HMAC-SHA256 hash for a receipt."""
        message = (
            f"{receipt.id}:{receipt.receipt_number}:"
            f"{receipt.cart_id}:{receipt.generated_at.isoformat()}"
        )
        return hmac.new(
            cls._get_secret(),
            message.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    @classmethod
    def generate_token(cls, receipt) -> str:
        """Generate a short 16-char verification token."""
        full_hash = cls.generate_hash(receipt)
        return full_hash[:16]

    @classmethod
    def verify(cls, receipt, provided_token: str) -> bool:
        """
        Verify a receipt token using constant-time comparison.
        """
        expected = cls.generate_token(receipt)
        return hmac.compare_digest(expected, provided_token)

    @classmethod
    def generate_verification_url(cls, receipt, base_url: str | None = None) -> str:
        """Build a public verification URL for a receipt."""
        token = cls.generate_token(receipt)
        base = base_url or getattr(settings, "RECEIPT_VERIFY_BASE_URL", "")
        return f"{base}/receipt/{receipt.id}?token={token}"
