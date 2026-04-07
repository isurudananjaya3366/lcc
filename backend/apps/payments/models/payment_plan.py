"""
Payment plan model.

Supports installment payment plans for invoices, with scheduled
installments and tracking of paid/pending amounts.
"""

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.mixins import UUIDMixin, TimestampMixin


class PlanStatus(models.TextChoices):
    """Payment plan lifecycle statuses."""

    ACTIVE = "ACTIVE", "Active"
    COMPLETED = "COMPLETED", "Completed"
    DEFAULTED = "DEFAULTED", "Defaulted"
    CANCELLED = "CANCELLED", "Cancelled"


class PlanFrequency(models.TextChoices):
    """Installment frequency options."""

    WEEKLY = "WEEKLY", "Weekly"
    BIWEEKLY = "BIWEEKLY", "Bi-Weekly"
    MONTHLY = "MONTHLY", "Monthly"
    QUARTERLY = "QUARTERLY", "Quarterly"
    CUSTOM = "CUSTOM", "Custom"


class InstallmentStatus(models.TextChoices):
    """Individual installment statuses."""

    PENDING = "PENDING", "Pending"
    PAID = "PAID", "Paid"
    PARTIAL = "PARTIAL", "Partial"
    OVERDUE = "OVERDUE", "Overdue"
    CANCELLED = "CANCELLED", "Cancelled"


class PaymentPlan(UUIDMixin, TimestampMixin, models.Model):
    """
    Installment payment plan for an invoice.

    Allows a customer to pay an invoice over multiple scheduled
    installments with configurable frequency.
    """

    plan_number = models.CharField(
        max_length=30,
        unique=True,
        db_index=True,
        verbose_name="Plan Number",
        help_text="Format: PP-YYYY-NNNNN",
    )
    plan_name = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Plan Name",
        help_text="Optional descriptive name for this payment plan.",
    )
    invoice = models.ForeignKey(
        "invoices.Invoice",
        on_delete=models.PROTECT,
        related_name="payment_plans",
        verbose_name="Invoice",
    )
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        related_name="payment_plans",
        verbose_name="Customer",
    )
    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Total Amount",
        help_text="Total amount to be paid via this plan.",
    )
    number_of_installments = models.IntegerField(
        verbose_name="Number of Installments",
    )
    frequency = models.CharField(
        max_length=20,
        choices=PlanFrequency.choices,
        default=PlanFrequency.MONTHLY,
        verbose_name="Frequency",
    )
    start_date = models.DateField(
        verbose_name="Start Date",
        help_text="Date of the first installment.",
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="End Date",
        help_text="Date of the last installment.",
    )
    status = models.CharField(
        max_length=20,
        choices=PlanStatus.choices,
        default=PlanStatus.ACTIVE,
        db_index=True,
        verbose_name="Status",
    )
    last_payment_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Last Payment Date",
        help_text="Date of the most recent installment payment.",
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Completed At",
        help_text="Timestamp when plan was fully completed.",
    )
    allow_early_payment = models.BooleanField(
        default=True,
        verbose_name="Allow Early Payment",
        help_text="Whether early installment payments are permitted.",
    )
    late_fee_applicable = models.BooleanField(
        default=False,
        verbose_name="Late Fee Applicable",
        help_text="Whether late fees apply to overdue installments.",
    )
    grace_period_days = models.IntegerField(
        default=3,
        verbose_name="Grace Period Days",
        help_text="Days after due date before late fees apply.",
    )
    max_missed_installments = models.IntegerField(
        default=2,
        verbose_name="Max Missed Installments",
        help_text="Number of missed installments before defaulting the plan.",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_payment_plans",
        verbose_name="Created By",
    )
    notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Notes",
    )

    class Meta:
        db_table = "payments_paymentplan"
        ordering = ["-created_on"]
        verbose_name = "Payment Plan"
        verbose_name_plural = "Payment Plans"
        constraints = [
            models.CheckConstraint(
                check=models.Q(total_amount__gt=0),
                name="plan_total_positive",
            ),
            models.CheckConstraint(
                check=models.Q(number_of_installments__gt=0),
                name="plan_installments_positive",
            ),
        ]

    def __str__(self):
        return f"{self.plan_number} - {self.total_amount} ({self.status})"

    @property
    def amount_paid(self):
        """Total amount paid across installments."""
        return (
            self.installments.filter(
                status__in=[InstallmentStatus.PAID, InstallmentStatus.PARTIAL]
            ).aggregate(
                total=models.Sum("amount_paid")
            )["total"]
            or Decimal("0")
        )

    @property
    def amount_remaining(self):
        """Remaining amount to be paid."""
        return self.total_amount - self.amount_paid

    @property
    def is_complete(self):
        """Whether all installments are paid."""
        return self.amount_remaining <= 0

    def get_next_due_installment(self):
        """Return the next pending/overdue installment by due date."""
        return self.installments.filter(
            status__in=[InstallmentStatus.PENDING, InstallmentStatus.OVERDUE, InstallmentStatus.PARTIAL],
        ).order_by("due_date").first()

    def get_overdue_installments(self):
        """Return all overdue installments."""
        return self.installments.filter(
            status=InstallmentStatus.OVERDUE,
        ).order_by("due_date")

    def is_defaulted(self):
        """Check if overdue count exceeds max_missed_installments."""
        overdue_count = self.installments.filter(
            status=InstallmentStatus.OVERDUE,
        ).count()
        return overdue_count >= self.max_missed_installments

    def get_completion_percentage(self):
        """Return percentage of plan completed based on amount paid."""
        if self.total_amount <= 0:
            return Decimal("0")
        return (self.amount_paid / self.total_amount * 100).quantize(Decimal("0.01"))


class PaymentPlanInstallment(UUIDMixin, TimestampMixin, models.Model):
    """
    Individual installment within a payment plan.
    """

    payment_plan = models.ForeignKey(
        PaymentPlan,
        on_delete=models.CASCADE,
        related_name="installments",
        verbose_name="Payment Plan",
    )
    installment_number = models.IntegerField(
        verbose_name="Installment Number",
        help_text="Sequential number (1, 2, 3...).",
    )
    due_date = models.DateField(
        verbose_name="Due Date",
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Amount",
        help_text="Total amount due for this installment.",
    )
    amount_paid = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name="Amount Paid",
        help_text="Amount paid so far for this installment.",
    )
    status = models.CharField(
        max_length=20,
        choices=InstallmentStatus.choices,
        default=InstallmentStatus.PENDING,
        db_index=True,
        verbose_name="Status",
    )
    payment = models.ForeignKey(
        "payments.Payment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="installment",
        verbose_name="Payment",
        help_text="Linked payment when this installment is paid.",
    )
    paid_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Paid Date",
    )
    late_fee_applied = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name="Late Fee Applied",
        help_text="Late fee amount applied to this installment.",
    )
    reminder_sent_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Reminder Sent Date",
        help_text="Date when payment reminder was last sent.",
    )

    class Meta:
        db_table = "payments_paymentplaninstallment"
        ordering = ["installment_number"]
        verbose_name = "Payment Plan Installment"
        verbose_name_plural = "Payment Plan Installments"
        unique_together = [("payment_plan", "installment_number")]
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount__gt=0),
                name="installment_amount_positive",
            ),
        ]

    def __str__(self):
        return (
            f"Installment {self.installment_number} of "
            f"{self.payment_plan_id} - {self.amount} ({self.status})"
        )

    def calculate_outstanding(self):
        """Amount still owed for this installment."""
        return self.amount - self.amount_paid + self.late_fee_applied

    def is_overdue(self):
        """Check if installment is past due date."""
        if self.status in (InstallmentStatus.PAID, InstallmentStatus.CANCELLED):
            return False
        return self.due_date < timezone.now().date()

    def days_overdue(self):
        """Number of days past due date. Returns 0 if not overdue."""
        if not self.is_overdue():
            return 0
        return (timezone.now().date() - self.due_date).days
