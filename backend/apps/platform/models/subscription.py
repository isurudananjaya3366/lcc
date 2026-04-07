"""
Subscription plan model for the LankaCommerce Cloud platform.

Defines SaaS subscription tiers, pricing, and resource limits for
tenants. Each plan represents a service tier with specific pricing
in LKR (Sri Lankan Rupee, ₨), billing cycle options, and resource
quotas (users, products, locations, storage, transactions).

This model resides exclusively in the public (shared) schema and is
accessible from all tenant contexts. Tenants reference their active
plan to determine resource limits and available features.

Table: platform_subscriptionplan
"""

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify

from apps.platform.models.mixins import (
    SoftDeleteMixin,
    StatusMixin,
    TimestampMixin,
    UUIDMixin,
)

# ════════════════════════════════════════════════════════════════════
# Constants
# ════════════════════════════════════════════════════════════════════

#: Default currency for all pricing fields.
CURRENCY_CODE = "LKR"
CURRENCY_SYMBOL = "₨"

#: Billing cycle choices for plan pricing.
BILLING_CYCLE_MONTHLY = "monthly"
BILLING_CYCLE_ANNUAL = "annual"
BILLING_CYCLE_CHOICES = [
    (BILLING_CYCLE_MONTHLY, "Monthly"),
    (BILLING_CYCLE_ANNUAL, "Annual"),
]

#: Maximum digits for pricing fields (supports up to 9,999,999.99 LKR).
PRICE_MAX_DIGITS = 10
PRICE_DECIMAL_PLACES = 2

#: Sentinel value for unlimited resource limits.
#: Use -1 to represent "no limit" for integer limit fields.
#: Application code should check: if limit == UNLIMITED then skip enforcement.
UNLIMITED = -1

#: Storage limit units (stored in MB for precision).
STORAGE_UNIT = "MB"
STORAGE_MB_PER_GB = 1024


class SubscriptionPlan(UUIDMixin, TimestampMixin, StatusMixin, SoftDeleteMixin, models.Model):
    """
    SaaS subscription plan defining pricing and billing for tenants.

    Each plan represents a service tier (e.g., Free, Starter, Pro,
    Enterprise) with monthly and annual pricing in LKR. Plans are
    displayed to tenants in order of display_order for upsell purposes.

    Pricing is denominated in Sri Lankan Rupees (LKR, ₨) as this
    platform targets the Sri Lankan market. All price fields use
    Decimal to avoid floating-point precision issues.

    Resource limits use -1 (UNLIMITED constant) to represent
    unlimited access. Application code should check limit values
    before enforcement: if limit == UNLIMITED, skip the check.
    """

    # ════════════════════════════════════════════════════════════════
    # Plan Identity
    # ════════════════════════════════════════════════════════════════

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Plan name",
        help_text="Display name of the subscription plan (e.g., 'Starter', 'Pro').",
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name="Slug",
        help_text="URL-safe identifier, auto-generated from plan name.",
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name="Description",
        help_text="Detailed description of the plan and its features.",
    )

    # ════════════════════════════════════════════════════════════════
    # Pricing (LKR — Sri Lankan Rupee, ₨)
    # ════════════════════════════════════════════════════════════════

    monthly_price = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS,
        decimal_places=PRICE_DECIMAL_PLACES,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Monthly price (LKR)",
        help_text="Monthly subscription price in Sri Lankan Rupees (₨).",
    )
    annual_price = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS,
        decimal_places=PRICE_DECIMAL_PLACES,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Annual price (LKR)",
        help_text="Annual subscription price in Sri Lankan Rupees (₨).",
    )

    # ════════════════════════════════════════════════════════════════
    # Billing Cycle
    # ════════════════════════════════════════════════════════════════

    default_billing_cycle = models.CharField(
        max_length=10,
        choices=BILLING_CYCLE_CHOICES,
        default=BILLING_CYCLE_MONTHLY,
        verbose_name="Default billing cycle",
        help_text="Default billing interval when a tenant subscribes to this plan.",
    )
    is_free = models.BooleanField(
        default=False,
        verbose_name="Free plan",
        help_text="Whether this plan is free (no payment required).",
    )
    has_trial = models.BooleanField(
        default=True,
        verbose_name="Has trial period",
        help_text="Whether this plan offers a trial period before billing starts.",
    )
    trial_days = models.PositiveIntegerField(
        default=14,
        verbose_name="Trial days",
        help_text="Number of trial days before billing begins.",
    )

    # ════════════════════════════════════════════════════════════════
    # Resource Limits
    # ════════════════════════════════════════════════════════════════
    # Use -1 (UNLIMITED) for unlimited access.
    # Storage is stored in MB for precision.

    max_users = models.IntegerField(
        default=1,
        validators=[MinValueValidator(UNLIMITED)],
        verbose_name="Max users",
        help_text="Maximum number of users allowed. Use -1 for unlimited.",
    )
    max_products = models.IntegerField(
        default=100,
        validators=[MinValueValidator(UNLIMITED)],
        verbose_name="Max products",
        help_text="Maximum number of products allowed. Use -1 for unlimited.",
    )
    max_locations = models.IntegerField(
        default=1,
        validators=[MinValueValidator(UNLIMITED)],
        verbose_name="Max locations",
        help_text="Maximum number of store locations allowed. Use -1 for unlimited.",
    )
    storage_limit_mb = models.IntegerField(
        default=512,
        validators=[MinValueValidator(UNLIMITED)],
        verbose_name="Storage limit (MB)",
        help_text="Maximum storage in megabytes. Use -1 for unlimited.",
    )
    max_monthly_transactions = models.IntegerField(
        default=1000,
        validators=[MinValueValidator(UNLIMITED)],
        verbose_name="Max monthly transactions",
        help_text="Maximum transactions per month. Use -1 for unlimited.",
    )

    # ════════════════════════════════════════════════════════════════
    # Status & Visibility
    # ════════════════════════════════════════════════════════════════

    is_archived = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Archived",
        help_text="Whether this plan is archived (hidden from new subscriptions).",
    )
    is_public = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Publicly visible",
        help_text="Whether this plan is visible on the public pricing page.",
    )

    # ════════════════════════════════════════════════════════════════
    # Feature References
    # ════════════════════════════════════════════════════════════════
    # Stores enabled feature keys as a JSON list. When FeatureFlag
    # models are created (Group-D), plans will reference flags by
    # key. Until then, this field provides a lightweight way to
    # associate features with plans without a separate join table.
    #
    # Example: ["multi_currency", "api_access", "advanced_reports"]
    #
    # Feature access is enforced by checking whether a feature key
    # exists in the tenant's active plan's feature_keys list.

    feature_keys = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Feature keys",
        help_text=(
            "List of enabled feature keys for this plan. "
            "Example: [\"multi_currency\", \"api_access\"]."
        ),
    )

    # ════════════════════════════════════════════════════════════════
    # Ordering & Display
    # ════════════════════════════════════════════════════════════════

    display_order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Display order",
        help_text="Ordering for plan display (lower numbers appear first).",
    )

    class Meta:
        verbose_name = "Subscription Plan"
        verbose_name_plural = "Subscription Plans"
        ordering = ["display_order", "monthly_price"]
        indexes = [
            models.Index(
                fields=["is_active", "is_public", "display_order"],
                name="idx_subplan_active_order",
            ),
            models.Index(
                fields=["slug"],
                name="idx_subplan_slug",
            ),
            models.Index(
                fields=["is_archived", "is_active"],
                name="idx_subplan_archived",
            ),
        ]

    def __str__(self):
        """Return plan name with monthly price."""
        return f"{self.name} ({CURRENCY_SYMBOL}{self.monthly_price}/mo)"

    def clean(self):
        """Validate pricing and limit constraints."""
        from django.core.exceptions import ValidationError

        errors = {}

        # Auto-generate slug from name if not provided
        if not self.slug and self.name:
            self.slug = slugify(self.name)

        # Free plans must have zero pricing
        if self.is_free:
            if self.monthly_price and self.monthly_price > 0:
                errors["monthly_price"] = "Free plans must have zero monthly price."
            if self.annual_price and self.annual_price > 0:
                errors["annual_price"] = "Free plans must have zero annual price."

        # Paid plans should have positive pricing
        if not self.is_free:
            if self.monthly_price is not None and self.monthly_price <= 0:
                errors["monthly_price"] = "Paid plans must have a positive monthly price."

        # Validate resource limits (must be -1 for unlimited or >= 0)
        limit_fields = [
            "max_users",
            "max_products",
            "max_locations",
            "storage_limit_mb",
            "max_monthly_transactions",
        ]
        for field_name in limit_fields:
            value = getattr(self, field_name, None)
            if value is not None and value < UNLIMITED:
                errors[field_name] = (
                    f"Value must be -1 (unlimited) or a non-negative integer, "
                    f"got {value}."
                )

        # Archived plans should not be public
        if self.is_archived and self.is_public:
            errors["is_public"] = "Archived plans should not be publicly visible."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Auto-generate slug and run validation before save."""
        if not self.slug and self.name:
            self.slug = slugify(self.name)
        self.full_clean()
        super().save(*args, **kwargs)

    # ════════════════════════════════════════════════════════════════
    # Properties
    # ════════════════════════════════════════════════════════════════

    @property
    def annual_savings(self):
        """Calculate annual savings compared to monthly billing."""
        monthly_annual = self.monthly_price * 12
        return monthly_annual - self.annual_price

    @property
    def annual_discount_percent(self):
        """Calculate annual discount percentage vs monthly billing."""
        monthly_annual = self.monthly_price * 12
        if monthly_annual == 0:
            return 0
        return round((self.annual_savings / monthly_annual) * 100, 1)

    @property
    def is_paid(self):
        """Whether this is a paid plan (not free)."""
        return not self.is_free

    @property
    def storage_limit_gb(self):
        """Storage limit converted to gigabytes, or -1 if unlimited."""
        if self.storage_limit_mb == UNLIMITED:
            return UNLIMITED
        return round(self.storage_limit_mb / STORAGE_MB_PER_GB, 2)

    @property
    def has_unlimited_users(self):
        """Whether this plan allows unlimited users."""
        return self.max_users == UNLIMITED

    @property
    def has_unlimited_products(self):
        """Whether this plan allows unlimited products."""
        return self.max_products == UNLIMITED

    @property
    def has_unlimited_locations(self):
        """Whether this plan allows unlimited locations."""
        return self.max_locations == UNLIMITED

    @property
    def has_unlimited_storage(self):
        """Whether this plan allows unlimited storage."""
        return self.storage_limit_mb == UNLIMITED

    @property
    def has_unlimited_transactions(self):
        """Whether this plan allows unlimited monthly transactions."""
        return self.max_monthly_transactions == UNLIMITED

    @property
    def is_selectable(self):
        """Whether this plan can be selected by new tenants."""
        return self.is_active and self.is_public and not self.is_archived and not self.is_deleted
