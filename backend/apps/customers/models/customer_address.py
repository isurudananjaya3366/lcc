"""
CustomerAddress model for the customers application.

Stores multiple addresses per customer with support for Sri Lanka-specific
location fields including districts and provinces.
"""

import uuid
import re

from django.core.exceptions import ValidationError
from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin
from apps.customers.constants import ADDRESS_TYPE_CHOICES, ADDRESS_TYPE_BILLING


class CustomerAddress(UUIDMixin, TimestampMixin, models.Model):
    """
    Address record linked to a customer.

    Supports multiple addresses per customer with type classification
    (billing, shipping, home, work, other) and default flags for
    billing and shipping. Includes Sri Lanka district/province fields.
    """

    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.CASCADE,
        related_name="addresses",
        verbose_name="Customer",
    )
    address_type = models.CharField(
        max_length=20,
        choices=ADDRESS_TYPE_CHOICES,
        default=ADDRESS_TYPE_BILLING,
        verbose_name="Address Type",
        help_text="Purpose of this address.",
    )

    # ── Core Address Fields ─────────────────────────────────────────
    address_line_1 = models.CharField(
        max_length=255,
        verbose_name="Address Line 1",
        help_text="House number, street name.",
    )
    address_line_2 = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Address Line 2",
        help_text="Additional location details.",
    )
    city = models.CharField(
        max_length=100,
        verbose_name="City",
        help_text="City or town name.",
    )

    # ── Sri Lanka Address Fields ────────────────────────────────────
    district = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="District",
        help_text="Sri Lanka District (e.g., Colombo District).",
    )
    province = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Province",
        help_text="Sri Lanka Province (e.g., Western Province).",
    )

    # ── Postal Fields ───────────────────────────────────────────────
    postal_code = models.CharField(
        max_length=10,
        blank=True,
        default="",
        verbose_name="Postal Code",
        help_text="Sri Lanka postal codes are 5 digits.",
    )
    country = models.CharField(
        max_length=100,
        default="Sri Lanka",
        verbose_name="Country",
    )

    # ── Default Flags ───────────────────────────────────────────────
    is_default_billing = models.BooleanField(
        default=False,
        verbose_name="Default Billing",
        help_text="Mark as default billing address.",
    )
    is_default_shipping = models.BooleanField(
        default=False,
        verbose_name="Default Shipping",
        help_text="Mark as default shipping address.",
    )

    class Meta:
        db_table = "customers_customer_address"
        verbose_name = "Customer Address"
        verbose_name_plural = "Customer Addresses"
        ordering = ["-is_default_billing", "-is_default_shipping", "-created_on"]
        indexes = [
            models.Index(
                fields=["customer", "address_type"],
                name="idx_addr_customer_type",
            ),
            models.Index(
                fields=["district"],
                name="idx_addr_district",
            ),
            models.Index(
                fields=["province"],
                name="idx_addr_province",
            ),
        ]

    def __str__(self):
        return f"{self.get_address_type_display()} - {self.address_line_1}, {self.city}"

    def save(self, *args, **kwargs):
        """Ensure only one default billing/shipping per customer."""
        if self.is_default_billing:
            CustomerAddress.objects.filter(
                customer=self.customer,
                is_default_billing=True,
            ).exclude(pk=self.pk).update(is_default_billing=False)
        if self.is_default_shipping:
            CustomerAddress.objects.filter(
                customer=self.customer,
                is_default_shipping=True,
            ).exclude(pk=self.pk).update(is_default_shipping=False)
        super().save(*args, **kwargs)

    def clean(self):
        """Validate address data."""
        super().clean()

        # Validate district-province mapping for Sri Lanka addresses
        if self.country == "Sri Lanka" and self.district and self.province:
            from apps.customers.validators import validate_district_province
            validate_district_province(self.district, self.province)

        # Validate postal code format for Sri Lanka
        if self.country == "Sri Lanka" and self.postal_code:
            if not re.match(r"^\d{5}$", self.postal_code):
                raise ValidationError(
                    {"postal_code": "Sri Lanka postal codes must be 5 digits."}
                )

    @property
    def is_default(self):
        """Return True if this is a default address for any purpose."""
        return self.is_default_billing or self.is_default_shipping

    @property
    def full_address(self):
        """Return formatted full address string."""
        parts = [self.address_line_1]
        if self.address_line_2:
            parts.append(self.address_line_2)
        parts.append(self.city)
        if self.district:
            parts.append(self.district)
        if self.province:
            parts.append(self.province)
        if self.postal_code:
            parts.append(self.postal_code)
        parts.append(self.country)
        return ", ".join(parts)
