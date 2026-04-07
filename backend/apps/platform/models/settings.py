"""
Platform settings model for the LankaCommerce Cloud platform.

Provides a singleton settings record in the public schema that stores
platform-wide configuration: branding identity, contact information,
localization defaults, feature toggles, billing configuration, and
notification settings. Only one row is ever stored in this table.

Table: platform_platformsetting
Schema: public (shared)
Singleton: Yes — enforced via save() override and Meta constraints.
"""

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, URLValidator
from django.core.cache import cache
from django.db import models
from django.utils import timezone

from apps.platform.models.mixins import TimestampMixin, UUIDMixin

# ── Constants ────────────────────────────────────────────────

# Branding defaults
DEFAULT_PLATFORM_NAME = "LankaCommerce Cloud"
DEFAULT_PRIMARY_COLOR = "#1E40AF"
PLATFORM_NAME_MAX_LENGTH = 150
COLOR_HEX_REGEX = r"^#[0-9A-Fa-f]{6}$"

# Contact defaults
DEFAULT_SUPPORT_EMAIL = "support@lankacommerce.lk"
DEFAULT_SUPPORT_PHONE = "+94 11 000 0000"
PHONE_REGEX = r"^\+94\s?\d{2}\s?\d{3}\s?\d{4}$"

# Localization defaults
DEFAULT_TIMEZONE = "Asia/Colombo"
DEFAULT_CURRENCY = "LKR"
CURRENCY_SYMBOL = "₨"

TIMEZONE_MAX_LENGTH = 50
CURRENCY_MAX_LENGTH = 3

# Billing defaults
DEFAULT_TAX_RATE = 0
TAX_MAX_DIGITS = 5
TAX_DECIMAL_PLACES = 2

# Notification defaults
DEFAULT_NOTIFICATION_EMAIL = "noreply@lankacommerce.lk"

# Cache settings
SETTINGS_CACHE_KEY = "platform_settings"
SETTINGS_CACHE_TTL = 3600  # 1 hour in seconds


# ── Model ────────────────────────────────────────────────────


class PlatformSetting(UUIDMixin, TimestampMixin, models.Model):
    """
    Singleton platform-wide settings stored in the public schema.

    Holds branding identity, contact information, and localization
    defaults that apply across the entire platform. Only one row
    is permitted; the save() method enforces this constraint.

    Inheritance:
        - UUIDMixin: UUID v4 primary key
        - TimestampMixin: created_on / updated_on audit fields
        - No StatusMixin or SoftDeleteMixin — settings are always active
          and must never be soft-deleted.
    """

    # ── Branding Fields ──────────────────────────────────────

    platform_name = models.CharField(
        max_length=PLATFORM_NAME_MAX_LENGTH,
        default=DEFAULT_PLATFORM_NAME,
        help_text="Display name of the platform shown across the UI.",
    )

    logo_url = models.URLField(
        max_length=500,
        blank=True,
        default="",
        validators=[URLValidator()],
        help_text="URL to the platform logo image.",
    )

    primary_color = models.CharField(
        max_length=7,
        default=DEFAULT_PRIMARY_COLOR,
        validators=[
            RegexValidator(
                regex=COLOR_HEX_REGEX,
                message="Enter a valid hex color code (e.g. #1E40AF).",
            ),
        ],
        help_text="Primary brand color in hex format (e.g. #1E40AF).",
    )

    # ── Contact Fields ───────────────────────────────────────

    support_email = models.EmailField(
        max_length=254,
        default=DEFAULT_SUPPORT_EMAIL,
        help_text="Primary support email address displayed to users.",
    )

    support_phone = models.CharField(
        max_length=20,
        default=DEFAULT_SUPPORT_PHONE,
        validators=[
            RegexValidator(
                regex=PHONE_REGEX,
                message="Enter a valid Sri Lankan phone number in +94 format.",
            ),
        ],
        help_text="Support phone number in +94 (Sri Lanka) format.",
    )

    # ── Localization Fields ──────────────────────────────────

    default_timezone = models.CharField(
        max_length=TIMEZONE_MAX_LENGTH,
        default=DEFAULT_TIMEZONE,
        help_text="Platform default timezone. Uses Asia/Colombo for Sri Lanka.",
    )

    default_currency = models.CharField(
        max_length=CURRENCY_MAX_LENGTH,
        default=DEFAULT_CURRENCY,
        help_text="Default currency code (ISO 4217). LKR for Sri Lankan Rupee (₨).",
    )

    # ── Feature Toggle Fields ────────────────────────────────

    enable_webstore = models.BooleanField(
        default=True,
        help_text="Enable the public webstore/e-commerce storefront globally.",
    )

    enable_api_access = models.BooleanField(
        default=True,
        help_text="Enable REST API access for tenants.",
    )

    enable_multi_currency = models.BooleanField(
        default=False,
        help_text="Enable multi-currency support across the platform.",
    )

    maintenance_mode = models.BooleanField(
        default=False,
        help_text=(
            "When enabled, the platform displays a maintenance page "
            "to all non-admin users."
        ),
    )

    # ── Billing Configuration Fields ─────────────────────────

    default_tax_rate = models.DecimalField(
        max_digits=TAX_MAX_DIGITS,
        decimal_places=TAX_DECIMAL_PLACES,
        default=DEFAULT_TAX_RATE,
        help_text="Default tax rate as a percentage (e.g. 15.00 for 15%).",
    )

    tax_inclusive_pricing = models.BooleanField(
        default=True,
        help_text=(
            "When True, displayed prices include tax. "
            "Standard practice in Sri Lanka."
        ),
    )

    billing_currency = models.CharField(
        max_length=CURRENCY_MAX_LENGTH,
        default=DEFAULT_CURRENCY,
        help_text="Currency used for platform billing and invoices (ISO 4217).",
    )

    # ── Notification Configuration Fields ────────────────────

    enable_email_notifications = models.BooleanField(
        default=True,
        help_text="Enable email notifications for platform events.",
    )

    enable_sms_notifications = models.BooleanField(
        default=False,
        help_text="Enable SMS notifications. Requires SMS provider integration.",
    )

    notification_sender_email = models.EmailField(
        max_length=254,
        default=DEFAULT_NOTIFICATION_EMAIL,
        help_text="Default sender email address for platform notifications.",
    )

    # ── Meta ─────────────────────────────────────────────────

    class Meta:
        db_table = "platform_platformsetting"
        verbose_name = "Platform Setting"
        verbose_name_plural = "Platform Settings"

    # ── Singleton Behavior ───────────────────────────────────

    def save(self, *args, **kwargs):
        """
        Enforce singleton: only one PlatformSetting row may exist.

        On first save, the record is created normally. On subsequent
        saves, the existing record is updated. If a second row is
        attempted, a ValidationError is raised.

        Cache is invalidated after every save to ensure downstream
        consumers receive the latest settings.
        """
        if not self.pk:
            # New record — ensure no other row exists
            if PlatformSetting.objects.exists():
                raise ValidationError(
                    "Only one PlatformSetting record is allowed. "
                    "Update the existing record instead of creating a new one."
                )
        self.full_clean()
        super().save(*args, **kwargs)
        # Invalidate cached settings so next load() fetches fresh data
        cache.delete(SETTINGS_CACHE_KEY)

    def delete(self, *args, **kwargs):
        """Prevent deletion of the singleton settings record."""
        raise ValidationError(
            "The platform settings record cannot be deleted."
        )

    def __str__(self):
        return f"{self.platform_name} — Settings"

    # ── Properties ───────────────────────────────────────────

    @property
    def currency_display(self):
        """Return currency code with symbol, e.g. 'LKR (₨)'."""
        if self.default_currency == "LKR":
            return f"LKR ({CURRENCY_SYMBOL})"
        return self.default_currency

    @classmethod
    def load(cls):
        """
        Load the singleton settings instance with caching.

        Checks the Django cache first (key: platform_settings, TTL: 1 hour).
        On cache miss, fetches from the database (or creates with defaults)
        and stores the result in cache.

        This is the recommended way to access platform settings.
        """
        settings = cache.get(SETTINGS_CACHE_KEY)
        if settings is not None:
            return settings

        obj, _created = cls.objects.get_or_create(
            pk=cls.objects.values_list("pk", flat=True).first()
            or None,
            defaults={
                "platform_name": DEFAULT_PLATFORM_NAME,
                "primary_color": DEFAULT_PRIMARY_COLOR,
                "support_email": DEFAULT_SUPPORT_EMAIL,
                "support_phone": DEFAULT_SUPPORT_PHONE,
                "default_timezone": DEFAULT_TIMEZONE,
                "default_currency": DEFAULT_CURRENCY,
            },
        )
        cache.set(SETTINGS_CACHE_KEY, obj, SETTINGS_CACHE_TTL)
        return obj
