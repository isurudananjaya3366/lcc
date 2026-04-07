"""VendorCommunication model for logging vendor interactions."""

from django.conf import settings
from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin
from apps.vendors.constants import COMMUNICATION_TYPE_CHOICES, COMMUNICATION_TYPE_EMAIL


class VendorCommunication(UUIDMixin, TimestampMixin, models.Model):
    """Record of vendor communication/interaction."""

    vendor = models.ForeignKey(
        "vendors.Vendor",
        on_delete=models.CASCADE,
        related_name="communications",
    )
    communication_type = models.CharField(
        max_length=30,
        choices=COMMUNICATION_TYPE_CHOICES,
        default=COMMUNICATION_TYPE_EMAIL,
        verbose_name="Communication Type",
    )
    subject = models.CharField(max_length=255)
    content = models.TextField(blank=True, default="")
    contacted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vendor_communications",
    )
    contact_date = models.DateTimeField()
    # related_po FK deferred until SubPhase-11 Purchase Orders module is implemented
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_notes = models.TextField(blank=True, default="")
    is_follow_up_complete = models.BooleanField(default=False)

    class Meta:
        db_table = "vendors_vendor_communication"
        verbose_name = "Vendor Communication"
        verbose_name_plural = "Vendor Communications"
        ordering = ["-contact_date"]

    def __str__(self):
        return f"{self.get_communication_type_display()}: {self.subject} ({self.vendor.company_name})"
