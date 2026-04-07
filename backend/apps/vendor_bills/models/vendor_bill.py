"""VendorBill model for tracking vendor invoices."""

from datetime import date
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import SoftDeleteMixin, TimestampMixin, UUIDMixin
from apps.vendor_bills.constants import (
    BILL_STATUS_CHOICES,
    BILL_STATUS_DRAFT,
    DEFAULT_CURRENCY,
    MATCHING_STATUS_CHOICES,
    MATCHING_STATUS_NOT_MATCHED,
    PAYMENT_TERMS_CHOICES,
    PAYMENT_TERMS_NET30,
)


class VendorBill(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """Represents a vendor bill/invoice for goods or services received."""

    # Core fields
    bill_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        db_index=True,
        help_text="Auto-generated bill number (BILL-YYYY-NNNNN)",
    )
    status = models.CharField(
        max_length=20,
        choices=BILL_STATUS_CHOICES,
        default=BILL_STATUS_DRAFT,
        db_index=True,
        help_text="Current bill status",
    )

    # Vendor fields (Task 05)
    vendor = models.ForeignKey(
        "vendors.Vendor",
        on_delete=models.PROTECT,
        related_name="bills",
        help_text="Vendor who issued this bill",
    )
    vendor_invoice_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Vendor's own invoice/reference number",
    )

    # PO Reference (Task 06)
    purchase_order = models.ForeignKey(
        "purchases.PurchaseOrder",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bills",
        help_text="Associated purchase order (optional for manual bills)",
    )

    # Date fields (Task 07)
    bill_date = models.DateField(
        help_text="Date on the vendor's invoice",
    )
    received_date = models.DateField(
        help_text="Date the bill was received",
    )
    due_date = models.DateField(
        db_index=True,
        help_text="Payment due date",
    )

    # Financial fields (Task 08)
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Sum of line item totals before tax and discount",
    )
    tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Total tax amount",
    )
    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Total discount amount",
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Grand total (subtotal + tax - discount)",
    )
    currency = models.CharField(
        max_length=3,
        default=DEFAULT_CURRENCY,
        help_text="Bill currency code",
    )

    # Payment fields (Task 09)
    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Amount paid so far",
    )
    payment_terms = models.CharField(
        max_length=50,
        choices=PAYMENT_TERMS_CHOICES,
        default=PAYMENT_TERMS_NET30,
        help_text="Payment terms for this bill",
    )

    # User fields (Task 10)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_bills",
        help_text="User who created this bill",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_bills",
        help_text="User who approved this bill",
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the bill was approved",
    )

    # Notes fields (Task 11)
    notes = models.TextField(
        blank=True,
        help_text="General notes visible to all",
    )
    internal_notes = models.TextField(
        blank=True,
        help_text="Internal notes not shared with vendor",
    )
    dispute_reason = models.TextField(
        blank=True,
        null=True,
        help_text="Reason for disputing the bill",
    )

    # Document fields (Task 12)
    attachment = models.FileField(
        upload_to="vendor_bills/%Y/",
        blank=True,
        null=True,
        help_text="Scanned copy of vendor invoice",
    )

    # Matching fields (Task 13)
    is_matched = models.BooleanField(
        default=False,
        help_text="Whether this bill has been matched to PO/GRN",
    )
    matched_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the bill was matched",
    )
    matching_variance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Absolute variance amount from matching",
    )
    matching_variance_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Variance as a percentage of PO total",
    )
    matching_status = models.CharField(
        max_length=30,
        choices=MATCHING_STATUS_CHOICES,
        default=MATCHING_STATUS_NOT_MATCHED,
        help_text="Status of the 3-way matching process",
    )

    class Meta:
        ordering = ["-created_on"]
        verbose_name = "Vendor Bill"
        verbose_name_plural = "Vendor Bills"
        indexes = [
            models.Index(fields=["status"], name="idx_vendorbill_status"),
            models.Index(fields=["due_date"], name="idx_vendorbill_due_date"),
            models.Index(fields=["bill_date"], name="idx_vendorbill_bill_date"),
            models.Index(fields=["status", "vendor"], name="idx_status_vendor"),
            models.Index(fields=["status", "due_date"], name="idx_status_due"),
            models.Index(fields=["vendor", "bill_date"], name="idx_vendor_date"),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(subtotal__gte=Decimal("0")),
                name="vendorbill_subtotal_non_negative",
            ),
            models.CheckConstraint(
                check=models.Q(tax_amount__gte=Decimal("0")),
                name="vendorbill_tax_non_negative",
            ),
            models.CheckConstraint(
                check=models.Q(discount_amount__gte=Decimal("0")),
                name="vendorbill_discount_non_negative",
            ),
            models.CheckConstraint(
                check=models.Q(total__gte=Decimal("0")),
                name="vendorbill_total_non_negative",
            ),
            models.CheckConstraint(
                check=models.Q(amount_paid__gte=Decimal("0")),
                name="vendorbill_amount_paid_non_negative",
            ),
        ]

    def __str__(self):
        return f"{self.bill_number} - {self.vendor}"

    def save(self, *args, **kwargs):
        if not self.bill_number:
            self.bill_number = self._generate_bill_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_bill_number():
        """Generate next bill number in BILL-YYYY-NNNNN format."""
        current_year = timezone.now().year
        prefix = f"BILL-{current_year}-"
        last_bill = (
            VendorBill.objects.filter(bill_number__startswith=prefix)
            .order_by("-bill_number")
            .first()
        )
        if last_bill:
            last_seq = int(last_bill.bill_number.split("-")[-1])
            next_seq = last_seq + 1
        else:
            next_seq = 1
        return f"{prefix}{next_seq:05d}"

    # Date properties (Task 07)
    @property
    def is_overdue(self):
        """Check if the bill is past its due date and not fully paid."""
        if self.status in (BILL_STATUS_DRAFT, "paid", "cancelled"):
            return False
        return self.due_date < date.today()

    @property
    def days_until_due(self):
        """Days remaining until the due date (negative if overdue)."""
        return (self.due_date - date.today()).days

    @property
    def days_overdue(self):
        """Number of days the bill is overdue (0 if not overdue)."""
        if not self.is_overdue:
            return 0
        return (date.today() - self.due_date).days

    @property
    def aging_bucket(self):
        """Return the aging bucket for this bill."""
        from apps.vendor_bills.constants import (
            AGING_1_30,
            AGING_31_60,
            AGING_61_90,
            AGING_CURRENT,
            AGING_OVER_90,
        )

        days = self.days_overdue
        if days <= 0:
            return AGING_CURRENT
        elif days <= 30:
            return AGING_1_30
        elif days <= 60:
            return AGING_31_60
        elif days <= 90:
            return AGING_61_90
        else:
            return AGING_OVER_90

    @property
    def amount_due(self):
        """Calculate the remaining amount due."""
        return self.total - self.amount_paid

    def recalculate_from_lines(self):
        """Recalculate bill totals from line items."""
        from django.db.models import Sum

        aggregates = self.line_items.aggregate(
            total_base=Sum("line_total"),
            total_tax=Sum("tax_amount"),
        )
        self.subtotal = (aggregates["total_base"] or Decimal("0.00")) - (
            aggregates["total_tax"] or Decimal("0.00")
        )
        self.tax_amount = aggregates["total_tax"] or Decimal("0.00")
        self.total = (self.subtotal + self.tax_amount) - self.discount_amount
        self.save(update_fields=["subtotal", "tax_amount", "total"])
