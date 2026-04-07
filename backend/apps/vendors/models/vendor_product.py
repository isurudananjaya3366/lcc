"""VendorProduct model linking vendors to products they supply."""

from decimal import Decimal
from django.db import models
from apps.core.mixins import UUIDMixin, TimestampMixin


class VendorProduct(UUIDMixin, TimestampMixin, models.Model):
    """Links a vendor to a product with vendor-specific pricing and terms."""

    vendor = models.ForeignKey(
        "vendors.Vendor",
        on_delete=models.CASCADE,
        related_name="vendor_products",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="vendor_products",
    )
    # Core fields (Task 36)
    vendor_sku = models.CharField(max_length=100, blank=True, default="")
    vendor_product_name = models.CharField(max_length=255, blank=True, default="")
    description = models.TextField(blank=True, default="")
    # Pricing fields (Task 37)
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    bulk_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    bulk_qty = models.IntegerField(null=True, blank=True)
    currency = models.CharField(max_length=3, default="LKR")
    # Order fields (Task 38)
    min_order_qty = models.IntegerField(default=1)
    order_multiple = models.IntegerField(null=True, blank=True)
    lead_time_days = models.IntegerField(default=7)
    # Status fields (Task 39)
    is_active = models.BooleanField(default=True)
    is_preferred = models.BooleanField(default=False)
    last_ordered_date = models.DateField(null=True, blank=True)
    last_cost = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True, default="")

    class Meta:
        db_table = "vendors_vendor_product"
        verbose_name = "Vendor Product"
        verbose_name_plural = "Vendor Products"
        ordering = ["vendor", "product"]
        constraints = [
            models.UniqueConstraint(
                fields=["vendor", "product"],
                name="uq_vendor_product",
            ),
        ]

    def __str__(self):
        return f"{self.vendor.company_name} - {self.vendor_sku or self.product}"
