"""
Signals for stock level and movement changes.

Maintains data consistency by updating product-level aggregated stock
when individual StockLevel records change, emits custom signals for
stock operations, and provides pre-save validation.
"""

import logging

import django.dispatch
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)

# ── Custom Signals (Task 54) ────────────────────────────────────────
stock_level_changed = django.dispatch.Signal()  # sender, instance, operation_type, user
stock_movement_created = django.dispatch.Signal()  # sender, instance, user


@receiver(pre_save, sender="inventory.StockLevel")
def validate_stock_level(sender, instance, **kwargs):
    """Validate stock level data before saving."""
    if instance.quantity < 0:
        logger.warning(
            "Attempting to save StockLevel pk=%s with negative quantity=%s",
            instance.pk,
            instance.quantity,
        )
    if instance.reserved_quantity < 0:
        logger.warning(
            "Attempting to save StockLevel pk=%s with negative reserved_quantity=%s",
            instance.pk,
            instance.reserved_quantity,
        )


@receiver(post_save, sender="inventory.StockLevel")
def update_product_total_stock(sender, instance, created, **kwargs):
    """Update product's aggregated total stock after StockLevel save."""
    try:
        from apps.inventory.stock.models.stock_level import StockLevel

        product = instance.product
        total = StockLevel.objects.get_total_stock(product, instance.variant)
        # Update product stock if it has a stock-tracking field
        if hasattr(product, "total_stock"):
            type(product).objects.filter(pk=product.pk).update(total_stock=total)
        logger.debug(
            "Updated total stock for product pk=%s: %s",
            product.pk,
            total,
        )
    except Exception:
        logger.exception("Failed to update product total stock for StockLevel pk=%s", instance.pk)


@receiver(post_delete, sender="inventory.StockLevel")
def recalculate_product_stock_on_delete(sender, instance, **kwargs):
    """Recalculate product total stock after StockLevel deletion."""
    try:
        from apps.inventory.stock.models.stock_level import StockLevel

        product = instance.product
        total = StockLevel.objects.get_total_stock(product, instance.variant)
        if hasattr(product, "total_stock"):
            type(product).objects.filter(pk=product.pk).update(total_stock=total)
        logger.debug(
            "Recalculated total stock for product pk=%s after deletion: %s",
            product.pk,
            total,
        )
    except Exception:
        logger.exception("Failed to recalculate stock on delete for product")


@receiver(post_save, sender="inventory.StockMovement")
def emit_movement_created(sender, instance, created, **kwargs):
    """Emit stock_movement_created signal for new movements."""
    if created:
        stock_movement_created.send(
            sender=sender,
            instance=instance,
            user=instance.created_by,
        )
