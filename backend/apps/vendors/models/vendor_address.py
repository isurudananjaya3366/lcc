"""VendorAddress model for multiple addresses per vendor."""

from django.db import models
from apps.core.mixins import UUIDMixin, TimestampMixin
from apps.vendors.constants import ADDRESS_TYPE_CHOICES, ADDRESS_TYPE_MAIN


class VendorAddress(UUIDMixin, TimestampMixin, models.Model):
    """Address associated with a vendor (main, warehouse, billing, shipping)."""

    vendor = models.ForeignKey(
        "vendors.Vendor",
        on_delete=models.CASCADE,
        related_name="addresses",
    )
    address_type = models.CharField(
        max_length=30,
        choices=ADDRESS_TYPE_CHOICES,
        default=ADDRESS_TYPE_MAIN,
    )
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, default="")
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100, blank=True, default="")
    province = models.CharField(max_length=100, blank=True, default="")
    postal_code = models.CharField(max_length=20, blank=True, default="")
    country = models.CharField(max_length=100, default="Sri Lanka")
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, default="")

    class Meta:
        db_table = "vendors_vendor_address"
        verbose_name = "Vendor Address"
        verbose_name_plural = "Vendor Addresses"
        ordering = ["-is_default", "address_type"]

    def __str__(self):
        return f"{self.get_address_type_display()} - {self.city} ({self.vendor.company_name})"

    @property
    def full_address(self):
        parts = [self.address_line_1, self.address_line_2, self.city, self.district, self.province, self.postal_code, self.country]
        return ", ".join(p for p in parts if p)
