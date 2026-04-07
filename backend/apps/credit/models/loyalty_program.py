"""
Loyalty Program model.

Defines the LoyaltyProgram model for configuring tenant-specific
loyalty programs with points earning rates, redemption values,
and program lifecycle management.
"""

from django.db import models
from django.utils import timezone

from apps.core.mixins import UUIDMixin, TimestampMixin, SoftDeleteMixin


class LoyaltyProgram(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """
    Loyalty program configuration for a tenant.

    Stores the rules for earning, redeeming, and expiring loyalty points.
    Each tenant can have multiple programs but typically only one active at a time.
    """

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="loyalty_programs",
    )
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)

    # Points earning settings
    points_per_currency = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1,
        help_text="Points awarded per Rs. 100 spent.",
    )
    min_purchase_for_points = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Minimum purchase amount to earn points.",
    )

    # Points expiry
    points_expiry_months = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Months until earned points expire. Null = never expire.",
    )

    # Redemption settings
    min_points_for_redemption = models.PositiveIntegerField(
        default=100,
        help_text="Minimum points required for redemption.",
    )
    redemption_value_per_point = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1,
        help_text="Discount value per point redeemed (Rs.).",
    )

    # Program lifecycle
    is_active = models.BooleanField(default=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    # Versioning
    version = models.PositiveIntegerField(default=1)

    class Meta:
        app_label = "credit"
        db_table = "credit_loyalty_program"
        ordering = ["-created_on"]
        indexes = [
            models.Index(fields=["tenant", "is_active"], name="idx_program_tenant_active"),
        ]

    def __str__(self):
        return f"{self.name} (v{self.version})"

    @property
    def is_currently_active(self):
        """Check if program is active and within date range."""
        if not self.is_active:
            return False
        today = timezone.now().date()
        if self.start_date and today < self.start_date:
            return False
        if self.end_date and today > self.end_date:
            return False
        return True

    @property
    def days_until_expiry(self):
        """Calculate days until program end date."""
        if self.end_date is None:
            return None
        today = timezone.now().date()
        return (self.end_date - today).days

    def clean(self):
        """Validate program dates."""
        from django.core.exceptions import ValidationError

        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError({"end_date": "End date must be after start date."})
