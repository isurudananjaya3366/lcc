"""
Payment model for the sales application.

Defines the Payment model which records individual payment
transactions against invoices. Supports partial payments —
multiple Payment records can be linked to a single Invoice.
All monetary values are stored in LKR (₨).
"""

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from apps.core.mixins import UUIDMixin, TimestampMixin
from apps.sales.constants import (
    DEFAULT_PAYMENT_METHOD,
    PAYMENT_METHOD_CHOICES,
)

# Price field constants (consistent across all apps)
PRICE_MAX_DIGITS = 10
PRICE_DECIMAL_PLACES = 2


class Payment(UUIDMixin, TimestampMixin, models.Model):
    """
    Payment transaction against an invoice.

    Records individual payments received for an invoice. An invoice
    can have multiple payments (partial payment support). Each payment
    captures the method, amount, date, and optional reference number.
    All monetary values are in LKR (₨).

    Fields:
        invoice: FK to the Invoice being paid.
        payment_method: Method of payment (cash, card, etc.).
        amount: Payment amount in LKR.
        payment_date: Date and time the payment was received.
        reference_number: Optional transaction/cheque reference.
        notes: Optional notes about this payment.
        received_by: User who recorded the payment.
    """

    # ── Invoice FK ──────────────────────────────────────────────────
    invoice = models.ForeignKey(
        "sales.Invoice",
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Invoice",
        help_text="The invoice this payment is applied to.",
    )

    # ── Payment Method ──────────────────────────────────────────────
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default=DEFAULT_PAYMENT_METHOD,
        db_index=True,
        verbose_name="Payment Method",
        help_text="Method of payment (cash, card, bank transfer, cheque, mobile).",
    )

    # ── Amount (LKR) ────────────────────────────────────────────────
    amount = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS,
        decimal_places=PRICE_DECIMAL_PLACES,
        validators=[MinValueValidator(0.01)],
        verbose_name="Amount (LKR)",
        help_text="Payment amount in LKR (₨). Must be greater than zero.",
    )

    # ── Payment Date ────────────────────────────────────────────────
    payment_date = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Payment Date",
        help_text="Date and time the payment was received.",
    )

    # ── Reference ───────────────────────────────────────────────────
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Reference Number",
        help_text=(
            "Transaction or cheque reference number. "
            "Optional for cash payments."
        ),
    )

    # ── Notes & Audit ───────────────────────────────────────────────
    notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Notes",
        help_text="Optional notes about this payment.",
    )
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="received_payments",
        verbose_name="Received By",
        help_text="The user who recorded this payment.",
    )

    class Meta:
        db_table = "sales_payment"
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ["-payment_date"]
        indexes = [
            models.Index(
                fields=["invoice", "payment_method"],
                name="idx_payment_invoice_method",
            ),
            models.Index(
                fields=["-payment_date"],
                name="idx_payment_date_desc",
            ),
        ]

    def __str__(self):
        return (
            f"Payment {self.amount} LKR via "
            f"{self.get_payment_method_display()} — {self.invoice}"
        )

    @property
    def is_cash(self):
        """Return True if this is a cash payment."""
        return self.payment_method == "cash"

    @property
    def is_card(self):
        """Return True if this is a card payment."""
        return self.payment_method == "card"
