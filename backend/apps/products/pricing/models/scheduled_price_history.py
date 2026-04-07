"""
ScheduledPriceHistory – archive of expired scheduled prices.
"""

from django.conf import settings
from django.db import models

from apps.core.models import BaseModel

from ..fields import PriceField


class ScheduledPriceHistory(BaseModel):
    """Record kept before an expired ScheduledPrice is cleaned up."""

    original_id = models.UUIDField(help_text="PK of the original ScheduledPrice.")
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="scheduled_prices_history",
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="scheduled_prices_history",
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    sale_price = PriceField()
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    priority = models.IntegerField(default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    archived_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "pricing_scheduled_history"
        ordering = ["-archived_at"]
        indexes = [
            models.Index(fields=["product", "archived_at"], name="idx_sph_prod_arch"),
            models.Index(fields=["start_datetime", "end_datetime"], name="idx_sph_dates"),
        ]

    def __str__(self):
        return f"[Archived] {self.name} ({self.start_datetime:%Y-%m-%d} → {self.end_datetime:%Y-%m-%d})"
