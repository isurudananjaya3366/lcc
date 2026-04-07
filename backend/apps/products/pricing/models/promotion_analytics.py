"""
PromotionAnalytics – tracks performance metrics for promotions.
"""

from decimal import Decimal

from django.db import models
from django.utils import timezone

from apps.core.models import BaseModel


class PromotionAnalytics(BaseModel):
    """Aggregated analytics for any type of promotion."""

    scheduled_price = models.OneToOneField(
        "pricing.ScheduledPrice",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="analytics",
    )
    flash_sale = models.OneToOneField(
        "pricing.FlashSale",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="analytics",
    )
    promotional_price = models.OneToOneField(
        "pricing.PromotionalPrice",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="analytics",
    )

    views = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)
    conversions = models.PositiveIntegerField(default=0)
    revenue_generated = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    discount_given = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    last_aggregated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "pricing_promotion_analytics"
        verbose_name = "Promotion Analytics"
        verbose_name_plural = "Promotion Analytics"

    def __str__(self):
        promo = self.scheduled_price or self.flash_sale or self.promotional_price
        label = getattr(promo, "name", "Unknown")
        return f"Analytics: {label}"

    # ── Incrementers ───────────────────────────────────────────

    def increment_views(self, count: int = 1):
        self.views += count
        self.save(update_fields=["views", "updated_on"])

    def increment_clicks(self, count: int = 1):
        self.clicks += count
        self.save(update_fields=["clicks", "updated_on"])

    def record_conversion(self, order_value: Decimal, discount_amount: Decimal):
        self.conversions += 1
        self.revenue_generated += order_value
        self.discount_given += discount_amount
        self.calculate_metrics()
        self.save(update_fields=[
            "conversions", "revenue_generated", "discount_given",
            "conversion_rate", "average_order_value", "updated_on",
        ])

    def calculate_metrics(self):
        if self.clicks > 0:
            self.conversion_rate = Decimal(str(
                round(self.conversions / self.clicks * 100, 2)
            ))
        if self.conversions > 0:
            self.average_order_value = (self.revenue_generated / self.conversions).quantize(Decimal("0.01"))
        self.last_aggregated_at = timezone.now()

    # ── Properties ─────────────────────────────────────────────

    @property
    def roi(self) -> Decimal:
        if self.discount_given > 0:
            return ((self.revenue_generated - self.discount_given) / self.discount_given * 100).quantize(Decimal("0.01"))
        return Decimal("0")

    @property
    def click_through_rate(self) -> Decimal:
        if self.views > 0:
            return Decimal(str(round(self.clicks / self.views * 100, 2)))
        return Decimal("0")
