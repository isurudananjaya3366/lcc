"""
GoodsReceipt model for the purchases application.

Tracks receipt of goods against a purchase order.
"""

from datetime import date

from django.conf import settings
from django.db import models
from django.db.models import Max

from apps.core.mixins import UUIDMixin, TimestampMixin
from apps.purchases.constants import (
    DEFAULT_GRN_STATUS,
    DEFAULT_INSPECTION_STATUS,
    GRN_STATUS_CHOICES,
    INSPECTION_STATUS_CHOICES,
)


class GoodsReceipt(UUIDMixin, TimestampMixin, models.Model):
    """Record of goods received against a purchase order."""

    grn_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        db_index=True,
        help_text="Auto-generated GRN number (GRN-YYYY-NNNNN)",
    )
    purchase_order = models.ForeignKey(
        "purchases.PurchaseOrder",
        on_delete=models.PROTECT,
        related_name="goods_receipts",
    )
    status = models.CharField(
        max_length=20,
        choices=GRN_STATUS_CHOICES,
        default=DEFAULT_GRN_STATUS,
        db_index=True,
        help_text="GRN lifecycle status",
    )
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="goods_receipts",
    )
    received_at = models.DateTimeField(auto_now_add=True)
    delivery_note_number = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Supplier's delivery note reference",
    )
    carrier = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )
    delivery_date = models.DateField(
        null=True,
        blank=True,
        default=date.today,
    )

    # Delivery Details (Task 53)
    delivery_time = models.TimeField(
        null=True,
        blank=True,
        help_text="Time of delivery",
    )
    driver_name = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Name of delivery driver",
    )
    vehicle_number = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="Vehicle/truck registration number",
    )

    # Inspection Fields (Task 54)
    inspection_status = models.CharField(
        max_length=20,
        choices=INSPECTION_STATUS_CHOICES,
        default=DEFAULT_INSPECTION_STATUS,
    )
    inspection_notes = models.TextField(blank=True, default="")
    inspected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inspected_goods_receipts",
        help_text="User who performed the inspection",
    )
    inspected_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the inspection was performed",
    )
    inspection_passed = models.BooleanField(
        null=True,
        blank=True,
        help_text="Whether the overall inspection passed",
    )

    notes = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "Goods Receipt"
        verbose_name_plural = "Goods Receipts"
        ordering = ["-created_on"]
        indexes = [
            models.Index(fields=["grn_number"], name="idx_grn_number"),
            models.Index(fields=["purchase_order"], name="idx_grn_po"),
        ]

    def __str__(self):
        return self.grn_number or "New GRN"

    def save(self, *args, **kwargs):
        if not self.grn_number:
            self.grn_number = self._generate_grn_number()
        super().save(*args, **kwargs)

    def _generate_grn_number(self):
        """Auto-generate GRN number using POSettings prefix if available."""
        prefix = "GRN"
        try:
            from apps.purchases.models.po_settings import POSettings
            settings = POSettings.objects.first()
            if settings and settings.grn_number_prefix:
                prefix = settings.grn_number_prefix
        except Exception:
            pass

        year = date.today().year
        full_prefix = f"{prefix}-{year}-"
        last = GoodsReceipt.objects.filter(
            grn_number__startswith=full_prefix
        ).aggregate(max_num=Max("grn_number"))
        max_num = last["max_num"]
        if max_num:
            try:
                seq = int(max_num.split("-")[-1]) + 1
            except (ValueError, IndexError):
                seq = 1
        else:
            seq = 1
        return f"{full_prefix}{seq:05d}"
