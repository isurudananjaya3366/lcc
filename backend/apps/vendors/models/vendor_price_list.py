"""VendorPriceList and VendorPriceListItem models."""

from decimal import Decimal
from django.conf import settings
from django.db import models
from apps.core.mixins import UUIDMixin, TimestampMixin


class VendorPriceList(UUIDMixin, TimestampMixin, models.Model):
    """Price list from a vendor with effective date range."""

    vendor = models.ForeignKey(
        "vendors.Vendor",
        on_delete=models.CASCADE,
        related_name="price_lists",
    )
    name = models.CharField(max_length=200)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    notes = models.TextField(blank=True, default="")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vendor_price_lists_created",
    )

    class Meta:
        db_table = "vendors_vendor_price_list"
        verbose_name = "Vendor Price List"
        verbose_name_plural = "Vendor Price Lists"
        ordering = ["-is_current", "-effective_from"]

    def __str__(self):
        return f"{self.vendor.company_name} - {self.name}"


class VendorPriceListItem(UUIDMixin, TimestampMixin, models.Model):
    """Individual product pricing within a vendor price list."""

    price_list = models.ForeignKey(
        VendorPriceList,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="vendor_price_list_items",
    )
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    min_qty = models.IntegerField(default=1)
    max_qty = models.IntegerField(null=True, blank=True)
    notes = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        db_table = "vendors_vendor_price_list_item"
        verbose_name = "Vendor Price List Item"
        verbose_name_plural = "Vendor Price List Items"
        ordering = ["product"]
        constraints = [
            models.UniqueConstraint(
                fields=["price_list", "product"],
                name="uq_price_list_product",
            ),
        ]

    def __str__(self):
        return f"{self.product} - {self.unit_price}"
