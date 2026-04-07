"""
POHistory model for the purchases application.

Tracks all changes to purchase orders for audit trail purposes.
"""

from django.conf import settings
from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin
from apps.purchases.constants import CHANGE_TYPE_CHOICES, CHANGE_TYPE_CREATED


class POHistory(UUIDMixin, TimestampMixin, models.Model):
    """Audit log entry for purchase order changes."""

    purchase_order = models.ForeignKey(
        "purchases.PurchaseOrder",
        on_delete=models.CASCADE,
        related_name="history_entries",
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="po_history_entries",
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
        help_text="Snapshot of PO state at time of change for audit.",
    )

    class Meta:
        verbose_name = "PO History"
        verbose_name_plural = "PO History Entries"
        ordering = ["-created_on"]
        indexes = [
            models.Index(fields=["purchase_order"], name="idx_poh_po"),
            models.Index(fields=["created_on"], name="idx_poh_changed_at"),
        ]

    def __str__(self):
        return f"{self.purchase_order} - {self.get_change_type_display()}"
