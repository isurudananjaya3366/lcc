"""
BarcodeScan model — audit log for every barcode scan event.

Records who scanned what location, when, and for what purpose,
enabling analytics and operational insight.
"""

from django.conf import settings
from django.db import models

from apps.inventory.warehouses.constants import SCAN_TYPE_CHOICES
from apps.core.mixins import TimestampMixin, UUIDMixin


class BarcodeScan(UUIDMixin, TimestampMixin, models.Model):
    """
    Audit record of a single barcode scan.

    Nullable ``location`` allows logging of failed / unrecognised scans.
    """

    location = models.ForeignKey(
        "inventory.StorageLocation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="scans",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="barcode_scans",
    )

    scan_type = models.CharField(
        max_length=20,
        choices=SCAN_TYPE_CHOICES,
        db_index=True,
    )

    scanned_barcode = models.CharField(
        max_length=100,
        help_text="Raw barcode value as scanned (may include errors)",
    )

    success = models.BooleanField(
        default=True,
        db_index=True,
        help_text="True if the barcode resolved to a valid location",
    )

    device_id = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Identifier of the scanning device or terminal",
    )

    context_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Extra context (order_id, transfer_id, etc.)",
    )

    class Meta:
        app_label = "inventory"
        db_table = "inventory_barcode_scans"
        verbose_name = "Barcode Scan"
        verbose_name_plural = "Barcode Scans"
        ordering = ["-created_on"]
        indexes = [
            models.Index(fields=["location", "created_on"]),
            models.Index(fields=["user", "created_on"]),
            models.Index(fields=["scan_type", "created_on"]),
            models.Index(fields=["success", "created_on"]),
        ]

    def __str__(self):
        loc = self.location.code if self.location else "INVALID"
        return f"{self.scan_type} – {loc} @ {self.created_on}"

    @property
    def scan_result(self):
        return "Success" if self.success else "Failed"
