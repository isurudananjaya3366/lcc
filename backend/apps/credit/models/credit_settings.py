"""
CreditSettings model for tenant-specific credit configuration.

Stores default credit limits, payment terms, interest rates,
approval thresholds, and risk management settings per tenant.
"""

from decimal import Decimal

from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin


class CreditSettingsManager(models.Manager):
    """Custom manager for CreditSettings."""

    def get_or_create_for_tenant(self, tenant):
        """Get or create settings for a given tenant."""
        settings, _ = self.get_or_create(tenant=tenant)
        return settings


class CreditSettings(UUIDMixin, TimestampMixin, models.Model):
    """
    Tenant-specific credit configuration.

    Each tenant has one CreditSettings instance that controls
    default credit limits, payment terms, approval thresholds,
    and risk management parameters.
    """

    tenant = models.OneToOneField(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="credit_settings",
    )

    # ── Default Credit Configuration ───────────────────────────────
    default_credit_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("50000.00"),
        help_text="Default credit limit for new accounts (LKR).",
    )
    default_payment_terms_days = models.PositiveIntegerField(
        default=30,
        help_text="Default payment terms in days (Net 30).",
    )
    default_grace_period_days = models.PositiveIntegerField(
        default=5,
        help_text="Default grace period in days.",
    )
    default_interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("18.00"),
        help_text="Default annual interest rate (%).",
    )

    # ── Approval Thresholds ────────────────────────────────────────
    min_credit_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("10000.00"),
        help_text="Minimum credit limit allowed (LKR).",
    )
    max_credit_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("5000000.00"),
        help_text="Maximum credit limit allowed (LKR).",
    )
    auto_approval_threshold = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("100000.00"),
        help_text="Credit limits below this are auto-approved (LKR).",
    )
    requires_manager_approval_above = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("500000.00"),
        help_text="Requires manager approval above this amount (LKR).",
    )

    # ── Risk Management ────────────────────────────────────────────
    auto_suspend_after_late_payments = models.PositiveIntegerField(
        default=3,
        help_text="Auto-suspend after X late payments.",
    )
    auto_suspend_risk_score = models.PositiveIntegerField(
        default=80,
        help_text="Auto-suspend if risk score exceeds this.",
    )
    days_before_overdue_notification = models.PositiveIntegerField(
        default=3,
        help_text="Send notification X days before due date.",
    )

    objects = CreditSettingsManager()

    class Meta:
        verbose_name = "Credit Settings"
        verbose_name_plural = "Credit Settings"
        db_table = "credit_settings"

    def __str__(self):
        return f"Credit Settings - {self.tenant}"

    def clean(self):
        """Validate settings constraints."""
        from django.core.exceptions import ValidationError

        errors = {}
        if self.min_credit_limit >= self.max_credit_limit:
            errors["min_credit_limit"] = (
                "Minimum credit limit must be less than maximum."
            )
        if self.auto_approval_threshold > self.requires_manager_approval_above:
            errors["auto_approval_threshold"] = (
                "Auto-approval threshold must not exceed manager approval threshold."
            )
        if errors:
            raise ValidationError(errors)

    def reset_to_defaults(self):
        """Reset all fields to their default values."""
        self.default_credit_limit = Decimal("50000.00")
        self.default_payment_terms_days = 30
        self.default_grace_period_days = 5
        self.default_interest_rate = Decimal("18.00")
        self.min_credit_limit = Decimal("10000.00")
        self.max_credit_limit = Decimal("5000000.00")
        self.auto_approval_threshold = Decimal("100000.00")
        self.requires_manager_approval_above = Decimal("500000.00")
        self.auto_suspend_after_late_payments = 3
        self.auto_suspend_risk_score = 80
        self.days_before_overdue_notification = 3
        self.save()

    @classmethod
    def get_for_current_tenant(cls):
        """Get CreditSettings for the current tenant (from connection)."""
        from django.db import connection

        tenant = connection.tenant
        return cls.objects.get_or_create_for_tenant(tenant)
