"""
Payment history model.

Maintains a complete audit trail of all payment status changes,
modifications, and significant events for compliance and dispute resolution.
"""

from django.conf import settings
from django.db import models

from apps.core.mixins import UUIDMixin


class PaymentHistoryAction(models.TextChoices):
    """Payment history action types."""

    CREATED = "CREATED", "Payment Created"
    STATUS_CHANGE = "STATUS_CHANGE", "Status Changed"
    AMOUNT_MODIFIED = "AMOUNT_MODIFIED", "Amount Modified"
    APPROVED = "APPROVED", "Payment Approved"
    REJECTED = "REJECTED", "Payment Rejected"
    ALLOCATED = "ALLOCATED", "Allocated to Invoice"
    REFUNDED = "REFUNDED", "Payment Refunded"
    NOTE_ADDED = "NOTE_ADDED", "Note Added"
    METHOD_MODIFIED = "METHOD_MODIFIED", "Payment Method Modified"
    CUSTOMER_CHANGED = "CUSTOMER_CHANGED", "Customer Changed"


class PaymentHistory(UUIDMixin, models.Model):
    """
    Payment history tracking model.

    Records all changes and significant events for payments,
    providing a complete audit trail for compliance and disputes.
    """

    payment = models.ForeignKey(
        "payments.Payment",
        on_delete=models.CASCADE,
        related_name="history",
        verbose_name="Payment",
        help_text="Payment this history entry relates to.",
    )
    action = models.CharField(
        max_length=50,
        choices=PaymentHistoryAction.choices,
        verbose_name="Action",
        help_text="Type of action/change.",
    )
    old_value = models.JSONField(
        blank=True,
        null=True,
        default=None,
        verbose_name="Old Value",
        help_text="Previous value before change (JSON).",
    )
    new_value = models.JSONField(
        blank=True,
        null=True,
        default=None,
        verbose_name="New Value",
        help_text="New value after change (JSON).",
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payment_changes",
        verbose_name="Changed By",
        help_text="User who made the change.",
    )
    changed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Changed At",
        help_text="When the change occurred.",
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name="Description",
        help_text="Human-readable description of the change.",
    )
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name="IP Address",
        help_text="IP address of user (for security audit).",
    )

    class Meta:
        db_table = "payments_paymenthistory"
        ordering = ["-changed_at"]
        verbose_name = "Payment History"
        verbose_name_plural = "Payment Histories"
        indexes = [
            models.Index(
                fields=["payment", "-changed_at"],
                name="idx_payhistory_payment_date",
            ),
            models.Index(
                fields=["action", "-changed_at"],
                name="idx_payhistory_action_date",
            ),
        ]

    def __str__(self):
        return f"{self.payment_id} - {self.action} at {self.changed_at}"

    def get_change_summary(self):
        """Return a human-readable summary of the change."""
        if self.action == PaymentHistoryAction.STATUS_CHANGE:
            old_status = self.old_value.get("status") if self.old_value else "N/A"
            new_status = self.new_value.get("status") if self.new_value else "N/A"
            return f"Status changed from {old_status} to {new_status}"
        if self.action == PaymentHistoryAction.ALLOCATED:
            inv = self.new_value.get("invoice_number") if self.new_value else "N/A"
            amt = self.new_value.get("allocated_amount") if self.new_value else "0"
            return f"Allocated Rs. {amt} to Invoice {inv}"
        return self.description or f"{self.action} performed"
