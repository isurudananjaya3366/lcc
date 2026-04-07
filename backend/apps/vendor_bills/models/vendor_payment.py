"""VendorPayment model for recording payments to vendors."""

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import SoftDeleteMixin, TimestampMixin, UUIDMixin
from apps.vendor_bills.constants import (
    PAYMENT_METHOD_BANK_TRANSFER,
    PAYMENT_METHOD_CHOICES,
    VENDOR_PAYMENT_STATUS_CHOICES,
    VENDOR_PAYMENT_STATUS_COMPLETED,
    VENDOR_PAYMENT_STATUS_PENDING,
)


class VendorPayment(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """Records a payment made to a vendor for a bill or as an advance."""

    # Core fields
    payment_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        db_index=True,
        help_text="Auto-generated payment number (PAY-YYYY-NNNNN)",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Payment amount",
    )
    payment_date = models.DateField(
        db_index=True,
        help_text="Date the payment was made",
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default=PAYMENT_METHOD_BANK_TRANSFER,
        help_text="Method of payment",
    )
    status = models.CharField(
        max_length=20,
        choices=VENDOR_PAYMENT_STATUS_CHOICES,
        default=VENDOR_PAYMENT_STATUS_PENDING,
        db_index=True,
        help_text="Current payment status",
    )

    # Relationships
    vendor = models.ForeignKey(
        "vendors.Vendor",
        on_delete=models.PROTECT,
        related_name="payments",
        help_text="Vendor receiving this payment",
    )
    vendor_bill = models.ForeignKey(
        "vendor_bills.VendorBill",
        on_delete=models.CASCADE,
        related_name="payments",
        null=True,
        blank=True,
        help_text="Bill this payment applies to (null for advances)",
    )

    # Reference / tracking
    reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="External reference or transaction reference",
    )
    check_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Check/cheque number if payment method is check",
    )
    bank_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Bank name for bank transfers",
    )
    bank_account_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="Bank account number used for payment",
    )
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Transaction ID from bank or gateway",
    )

    # Notes
    notes = models.TextField(
        blank=True,
        help_text="Payment notes",
    )

    # User fields
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_payments",
        help_text="User who recorded this payment",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_payments",
        help_text="User who approved this payment",
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the payment was approved",
    )

    # Advance payment flag
    is_advance = models.BooleanField(
        default=False,
        help_text="Whether this is an advance payment without a bill",
    )

    # Currency
    currency = models.CharField(
        max_length=3,
        default="LKR",
        help_text="Payment currency code",
    )

    class Meta:
        ordering = ["-payment_date", "-created_on"]
        verbose_name = "Vendor Payment"
        verbose_name_plural = "Vendor Payments"
        indexes = [
            models.Index(fields=["status"], name="idx_vpay_status"),
            models.Index(fields=["payment_date"], name="idx_vpay_date"),
            models.Index(fields=["vendor", "payment_date"], name="idx_vpay_vendor_date"),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount__gt=Decimal("0")),
                name="vpay_amount_positive",
            ),
        ]

    def __str__(self):
        return f"{self.payment_number} - {self.vendor} - {self.amount}"

    def save(self, *args, **kwargs):
        if not self.payment_number:
            self.payment_number = self._generate_payment_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_payment_number():
        """Generate next payment number in PAY-YYYY-NNNNN format."""
        current_year = timezone.now().year
        prefix = f"PAY-{current_year}-"
        last_payment = (
            VendorPayment.objects.filter(payment_number__startswith=prefix)
            .order_by("-payment_number")
            .first()
        )
        if last_payment:
            last_seq = int(last_payment.payment_number.split("-")[-1])
            next_seq = last_seq + 1
        else:
            next_seq = 1
        return f"{prefix}{next_seq:05d}"

    @property
    def is_completed(self):
        """Check if the payment has been completed."""
        return self.status == VENDOR_PAYMENT_STATUS_COMPLETED
