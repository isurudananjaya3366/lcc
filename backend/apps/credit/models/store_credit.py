"""
StoreCredit and StoreCreditTransaction models.

StoreCredit tracks store credit balances per customer (separate from loyalty points).
StoreCreditTransaction records all credit movements for audit trail.
"""

from datetime import date, timedelta
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.mixins import UUIDMixin, TimestampMixin, SoftDeleteMixin
from apps.credit.constants import StoreCreditSource, StoreCreditTransactionType


class StoreCreditManager(models.Manager):
    """Custom manager for StoreCredit with expiry-related queries."""

    def expired(self):
        """Get all expired credits with positive balance."""
        today = date.today()
        return self.filter(
            expiry_date__isnull=False,
            expiry_date__lt=today,
            balance__gt=Decimal("0.00"),
        ).exclude(
            # Exclude those still within grace period
            expiry_date__gte=today - models.F("grace_period_days"),
        )

    def expiring_soon(self, days=7):
        """Get credits expiring within given days that haven't been notified."""
        today = date.today()
        future_date = today + timedelta(days=days)
        return self.filter(
            expiry_date__gte=today,
            expiry_date__lte=future_date,
            expiry_reminder_sent=False,
            balance__gt=Decimal("0.00"),
        )


class StoreCredit(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """
    Store credit account linked via OneToOne to Customer.

    Tracks credit balances from refunds, gifts, promotional credits,
    and loyalty point conversions. Supports optional expiry dates
    with grace periods.
    """

    # ── Relationships ───────────────────────────────────────────────
    customer = models.OneToOneField(
        "customers.Customer",
        on_delete=models.CASCADE,
        related_name="store_credit",
    )

    # ── Balance Fields ──────────────────────────────────────────────
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Current available store credit balance.",
    )
    total_issued = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Lifetime accumulated credits issued.",
    )
    total_used = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Lifetime accumulated credits used.",
    )
    currency = models.CharField(
        max_length=3,
        default="LKR",
        help_text="Currency code for credits.",
    )
    original_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Original amount when first issued.",
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about this credit account.",
    )

    # ── Source Tracking ─────────────────────────────────────────────
    created_from = models.CharField(
        max_length=20,
        choices=StoreCreditSource.choices,
        default=StoreCreditSource.ADJUSTMENT,
        help_text="Source of the credit.",
    )
    source_reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="Reference to source (order ID, invoice, etc.).",
    )
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="issued_credits",
        help_text="User who issued this credit.",
    )
    last_transaction_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last credit transaction timestamp.",
    )

    # ── Expiry Fields ───────────────────────────────────────────────
    expiry_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when credit expires (null = never expires).",
    )
    grace_period_days = models.IntegerField(
        default=0,
        help_text="Days of grace period after expiry date.",
    )
    expiry_reminder_sent = models.BooleanField(
        default=False,
        help_text="Whether expiry reminder has been sent.",
    )

    objects = StoreCreditManager()

    class Meta:
        db_table = "credit_store_credits"
        verbose_name = "Store Credit"
        verbose_name_plural = "Store Credits"
        ordering = ["-balance", "customer"]
        indexes = [
            models.Index(fields=["created_from"]),
            models.Index(fields=["expiry_date"]),
        ]

    def __str__(self):
        name = getattr(self.customer, "name", str(self.customer_id))
        return f"Customer: {name} - Balance: Rs. {self.balance:.2f}"

    # ── Properties ──────────────────────────────────────────────────

    @property
    def is_expired(self):
        """Check if credit has expired (including grace period)."""
        if not self.expiry_date:
            return False
        today = date.today()
        final_expiry = self.expiry_date + timedelta(days=self.grace_period_days)
        return today > final_expiry

    @property
    def days_until_expiry(self):
        """Calculate days until expiry date (not including grace)."""
        if not self.expiry_date:
            return None
        return (self.expiry_date - date.today()).days

    @property
    def is_zero_balance(self):
        """Check if balance is zero."""
        return self.balance == Decimal("0.00")

    @property
    def source_display(self):
        """Human-readable source type."""
        return self.get_created_from_display()

    # ── Methods ─────────────────────────────────────────────────────

    def has_balance(self, amount):
        """Check if customer has sufficient non-expired credit."""
        return not self.is_expired and self.balance >= amount

    def get_available_balance(self):
        """Return balance only if not expired."""
        if self.is_expired:
            return Decimal("0.00")
        return self.balance

    def should_send_expiry_reminder(self, days_before=7):
        """Check if an expiry reminder should be sent."""
        if not self.expiry_date or self.expiry_reminder_sent:
            return False
        days_left = self.days_until_expiry
        return days_left is not None and 0 < days_left <= days_before

    def save(self, *args, **kwargs):
        # Auto-set 90-day expiry for promotional credits if not set
        if (
            self.created_from == StoreCreditSource.PROMOTIONAL
            and not self.expiry_date
            and not self.pk
        ):
            self.expiry_date = date.today() + timedelta(days=90)
        super().save(*args, **kwargs)


class StoreCreditTransaction(UUIDMixin, TimestampMixin, models.Model):
    """
    Audit trail for store credit movements.

    Records every issuance, redemption, expiry, and adjustment
    with before/after balance snapshots.
    """

    store_credit = models.ForeignKey(
        StoreCredit,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    transaction_type = models.CharField(
        max_length=10,
        choices=StoreCreditTransactionType.choices,
        db_index=True,
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Positive for issuance, negative for redemption.",
    )
    balance_before = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    balance_after = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="Order ID, invoice reference, etc.",
    )
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="store_credit_transactions",
    )
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "credit_store_credit_transactions"
        verbose_name = "Store Credit Transaction"
        verbose_name_plural = "Store Credit Transactions"
        ordering = ["-created_on"]
        indexes = [
            models.Index(fields=["store_credit", "-created_on"]),
            models.Index(fields=["reference"]),
        ]

    def __str__(self):
        return (
            f"{self.get_transaction_type_display()} - "
            f"Rs. {self.amount} ({self.created_on.date() if self.created_on else ''})"
        )

    @property
    def is_positive(self):
        """Check if transaction added credit."""
        return self.amount > 0

    @property
    def is_negative(self):
        """Check if transaction reduced credit."""
        return self.amount < 0
