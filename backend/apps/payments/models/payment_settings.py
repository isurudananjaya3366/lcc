"""
Payment settings model.

Per-tenant configuration for payment processing options,
thresholds, and policies.
"""

from decimal import Decimal

from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin


class LateFeeType(models.TextChoices):
    """Late fee calculation types."""

    PERCENTAGE = "PERCENTAGE", "Percentage of Outstanding"
    FIXED = "FIXED", "Fixed Amount"


class PaymentSettings(UUIDMixin, TimestampMixin, models.Model):
    """
    Tenant-specific payment configuration.

    Controls payment processing options, approval thresholds,
    duplicate detection windows, default currency, late fees,
    notifications, receipt customization, and allocation settings.
    Only one record per tenant (enforced by unique constraint on implicit tenant).
    """

    # ── General Payment Settings ────────────────────────────────────

    default_currency = models.CharField(
        max_length=3,
        default="LKR",
        verbose_name="Default Currency",
        help_text="Default currency for payments.",
    )
    default_payment_terms_days = models.IntegerField(
        default=30,
        verbose_name="Default Payment Terms (days)",
        help_text="Default payment terms in days (e.g., Net 30).",
    )
    approval_threshold = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Approval Threshold",
        help_text="Payments above this amount require approval. 0 = no approval required.",
    )
    duplicate_detection_minutes = models.IntegerField(
        default=5,
        verbose_name="Duplicate Detection Window (minutes)",
        help_text="Time window for duplicate payment detection.",
    )
    require_invoice_for_payment = models.BooleanField(
        default=False,
        verbose_name="Require Invoice",
        help_text="Whether payments must be linked to an invoice.",
    )
    allow_overpayment = models.BooleanField(
        default=False,
        verbose_name="Allow Overpayment",
        help_text="Whether payments can exceed invoice balance.",
    )
    convert_overpayment_to_credit = models.BooleanField(
        default=True,
        verbose_name="Convert Overpayment to Credit",
        help_text="Convert overpayments to store credit.",
    )
    require_customer_for_payment = models.BooleanField(
        default=True,
        verbose_name="Require Customer",
        help_text="Require customer to be specified for all payments.",
    )
    auto_complete_cash = models.BooleanField(
        default=True,
        verbose_name="Auto-Complete Cash",
        help_text="Automatically mark cash payments as completed.",
    )
    enable_processing_fees = models.BooleanField(
        default=False,
        verbose_name="Enable Processing Fees",
        help_text="Whether to calculate and charge processing fees.",
    )
    auto_allocate_to_oldest = models.BooleanField(
        default=True,
        verbose_name="Auto-Allocate to Oldest",
        help_text="Automatically allocate payments to oldest invoices first.",
    )

    # ── Late Fee Configuration ──────────────────────────────────────

    grace_period_days = models.IntegerField(
        default=0,
        verbose_name="Grace Period (days)",
        help_text="Grace period before applying late fees.",
    )
    enable_late_fees = models.BooleanField(
        default=False,
        verbose_name="Enable Late Fees",
        help_text="Enable late payment fees.",
    )
    late_fee_type = models.CharField(
        max_length=20,
        choices=LateFeeType.choices,
        default=LateFeeType.PERCENTAGE,
        verbose_name="Late Fee Type",
        help_text="Type of late fee calculation.",
    )
    late_fee_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Late Fee Value",
        help_text="Late fee amount (percentage or fixed amount in LKR).",
    )
    late_fee_frequency = models.CharField(
        max_length=20,
        choices=[
            ("ONCE", "Once"),
            ("DAILY", "Daily"),
            ("WEEKLY", "Weekly"),
            ("MONTHLY", "Monthly"),
        ],
        default="ONCE",
        verbose_name="Late Fee Frequency",
        help_text="How often to apply late fees.",
    )

    # ── Notification Settings ───────────────────────────────────────

    send_payment_confirmation = models.BooleanField(
        default=True,
        verbose_name="Send Payment Confirmation",
        help_text="Send email confirmation on payment receipt.",
    )
    send_payment_receipt = models.BooleanField(
        default=True,
        verbose_name="Send Payment Receipt",
        help_text="Auto-generate and send payment receipts.",
    )
    payment_reminder_days = models.IntegerField(
        default=7,
        verbose_name="Payment Reminder Days",
        help_text="Days before due date to send payment reminder.",
    )
    send_overdue_reminders = models.BooleanField(
        default=True,
        verbose_name="Send Overdue Reminders",
        help_text="Send reminders for overdue payments.",
    )

    # ── Receipt Settings ────────────────────────────────────────────

    receipt_prefix = models.CharField(
        max_length=10,
        default="REC",
        verbose_name="Receipt Prefix",
        help_text="Prefix for receipt numbers (e.g., REC-2026-00001).",
    )
    receipt_header_text = models.TextField(
        blank=True,
        default="",
        verbose_name="Receipt Header Text",
        help_text="Custom header text for payment receipts.",
    )
    receipt_footer_text = models.TextField(
        blank=True,
        default="",
        verbose_name="Receipt Footer Text",
        help_text="Custom footer text for payment receipts (terms, contact info).",
    )
    include_company_logo = models.BooleanField(
        default=True,
        verbose_name="Include Company Logo",
        help_text="Include company logo on receipts.",
    )
    include_payment_method_details = models.BooleanField(
        default=True,
        verbose_name="Include Payment Method Details",
        help_text="Include payment method details (card last 4, etc.) on receipt.",
    )

    # ── Currency Settings ───────────────────────────────────────────

    currency_symbol = models.CharField(
        max_length=5,
        default="Rs.",
        verbose_name="Currency Symbol",
        help_text="Currency symbol for display.",
    )
    decimal_places = models.IntegerField(
        default=2,
        verbose_name="Decimal Places",
        help_text="Number of decimal places for currency.",
    )

    class Meta:
        db_table = "payments_paymentsettings"
        verbose_name = "Payment Settings"
        verbose_name_plural = "Payment Settings"

    def __str__(self):
        return f"PaymentSettings (currency={self.default_currency})"

    def calculate_late_fee(self, outstanding_amount):
        """
        Calculate late fee based on settings.

        Args:
            outstanding_amount: Decimal outstanding balance.

        Returns:
            Decimal: Late fee amount.
        """
        if not self.enable_late_fees:
            return Decimal("0.00")

        if self.late_fee_type == LateFeeType.PERCENTAGE:
            fee = outstanding_amount * (self.late_fee_value / 100)
        else:
            fee = self.late_fee_value

        return fee.quantize(Decimal("0.01"))

    def get_receipt_number_format(self):
        """Get receipt number format string."""
        return f"{self.receipt_prefix}-{{year}}-{{sequence:05d}}"
