"""
Custom managers for the pricing models.
"""

from django.db.models import F, Q
from django.utils import timezone

from apps.core.managers import AliveManager


class ProductPriceManager(AliveManager):
    """Enhanced manager for ProductPrice with common query helpers."""

    def get_queryset(self):
        return super().get_queryset().select_related("product", "tax_class")

    def active_sales(self):
        now = timezone.now()
        return self.get_queryset().filter(
            sale_price__isnull=False,
            sale_price_start__lte=now,
            sale_price_end__gte=now,
        )

    def upcoming_sales(self):
        now = timezone.now()
        return self.get_queryset().filter(
            sale_price__isnull=False,
            sale_price_start__gt=now,
        )

    def expired_sales(self):
        now = timezone.now()
        return self.get_queryset().filter(
            sale_price__isnull=False,
            sale_price_end__lt=now,
        )

    def with_wholesale_pricing(self):
        return self.get_queryset().filter(wholesale_price__isnull=False)

    def taxable_products(self):
        return self.get_queryset().filter(is_taxable=True)

    def tax_exempt_products(self):
        return self.get_queryset().filter(is_taxable=False)

    def for_customer_type(self, customer_type: str):
        if customer_type in ("wholesale", "b2b"):
            return self.with_wholesale_pricing()
        return self.get_queryset()

    def profitable_products(self):
        return self.get_queryset().filter(
            cost_price__isnull=False,
            base_price__gt=F("cost_price"),
        )

    def products_in_price_range(self, min_price=None, max_price=None):
        qs = self.get_queryset()
        if min_price is not None:
            qs = qs.filter(base_price__gte=min_price)
        if max_price is not None:
            qs = qs.filter(base_price__lte=max_price)
        return qs
