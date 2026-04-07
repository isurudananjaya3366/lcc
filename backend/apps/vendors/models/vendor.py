"""
Vendor model for the vendors application.

Defines the full Vendor model with core identification, address,
contact, payment terms, lead time, rating, and audit fields.
"""

from decimal import Decimal

from django.conf import settings
from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin, SoftDeleteMixin
from apps.vendors.constants import (
    DEFAULT_VENDOR_STATUS,
    DEFAULT_VENDOR_TYPE,
    VENDOR_STATUS_CHOICES,
    VENDOR_TYPE_CHOICES,
)


class Vendor(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """
    Full vendor record for a tenant.

    Represents a business or individual that supplies products or
    services, with comprehensive fields for identification, contact,
    payment terms, ordering parameters, and performance tracking.
    """

    # ── Core Fields (Task 05) ───────────────────────────────────────
    vendor_code = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        blank=True,
        default="",
        verbose_name="Vendor Code",
        help_text="Auto-generated unique vendor code (VND-NNNNN).",
    )
    company_name = models.CharField(
        max_length=200,
        verbose_name="Company Name",
        help_text="Legal or trading name of the vendor.",
    )
    display_name = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Display Name",
        help_text="Short display name for the vendor.",
    )
    status = models.CharField(
        max_length=30,
        choices=VENDOR_STATUS_CHOICES,
        default=DEFAULT_VENDOR_STATUS,
        db_index=True,
        verbose_name="Status",
    )

    # ── Type Fields (Task 06) ──────────────────────────────────────
    vendor_type = models.CharField(
        max_length=30,
        choices=VENDOR_TYPE_CHOICES,
        default=DEFAULT_VENDOR_TYPE,
        verbose_name="Vendor Type",
    )
    business_registration = models.CharField(
        max_length=50,
        blank=True,
        default="",
        verbose_name="Business Registration",
        help_text="Business registration number.",
    )
    tax_id = models.CharField(
        max_length=50,
        blank=True,
        default="",
        db_index=True,
        verbose_name="Tax ID",
        help_text="Tax identification number (TIN/BRN).",
    )
    is_local_vendor = models.BooleanField(
        default=True,
        verbose_name="Local Vendor",
        help_text="Whether this is a local (Sri Lankan) vendor.",
    )
    country = models.CharField(
        max_length=100,
        default="Sri Lanka",
        verbose_name="Country",
    )

    # ── Address Fields (Task 07) ────────────────────────────────────
    address_line_1 = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Address Line 1",
    )
    address_line_2 = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Address Line 2",
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="City",
    )
    district = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="District",
    )
    province = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Province",
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        default="",
        verbose_name="Postal Code",
    )

    # ── Contact Fields (Task 08) ────────────────────────────────────
    primary_email = models.EmailField(
        max_length=255,
        blank=True,
        default="",
        db_index=True,
        verbose_name="Primary Email",
    )
    secondary_email = models.EmailField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Secondary Email",
    )
    primary_phone = models.CharField(
        max_length=20,
        blank=True,
        default="",
        verbose_name="Primary Phone",
    )
    secondary_phone = models.CharField(
        max_length=20,
        blank=True,
        default="",
        verbose_name="Secondary Phone",
    )
    mobile = models.CharField(
        max_length=20,
        blank=True,
        default="",
        verbose_name="Mobile",
    )
    fax = models.CharField(
        max_length=20,
        blank=True,
        default="",
        verbose_name="Fax",
    )
    website = models.URLField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Website",
    )

    # ── Payment Terms Fields (Task 09) ──────────────────────────────
    payment_terms_days = models.IntegerField(
        default=30,
        verbose_name="Payment Terms (Days)",
        help_text="Number of days for payment after invoice.",
    )
    payment_terms_description = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Payment Terms Description",
    )
    credit_limit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Credit Limit",
    )
    currency = models.CharField(
        max_length=3,
        default="LKR",
        verbose_name="Currency",
    )
    requires_purchase_order = models.BooleanField(
        default=True,
        verbose_name="Requires Purchase Order",
    )
    accepts_returns = models.BooleanField(
        default=True,
        verbose_name="Accepts Returns",
    )

    # ── Lead Time Fields (Task 10) ──────────────────────────────────
    default_lead_time_days = models.IntegerField(
        default=7,
        verbose_name="Default Lead Time (Days)",
    )
    minimum_order_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Minimum Order Value",
    )
    minimum_order_quantity = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Minimum Order Quantity",
    )
    order_multiple = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Order Multiple",
    )

    # ── Notes Fields (Task 11) ──────────────────────────────────────
    notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Notes",
    )
    internal_notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Internal Notes",
    )
    tags = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Tags",
    )

    # ── Rating Fields (Task 12) ─────────────────────────────────────
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Rating",
    )
    total_orders = models.IntegerField(
        default=0,
        verbose_name="Total Orders",
    )
    total_spend = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Total Spend",
    )
    last_rating_update = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Last Rating Update",
    )
    is_preferred_vendor = models.BooleanField(
        default=False,
        verbose_name="Preferred Vendor",
    )

    # ── Audit / Date Fields (Task 13) ───────────────────────────────
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vendors_created",
        verbose_name="Created By",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vendors_updated",
        verbose_name="Updated By",
    )
    first_order_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="First Order Date",
    )
    last_order_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Last Order Date",
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Approved At",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vendors_approved",
        verbose_name="Approved By",
    )

    # ── Logo (Task 15) ──────────────────────────────────────────────
    logo = models.ImageField(
        upload_to="vendors/logos/",
        blank=True,
        null=True,
        verbose_name="Logo",
    )

    class Meta:
        db_table = "vendors_vendor"
        verbose_name = "Vendor"
        verbose_name_plural = "Vendors"
        ordering = ["company_name"]
        indexes = [
            models.Index(fields=["vendor_code"], name="idx_vendor_code"),
            models.Index(fields=["company_name"], name="idx_vendor_company"),
            models.Index(fields=["status"], name="idx_vendor_status"),
            models.Index(fields=["vendor_type"], name="idx_vendor_type"),
            models.Index(fields=["primary_email"], name="idx_vendor_email"),
            models.Index(fields=["rating"], name="idx_vendor_rating"),
            models.Index(
                fields=["is_preferred_vendor"],
                name="idx_vendor_preferred",
            ),
            models.Index(
                fields=["status", "vendor_type"],
                name="idx_vendor_status_type",
            ),
            models.Index(
                fields=["is_preferred_vendor", "rating"],
                name="idx_vendor_preferred_rating",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["vendor_code"],
                condition=~models.Q(vendor_code=""),
                name="uq_vendor_code_nonempty",
            ),
            models.CheckConstraint(
                condition=models.Q(rating__gte=0, rating__lte=5),
                name="vendor_rating_range",
            ),
            models.CheckConstraint(
                condition=models.Q(payment_terms_days__gte=0),
                name="vendor_payment_terms_positive",
            ),
            models.CheckConstraint(
                condition=models.Q(credit_limit__gte=0)
                | models.Q(credit_limit__isnull=True),
                name="vendor_credit_limit_positive",
            ),
            models.CheckConstraint(
                condition=models.Q(default_lead_time_days__gte=0),
                name="vendor_lead_time_positive",
            ),
            models.UniqueConstraint(
                fields=["tax_id"],
                condition=~models.Q(tax_id=""),
                name="vendor_tax_id_unique",
            ),
        ]

    def __str__(self) -> str:
        if self.vendor_code:
            return f"{self.vendor_code} - {self.company_name}"
        return self.company_name

    def save(self, *args, **kwargs):
        if not self.vendor_code:
            from apps.vendors.services.code_generator import generate_vendor_code

            self.vendor_code = generate_vendor_code()
        super().save(*args, **kwargs)

    @property
    def full_address(self) -> str:
        """Return formatted full address string."""
        parts = [
            self.address_line_1,
            self.address_line_2,
            self.city,
            self.district,
            self.province,
            self.postal_code,
            self.country,
        ]
        return ", ".join(p for p in parts if p)

    @property
    def logo_url(self) -> str | None:
        """Return the URL of the logo if it exists."""
        if self.logo and hasattr(self.logo, "url"):
            return self.logo.url
        return None
