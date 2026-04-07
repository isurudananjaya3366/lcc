"""
Refund model.

Tracks refund transactions linked to original payments with
approval workflow and multiple refund methods.
"""

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.mixins import UUIDMixin, TimestampMixin


class RefundReason(models.TextChoices):
    """Reasons for issuing a refund."""

    CUSTOMER_REQUEST = "CUSTOMER_REQUEST", "Customer Request"
    OVERPAYMENT = "OVERPAYMENT", "Overpayment"
    DUPLICATE = "DUPLICATE", "Duplicate Payment"
    CANCELLED = "CANCELLED", "Order Cancelled"
    RETURN = "RETURN", "Goods Return"
    DEFECTIVE = "DEFECTIVE", "Defective Product"
    LATE_DELIVERY = "LATE_DELIVERY", "Delivery Issues"
    PRICING_ERROR = "PRICING_ERROR", "Pricing Error"
    SERVICE_ISSUE = "SERVICE_ISSUE", "Service Not Rendered"
    BILLING_ERROR = "BILLING_ERROR", "Billing Error"
    GOODWILL = "GOODWILL", "Goodwill Gesture"
    OTHER = "OTHER", "Other"


class RefundMethod(models.TextChoices):
    """Method for issuing the refund."""

    ORIGINAL = "ORIGINAL", "Original Payment Method"
    CASH = "CASH", "Cash"
    BANK_TRANSFER = "BANK_TRANSFER", "Bank Transfer"
    CHECK = "CHECK", "Check"
    STORE_CREDIT = "STORE_CREDIT", "Store Credit"


class RefundStatus(models.TextChoices):
    """Refund lifecycle statuses."""

    PENDING = "PENDING", "Pending"
    APPROVED = "APPROVED", "Approved"
    PROCESSING = "PROCESSING", "Processing"
    PROCESSED = "PROCESSED", "Processed"
    REJECTED = "REJECTED", "Rejected"
    FAILED = "FAILED", "Failed"
    CANCELLED = "CANCELLED", "Cancelled"


REFUND_TRANSITIONS = {
    RefundStatus.PENDING: [RefundStatus.APPROVED, RefundStatus.REJECTED, RefundStatus.CANCELLED],
    RefundStatus.APPROVED: [RefundStatus.PROCESSING, RefundStatus.PROCESSED, RefundStatus.CANCELLED],
    RefundStatus.PROCESSING: [RefundStatus.PROCESSED, RefundStatus.FAILED],
    RefundStatus.PROCESSED: [],
    RefundStatus.REJECTED: [],
    RefundStatus.FAILED: [RefundStatus.PROCESSING],  # Allow retry
    RefundStatus.CANCELLED: [],
}


class Refund(UUIDMixin, TimestampMixin, models.Model):
    """
    Refund record linked to an original payment.

    Tracks the full lifecycle from request through approval
    to processing, with support for multiple refund methods.
    """

    refund_number = models.CharField(
        max_length=30,
        unique=True,
        db_index=True,
        verbose_name="Refund Number",
        help_text="Format: REF-YYYY-NNNNN",
    )
    original_payment = models.ForeignKey(
        "payments.Payment",
        on_delete=models.PROTECT,
        related_name="refunds",
        verbose_name="Original Payment",
        help_text="The original payment being refunded.",
    )
    invoice = models.ForeignKey(
        "invoices.Invoice",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="refunds",
        verbose_name="Invoice",
        help_text="Invoice related to this refund.",
    )
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="refunds",
        verbose_name="Customer",
        help_text="Customer receiving the refund.",
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Refund Amount",
    )
    reason = models.CharField(
        max_length=30,
        choices=RefundReason.choices,
        verbose_name="Reason",
    )
    reason_notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Reason Details",
        help_text="Additional details about the refund reason.",
    )
    refund_method = models.CharField(
        max_length=20,
        choices=RefundMethod.choices,
        default=RefundMethod.ORIGINAL,
        verbose_name="Refund Method",
    )
    status = models.CharField(
        max_length=20,
        choices=RefundStatus.choices,
        default=RefundStatus.PENDING,
        db_index=True,
        verbose_name="Status",
    )
    rejection_reason = models.TextField(
        blank=True,
        default="",
        verbose_name="Rejection Reason",
        help_text="Reason for rejection (if rejected).",
    )

    # ── User References ─────────────────────────────────────────────
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="refunds_requested",
        verbose_name="Requested By",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="refunds_approved",
        verbose_name="Approved By",
    )
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="refunds_processed",
        verbose_name="Processed By",
    )

    # ── Timestamps ──────────────────────────────────────────────────
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Approved At",
    )
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Processed At",
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Completed At",
        help_text="When refund was fully completed.",
    )

    # ── External References ─────────────────────────────────────────
    transaction_id = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Transaction ID",
        help_text="External refund transaction ID (payment gateway).",
    )
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Reference Number",
        help_text="Bank/payment processor reference number.",
    )

    # ── Bank Details (for BANK_TRANSFER refunds) ────────────────────
    bank_account_name = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Account Holder Name",
    )
    bank_account_number = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Bank Account Number",
    )
    bank_name = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Bank Name",
    )
    bank_branch = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Bank Branch",
    )

    # ── Check Details (for CHECK refunds) ───────────────────────────
    check_number = models.CharField(
        max_length=50,
        blank=True,
        default="",
        verbose_name="Check Number",
    )
    check_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Check Date",
    )

    # ── Store Credit Details ────────────────────────────────────────
    store_credit_id = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Store Credit ID",
        help_text="Store credit ID created for this refund.",
    )

    # ── Notes ───────────────────────────────────────────────────────
    notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Notes",
    )
    customer_notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Customer Notes",
        help_text="Notes visible to the customer.",
    )

    class Meta:
        db_table = "payments_refund"
        ordering = ["-created_on"]
        verbose_name = "Refund"
        verbose_name_plural = "Refunds"
        indexes = [
            models.Index(fields=["status"], name="idx_refund_status"),
            models.Index(fields=["original_payment"], name="idx_refund_payment"),
            models.Index(fields=["customer", "-created_on"], name="idx_refund_customer"),
            models.Index(fields=["invoice"], name="idx_refund_invoice"),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount__gt=0),
                name="refund_amount_positive",
            ),
        ]

    def __str__(self):
        return f"{self.refund_number} - {self.amount} ({self.status})"

    # ── Helper Methods ──────────────────────────────────────────────

    def can_be_cancelled(self):
        """Check if refund can be cancelled."""
        return self.status in (RefundStatus.PENDING, RefundStatus.APPROVED)

    def can_be_approved(self):
        """Check if refund can be approved."""
        return self.status == RefundStatus.PENDING

    def can_be_rejected(self):
        """Check if refund can be rejected."""
        return self.status == RefundStatus.PENDING

    def can_be_processed(self):
        """Check if refund can be processed."""
        return self.status in (RefundStatus.APPROVED, RefundStatus.FAILED)

    def is_pending_approval(self):
        """Check if refund is pending approval."""
        return self.status == RefundStatus.PENDING

    def is_completed(self):
        """Check if refund has been processed/completed."""
        return self.status == RefundStatus.PROCESSED

    def get_processing_time(self):
        """Calculate processing time from request to completion."""
        if self.completed_at and self.created_on:
            return self.completed_at - self.created_on
        if self.processed_at and self.created_on:
            return self.processed_at - self.created_on
        return None
