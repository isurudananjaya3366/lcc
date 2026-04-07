"""
Payment method configuration model.

Per-tenant configuration for payment methods including
activation, display settings, amount limits, gateway settings,
reconciliation, and method-specific options.
"""

from decimal import Decimal

from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin


class PaymentMethodConfig(UUIDMixin, TimestampMixin, models.Model):
    """
    Tenant-specific payment method configuration.

    Controls which payment methods are available, their display order,
    amount restrictions, processing fees, gateway integration, and
    method-specific settings per tenant.
    """

    # ── Core Fields (Task 14) ───────────────────────────────────────
    method = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        verbose_name="Payment Method",
        help_text="The payment method code (e.g. CASH, CARD).",
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Active",
        help_text="Whether this payment method is currently available.",
    )
    is_enabled = models.BooleanField(
        default=False,
        verbose_name="Enabled",
        help_text="Whether this payment method is enabled for transactions.",
    )
    display_name = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Display Name",
    )
    display_order = models.IntegerField(
        default=0,
        verbose_name="Display Order",
    )
    instructions = models.TextField(
        blank=True,
        default="",
        verbose_name="Customer Instructions",
        help_text="Instructions displayed to customer for this method.",
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        default="",
        verbose_name="Icon",
        help_text="UI icon identifier for this method.",
    )

    # ── Amount Limits ───────────────────────────────────────────────
    min_amount = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        verbose_name="Minimum Amount",
    )
    max_amount = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        verbose_name="Maximum Amount",
    )
    daily_limit = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        verbose_name="Daily Limit",
        help_text="Maximum total amount via this method per day (fraud prevention).",
    )

    # ── Processing Fee ──────────────────────────────────────────────
    processing_fee_type = models.CharField(
        max_length=20,
        blank=True,
        default="",
        verbose_name="Fee Type",
        help_text="PERCENTAGE or FIXED.",
    )
    processing_fee_value = models.DecimalField(
        max_digits=10, decimal_places=4, default=Decimal("0"),
        verbose_name="Fee Value",
    )

    # ── Approval ────────────────────────────────────────────────────
    requires_approval = models.BooleanField(
        default=False,
        verbose_name="Requires Approval",
    )
    approval_threshold = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        verbose_name="Approval Threshold",
        help_text="Amounts above this require manager approval.",
    )

    # ── Gateway / Processor (Task 15) ───────────────────────────────
    gateway_name = models.CharField(
        max_length=100, blank=True, default="",
        verbose_name="Gateway Name",
        help_text="Payment gateway provider (e.g. Stripe, PayHere).",
    )
    gateway_merchant_id = models.CharField(
        max_length=100, blank=True, default="",
        verbose_name="Gateway Merchant ID",
    )
    gateway_api_key_reference = models.CharField(
        max_length=100, blank=True, default="",
        verbose_name="API Key Reference",
        help_text="Reference to secure vault for API key (never store raw key).",
    )

    # ── Reconciliation ──────────────────────────────────────────────
    auto_reconcile = models.BooleanField(
        default=False,
        verbose_name="Auto Reconcile",
    )
    reconciliation_account = models.CharField(
        max_length=50, blank=True, default="",
        verbose_name="GL Account Code",
    )
    settlement_period_days = models.IntegerField(
        default=1,
        verbose_name="Settlement Period (Days)",
    )

    # ── Receipt Customization ───────────────────────────────────────
    show_on_receipt = models.BooleanField(
        default=True,
        verbose_name="Show on Receipt",
    )
    receipt_label = models.CharField(
        max_length=100, blank=True, default="",
        verbose_name="Receipt Label",
    )
    receipt_message = models.TextField(
        blank=True, default="",
        verbose_name="Receipt Message",
    )

    # ── Business Rules ──────────────────────────────────────────────
    allow_partial_payment = models.BooleanField(default=True, verbose_name="Allow Partial")
    allow_split_payment = models.BooleanField(default=True, verbose_name="Allow Split")
    allow_refund = models.BooleanField(default=True, verbose_name="Allow Refund")
    refund_within_days = models.IntegerField(
        null=True, blank=True,
        verbose_name="Refund Window (Days)",
    )

    # ── Check-Specific ──────────────────────────────────────────────
    check_clearing_days = models.IntegerField(
        default=3,
        verbose_name="Check Clearing Days",
    )
    allow_post_dated_checks = models.BooleanField(
        default=False,
        verbose_name="Allow Post-Dated Checks",
    )
    max_post_dated_days = models.IntegerField(
        null=True, blank=True,
        verbose_name="Max Post-Dated Days",
    )

    # ── Card-Specific ───────────────────────────────────────────────
    accepted_card_types = models.JSONField(
        null=True, blank=True, default=None,
        verbose_name="Accepted Card Types",
        help_text='["VISA", "MASTERCARD", "AMEX"]',
    )
    require_cvv = models.BooleanField(default=True, verbose_name="Require CVV")
    require_billing_address = models.BooleanField(
        default=False, verbose_name="Require Billing Address",
    )

    # ── Mobile-Specific ─────────────────────────────────────────────
    supported_providers = models.JSONField(
        null=True, blank=True, default=None,
        verbose_name="Supported Providers",
        help_text='["FriMi", "eZ Cash", "mCash"]',
    )
    provider_merchant_ids = models.JSONField(
        null=True, blank=True, default=None,
        verbose_name="Provider Merchant IDs",
        help_text='{"FriMi": "MERCHANT-ID"}',
    )

    # ── Legacy / Extended Settings ──────────────────────────────────
    settings = models.JSONField(
        null=True, blank=True, default=None,
        verbose_name="Additional Settings",
        help_text="Catch-all for extra method-specific configuration.",
    )

    class Meta:
        db_table = "payments_paymentmethodconfig"
        ordering = ["display_order", "method"]
        verbose_name = "Payment Method Configuration"
        verbose_name_plural = "Payment Method Configurations"

    def __str__(self):
        name = self.display_name or self.method
        status = "active" if self.is_active else "inactive"
        return f"{name} ({status})"

    @property
    def effective_display_name(self):
        """Return custom display name or fall back to method code."""
        return self.display_name or self.method

    # ── Business Methods (Task 14) ──────────────────────────────────

    def is_amount_valid(self, amount):
        """Check if amount is within allowed limits."""
        if self.min_amount is not None and amount < self.min_amount:
            return False, f"Amount below minimum ({self.min_amount})"
        if self.max_amount is not None and amount > self.max_amount:
            return False, f"Amount above maximum ({self.max_amount})"
        return True, ""

    def calculate_processing_fee(self, amount):
        """Calculate processing fee for the given amount."""
        if self.processing_fee_type == "PERCENTAGE":
            return (amount * self.processing_fee_value / Decimal("100")).quantize(
                Decimal("0.01")
            )
        if self.processing_fee_type == "FIXED":
            return self.processing_fee_value
        return Decimal("0.00")

    def requires_approval_for_amount(self, amount):
        """Check if the given amount requires approval."""
        if self.requires_approval:
            return True
        if self.approval_threshold and amount >= self.approval_threshold:
            return True
        return False
