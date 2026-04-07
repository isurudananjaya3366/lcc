"""
Payments constants module.

Defines choices, status values, transition rules, and other constants
used across the payments application models.
"""

from django.db import models


class PaymentMethod(models.TextChoices):
    """Supported payment methods."""

    CASH = "CASH", "Cash"
    CARD = "CARD", "Card"
    BANK_TRANSFER = "BANK_TRANSFER", "Bank Transfer"
    MOBILE = "MOBILE", "Mobile Payment"
    CHECK = "CHECK", "Check"
    STORE_CREDIT = "STORE_CREDIT", "Store Credit"


class PaymentStatus(models.TextChoices):
    """
    Payment lifecycle statuses.

    Lifecycle:
        PENDING → COMPLETED (terminal)
        PENDING → FAILED → PENDING (retry)
        PENDING → CANCELLED (terminal)
        COMPLETED → REFUNDED (terminal)
    """

    PENDING = "PENDING", "Pending"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"
    CANCELLED = "CANCELLED", "Cancelled"
    REFUNDED = "REFUNDED", "Refunded"


# Status transition rules
ALLOWED_TRANSITIONS = {
    PaymentStatus.PENDING: [
        PaymentStatus.COMPLETED,
        PaymentStatus.FAILED,
        PaymentStatus.CANCELLED,
    ],
    PaymentStatus.COMPLETED: [PaymentStatus.REFUNDED],
    PaymentStatus.FAILED: [PaymentStatus.PENDING],
    PaymentStatus.CANCELLED: [],
    PaymentStatus.REFUNDED: [],
}

TERMINAL_STATES = {PaymentStatus.CANCELLED, PaymentStatus.REFUNDED}

# Payment number prefix
PAYMENT_NUMBER_PREFIX = "PAY"
