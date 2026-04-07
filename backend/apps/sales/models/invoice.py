"""
Invoice model for the sales application.

Defines the Invoice model which handles billing within a tenant
schema. Invoices can optionally link to orders, track a status
lifecycle, and support partial payments. All monetary values are
stored in LKR (₨).
"""

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.mixins import UUIDMixin, TimestampMixin, SoftDeleteMixin
from apps.sales.constants import (
    DEFAULT_INVOICE_STATUS,
    INVOICE_STATUS_CHOICES,
    INVOICE_STATUS_PAID,
    INVOICE_STATUS_CANCELLED,
)

# Price field constants (consistent across all apps)
PRICE_MAX_DIGITS = 10
PRICE_DECIMAL_PLACES = 2


class Invoice(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """
    Sales invoice for billing.

    Manages the invoicing lifecycle from draft creation through to
    payment collection. Invoices can optionally link to an order,
    and support partial payments through related Payment records.
    All monetary values are in LKR (₨).

    Status workflow:
        draft → sent → paid
                    ↘ partially_paid → paid
                    ↘ overdue
                              ↘ cancelled

    Fields:
        invoice_number: Unique invoice identifier within the tenant.
        order: Optional FK to the Order being invoiced.
        customer: FK to the Customer being billed.
        status: Current invoice status in the lifecycle.
        invoice_date: Date the invoice was issued.
        due_date: Payment due date.
        subtotal: Sum of all line item amounts before tax/discount.
        tax_amount: Total tax on the invoice.
        discount_amount: Total discount applied.
        total_amount: Final amount due (subtotal + tax - discount).
        amount_paid: Total amount received via payments.
        notes: Optional notes about this invoice.
        created_by: User who created the invoice.
    """

    # ── Invoice Number ──────────────────────────────────────────────
    invoice_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="Invoice Number",
        help_text=(
            "Unique invoice identifier within the tenant. "
            "Uses tenant-specific prefix + sequence."
        ),
    )

    # ── Order FK (Optional) ─────────────────────────────────────────
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sales_invoices",
        verbose_name="Order",
        help_text="Optional link to the order being invoiced.",
    )

    # ── Customer FK ─────────────────────────────────────────────────
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        related_name="sales_invoices",
        verbose_name="Customer",
        help_text="The customer being billed.",
    )

    # ── Status ──────────────────────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=INVOICE_STATUS_CHOICES,
        default=DEFAULT_INVOICE_STATUS,
        db_index=True,
        verbose_name="Invoice Status",
        help_text="Current status in the invoice lifecycle.",
    )

    # ── Dates ───────────────────────────────────────────────────────
    invoice_date = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Invoice Date",
        help_text="Date and time the invoice was issued.",
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Due Date",
        help_text="Payment due date for this invoice.",
    )

    # ── Financial Totals (LKR) ──────────────────────────────────────
    subtotal = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS,
        decimal_places=PRICE_DECIMAL_PLACES,
        default=0,
        verbose_name="Subtotal (LKR)",
        help_text="Sum of all line item amounts before tax and discount.",
    )
    tax_amount = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS,
        decimal_places=PRICE_DECIMAL_PLACES,
        default=0,
        verbose_name="Tax Amount (LKR)",
        help_text="Total tax amount for the invoice.",
    )
    discount_amount = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS,
        decimal_places=PRICE_DECIMAL_PLACES,
        default=0,
        verbose_name="Discount Amount (LKR)",
        help_text="Total discount applied to the invoice.",
    )
    total_amount = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS,
        decimal_places=PRICE_DECIMAL_PLACES,
        default=0,
        verbose_name="Total Amount (LKR)",
        help_text="Final amount due (subtotal + tax - discount).",
    )
    amount_paid = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS,
        decimal_places=PRICE_DECIMAL_PLACES,
        default=0,
        verbose_name="Amount Paid (LKR)",
        help_text="Total amount received via payments.",
    )

    # ── Notes & Audit ───────────────────────────────────────────────
    notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Notes",
        help_text="Optional notes about this invoice.",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_invoices",
        verbose_name="Created By",
        help_text="The user who created this invoice.",
    )

    class Meta:
        db_table = "sales_invoice"
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
        ordering = ["-invoice_date"]
        indexes = [
            models.Index(
                fields=["status", "invoice_date"],
                name="idx_invoice_status_date",
            ),
            models.Index(
                fields=["customer", "status"],
                name="idx_invoice_customer_status",
            ),
            models.Index(
                fields=["-invoice_date"],
                name="idx_invoice_date_desc",
            ),
            models.Index(
                fields=["due_date"],
                name="idx_invoice_due_date",
            ),
        ]

    def __str__(self):
        return f"Invoice {self.invoice_number} — {self.get_status_display()}"

    def calculate_totals(self):
        """Recalculate invoice totals."""
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount

    @property
    def balance_due(self):
        """Return the remaining balance to be paid."""
        return self.total_amount - self.amount_paid

    @property
    def is_paid(self):
        """Return True if the invoice is fully paid."""
        return self.status == INVOICE_STATUS_PAID

    @property
    def is_overdue(self):
        """Return True if the invoice is past due date and unpaid."""
        if self.due_date and self.status not in (
            INVOICE_STATUS_PAID,
            INVOICE_STATUS_CANCELLED,
        ):
            return timezone.now().date() > self.due_date
        return False

    @property
    def is_cancelled(self):
        """Return True if the invoice has been cancelled."""
        return self.status == INVOICE_STATUS_CANCELLED
