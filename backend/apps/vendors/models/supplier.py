"""
Supplier model for the vendors application.

Defines the Supplier model which stores vendor/supplier profiles
for each tenant. Suppliers provide products and services to the
business, with their own contact details, addresses, tax IDs,
and agreed payment terms.

Note: The document series refers to this as "Supplier" and the
app as "suppliers". The project uses the "vendors" app name but
the model remains Supplier for domain clarity.
"""

from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin, SoftDeleteMixin
from apps.vendors.constants import (
    DEFAULT_PAYMENT_TERMS,
    PAYMENT_TERMS_CHOICES,
)


class Supplier(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """
    Supplier / vendor record for a tenant.

    Represents a business or individual that supplies products or
    services. Each supplier has contact information, address details,
    Sri Lankan tax identification, and agreed payment terms.

    Fields:
        name: Legal or trading name of the supplier.
        contact_person: Name of the primary contact at the supplier.
        email: Primary email address.
        phone: Primary phone number (+94 XX XXX XXXX format).
        mobile: Mobile phone number.
        website: Supplier website URL (optional).
        address_line_1 / _2: Business address lines.
        city, state_province, postal_code, country: Address details.
        tax_id: Sri Lankan business registration number (BRN) or
            tax identification number (TIN).
        vat_number: VAT registration number (if applicable).
        payment_terms: Agreed payment terms (immediate, net_15,
            net_30, net_60, cod).
        is_active: Whether this supplier is active for orders.
        notes: Internal notes about the supplier.
    """

    # ── Name Fields ─────────────────────────────────────────────────
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Supplier Name",
        help_text="Legal or trading name of the supplier.",
    )
    contact_person = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Contact Person",
        help_text="Name of the primary contact at the supplier.",
    )

    # ── Contact Fields ──────────────────────────────────────────────
    email = models.EmailField(
        blank=True,
        default="",
        verbose_name="Email",
        help_text="Primary email address for the supplier.",
    )
    phone = models.CharField(
        max_length=30,
        blank=True,
        default="",
        verbose_name="Phone",
        help_text="Primary phone number (+94 XX XXX XXXX format).",
    )
    mobile = models.CharField(
        max_length=30,
        blank=True,
        default="",
        verbose_name="Mobile",
        help_text="Mobile phone number.",
    )
    website = models.URLField(
        blank=True,
        default="",
        verbose_name="Website",
        help_text="Supplier website URL.",
    )

    # ── Address Fields ──────────────────────────────────────────────
    address_line_1 = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Address Line 1",
        help_text="Primary business address line.",
    )
    address_line_2 = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Address Line 2",
        help_text="Secondary address line.",
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="City",
    )
    state_province = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="State / Province",
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        default="",
        verbose_name="Postal Code",
    )
    country = models.CharField(
        max_length=100,
        default="Sri Lanka",
        verbose_name="Country",
    )

    # ── Tax & Registration ──────────────────────────────────────────
    tax_id = models.CharField(
        max_length=50,
        blank=True,
        default="",
        db_index=True,
        verbose_name="Tax ID / BRN",
        help_text=(
            "Sri Lankan business registration number (BRN) or "
            "tax identification number (TIN)."
        ),
    )
    vat_number = models.CharField(
        max_length=50,
        blank=True,
        default="",
        verbose_name="VAT Number",
        help_text="VAT registration number (if applicable).",
    )

    # ── Payment Terms ───────────────────────────────────────────────
    payment_terms = models.CharField(
        max_length=20,
        choices=PAYMENT_TERMS_CHOICES,
        default=DEFAULT_PAYMENT_TERMS,
        verbose_name="Payment Terms",
        help_text="Agreed payment terms with the supplier.",
    )

    # ── Status & Notes ──────────────────────────────────────────────
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Active",
        help_text="Whether this supplier is active for purchase orders.",
    )
    notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Notes",
        help_text="Internal notes about this supplier.",
    )

    class Meta:
        db_table = "vendors_supplier"
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"
        ordering = ["name"]
        indexes = [
            models.Index(
                fields=["is_active"],
                name="idx_supplier_active",
            ),
            models.Index(
                fields=["email"],
                name="idx_supplier_email",
            ),
            models.Index(
                fields=["payment_terms"],
                name="idx_supplier_payment_terms",
            ),
        ]

    def __str__(self):
        return self.name

    @property
    def full_address(self):
        """Return formatted address string."""
        parts = [
            self.address_line_1,
            self.address_line_2,
            self.city,
            self.state_province,
            self.postal_code,
            self.country,
        ]
        return ", ".join(part for part in parts if part)
