"""
Customer model for the customers application.

Defines the Customer model which stores customer profiles for each
tenant. Customers can be individuals, businesses, wholesale buyers,
VIP customers, government entities, or non-profit organizations.
Each customer type may have different credit limits, pricing tiers,
and contact patterns.
"""

from decimal import Decimal

from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.db.models import Q

from apps.core.mixins import UUIDMixin, TimestampMixin, SoftDeleteMixin
from apps.customers.constants import (
    CUSTOMER_TYPE_CHOICES,
    DEFAULT_CUSTOMER_TYPE,
    DEFAULT_CREDIT_LIMIT,
    CUSTOMER_STATUS_CHOICES,
    DEFAULT_CUSTOMER_STATUS,
    CUSTOMER_SOURCE_CHOICES,
    DEFAULT_CUSTOMER_SOURCE,
)


class Customer(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """
    Customer record for a tenant.

    Supports individual walk-in customers as well as business, wholesale,
    VIP, government, and non-profit accounts. Each customer has name,
    contact, and address information plus financial tracking fields.
    """

    # ── Core Identity ───────────────────────────────────────────────
    customer_code = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        default="",
        verbose_name="Customer Code",
        help_text="Auto-generated unique code (e.g. CUST-00001).",
    )

    # ── Name Fields ─────────────────────────────────────────────────
    first_name = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="First Name",
        help_text="Customer's first name (for individuals).",
    )
    last_name = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Last Name",
        help_text="Customer's last name (for individuals).",
    )
    display_name = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Display Name",
        help_text="Computed display name for lists and reports.",
    )
    business_name = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Business Name",
        help_text="Company or business name (for business/wholesale customers).",
    )

    # ── Contact Fields ──────────────────────────────────────────────
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Email",
        help_text="Primary email address for the customer.",
    )
    phone = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name="Phone",
        help_text="Primary phone number (+94 XX XXX XXXX format).",
    )
    mobile = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name="Mobile",
        help_text="Secondary / mobile phone number.",
    )

    # ── Billing Address ─────────────────────────────────────────────
    billing_address_line_1 = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Billing Address Line 1",
        help_text="Primary billing address line.",
    )
    billing_address_line_2 = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Billing Address Line 2",
        help_text="Secondary billing address line.",
    )
    billing_city = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Billing City",
    )
    billing_state_province = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Billing State / Province",
    )
    billing_postal_code = models.CharField(
        max_length=20,
        blank=True,
        default="",
        verbose_name="Billing Postal Code",
    )
    billing_country = models.CharField(
        max_length=100,
        default="Sri Lanka",
        verbose_name="Billing Country",
    )

    # ── Shipping Address ────────────────────────────────────────────
    shipping_address_line_1 = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Shipping Address Line 1",
        help_text="Primary shipping address line.",
    )
    shipping_address_line_2 = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Shipping Address Line 2",
        help_text="Secondary shipping address line.",
    )
    shipping_city = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Shipping City",
    )
    shipping_state_province = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Shipping State / Province",
    )
    shipping_postal_code = models.CharField(
        max_length=20,
        blank=True,
        default="",
        verbose_name="Shipping Postal Code",
    )
    shipping_country = models.CharField(
        max_length=100,
        default="Sri Lanka",
        verbose_name="Shipping Country",
    )

    # ── Type & Status ───────────────────────────────────────────────
    customer_type = models.CharField(
        max_length=20,
        choices=CUSTOMER_TYPE_CHOICES,
        default=DEFAULT_CUSTOMER_TYPE,
        db_index=True,
        verbose_name="Customer Type",
        help_text="Classification: individual, business, wholesale, VIP, government, non-profit.",
    )
    status = models.CharField(
        max_length=20,
        choices=CUSTOMER_STATUS_CHOICES,
        default=DEFAULT_CUSTOMER_STATUS,
        db_index=True,
        verbose_name="Status",
        help_text="Customer account status.",
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Active",
        help_text="Whether this customer is active for transactions.",
    )

    # ── Type-Specific Fields (Business / Government / Non-Profit) ──
    company_registration = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Company Registration",
        help_text="Business registration number.",
    )
    department_name = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Department Name",
        help_text="Department name (for government / corporate).",
    )
    department_code = models.CharField(
        max_length=50,
        blank=True,
        default="",
        verbose_name="Department Code",
        help_text="Department code (for government / corporate).",
    )
    organization_name = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Organization Name",
        help_text="Organization name (for non-profit / government).",
    )
    registration_number = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Registration Number",
        help_text="Official registration number.",
    )
    tax_exempt_status = models.BooleanField(
        default=False,
        verbose_name="Tax Exempt",
        help_text="Whether the customer is exempt from tax.",
    )

    # ── Tax Fields ──────────────────────────────────────────────────
    tax_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Tax ID / TIN",
        help_text="Sri Lanka Tax Identification Number (TIN).",
    )
    vat_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="VAT Number",
        help_text="VAT Registration Number.",
    )

    # ── Date Tracking ───────────────────────────────────────────────
    first_purchase_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="First Purchase Date",
        help_text="Date of first purchase (set once, immutable).",
    )
    last_purchase_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Last Purchase Date",
        help_text="Date of most recent purchase.",
    )
    last_contact_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Last Contact Date",
        help_text="Date of most recent contact with customer.",
    )
    next_follow_up_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Next Follow-Up Date",
        help_text="Scheduled follow-up date for CRM.",
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        verbose_name="Date of Birth",
        help_text="Customer date of birth (individuals).",
    )

    # ── Financial Fields ────────────────────────────────────────────
    credit_limit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Credit Limit (LKR)",
        help_text="Maximum credit allowed in LKR. NULL = no credit.",
    )
    current_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Current Balance (LKR)",
        help_text="Outstanding balance owed by the customer.",
    )
    total_purchases = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Total Purchases (LKR)",
        help_text="Cumulative purchase amount.",
    )
    total_payments = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Total Payments (LKR)",
        help_text="Cumulative payment amount.",
    )
    outstanding_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Outstanding Balance (LKR)",
        help_text="Current outstanding balance.",
    )
    order_count = models.IntegerField(
        default=0,
        verbose_name="Order Count",
        help_text="Total number of orders placed.",
    )

    # ── Marketing Fields ────────────────────────────────────────────
    accepts_marketing = models.BooleanField(
        default=False,
        verbose_name="Accepts Marketing",
        help_text="Whether the customer opted in for marketing.",
    )
    marketing_opt_in_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Marketing Opt-In Date",
    )
    marketing_opt_out_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Marketing Opt-Out Date",
    )
    last_marketing_email_sent = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Last Marketing Email Sent",
    )
    marketing_email_count = models.IntegerField(
        default=0,
        verbose_name="Marketing Email Count",
        help_text="Number of marketing emails sent to this customer.",
    )

    # ── Notes ───────────────────────────────────────────────────────
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notes",
        help_text="General notes about customer (visible to all staff).",
    )
    internal_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Internal Notes",
        help_text="Internal notes (not visible to customer).",
    )

    # ── Source & Tracking ───────────────────────────────────────────
    source = models.CharField(
        max_length=20,
        choices=CUSTOMER_SOURCE_CHOICES,
        default=DEFAULT_CUSTOMER_SOURCE,
        verbose_name="Source",
        help_text="How this customer was acquired.",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="created_customers",
        verbose_name="Created By",
        help_text="User who created this customer record.",
    )

    # ── Profile Image ──────────────────────────────────────────────
    profile_image = models.ImageField(
        upload_to="customers/profile_images/",
        blank=True,
        null=True,
        verbose_name="Profile Image",
        help_text="Customer profile image (JPEG/PNG, max 2MB).",
    )

    # ── Full-Text Search ────────────────────────────────────────────
    search_vector = SearchVectorField(
        null=True,
        blank=True,
        editable=False,
        help_text="Auto-populated search vector for PostgreSQL FTS.",
    )

    class Meta:
        db_table = "customers_customer"
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
        ordering = ["display_name", "first_name", "last_name"]
        indexes = [
            models.Index(
                fields=["customer_code"],
                name="idx_customer_code",
            ),
            models.Index(
                fields=["customer_type", "is_active"],
                name="idx_customer_type_active",
            ),
            models.Index(
                fields=["email"],
                name="idx_customer_email",
            ),
            models.Index(
                fields=["phone"],
                name="idx_customer_phone",
            ),
            models.Index(
                fields=["first_name", "last_name"],
                name="idx_customer_name",
            ),
            models.Index(
                fields=["display_name"],
                name="idx_customer_display",
            ),
            models.Index(
                fields=["status"],
                name="idx_customer_status",
            ),
            models.Index(
                fields=["created_on"],
                name="idx_customer_created",
            ),
            models.Index(
                fields=["last_purchase_date"],
                name="idx_customer_last_purchase",
            ),
            models.Index(
                fields=["outstanding_balance"],
                name="idx_customer_outstanding",
            ),
            models.Index(
                fields=["source"],
                name="idx_customer_source",
            ),
            models.Index(
                fields=["next_follow_up_date"],
                name="idx_customer_follow_up",
            ),
            models.Index(
                fields=["total_purchases"],
                name="idx_customer_total_purchases",
            ),
            GinIndex(
                fields=["search_vector"],
                name="idx_customer_search_vector",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(total_purchases__gte=0),
                name="positive_total_purchases",
            ),
            models.CheckConstraint(
                check=Q(total_payments__gte=0),
                name="positive_total_payments",
            ),
            models.CheckConstraint(
                check=Q(credit_limit__gte=0) | Q(credit_limit__isnull=True),
                name="positive_credit_limit",
            ),
        ]

    def __str__(self):
        name = self.display_name or self.business_name or self.full_name
        if self.customer_code:
            return f"{name} ({self.customer_code})"
        return name or f"Customer {self.pk}"

    def save(self, *args, **kwargs):
        """Auto-populate display_name and customer_code on save."""
        if not self.display_name:
            self.display_name = self._compute_display_name()
        if not self.customer_code:
            from apps.customers.services.code_generator import CustomerCodeGenerator
            self.customer_code = CustomerCodeGenerator.generate()
        super().save(*args, **kwargs)

    def _compute_display_name(self):
        """Compute display name from business name or individual name."""
        if self.business_name:
            return self.business_name
        full = f"{self.first_name} {self.last_name}".strip()
        return full or ""

    @property
    def full_name(self):
        """Return the customer's full name."""
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def has_credit(self):
        """Return True if this customer has a credit limit > 0."""
        return self.credit_limit is not None and self.credit_limit > 0

    @property
    def available_credit(self):
        """Return remaining available credit (credit_limit - outstanding_balance)."""
        if not self.credit_limit or self.credit_limit <= 0:
            return Decimal("0.00")
        return max(Decimal("0.00"), self.credit_limit - self.outstanding_balance)

    @property
    def credit_available(self):
        """Alias for available_credit."""
        return self.available_credit

    @property
    def average_order_value(self):
        """Return average order value (total_purchases / order_count)."""
        if self.order_count and self.order_count > 0:
            return self.total_purchases / self.order_count
        return Decimal("0.00")

    @property
    def image_url(self):
        """Return profile image URL or None."""
        if self.profile_image:
            return self.profile_image.url
        return None

    @property
    def has_profile_image(self):
        """Return True if profile image is uploaded."""
        return bool(self.profile_image)
