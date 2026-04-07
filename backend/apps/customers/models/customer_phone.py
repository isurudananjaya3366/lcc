"""
CustomerPhone model for the customers application.

Stores multiple phone numbers per customer with type classification,
Sri Lanka phone format validation, and WhatsApp support.
"""

from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin
from apps.customers.constants import PHONE_TYPE_CHOICES, PHONE_TYPE_MOBILE


class CustomerPhone(UUIDMixin, TimestampMixin, models.Model):
    """
    Phone number record linked to a customer.

    Supports multiple phone numbers per customer with type classification
    (mobile, landline, WhatsApp, work, other). Includes primary phone
    designation, verification tracking, and WhatsApp indicator.
    """

    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.CASCADE,
        related_name="phone_numbers",
        verbose_name="Customer",
    )
    phone_type = models.CharField(
        max_length=20,
        choices=PHONE_TYPE_CHOICES,
        default=PHONE_TYPE_MOBILE,
        verbose_name="Phone Type",
        help_text="Type of phone number.",
    )

    # ── Phone Number Fields ─────────────────────────────────────────
    phone_number = models.CharField(
        max_length=20,
        verbose_name="Phone Number",
        help_text="Format: +94 77 123 4567",
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name="Primary",
        help_text="Mark as primary phone number.",
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name="Verified",
        help_text="Whether this phone number has been verified.",
    )
    verified_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Verified At",
        help_text="Timestamp of phone verification.",
    )

    # ── WhatsApp ────────────────────────────────────────────────────
    is_whatsapp = models.BooleanField(
        default=False,
        verbose_name="WhatsApp",
        help_text="Whether this number has WhatsApp.",
    )

    class Meta:
        db_table = "customers_customer_phone"
        verbose_name = "Customer Phone"
        verbose_name_plural = "Customer Phones"
        ordering = ["-is_primary", "-created_on"]
        indexes = [
            models.Index(
                fields=["customer", "phone_type"],
                name="idx_phone_customer_type",
            ),
            models.Index(
                fields=["phone_number"],
                name="idx_phone_number",
            ),
        ]

    def __str__(self):
        primary = " (Primary)" if self.is_primary else ""
        return f"{self.get_phone_type_display()}: {self.phone_number}{primary}"

    def save(self, *args, **kwargs):
        """Ensure only one primary phone per customer."""
        if self.is_primary:
            CustomerPhone.objects.filter(
                customer=self.customer,
                is_primary=True,
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)

    def clean(self):
        """Validate phone number format."""
        super().clean()
        if self.phone_number:
            from apps.customers.validators import validate_phone_number
            validate_phone_number(self.phone_number)
