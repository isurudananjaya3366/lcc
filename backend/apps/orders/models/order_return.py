"""
OrderReturn and ReturnLineItem models (Tasks 67-72).

Handles customer return requests including reason tracking, approval workflow,
item condition inspection, and refund calculations.
"""

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone

from apps.core.mixins import UUIDMixin, TimestampMixin, SoftDeleteMixin


PRICE_MAX_DIGITS = 12
PRICE_DECIMAL_PLACES = 2
QUANTITY_MAX_DIGITS = 12
QUANTITY_DECIMAL_PLACES = 3


# ════════════════════════════════════════════════════════════════════════
# Return Choices (Tasks 68, 69)
# ════════════════════════════════════════════════════════════════════════


class ReturnReason(models.TextChoices):
    """Reason for a return request (Task 68)."""

    DEFECTIVE = "defective", "Defective"
    WRONG_ITEM = "wrong_item", "Wrong Item"
    CHANGED_MIND = "changed_mind", "Changed Mind"
    NOT_AS_DESCRIBED = "not_as_described", "Not As Described"
    BETTER_PRICE = "better_price", "Better Price"
    DUPLICATE = "duplicate", "Duplicate Order"
    OTHER = "other", "Other"


class ReturnStatus(models.TextChoices):
    """
    Return lifecycle statuses (Task 69).

    Workflow:
        REQUESTED → APPROVED → RECEIVED → REFUNDED
        REQUESTED → REJECTED
    """

    REQUESTED = "requested", "Requested"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    RECEIVED = "received", "Received"
    REFUNDED = "refunded", "Refunded"


class ItemCondition(models.TextChoices):
    """Condition of a returned item (Task 70)."""

    UNOPENED = "unopened", "Unopened"
    OPENED = "opened", "Opened"
    DAMAGED = "damaged", "Damaged"


class RefundMethod(models.TextChoices):
    """Method used to issue a refund (Task 71)."""

    ORIGINAL_PAYMENT = "original_payment", "Original Payment Method"
    STORE_CREDIT = "store_credit", "Store Credit"
    BANK_TRANSFER = "bank_transfer", "Bank Transfer"
    CASH = "cash", "Cash"


# Allowed return status transitions
RETURN_ALLOWED_TRANSITIONS = {
    ReturnStatus.REQUESTED: [ReturnStatus.APPROVED, ReturnStatus.REJECTED],
    ReturnStatus.APPROVED: [ReturnStatus.RECEIVED],
    ReturnStatus.REJECTED: [],
    ReturnStatus.RECEIVED: [ReturnStatus.REFUNDED],
    ReturnStatus.REFUNDED: [],
}

RETURN_TERMINAL_STATES = {ReturnStatus.REJECTED, ReturnStatus.REFUNDED}


# ════════════════════════════════════════════════════════════════════════
# OrderReturn Model (Task 67)
# ════════════════════════════════════════════════════════════════════════


class OrderReturn(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """
    A return request against an order.

    Tracks the return lifecycle from customer request through
    approval, receipt, inspection, and refund.
    """

    # ── Order Reference ─────────────────────────────────────────────
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="returns",
        verbose_name="Order",
    )

    # ── Return Number ───────────────────────────────────────────────
    return_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Return Number",
        help_text="Auto-generated: RET-{YEAR}-{SEQ}",
    )

    # ── Reason (Task 68) ───────────────────────────────────────────
    reason = models.CharField(
        max_length=30,
        choices=ReturnReason.choices,
        default=ReturnReason.OTHER,
    )
    reason_detail = models.TextField(
        blank=True,
        default="",
        help_text="Additional details about the return reason.",
    )

    # ── Status (Task 69) ───────────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=ReturnStatus.choices,
        default=ReturnStatus.REQUESTED,
    )

    # ── Request Tracking ────────────────────────────────────────────
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="return_requests",
    )
    requested_at = models.DateTimeField(default=timezone.now)

    # ── Approval / Rejection (Task 69) ─────────────────────────────
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_returns",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rejected_returns",
    )
    rejected_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, default="")
    approval_notes = models.TextField(blank=True, default="")

    # ── Receipt Tracking ────────────────────────────────────────────
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="received_returns",
    )
    received_at = models.DateTimeField(null=True, blank=True)

    # ── Financial Fields (Task 71) ──────────────────────────────────
    refund_amount = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS,
        decimal_places=PRICE_DECIMAL_PLACES,
        default=0,
        validators=[MinValueValidator(0)],
    )
    restocking_fee = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS,
        decimal_places=PRICE_DECIMAL_PLACES,
        default=0,
        validators=[MinValueValidator(0)],
    )
    refund_shipping = models.BooleanField(
        default=False,
        help_text="Whether shipping costs are included in the refund.",
    )
    refund_method = models.CharField(
        max_length=30,
        choices=RefundMethod.choices,
        blank=True,
        default="",
    )
    refunded_at = models.DateTimeField(null=True, blank=True)
    refund_reference = models.CharField(
        max_length=100, blank=True, default="",
        help_text="Payment gateway refund reference/transaction ID.",
    )
    return_shipping_cost = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS,
        decimal_places=PRICE_DECIMAL_PLACES,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Cost of return shipping (charged to customer or refunded).",
    )

    # ── Notes & Metadata ────────────────────────────────────────────
    notes = models.TextField(blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "orders_order_return"
        ordering = ["-requested_at"]
        indexes = [
            models.Index(
                fields=["order", "status"],
                name="idx_return_order_status",
            ),
        ]

    def __str__(self):
        return f"{self.return_number} ({self.status})"

    # ── Financial Helpers (Task 71) ────────────────────────────────

    def calculate_refund_amount(self):
        """
        Calculate total refund from return line items minus restocking fees.

        Returns the net refund amount.
        """
        item_total = sum(
            item.refund_subtotal for item in self.return_line_items.all()
        )
        net = item_total - self.restocking_fee
        if self.refund_shipping and hasattr(self.order, "shipping_cost"):
            net += self.order.shipping_cost or Decimal("0")
        return max(net, Decimal("0"))

    def is_refund_eligible(self):
        """Check if this return is eligible for refund processing."""
        return self.status == ReturnStatus.RECEIVED

    def is_approved(self):
        """Whether this return has been approved."""
        return self.status in (
            ReturnStatus.APPROVED,
            ReturnStatus.RECEIVED,
            ReturnStatus.REFUNDED,
        )

    def is_completed(self):
        """Whether this return is in a terminal state."""
        return self.status in (
            ReturnStatus.REFUNDED,
            ReturnStatus.REJECTED,
            ReturnStatus.CANCELLED,
        )

    def can_receive(self):
        """Whether items can be received for this return."""
        return self.status == ReturnStatus.APPROVED


# ════════════════════════════════════════════════════════════════════════
# ReturnLineItem Model (Task 70)
# ════════════════════════════════════════════════════════════════════════


class ReturnLineItem(UUIDMixin, TimestampMixin, models.Model):
    """
    Individual item within a return request.

    Links to the original order line item, tracks the quantity being
    returned, the item condition upon receipt, and inspection results.
    """

    # ── Return Reference ────────────────────────────────────────────
    order_return = models.ForeignKey(
        "orders.OrderReturn",
        on_delete=models.CASCADE,
        related_name="return_line_items",
        verbose_name="Return",
    )

    # ── Original Order Line Item ────────────────────────────────────
    order_line_item = models.ForeignKey(
        "orders.OrderLineItem",
        on_delete=models.CASCADE,
        related_name="return_items",
        verbose_name="Order Line Item",
    )

    # ── Quantity ────────────────────────────────────────────────────
    quantity = models.DecimalField(
        max_digits=QUANTITY_MAX_DIGITS,
        decimal_places=QUANTITY_DECIMAL_PLACES,
        validators=[MinValueValidator(Decimal("0.001"))],
    )

    # ── Condition on Receipt (Task 70) ──────────────────────────────
    condition = models.CharField(
        max_length=20,
        choices=ItemCondition.choices,
        blank=True,
        default="",
    )

    # ── Inspection Fields (Task 70) ─────────────────────────────────
    inspected = models.BooleanField(default=False)
    inspected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inspected_return_items",
    )
    inspected_at = models.DateTimeField(null=True, blank=True)
    inspection_notes = models.TextField(blank=True, default="")

    # ── Financial per Item ──────────────────────────────────────────
    unit_refund_amount = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS,
        decimal_places=PRICE_DECIMAL_PLACES,
        default=0,
        validators=[MinValueValidator(0)],
    )
    restocking_fee_per_unit = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS,
        decimal_places=PRICE_DECIMAL_PLACES,
        default=0,
        validators=[MinValueValidator(0)],
    )

    # ── Stock Restoration Tracking ──────────────────────────────────
    stock_restored = models.BooleanField(default=False)
    stock_restored_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "orders_return_line_item"
        unique_together = [("order_return", "order_line_item")]

    def __str__(self):
        return (
            f"{self.order_line_item.item_name} x{self.quantity} "
            f"({self.condition or 'not inspected'})"
        )

    @property
    def refund_subtotal(self):
        """Net refund for this line item after restocking fees."""
        gross = self.unit_refund_amount * self.quantity
        fees = self.restocking_fee_per_unit * self.quantity
        return max(gross - fees, Decimal("0"))
