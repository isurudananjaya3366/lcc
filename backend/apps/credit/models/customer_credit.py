"""
CustomerCredit model for credit account management.

Tracks credit limits, balances, payment terms, risk assessment,
and approval status for each customer's credit account.
"""

from datetime import date, timedelta
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone

from apps.core.mixins import UUIDMixin, TimestampMixin, SoftDeleteMixin
from apps.credit.constants import CreditStatus


class CustomerCredit(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """
    Customer credit account linked via OneToOne to Customer.

    Tracks credit limits, available credit, outstanding balance,
    payment terms, risk scores, and approval status.
    """

    # ── Relationships ───────────────────────────────────────────────
    customer = models.OneToOneField(
        "customers.Customer",
        on_delete=models.CASCADE,
        related_name="credit_account",
    )

    # ── Status ──────────────────────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=CreditStatus.choices,
        default=CreditStatus.PENDING_APPROVAL,
        db_index=True,
        help_text="Current credit account status.",
    )

    # ── Credit Limit Fields (Task 05) ──────────────────────────────
    credit_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Maximum credit allowed (LKR).",
    )
    available_credit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Currently available credit (LKR).",
    )
    outstanding_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Current amount owed (LKR).",
    )

    # ── Credit Terms Fields (Task 06) ──────────────────────────────
    payment_terms_days = models.PositiveIntegerField(
        default=30,
        help_text="Payment due in X days (e.g., Net 30).",
    )
    grace_period_days = models.PositiveIntegerField(
        default=5,
        help_text="Grace period before late fees apply.",
    )
    interest_rate_annual = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("18.00"),
        null=True,
        blank=True,
        help_text="Annual interest rate for overdue amounts (%).",
    )

    # ── Credit Status Fields (Task 07) ─────────────────────────────
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_credit_accounts",
        help_text="User who approved this credit account.",
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the credit account was approved.",
    )
    suspended_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="suspended_credit_accounts",
        help_text="User who suspended this credit account.",
    )
    suspended_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the credit account was suspended.",
    )
    suspended_reason = models.TextField(
        blank=True,
        default="",
        help_text="Reason for credit suspension.",
    )
    notes = models.TextField(
        blank=True,
        default="",
        help_text="Internal notes about this credit account.",
    )

    # ── Credit Date Fields (Task 08) ───────────────────────────────
    last_payment_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of last payment received.",
    )
    last_purchase_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of last credit purchase.",
    )
    next_payment_due = models.DateField(
        null=True,
        blank=True,
        help_text="Next payment due date.",
    )
    account_opened_date = models.DateField(
        auto_now_add=True,
        help_text="When credit account was opened.",
    )

    # ── Credit Risk Fields (Task 09) ───────────────────────────────
    risk_score = models.PositiveIntegerField(
        default=50,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Risk score 0-100 (higher = riskier).",
    )
    late_payment_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of late payments.",
    )
    default_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of payment defaults (90+ days overdue).",
    )
    total_payments_made = models.PositiveIntegerField(
        default=0,
        help_text="Total number of payments received.",
    )
    on_time_payment_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("100.00"),
        help_text="Percentage of on-time payments.",
    )
    last_assessment_date = models.DateField(
        null=True,
        blank=True,
        help_text="When risk was last assessed.",
    )

    class Meta:
        verbose_name = "Customer Credit Account"
        verbose_name_plural = "Customer Credit Accounts"
        db_table = "credit_customer_credit"
        ordering = ["-created_on"]
        indexes = [
            models.Index(fields=["status"], name="credit_status_idx"),
            models.Index(fields=["next_payment_due"], name="credit_next_due_idx"),
            models.Index(fields=["risk_score"], name="credit_risk_score_idx"),
            models.Index(fields=["outstanding_balance"], name="credit_balance_idx"),
            models.Index(
                fields=["status", "outstanding_balance"],
                name="credit_status_balance_idx",
            ),
            models.Index(
                fields=["status", "next_payment_due"],
                name="credit_status_due_idx",
            ),
            models.Index(
                fields=["status", "risk_score"],
                name="credit_status_risk_idx",
            ),
            models.Index(
                fields=["customer", "status"],
                name="credit_customer_status_idx",
            ),
        ]

    def __str__(self):
        name = getattr(self.customer, "display_name", str(self.customer))
        return f"{name} - Rs. {self.credit_limit:,.2f}"

    # ── Properties ──────────────────────────────────────────────────

    @property
    def credit_utilization_percentage(self):
        """Return credit utilization as a percentage."""
        if self.credit_limit == 0:
            return Decimal("0")
        return (self.outstanding_balance / self.credit_limit) * 100

    @property
    def effective_payment_days(self):
        """Return total days including grace period."""
        return self.payment_terms_days + self.grace_period_days

    @property
    def days_since_last_payment(self):
        """Return days since last payment, or None."""
        if not self.last_payment_date:
            return None
        return (date.today() - self.last_payment_date).days

    @property
    def days_until_next_payment(self):
        """Return days until next payment (negative if overdue), or None."""
        if not self.next_payment_due:
            return None
        return (self.next_payment_due - date.today()).days

    @property
    def is_payment_overdue(self):
        """Return True if next payment is past due."""
        if not self.next_payment_due:
            return False
        return self.next_payment_due < date.today()

    # ── Methods ─────────────────────────────────────────────────────

    def calculate_due_date(self, from_date=None):
        """Calculate due date from a given date."""
        from_date = from_date or date.today()
        return from_date + timedelta(days=self.payment_terms_days)

    def calculate_effective_due_date(self, from_date=None):
        """Calculate effective due date including grace period."""
        from_date = from_date or date.today()
        return from_date + timedelta(days=self.effective_payment_days)

    def get_risk_level(self):
        """Return risk level based on risk_score."""
        if self.risk_score <= 30:
            return "LOW"
        elif self.risk_score <= 60:
            return "MEDIUM"
        else:
            return "HIGH"

    def calculate_payment_reliability(self):
        """Return payment reliability as decimal 0.0-1.0."""
        return self.on_time_payment_percentage / Decimal("100.00")

    def should_suspend(self):
        """Return True if account should be suspended based on risk."""
        return (
            self.late_payment_count >= 3
            or self.default_count >= 1
            or self.risk_score >= 80
        )

    def clean(self):
        """Validate field relationships."""
        from django.core.exceptions import ValidationError

        errors = {}
        if self.credit_limit < 0:
            errors["credit_limit"] = "Credit limit cannot be negative."
        if self.outstanding_balance < 0:
            errors["outstanding_balance"] = "Outstanding balance cannot be negative."
        if self.available_credit < 0:
            errors["available_credit"] = "Available credit cannot be negative."
        # Validate: available_credit should equal credit_limit - outstanding_balance
        expected = self.credit_limit - self.outstanding_balance
        if self.available_credit != expected and not errors:
            errors["available_credit"] = (
                f"Available credit should be {expected} "
                f"(credit_limit - outstanding_balance)."
            )
        if errors:
            raise ValidationError(errors)
