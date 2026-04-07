"""
QuoteSettings model for tenant-level quote configuration.

Task 50: Per-tenant settings for quote behavior, defaults, and numbering.
"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.quotes.constants import DiscountType


class QuoteSettings(models.Model):
    """Per-tenant configuration for the quotes module."""

    tenant = models.OneToOneField(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="quote_settings",
    )

    # Quote numbering
    default_validity_days = models.PositiveIntegerField(
        default=30,
        validators=[MinValueValidator(1), MaxValueValidator(365)],
        help_text="Default number of days a quote is valid",
    )
    quote_number_prefix = models.CharField(
        max_length=10,
        default="QT",
        help_text="Prefix for quote numbers",
    )
    quote_number_format = models.CharField(
        max_length=50,
        default="{prefix}-{year}-{number:05d}",
        help_text="Format template for quote numbers",
    )

    # Automation
    auto_expire_enabled = models.BooleanField(
        default=True,
        help_text="Automatically expire quotes past validity date",
    )
    require_approval = models.BooleanField(
        default=False,
        help_text="Require approval before sending quotes",
    )
    allow_guest_quotes = models.BooleanField(
        default=True,
        help_text="Allow quotes for non-registered customers",
    )

    # Default content
    default_terms_and_conditions = models.TextField(
        blank=True,
        help_text="Default terms and conditions for new quotes",
    )
    default_notes = models.TextField(
        blank=True,
        help_text="Default notes for new quotes",
    )

    # Default discount
    default_discount_type = models.CharField(
        max_length=20,
        choices=DiscountType.choices,
        null=True,
        blank=True,
        help_text="Default discount type for new quotes",
    )
    default_discount_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Default discount value for new quotes",
    )

    # Email settings
    send_quote_email_enabled = models.BooleanField(
        default=True,
        help_text="Enable sending quote emails",
    )
    send_expiry_reminders = models.BooleanField(
        default=True,
        help_text="Send reminders before quotes expire",
    )
    reminder_days_before_expiry = models.PositiveIntegerField(
        default=3,
        help_text="Days before expiry to send reminder",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "quotes_quotesettings"
        verbose_name = "Quote Settings"
        verbose_name_plural = "Quote Settings"

    def __str__(self):
        return f"Quote Settings for {self.tenant}"

    @classmethod
    def get_or_create_for_tenant(cls, tenant):
        """Get or create settings for a tenant."""
        obj, _created = cls.objects.get_or_create(tenant=tenant)
        return obj

    def generate_quote_number(self, quote_count):
        """Generate a quote number using the configured format."""
        from django.utils import timezone

        return self.quote_number_format.format(
            prefix=self.quote_number_prefix,
            year=timezone.now().year,
            number=quote_count,
        )
