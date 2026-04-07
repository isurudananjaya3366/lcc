"""VendorContact model for multiple contacts per vendor."""

from django.db import models
from apps.core.mixins import UUIDMixin, TimestampMixin
from apps.vendors.constants import CONTACT_ROLE_CHOICES, CONTACT_ROLE_OTHER


class VendorContact(UUIDMixin, TimestampMixin, models.Model):
    """Contact person associated with a vendor."""

    vendor = models.ForeignKey(
        "vendors.Vendor",
        on_delete=models.CASCADE,
        related_name="contacts",
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255, blank=True, default="")
    phone = models.CharField(max_length=20, blank=True, default="")
    mobile = models.CharField(max_length=20, blank=True, default="")
    whatsapp = models.CharField(max_length=20, blank=True, default="")
    role = models.CharField(
        max_length=30,
        choices=CONTACT_ROLE_CHOICES,
        default=CONTACT_ROLE_OTHER,
    )
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    department = models.CharField(max_length=100, blank=True, default="")
    job_title = models.CharField(max_length=100, blank=True, default="")
    notes = models.TextField(blank=True, default="")

    class Meta:
        db_table = "vendors_vendor_contact"
        verbose_name = "Vendor Contact"
        verbose_name_plural = "Vendor Contacts"
        ordering = ["-is_primary", "last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.vendor.company_name})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
