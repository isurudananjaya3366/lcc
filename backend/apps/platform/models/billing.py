"""
Billing record model for the LankaCommerce Cloud platform.

Defines the BillingRecord model for tracking tenant subscription
billing, invoice generation, and payment status. Each billing record
represents a single billing event for a tenant's subscription period.

Billing is denominated in Sri Lankan Rupees (LKR, ₨) as this
platform targets the Sri Lankan market. All monetary fields use
Decimal to avoid floating-point precision issues.

Business Registration Number (BRN) fields support Sri Lanka-specific
validation for tax compliance and invoice generation.

Table: platform_billingrecord
Schema: public (shared)

Billing lifecycle:
    1. A billing record is created at the start of each billing cycle
       with status 'pending' and the subscription amount.
    2. When payment is received, the status changes to 'paid' and
       the paid_on timestamp is recorded.
    3. If payment is not received by the due date, the status changes
       to 'overdue' and the overdue flag is set.
    4. Records can be cancelled (e.g., downgrade) or refunded.

Status transitions:
    pending → paid (payment received)
    pending → overdue (past due date)
    pending → cancelled (subscription change)
    overdue → paid (late payment received)
    paid → refunded (refund issued)
"""

from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from apps.platform.models.mixins import (
    SoftDeleteMixin,
    StatusMixin,
    TimestampMixin,
    UUIDMixin,
)

# ── Constants ────────────────────────────────────────────────

# Currency
CURRENCY_CODE = "LKR"
CURRENCY_SYMBOL = "₨"
AMOUNT_MAX_DIGITS = 12
AMOUNT_DECIMAL_PLACES = 2

# Invoice
INVOICE_NUMBER_MAX_LENGTH = 50
INVOICE_NOTES_MAX_LENGTH = 1000

# BRN (Business Registration Number — Sri Lanka)
BRN_MAX_LENGTH = 50

# Billing status choices
STATUS_PENDING = "pending"
STATUS_PAID = "paid"
STATUS_OVERDUE = "overdue"
STATUS_CANCELLED = "cancelled"
STATUS_REFUNDED = "refunded"

BILLING_STATUS_CHOICES = [
    (STATUS_PENDING, "Pending"),
    (STATUS_PAID, "Paid"),
    (STATUS_OVERDUE, "Overdue"),
    (STATUS_CANCELLED, "Cancelled"),
    (STATUS_REFUNDED, "Refunded"),
]

VALID_BILLING_STATUSES = [
    STATUS_PENDING,
    STATUS_PAID,
    STATUS_OVERDUE,
    STATUS_CANCELLED,
    STATUS_REFUNDED,
]

# Billing cycle choices (mirroring SubscriptionPlan)
CYCLE_MONTHLY = "monthly"
CYCLE_ANNUAL = "annual"

BILLING_CYCLE_CHOICES = [
    (CYCLE_MONTHLY, "Monthly"),
    (CYCLE_ANNUAL, "Annual"),
]

# BRN validator for Sri Lanka business registration format
# Sri Lanka BRN formats: PV00000, PB00000, GA00000, or numeric
brn_validator = RegexValidator(
    regex=r"^[A-Z]{2}\d{5,}$|^\d{5,}$",
    message=(
        "Enter a valid Sri Lanka Business Registration Number. "
        "Accepted formats: PV12345, PB12345, GA12345, or numeric."
    ),
)


# ── Model ────────────────────────────────────────────────────


class BillingRecord(UUIDMixin, TimestampMixin, StatusMixin, SoftDeleteMixin, models.Model):
    """
    Billing record for tenant subscription payments.

    Each record represents a single billing event for a tenant,
    including the subscription amount, billing period, payment
    status, and invoice details. Records are denominated in LKR
    and include Sri Lanka-specific BRN fields for tax compliance.

    Billing records use all four platform mixins for maximum
    data protection:
        - UUIDMixin: UUID v4 primary key
        - TimestampMixin: created_on / updated_on audit fields
        - StatusMixin: is_active / deactivated_on lifecycle flags
        - SoftDeleteMixin: is_deleted / deleted_on soft deletion

    Financial records are never physically deleted — they are
    soft-deleted to preserve the billing audit trail.
    """

    # ── Relationships ────────────────────────────────────────

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="billing_records",
        help_text="The tenant this billing record belongs to.",
    )

    subscription_plan = models.ForeignKey(
        "platform.SubscriptionPlan",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="billing_records",
        help_text=(
            "The subscription plan associated with this billing "
            "record. Null if the plan has been deleted."
        ),
    )

    # ── Billing Fields (Task 80) ─────────────────────────────

    amount = models.DecimalField(
        max_digits=AMOUNT_MAX_DIGITS,
        decimal_places=AMOUNT_DECIMAL_PLACES,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Billing amount in LKR (Sri Lankan Rupees, ₨).",
    )

    tax_amount = models.DecimalField(
        max_digits=AMOUNT_MAX_DIGITS,
        decimal_places=AMOUNT_DECIMAL_PLACES,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Tax amount in LKR applied to this billing record.",
    )

    total_amount = models.DecimalField(
        max_digits=AMOUNT_MAX_DIGITS,
        decimal_places=AMOUNT_DECIMAL_PLACES,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Total amount (amount + tax) in LKR.",
    )

    currency = models.CharField(
        max_length=3,
        default=CURRENCY_CODE,
        help_text="ISO 4217 currency code. Defaults to LKR.",
    )

    invoice_number = models.CharField(
        max_length=INVOICE_NUMBER_MAX_LENGTH,
        unique=True,
        db_index=True,
        help_text=(
            "Unique invoice number for this billing record. "
            "Format: INV-YYYYMM-NNNNN."
        ),
    )

    notes = models.TextField(
        max_length=INVOICE_NOTES_MAX_LENGTH,
        blank=True,
        default="",
        help_text="Optional notes or comments for this billing record.",
    )

    # ── BRN Validation Fields (Task 81) ──────────────────────

    business_registration_number = models.CharField(
        max_length=BRN_MAX_LENGTH,
        blank=True,
        default="",
        validators=[brn_validator],
        help_text=(
            "Sri Lanka Business Registration Number for tax "
            "compliance. Formats: PV12345, PB12345, GA12345."
        ),
    )

    brn_validated = models.BooleanField(
        default=False,
        help_text="Whether the BRN has been validated.",
    )

    brn_validated_on = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the BRN was last validated.",
    )

    # ── Billing Cycle Rules (Task 82) ────────────────────────

    billing_cycle = models.CharField(
        max_length=10,
        choices=BILLING_CYCLE_CHOICES,
        default=CYCLE_MONTHLY,
        help_text="Billing cycle for this record (monthly or annual).",
    )

    period_start = models.DateField(
        help_text="Start date of the billing period.",
    )

    period_end = models.DateField(
        help_text="End date of the billing period.",
    )

    due_date = models.DateField(
        help_text="Payment due date for this billing record.",
    )

    billing_status = models.CharField(
        max_length=20,
        choices=BILLING_STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True,
        help_text=(
            "Current payment status: pending, paid, overdue, "
            "cancelled, or refunded."
        ),
    )

    paid_on = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when payment was received.",
    )

    # ── Meta ─────────────────────────────────────────────────

    class Meta:
        db_table = "platform_billingrecord"
        verbose_name = "Billing Record"
        verbose_name_plural = "Billing Records"
        ordering = ["-period_start", "-created_on"]
        indexes = [
            models.Index(
                fields=["tenant", "-period_start"],
                name="idx_billing_tenant_period",
            ),
            models.Index(
                fields=["billing_status"],
                name="idx_billing_status",
            ),
            models.Index(
                fields=["invoice_number"],
                name="idx_billing_invoice",
            ),
            models.Index(
                fields=["tenant", "billing_status"],
                name="idx_billing_tenant_status",
            ),
            models.Index(
                fields=["due_date", "billing_status"],
                name="idx_billing_due_status",
            ),
            models.Index(
                fields=["-created_on"],
                name="idx_billing_created",
            ),
        ]

    # ── String Representation ────────────────────────────────

    def __str__(self):
        return (
            f"{self.invoice_number} — {CURRENCY_SYMBOL}"
            f"{self.total_amount} ({self.billing_status})"
        )

    # ── Properties ───────────────────────────────────────────

    @property
    def is_paid(self):
        """Return True if the billing record has been paid."""
        return self.billing_status == STATUS_PAID

    @property
    def is_overdue(self):
        """Return True if the billing record is overdue."""
        return self.billing_status == STATUS_OVERDUE

    @property
    def is_pending(self):
        """Return True if the billing record is pending payment."""
        return self.billing_status == STATUS_PENDING

    @property
    def is_cancelled(self):
        """Return True if the billing record has been cancelled."""
        return self.billing_status == STATUS_CANCELLED

    @property
    def is_refunded(self):
        """Return True if the billing record has been refunded."""
        return self.billing_status == STATUS_REFUNDED

    @property
    def has_brn(self):
        """Return True if a business registration number is set."""
        return bool(self.business_registration_number)

    @property
    def amount_display(self):
        """Return a formatted amount string with currency symbol."""
        return f"{CURRENCY_SYMBOL}{self.total_amount}"

    @property
    def period_display(self):
        """Return a human-readable billing period string."""
        return (
            f"{self.period_start:%Y-%m-%d} to "
            f"{self.period_end:%Y-%m-%d}"
        )
