"""
CustomerSettings model for the customers application.

Stores tenant-specific configuration for the customer module.
Since data lives within the tenant schema (django-tenants), this
model is a singleton per schema — no tenant FK is needed.
"""

from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin
from apps.customers.constants import (
    CUSTOMER_CODE_PREFIX,
    CUSTOMER_STATUS_ACTIVE,
    CUSTOMER_STATUS_CHOICES,
)


class CustomerSettings(UUIDMixin, TimestampMixin, models.Model):
    """
    Tenant-scoped customer configuration.

    Only one record should exist per tenant schema. Use
    ``CustomerSettings.objects.first()`` or the
    ``CustomerService.get_settings()`` helper to retrieve it.
    """

    # ── Code Generation ─────────────────────────────────────────────
    customer_code_prefix = models.CharField(
        max_length=10,
        default=CUSTOMER_CODE_PREFIX,
        verbose_name="Customer Code Prefix",
        help_text="Prefix for auto-generated customer codes (e.g. CUST).",
    )
    customer_code_start = models.IntegerField(
        default=1,
        verbose_name="Customer Code Start",
        help_text="Starting sequence number for new customer codes.",
    )

    # ── Validation Rules ────────────────────────────────────────────
    require_email = models.BooleanField(
        default=False,
        verbose_name="Require Email",
        help_text="Require email address when creating a customer.",
    )
    require_phone = models.BooleanField(
        default=False,
        verbose_name="Require Phone",
        help_text="Require phone number when creating a customer.",
    )
    default_status = models.CharField(
        max_length=20,
        choices=CUSTOMER_STATUS_CHOICES,
        default=CUSTOMER_STATUS_ACTIVE,
        verbose_name="Default Status",
        help_text="Default status for newly created customers.",
    )

    # ── Duplicate Rules ─────────────────────────────────────────────
    allow_duplicate_email = models.BooleanField(
        default=False,
        verbose_name="Allow Duplicate Email",
        help_text="Allow multiple customers with the same email.",
    )
    allow_duplicate_phone = models.BooleanField(
        default=True,
        verbose_name="Allow Duplicate Phone",
        help_text="Allow multiple customers with the same phone number.",
    )

    class Meta:
        db_table = "customers_customer_settings"
        verbose_name = "Customer Settings"
        verbose_name_plural = "Customer Settings"

    def __str__(self):
        return f"Customer Settings (prefix={self.customer_code_prefix})"

    def save(self, *args, **kwargs):
        """Enforce singleton: prevent creating a second record."""
        if self._state.adding and CustomerSettings.objects.exists():
            existing = CustomerSettings.objects.first()
            self.pk = existing.pk
            self._state.adding = False
        super().save(*args, **kwargs)
