"""
Signals for automatic price history tracking and promotion analytics.

Listens to ``post_save`` on ``ProductPrice`` and ``VariantPrice`` to
create ``PriceHistory`` records whenever a price field changes.
Also auto-creates ``PromotionAnalytics`` for new promotions.
"""

import logging
from decimal import Decimal

from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

from .middleware import get_current_user

logger = logging.getLogger(__name__)

# Price fields we track for each model
_PRODUCT_PRICE_FIELDS = ("base_price", "cost_price", "sale_price", "wholesale_price")
_VARIANT_PRICE_FIELDS = ("base_price", "cost_price", "sale_price", "wholesale_price")

# Mapping price field → price_type value stored in PriceHistory
_FIELD_TO_TYPE = {
    "base_price": "base",
    "cost_price": "cost",
    "sale_price": "sale",
    "wholesale_price": "wholesale",
}


def _record_change(instance, field_name, old_value, new_value, product, variant=None):
    """Create a PriceHistory entry for a single field change."""
    from .models import PriceHistory

    ct = ContentType.objects.get_for_model(instance)
    user = get_current_user()
    PriceHistory.objects.create(
        content_type=ct,
        object_id=instance.pk,
        product=product,
        variant=variant,
        price_type=_FIELD_TO_TYPE.get(field_name, field_name),
        old_value=old_value,
        new_value=new_value,
        changed_by=user if user and user.is_authenticated else None,
        change_source="manual",
    )


def _get_old_values(model_class, pk, fields):
    """Fetch previous field values from the database."""
    try:
        old = model_class.all_with_deleted.get(pk=pk)
        return {f: getattr(old, f) for f in fields}
    except model_class.DoesNotExist:
        return {}


@receiver(post_save, sender="pricing.ProductPrice")
def track_product_price_change(sender, instance, created, **kwargs):
    """Record PriceHistory for each changed price field on ProductPrice."""
    if created:
        # Record initial price as a history entry
        for field in _PRODUCT_PRICE_FIELDS:
            value = getattr(instance, field)
            if value is not None:
                _record_change(
                    instance=instance,
                    field_name=field,
                    old_value=None,
                    new_value=value,
                    product=instance.product,
                )
        return

    # For updates, compare with DB state before this save
    old_values = _get_old_values(sender, instance.pk, _PRODUCT_PRICE_FIELDS)
    for field in _PRODUCT_PRICE_FIELDS:
        old_val = old_values.get(field)
        new_val = getattr(instance, field)
        if old_val != new_val:
            _record_change(
                instance=instance,
                field_name=field,
                old_value=old_val,
                new_value=new_val,
                product=instance.product,
            )


@receiver(post_save, sender="pricing.VariantPrice")
def track_variant_price_change(sender, instance, created, **kwargs):
    """Record PriceHistory for each changed price field on VariantPrice."""
    product = instance.variant.product if instance.variant_id else None
    variant = instance.variant if instance.variant_id else None

    if created:
        for field in _VARIANT_PRICE_FIELDS:
            value = getattr(instance, field)
            if value is not None:
                _record_change(
                    instance=instance,
                    field_name=field,
                    old_value=None,
                    new_value=value,
                    product=product,
                    variant=variant,
                )
        return

    old_values = _get_old_values(sender, instance.pk, _VARIANT_PRICE_FIELDS)
    for field in _VARIANT_PRICE_FIELDS:
        old_val = old_values.get(field)
        new_val = getattr(instance, field)
        if old_val != new_val:
            _record_change(
                instance=instance,
                field_name=field,
                old_value=old_val,
                new_value=new_val,
                product=product,
                variant=variant,
            )


# ── Promotion analytics auto-create ───────────────────────────────


@receiver(post_save, sender="pricing.ScheduledPrice")
def create_scheduled_price_analytics(sender, instance, created, **kwargs):
    """Auto-create PromotionAnalytics when a ScheduledPrice is created."""
    if created:
        from .models.promotion_analytics import PromotionAnalytics
        PromotionAnalytics.objects.create(scheduled_price=instance)


@receiver(post_save, sender="pricing.PromotionalPrice")
def create_promotional_price_analytics(sender, instance, created, **kwargs):
    """Auto-create PromotionAnalytics when a PromotionalPrice is created."""
    if created:
        from .models.promotion_analytics import PromotionAnalytics
        PromotionAnalytics.objects.create(promotional_price=instance)


# ── Flash sale quantity tracking ───────────────────────────────────


class FlashSaleReservation:
    """
    Cache-based quantity reservation system for flash sales.

    During checkout, quantity is reserved to prevent overselling.
    Reservations expire after a configurable timeout.
    """

    RESERVATION_TIMEOUT = 600  # 10 minutes

    @classmethod
    def reserve(cls, flash_sale_id, quantity: int, session_id: str) -> bool:
        """Reserve quantity for a flash sale during checkout."""
        from .models.flash_sale import FlashSale

        try:
            flash_sale = FlashSale.objects.get(pk=flash_sale_id)
        except FlashSale.DoesNotExist:
            return False

        cache_key = f"flash_sale_reserved:{flash_sale_id}"
        reserved = cache.get(cache_key, 0)
        available = flash_sale.max_quantity - flash_sale.quantity_sold - reserved

        if available >= quantity:
            cache.set(cache_key, reserved + quantity, cls.RESERVATION_TIMEOUT)
            user_key = f"flash_sale_reservation:{session_id}:{flash_sale_id}"
            cache.set(user_key, quantity, cls.RESERVATION_TIMEOUT)
            logger.info("Reserved %d for flash sale %s (session %s)", quantity, flash_sale_id, session_id)
            return True
        return False

    @classmethod
    def release(cls, flash_sale_id, session_id: str):
        """Release a previously held reservation."""
        cache_key = f"flash_sale_reserved:{flash_sale_id}"
        user_key = f"flash_sale_reservation:{session_id}:{flash_sale_id}"
        quantity = cache.get(user_key, 0)
        if quantity:
            reserved = cache.get(cache_key, 0)
            cache.set(cache_key, max(0, reserved - quantity), cls.RESERVATION_TIMEOUT)
            cache.delete(user_key)
            logger.info("Released %d for flash sale %s (session %s)", quantity, flash_sale_id, session_id)

    @classmethod
    def get_available(cls, flash_sale_id) -> int:
        """Get available quantity considering current reservations."""
        from .models.flash_sale import FlashSale

        try:
            flash_sale = FlashSale.objects.get(pk=flash_sale_id)
        except FlashSale.DoesNotExist:
            return 0

        reserved = cache.get(f"flash_sale_reserved:{flash_sale_id}", 0)
        return max(0, flash_sale.max_quantity - flash_sale.quantity_sold - reserved)
