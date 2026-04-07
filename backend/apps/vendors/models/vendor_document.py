"""VendorDocument model for managing vendor-related documents."""

from django.conf import settings
from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin
from apps.vendors.constants import DOCUMENT_TYPE_CHOICES, DOCUMENT_TYPE_CONTRACT


def vendor_document_upload_path(instance, filename):
    """Generate upload path for vendor documents."""
    return f"vendor_documents/{instance.vendor_id}/{filename}"


class VendorDocument(UUIDMixin, TimestampMixin, models.Model):
    """Document attached to a vendor (contracts, certificates, etc.)."""

    vendor = models.ForeignKey(
        "vendors.Vendor",
        on_delete=models.CASCADE,
        related_name="documents",
    )
    document_type = models.CharField(
        max_length=30,
        choices=DOCUMENT_TYPE_CHOICES,
        default=DOCUMENT_TYPE_CONTRACT,
    )
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to=vendor_document_upload_path)
    expiry_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_vendor_documents",
    )

    class Meta:
        db_table = "vendors_vendor_document"
        verbose_name = "Vendor Document"
        verbose_name_plural = "Vendor Documents"
        ordering = ["-created_on"]

    def __str__(self):
        return f"{self.name} ({self.get_document_type_display()}) - {self.vendor.company_name}"
