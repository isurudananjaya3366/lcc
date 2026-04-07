"""
Payment model.

Core model for tracking payment transactions with support for
multiple payment methods, currencies, and invoice/order linkage.
"""

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.mixins import UUIDMixin, TimestampMixin, SoftDeleteMixin
from apps.payments.constants import PaymentMethod, PaymentStatus


class Payment(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """
    Payment record for a tenant.

    Tracks individual payment transactions including method, status,
    amount, and linkage to invoices, orders, and customers. Supports
    multi-currency with exchange rate tracking.
    """

    # ── Payment Number ──────────────────────────────────────────────
    payment_number = models.CharField(
        max_length=30,
        unique=True,
        db_index=True,
        blank=True,
        verbose_name="Payment Number",
        help_text="Auto-generated. Format: PAY-YYYY-NNNNN",
    )

    # ── Method & Status ─────────────────────────────────────────────
    method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        db_index=True,
        verbose_name="Payment Method",
        help_text="Method of payment (e.g. cash, card, bank transfer).",
    )
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True,
        verbose_name="Payment Status",
    )

    # ── Amount ──────────────────────────────────────────────────────
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Amount",
        help_text="Payment amount in the specified currency.",
    )

    # ── References ──────────────────────────────────────────────────
    invoice = models.ForeignKey(
        "invoices.Invoice",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name="Invoice",
        help_text="Linked invoice (if applicable).",
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name="Order",
        help_text="Linked order (if applicable).",
    )
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name="Customer",
        help_text="Customer who made the payment.",
    )

    # ── Date Fields ─────────────────────────────────────────────────
    payment_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Payment Date",
        help_text="Date the payment was received.",
    )
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Processed At",
        help_text="Timestamp when the payment was processed/completed.",
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Cancelled At",
        help_text="Timestamp when the payment was cancelled.",
    )

    # ── Currency Fields ─────────────────────────────────────────────
    currency = models.CharField(
        max_length=3,
        default="LKR",
        verbose_name="Currency",
        help_text="ISO 4217 currency code (e.g. LKR, USD).",
    )
    exchange_rate = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="Exchange Rate",
        help_text="Exchange rate to base currency (LKR). 1.0 for LKR payments.",
    )
    amount_in_base_currency = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Amount in Base Currency",
        help_text="Payment amount converted to base currency (LKR).",
    )

    # ── Method Details ──────────────────────────────────────────────
    method_details = models.JSONField(
        null=True,
        blank=True,
        default=None,
        verbose_name="Method Details",
        help_text=(
            "Method-specific details. Card: last4, card_type, approval_code. "
            "Check: check_number, bank_name. Mobile: provider, transaction_id."
        ),
    )

    # ── External References ─────────────────────────────────────────
    reference_number = models.CharField(
        max_length=50,
        blank=True,
        default="",
        verbose_name="Reference Number",
        help_text="External reference (gateway or bank reference).",
    )
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Transaction ID",
        help_text="External payment gateway transaction ID.",
    )

    # ── User References ─────────────────────────────────────────────
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments_received",
        verbose_name="Received By",
        help_text="User who received/recorded the payment.",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments_approved",
        verbose_name="Approved By",
        help_text="User who approved the payment.",
    )

    # ── Notes ───────────────────────────────────────────────────────
    notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Notes",
        help_text="Customer-visible notes about this payment.",
    )
    internal_notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Internal Notes",
        help_text="Internal notes (not visible to customer).",
    )

    # ── Refund Tracking ─────────────────────────────────────────────
    total_refunded = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name="Total Refunded",
        help_text="Total amount refunded from this payment.",
    )
    refund_status = models.CharField(
        max_length=25,
        default="NOT_REFUNDED",
        db_index=True,
        verbose_name="Refund Status",
        help_text="NOT_REFUNDED, PARTIALLY_REFUNDED, or FULLY_REFUNDED.",
    )

    class Meta:
        db_table = "payments"
        ordering = ["-created_on"]
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        indexes = [
            models.Index(fields=["status"], name="idx_payment_status"),
            models.Index(fields=["method"], name="idx_payment_method"),
            models.Index(fields=["payment_date"], name="idx_payment_date"),
            models.Index(fields=["customer"], name="idx_payment_customer"),
            models.Index(fields=["invoice"], name="idx_payment_invoice"),
            models.Index(fields=["order"], name="idx_payment_order"),
            models.Index(fields=["reference_number"], name="idx_payment_reference"),
            models.Index(fields=["currency"], name="idx_payment_currency"),
            models.Index(
                fields=["customer", "payment_date"],
                name="idx_payment_customer_date",
            ),
            models.Index(
                fields=["status", "method"],
                name="idx_payment_status_method",
            ),
            models.Index(
                fields=["payment_date", "status"],
                name="idx_payment_date_status",
            ),
            models.Index(
                fields=["created_on", "status"],
                name="idx_payment_created_status",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount__gt=0),
                name="payment_amount_positive",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(currency="LKR")
                    | models.Q(exchange_rate__isnull=False)
                ),
                name="payment_foreign_currency_rate_required",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(exchange_rate__isnull=True)
                    | models.Q(exchange_rate__gt=0)
                ),
                name="payment_exchange_rate_positive",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(processed_at__isnull=True)
                    | models.Q(cancelled_at__isnull=True)
                ),
                name="payment_not_both_processed_cancelled",
            ),
        ]

    def __str__(self):
        return f"{self.payment_number} ({self.currency} {self.amount:,.2f})"

    def get_absolute_url(self):
        return f"/api/v1/payments/{self.pk}/"

    def clean(self):
        """Model-level validation."""
        from django.core.exceptions import ValidationError

        errors = {}
        if self.amount is not None and self.amount <= 0:
            errors["amount"] = "Amount must be positive."
        if self.currency != "LKR" and not self.exchange_rate:
            errors["exchange_rate"] = "Exchange rate is required for foreign currencies."
        if self.exchange_rate is not None and self.exchange_rate <= 0:
            errors["exchange_rate"] = "Exchange rate must be positive."
        if self.processed_at and self.cancelled_at:
            errors["status"] = "Payment cannot be both processed and cancelled."
        if errors:
            raise ValidationError(errors)

    # ── Properties ──────────────────────────────────────────────────

    @property
    def has_invoice(self):
        """Whether this payment is linked to an invoice."""
        return self.invoice_id is not None

    @property
    def has_order(self):
        """Whether this payment is linked to an order."""
        return self.order_id is not None

    @property
    def has_customer(self):
        """Whether this payment is linked to a customer."""
        return self.customer_id is not None

    @property
    def is_processed(self):
        """Whether this payment has been processed/completed."""
        return self.status == PaymentStatus.COMPLETED

    @property
    def is_cancelled(self):
        """Whether this payment has been cancelled."""
        return self.status == PaymentStatus.CANCELLED

    @property
    def is_refunded(self):
        """Whether this payment has been refunded."""
        return self.status == PaymentStatus.REFUNDED

    @property
    def is_partially_refunded(self):
        """Whether this payment has been partially refunded."""
        return self.refund_status == "PARTIALLY_REFUNDED"

    @property
    def is_fully_refunded(self):
        """Whether this payment has been fully refunded."""
        return self.refund_status == "FULLY_REFUNDED"

    def get_total_refunded(self):
        """Calculate total refunded amount from PROCESSED refunds."""
        from apps.payments.models.refund import RefundStatus as RS

        return self.refunds.filter(
            status=RS.PROCESSED,
        ).aggregate(
            total=models.Sum("amount"),
        )["total"] or Decimal("0")

    def get_remaining_refundable(self):
        """Amount still available for refunding."""
        from apps.payments.models.refund import RefundStatus as RS

        total_refunded = self.get_total_refunded()
        pending_refunds = self.refunds.filter(
            status__in=[RS.PENDING, RS.APPROVED, RS.PROCESSING],
        ).aggregate(
            total=models.Sum("amount"),
        )["total"] or Decimal("0")

        return self.amount - total_refunded - pending_refunds

    def can_be_refunded(self, amount=None):
        """Check if this payment can be refunded (optionally for a specific amount)."""
        if self.status != PaymentStatus.COMPLETED:
            return False
        remaining = self.get_remaining_refundable()
        if remaining <= 0:
            return False
        if amount is not None:
            return Decimal(str(amount)) <= remaining
        return True

    def update_refund_status(self):
        """Recalculate and update refund tracking fields."""
        total_refunded = self.get_total_refunded()
        self.total_refunded = total_refunded
        if total_refunded == 0:
            self.refund_status = "NOT_REFUNDED"
        elif total_refunded >= self.amount:
            self.refund_status = "FULLY_REFUNDED"
        else:
            self.refund_status = "PARTIALLY_REFUNDED"
        self.save(update_fields=["total_refunded", "refund_status", "updated_on"])

    @property
    def is_pending(self):
        """Whether this payment is still pending."""
        return self.status == PaymentStatus.PENDING

    @property
    def is_failed(self):
        """Whether this payment has failed."""
        return self.status == PaymentStatus.FAILED

    @property
    def is_foreign_currency(self):
        """Whether this payment is in a foreign currency (not LKR)."""
        return self.currency != "LKR"

    @property
    def is_terminal(self):
        """Whether this payment is in a terminal state."""
        from apps.payments.constants import TERMINAL_STATES

        return self.status in TERMINAL_STATES

    # ── Receipt Helpers (Task 68) ───────────────────────────────────

    def has_receipt(self):
        """Check if this payment has an associated receipt."""
        try:
            return self.receipt is not None
        except Exception:
            return False

    def get_receipt(self):
        """Get the receipt for this payment, or None."""
        try:
            return self.receipt
        except Exception:
            return None

    # ── Date Helpers (Task 07) ──────────────────────────────────────

    @property
    def processing_duration(self):
        """Time from creation to processing."""
        if self.processed_at and self.created_on:
            return self.processed_at - self.created_on
        return None

    @property
    def is_dated_check(self):
        """Whether this is a post-dated check."""
        if self.method != PaymentMethod.CHECK or not self.payment_date:
            return False
        return self.payment_date > timezone.now().date()

    # ── Currency Helpers (Task 08) ──────────────────────────────────

    def get_base_amount(self):
        """Return amount in base currency (LKR)."""
        if self.amount_in_base_currency:
            return self.amount_in_base_currency
        return self.amount

    def convert_to_base(self):
        """Calculate and return amount converted to base currency."""
        if self.is_foreign_currency and self.exchange_rate:
            return (self.amount * self.exchange_rate).quantize(Decimal("0.01"))
        return self.amount

    def format_amount(self):
        """Format amount with currency code."""
        return f"{self.currency} {self.amount:,.2f}"

    # ── Method Details Helpers (Task 09) ────────────────────────────

    def get_detail(self, key, default=None):
        """Safely get a value from method_details."""
        if not self.method_details:
            return default
        return self.method_details.get(key, default)

    def set_detail(self, key, value):
        """Safely set a value in method_details."""
        if self.method_details is None:
            self.method_details = {}
        self.method_details[key] = value

    def get_card_last_four(self):
        """Get last four digits of card."""
        return self.get_detail("last_four", "")

    def get_check_number(self):
        """Get check number from method details."""
        return self.get_detail("check_number", "")

    def get_mobile_transaction_id(self):
        """Get mobile transaction ID."""
        return self.get_detail("transaction_id", "")

    def format_payment_details(self):
        """Return human-readable summary of method details."""
        if not self.method_details:
            return ""
        parts = []
        for key, value in self.method_details.items():
            label = key.replace("_", " ").title()
            parts.append(f"{label}: {value}")
        return ", ".join(parts)

    # ── Reference Helpers (Task 10) ─────────────────────────────────

    @property
    def has_reference(self):
        """Whether this payment has a reference number."""
        return bool(self.reference_number)

    def validate_reference_format(self):
        """Validate reference number format based on payment method."""
        if not self.reference_number:
            return True
        return len(self.reference_number) <= 100

    # ── User & Approval Helpers (Task 11) ───────────────────────────

    @property
    def is_approved(self):
        """Whether this payment has been approved."""
        return self.approved_by_id is not None

    def requires_approval(self):
        """Check if this payment requires approval based on settings."""
        from apps.payments.models.payment_settings import PaymentSettings

        try:
            settings_obj = PaymentSettings.objects.first()
            if settings_obj and settings_obj.approval_threshold:
                return self.amount >= settings_obj.approval_threshold
        except Exception:
            pass
        return False

    def approve(self, user):
        """Approve this payment."""
        self.approved_by = user
        self.save(update_fields=["approved_by", "updated_on"])

    # ── Notes Helpers (Task 12) ─────────────────────────────────────

    @property
    def has_notes(self):
        """Whether public notes exist."""
        return bool(self.notes)

    @property
    def has_internal_notes(self):
        """Whether internal notes exist."""
        return bool(self.internal_notes)

    def add_note(self, note_text, user=None, internal=False):
        """Append a timestamped note."""
        timestamp = timezone.now().strftime("%Y-%m-%d %H:%M")
        user_name = str(user) if user else "System"
        entry = f"[{timestamp}] {user_name}: {note_text}"
        if internal:
            self.internal_notes = (
                f"{self.internal_notes}\n{entry}" if self.internal_notes else entry
            )
            self.save(update_fields=["internal_notes", "updated_on"])
        else:
            self.notes = f"{self.notes}\n{entry}" if self.notes else entry
            self.save(update_fields=["notes", "updated_on"])

    def get_public_notes(self):
        """Return customer-visible notes."""
        return self.notes

    def get_internal_notes_for_staff(self):
        """Return internal notes for staff."""
        return self.internal_notes
