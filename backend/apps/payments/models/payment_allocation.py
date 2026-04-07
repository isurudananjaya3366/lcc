"""
Payment allocation model.

Tracks the allocation of a single payment across one or more invoices.
Supports partial and split payment scenarios.
"""

from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin


class PaymentAllocation(UUIDMixin, TimestampMixin, models.Model):
    """
    Tracks allocation of payment amounts to specific invoices.

    A single payment may be split across multiple invoices,
    and each allocation records how much was applied to which invoice.
    """

    payment = models.ForeignKey(
        "payments.Payment",
        on_delete=models.CASCADE,
        related_name="allocations",
        verbose_name="Payment",
        help_text="The payment being allocated.",
    )
    invoice = models.ForeignKey(
        "invoices.Invoice",
        on_delete=models.PROTECT,
        related_name="payment_allocations",
        verbose_name="Invoice",
        help_text="The invoice receiving the allocation.",
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Allocated Amount",
        help_text="Amount allocated from this payment to this invoice.",
    )
    notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Notes",
        help_text="Notes about this allocation.",
    )

    class Meta:
        db_table = "payments_paymentallocation"
        ordering = ["-created_on"]
        verbose_name = "Payment Allocation"
        verbose_name_plural = "Payment Allocations"
        unique_together = [("payment", "invoice")]
        indexes = [
            models.Index(
                fields=["invoice"],
                name="idx_payalloc_invoice",
            ),
            models.Index(
                fields=["invoice", "created_on"],
                name="idx_payalloc_invoice_date",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount__gt=0),
                name="payalloc_amount_positive",
            ),
        ]

    def __str__(self):
        return f"{self.payment_id} → {self.invoice_id}: {self.amount}"
