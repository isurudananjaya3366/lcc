"""
Invoice model for the invoices application.

Defines the Invoice model which tracks invoices within a tenant schema.
Supports standard invoices, SVAT invoices, credit notes, and debit notes
with full Sri Lanka tax compliance.
"""

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.mixins import UUIDMixin, TimestampMixin, SoftDeleteMixin
from apps.invoices.constants import (
    ALLOWED_TRANSITIONS,
    CURRENCY_SYMBOLS,
    CurrencyChoice,
    DiscountType,
    EDITABLE_STATES,
    InvoiceStatus,
    InvoiceType,
    TERMINAL_STATES,
    TaxScheme,
)


PRICE_MAX_DIGITS = 15
PRICE_DECIMAL_PLACES = 2


class InvoiceManager(models.Manager):
    """Custom manager for Invoice model."""

    def drafts(self):
        return self.filter(status=InvoiceStatus.DRAFT)

    def issued(self):
        return self.filter(status=InvoiceStatus.ISSUED)

    def paid(self):
        return self.filter(status=InvoiceStatus.PAID)

    def overdue(self):
        return self.filter(status=InvoiceStatus.OVERDUE)

    def active(self):
        """Invoices that are not cancelled, void, or soft-deleted."""
        return self.exclude(
            status__in=[InvoiceStatus.CANCELLED, InvoiceStatus.VOID]
        ).filter(is_deleted=False)

    def unpaid(self):
        """Invoices with outstanding balance."""
        return self.filter(
            status__in=[
                InvoiceStatus.ISSUED,
                InvoiceStatus.SENT,
                InvoiceStatus.PARTIAL,
                InvoiceStatus.OVERDUE,
            ]
        ).filter(is_deleted=False)


class Invoice(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """
    Invoice record for a tenant.

    Tracks the full lifecycle of an invoice from draft creation through
    payment or voiding. Supports standard invoices, simplified VAT (SVAT)
    invoices, credit notes, and debit notes with Sri Lanka compliance.
    """

    # ── Invoice Number & Type ───────────────────────────────────────
    invoice_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        blank=True,
        null=True,
        verbose_name="Invoice Number",
        help_text="Auto-generated on issue. Format: {PREFIX}-YYYY-NNNNN",
    )
    type = models.CharField(
        max_length=20,
        choices=InvoiceType.choices,
        default=InvoiceType.STANDARD,
        db_index=True,
        verbose_name="Invoice Type",
    )
    status = models.CharField(
        max_length=20,
        choices=InvoiceStatus.choices,
        default=InvoiceStatus.DRAFT,
        db_index=True,
        verbose_name="Invoice Status",
    )

    # ── Customer Information (Snapshot) ─────────────────────────────
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="invoices",
        db_index=True,
        verbose_name="Customer",
        help_text="Reference to customer record",
    )
    customer_name = models.CharField(
        max_length=255, blank=True, default="",
        help_text="Customer name at time of invoice",
    )
    customer_email = models.EmailField(
        max_length=255, blank=True, default="",
        help_text="Customer email at time of invoice",
    )
    customer_phone = models.CharField(
        max_length=20, blank=True, default="",
        help_text="Customer phone at time of invoice",
    )
    customer_address = models.TextField(
        blank=True, default="",
        help_text="Customer address at time of invoice",
    )
    customer_tax_id = models.CharField(
        max_length=50, blank=True, default="",
        help_text="Customer VAT or Tax ID number",
    )

    # ── Business/Seller Information (Snapshot) ──────────────────────
    business_name = models.CharField(
        max_length=255, blank=True, default="",
        help_text="Business name at time of invoice",
    )
    business_address = models.TextField(
        blank=True, default="",
        help_text="Business address at time of invoice",
    )
    business_phone = models.CharField(
        max_length=20, blank=True, default="",
        help_text="Business phone at time of invoice",
    )
    business_email = models.EmailField(
        max_length=255, blank=True, default="",
        help_text="Business email at time of invoice",
    )
    business_website = models.URLField(
        max_length=255, blank=True, default="",
        help_text="Business website URL",
    )

    # ── Sri Lanka Compliance Fields ─────────────────────────────────
    business_registration_number = models.CharField(
        max_length=50, blank=True, default="",
        help_text="Business Registration Number (BRN)",
    )
    vat_registration_number = models.CharField(
        max_length=50, blank=True, default="",
        help_text="VAT Registration Number",
    )
    svat_number = models.CharField(
        max_length=50, blank=True, default="",
        help_text="Simplified VAT Registration Number",
    )
    tax_scheme = models.CharField(
        max_length=20,
        choices=TaxScheme.choices,
        default=TaxScheme.VAT,
        help_text="Tax scheme applicable for this invoice",
    )

    # ── Date Fields ─────────────────────────────────────────────────
    issue_date = models.DateField(
        null=True, blank=True,
        help_text="Date the invoice was issued",
    )
    due_date = models.DateField(
        null=True, blank=True,
        help_text="Payment due date",
    )
    paid_date = models.DateField(
        null=True, blank=True,
        help_text="Date full payment was received",
    )
    cancelled_date = models.DateTimeField(
        null=True, blank=True,
        help_text="Date/time the invoice was cancelled",
    )
    voided_date = models.DateTimeField(
        null=True, blank=True,
        help_text="Date/time the invoice was voided",
    )
    sent_date = models.DateField(
        null=True, blank=True,
        help_text="Date invoice was sent to customer",
    )
    payment_terms = models.IntegerField(
        default=30,
        help_text="Payment terms in days (e.g., 30 for Net 30)",
    )

    # ── Financial Fields ────────────────────────────────────────────
    subtotal = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS, decimal_places=PRICE_DECIMAL_PLACES,
        default=Decimal("0.00"),
        help_text="Sum of line item totals before tax and discount",
    )
    discount_type = models.CharField(
        max_length=20,
        choices=DiscountType.choices,
        blank=True, default="",
        help_text="Header-level discount type",
    )
    discount_value = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS, decimal_places=PRICE_DECIMAL_PLACES,
        default=Decimal("0.00"),
        help_text="Discount value (percentage or fixed amount)",
    )
    discount_amount = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS, decimal_places=PRICE_DECIMAL_PLACES,
        default=Decimal("0.00"),
        help_text="Calculated discount amount",
    )
    tax_amount = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS, decimal_places=PRICE_DECIMAL_PLACES,
        default=Decimal("0.00"),
        help_text="Total tax amount",
    )
    total = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS, decimal_places=PRICE_DECIMAL_PLACES,
        default=Decimal("0.00"),
        help_text="Grand total (subtotal - discount + tax)",
    )
    amount_paid = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS, decimal_places=PRICE_DECIMAL_PLACES,
        default=Decimal("0.00"),
        help_text="Total amount paid",
    )
    balance_due = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS, decimal_places=PRICE_DECIMAL_PLACES,
        default=Decimal("0.00"),
        help_text="Remaining balance (total - amount_paid)",
    )

    # ── Tax Breakdown ───────────────────────────────────────────────
    tax_breakdown = models.JSONField(
        default=list, blank=True,
        help_text="Tax breakdown by rate [{rate, taxable_amount, tax_amount}]",
    )

    # ── Reference Fields ────────────────────────────────────────────
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="invoices",
        verbose_name="Source Order",
    )
    related_invoice = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name="adjustment_invoices",
        verbose_name="Related Invoice",
        help_text="Original invoice (for credit/debit notes)",
    )
    external_reference = models.CharField(
        max_length=255, blank=True, default="",
        help_text="External reference number",
    )

    # ── Metadata Fields ─────────────────────────────────────────────
    terms_and_conditions = models.TextField(
        blank=True, default="",
        help_text="Terms and conditions text for invoice",
    )
    payment_instructions = models.TextField(
        blank=True, default="",
        help_text="Payment instructions (bank details, etc.)",
    )
    footer_text = models.TextField(
        blank=True, default="",
        help_text="Custom footer text",
    )
    notes = models.TextField(
        blank=True, default="",
        help_text="Notes visible to customer",
    )
    internal_notes = models.TextField(
        blank=True, default="",
        help_text="Internal notes (not on invoice)",
    )
    custom_fields = models.JSONField(
        default=dict, blank=True,
        help_text="Custom fields for extensibility",
    )
    attachments = models.JSONField(
        default=list, blank=True,
        help_text="List of attachment file references",
    )
    tags = models.JSONField(
        default=list, blank=True,
        help_text="Tags for invoice categorization",
    )

    # ── Currency Fields ─────────────────────────────────────────────
    currency = models.CharField(
        max_length=3, default="LKR", db_index=True,
        help_text="Currency code (ISO 4217)",
    )
    exchange_rate = models.DecimalField(
        max_digits=12, decimal_places=6,
        default=Decimal("1.000000"),
        help_text="Exchange rate to LKR",
    )
    currency_symbol = models.CharField(
        max_length=10, default="LKR",
        help_text="Currency symbol for display",
    )
    base_currency_total = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS, decimal_places=PRICE_DECIMAL_PLACES,
        default=Decimal("0.00"),
        help_text="Total in base currency (LKR)",
    )

    # ── PDF Storage ─────────────────────────────────────────────────
    pdf_file = models.FileField(
        upload_to="invoices/pdfs/%Y/%m/",
        blank=True, null=True,
        help_text="Generated invoice PDF",
    )
    pdf_generated_at = models.DateTimeField(
        null=True, blank=True,
        help_text="When the PDF was last generated",
    )
    pdf_version = models.IntegerField(
        default=0,
        help_text="PDF generation version number",
    )

    # ── User Tracking ───────────────────────────────────────────────
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="invoices_created",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="invoices_updated",
    )

    objects = InvoiceManager()

    class Meta:
        ordering = ["-created_on"]
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
        indexes = [
            models.Index(fields=["status", "type"], name="inv_status_type_idx"),
            models.Index(fields=["customer"], name="inv_customer_idx"),
            models.Index(fields=["issue_date"], name="inv_issue_date_idx"),
            models.Index(fields=["due_date"], name="inv_due_date_idx"),
            models.Index(fields=["order"], name="inv_order_idx"),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(subtotal__gte=Decimal("0")),
                name="inv_subtotal_non_negative",
            ),
            models.CheckConstraint(
                check=models.Q(total__gte=Decimal("0")),
                name="inv_total_non_negative",
            ),
            models.CheckConstraint(
                check=models.Q(amount_paid__gte=Decimal("0")),
                name="inv_amount_paid_non_negative",
            ),
        ]

    def __str__(self):
        if self.invoice_number:
            return self.invoice_number
        return f"Draft {self.get_type_display()} ({str(self.id)[:8]})"

    # ── Properties ──────────────────────────────────────────────────

    @property
    def is_draft(self):
        return self.status == InvoiceStatus.DRAFT

    @property
    def is_editable(self):
        return self.status in EDITABLE_STATES

    @property
    def is_paid(self):
        return self.status == InvoiceStatus.PAID

    @property
    def is_overdue(self):
        if self.status in TERMINAL_STATES:
            return False
        if self.due_date and self.due_date < timezone.now().date():
            return self.balance_due > Decimal("0.00")
        return False

    @property
    def is_cancellable(self):
        return self.status == InvoiceStatus.DRAFT

    @property
    def is_voidable(self):
        return self.status in {
            InvoiceStatus.ISSUED,
            InvoiceStatus.SENT,
            InvoiceStatus.PARTIAL,
            InvoiceStatus.OVERDUE,
        }

    @property
    def needs_pdf_regeneration(self):
        if not self.pdf_generated_at:
            return True
        return self.pdf_generated_at < self.updated_on

    @property
    def days_overdue(self):
        if not self.due_date:
            return 0
        today = timezone.now().date()
        if today > self.due_date:
            return (today - self.due_date).days
        return 0

    @property
    def aging_bucket(self):
        """Return aging bucket: current, 30, 60, 90, 90+."""
        days = self.days_overdue
        if days <= 0:
            return "current"
        elif days <= 30:
            return "1-30"
        elif days <= 60:
            return "31-60"
        elif days <= 90:
            return "61-90"
        return "90+"

    # ── Methods ─────────────────────────────────────────────────────

    def get_available_transitions(self):
        """Return list of valid next statuses."""
        return ALLOWED_TRANSITIONS.get(self.status, [])

    def can_transition_to(self, new_status):
        """Check if transition to new_status is allowed."""
        return new_status in self.get_available_transitions()

    def format_currency(self):
        """Format total with currency symbol."""
        symbol = CURRENCY_SYMBOLS.get(self.currency, self.currency)
        return f"{symbol} {self.total:,.2f}"

    def calculate_base_currency_total(self):
        """Convert invoice total to LKR."""
        if self.currency == "LKR":
            self.base_currency_total = self.total
        else:
            self.base_currency_total = self.total * self.exchange_rate

    def recalculate_balance(self):
        """Recalculate balance_due from total and amount_paid."""
        self.balance_due = self.total - self.amount_paid
