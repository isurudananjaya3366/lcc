"""
Payment sequence model.

Tracks yearly payment number sequences for thread-safe
number generation per tenant.
"""

from django.db import models


class PaymentSequence(models.Model):
    """Tracks the yearly payment number sequence per tenant."""

    year = models.IntegerField(
        verbose_name="Year",
        help_text="Year for this sequence.",
    )
    last_number = models.IntegerField(
        default=0,
        verbose_name="Last Number",
        help_text="Last used sequence number for this year.",
    )

    class Meta:
        app_label = "payments"
        db_table = "payments_paymentsequence"
        unique_together = [("year",)]
        verbose_name = "Payment Sequence"
        verbose_name_plural = "Payment Sequences"

    def __str__(self):
        return f"PaymentSequence({self.year}: {self.last_number})"
