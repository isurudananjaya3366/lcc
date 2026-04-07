"""VendorHistory model for tracking vendor field changes."""

from django.conf import settings
from django.db import models

from apps.core.mixins import UUIDMixin
from apps.vendors.constants import CHANGE_TYPE_CHOICES, CHANGE_TYPE_UPDATE


class VendorHistory(UUIDMixin, models.Model):
    """Audit log entry for vendor field changes."""

    vendor = models.ForeignKey(
        "vendors.Vendor",
        on_delete=models.CASCADE,
        related_name="history_records",
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vendor_changes",
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    field_name = models.CharField(max_length=100)
    old_value = models.TextField(blank=True, default="")
    new_value = models.TextField(blank=True, default="")
    change_type = models.CharField(
        max_length=20,
        choices=CHANGE_TYPE_CHOICES,
        default=CHANGE_TYPE_UPDATE,
    )

    class Meta:
        db_table = "vendors_vendor_history"
        verbose_name = "Vendor History"
        verbose_name_plural = "Vendor Histories"
        ordering = ["-changed_at"]
        indexes = [
            models.Index(fields=["vendor"], name="idx_vh_vendor"),
            models.Index(fields=["changed_at"], name="idx_vh_changed_at"),
        ]

    def __str__(self):
        return f"{self.vendor.company_name} - {self.field_name} ({self.get_change_type_display()})"
