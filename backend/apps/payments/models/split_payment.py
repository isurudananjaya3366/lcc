"""
Split payment model.

Tracks a single transaction that is split across multiple payment methods.
For example, paying part with cash and part with card.
"""

from decimal import Decimal

from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin
from apps.payments.constants import PaymentMethod, PaymentStatus


class SplitPaymentStatus(models.TextChoices):
    """Split payment lifecycle statuses."""

    PENDING = "PENDING", "Pending"
    PARTIAL_COMPLETED = "PARTIAL_COMPLETED", "Partially Completed"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"


class SplitPayment(UUIDMixin, TimestampMixin, models.Model):
    """
    A split payment transaction where the total is paid via
    multiple payment method components.
    """

    split_payment_number = models.CharField(
        max_length=30,
        unique=True,
        db_index=True,
        verbose_name="Split Payment Number",
        help_text="Unique identifier for this split payment.",
    )
    invoice = models.ForeignKey(
        "invoices.Invoice",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="split_payments",
        verbose_name="Invoice",
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="split_payments",
        verbose_name="Order",
    )
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="split_payments",
        verbose_name="Customer",
    )
    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Total Amount",
        help_text="Total amount across all payment components.",
    )
    split_count = models.IntegerField(
        default=0,
        verbose_name="Split Count",
        help_text="Number of payment components.",
    )
    status = models.CharField(
        max_length=20,
        choices=SplitPaymentStatus.choices,
        default=SplitPaymentStatus.PENDING,
        db_index=True,
        verbose_name="Status",
    )
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Processed At",
        help_text="Timestamp when split payment was fully processed.",
    )
    notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Notes",
    )

    class Meta:
        db_table = "payments_splitpayment"
        ordering = ["-created_on"]
        verbose_name = "Split Payment"
        verbose_name_plural = "Split Payments"
        constraints = [
            models.CheckConstraint(
                check=models.Q(total_amount__gt=0),
                name="splitpay_total_positive",
            ),
        ]

    def __str__(self):
        return f"{self.split_payment_number} - {self.total_amount} ({self.status})"

    @property
    def components_total(self):
        """Sum of all component payment amounts."""
        return self.components.aggregate(
            total=models.Sum("amount")
        )["total"] or Decimal("0")

    @property
    def is_valid(self):
        """Whether component totals match the split payment total."""
        return self.components_total == self.total_amount

    def get_split_breakdown(self):
        """
        Return a breakdown of all components with method and amount.

        Returns:
            list[dict]: Each dict has method, amount, sequence, status.
        """
        return list(
            self.components.select_related("payment").values(
                "sequence", "method", "amount",
            ).annotate(
                payment_status=models.F("payment__status"),
            ).order_by("sequence")
        )

    def calculate_completed_amount(self):
        """
        Sum of amounts for components whose linked payment is COMPLETED.
        """
        return self.components.filter(
            payment__status=PaymentStatus.COMPLETED,
        ).aggregate(
            total=models.Sum("amount"),
        )["total"] or Decimal("0")

    @property
    def is_complete(self):
        """Whether all component payments are completed."""
        return self.calculate_completed_amount() == self.total_amount


class SplitPaymentComponent(UUIDMixin, models.Model):
    """
    A single component of a split payment, linking to a Payment record.
    """

    split_payment = models.ForeignKey(
        SplitPayment,
        on_delete=models.CASCADE,
        related_name="components",
        verbose_name="Split Payment",
    )
    payment = models.OneToOneField(
        "payments.Payment",
        on_delete=models.CASCADE,
        related_name="split_component",
        verbose_name="Payment",
    )
    method = models.CharField(
        max_length=30,
        choices=PaymentMethod.choices,
        verbose_name="Payment Method",
        help_text="Payment method for this component.",
        default="",
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name="Amount",
        help_text="Amount for this component.",
    )
    sequence = models.IntegerField(
        default=0,
        verbose_name="Sequence",
        help_text="Display ordering of this component.",
    )
    order_index = models.IntegerField(
        default=0,
        verbose_name="Order",
        help_text="Display ordering of this component (legacy).",
    )
    method_details = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Method Details",
        help_text="Method-specific details (card type, bank name, etc.).",
    )

    class Meta:
        db_table = "payments_splitpaymentcomponent"
        ordering = ["sequence"]
        verbose_name = "Split Payment Component"
        verbose_name_plural = "Split Payment Components"

    def __str__(self):
        return f"Component {self.sequence} of {self.split_payment_id} - {self.method} {self.amount}"
