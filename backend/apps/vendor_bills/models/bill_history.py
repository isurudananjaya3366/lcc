"""BillHistory model for the vendor_bills application.

Tracks all changes to vendor bills for audit trail purposes.
"""

from django.conf import settings
from django.db import models

from apps.core.mixins import TimestampMixin, UUIDMixin
from apps.vendor_bills.constants import CHANGE_TYPE_CHOICES, CHANGE_TYPE_CREATED


class BillHistory(UUIDMixin, TimestampMixin, models.Model):
    """Audit log entry for vendor bill changes."""

    vendor_bill = models.ForeignKey(
        "vendor_bills.VendorBill",
        on_delete=models.CASCADE,
        related_name="history_entries",
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bill_history_entries",
    )
    change_type = models.CharField(
        max_length=20,
        choices=CHANGE_TYPE_CHOICES,
        default=CHANGE_TYPE_CREATED,
    )
    old_status = models.CharField(max_length=20, blank=True, default="")
    new_status = models.CharField(max_length=20, blank=True, default="")
    description = models.TextField(blank=True, default="")
    changes = models.JSONField(default=dict, blank=True)
    data_snapshot = models.JSONField(
        default=dict,
        blank=True,
        help_text="Snapshot of bill state at time of change for audit.",
    )

    class Meta:
        verbose_name = "Bill History"
        verbose_name_plural = "Bill History Entries"
        ordering = ["-created_on"]
        indexes = [
            models.Index(fields=["vendor_bill"], name="idx_bh_vendor_bill"),
            models.Index(fields=["created_on"], name="idx_bh_changed_at"),
        ]

    def __str__(self):
        return f"{self.vendor_bill} - {self.get_change_type_display()}"
