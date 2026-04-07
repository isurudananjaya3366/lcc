"""
Invoice history model — tracks all changes to invoices.
"""

from django.conf import settings
from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin


class InvoiceHistory(UUIDMixin, TimestampMixin, models.Model):
    """Tracks actions and status changes on invoices."""

    invoice = models.ForeignKey(
        "invoices.Invoice",
        on_delete=models.CASCADE,
        related_name="history",
    )
    action = models.CharField(max_length=50, db_index=True)
    old_status = models.CharField(max_length=20, blank=True, default="")
    new_status = models.CharField(max_length=20, blank=True, default="")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    notes = models.TextField(blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_on"]
        verbose_name = "Invoice History"
        verbose_name_plural = "Invoice History"
        indexes = [
            models.Index(fields=["invoice"], name="invhistory_invoice_idx"),
            models.Index(fields=["action"], name="invhistory_action_idx"),
            models.Index(fields=["created_on"], name="invhistory_created_idx"),
        ]

    def __str__(self):
        return f"{self.invoice_id} — {self.action} at {self.created_on}"
