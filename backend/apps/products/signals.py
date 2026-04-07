"""
Django signal handlers for the products application.

Provides auto-name generation for product variants and logging
for variant lifecycle events.
"""

import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.products.models.product_variant import ProductVariant

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=ProductVariant)
def auto_generate_variant_name(sender, instance, **kwargs):
    """
    Auto-generate variant name from option values on save.

    Skips if the name is already set (allows manual override) or
    if the instance has no PK yet (M2M is not available before the
    first save).  Delegates to :func:`get_variant_name` for the
    actual formatting.
    """
    if instance.name:
        return
    if not instance.pk:
        return
    generated = get_variant_name(instance)
    if generated:
        instance.name = generated


@receiver(post_save, sender=ProductVariant)
def variant_post_save_handler(sender, instance, created, **kwargs):
    """Log variant creation and updates for audit trail."""
    if created:
        logger.info(
            "Variant '%s' created for product '%s'",
            instance.sku,
            instance.product_id,
        )
    else:
        logger.info("Variant '%s' updated", instance.sku)


def get_variant_name(
    variant, separator=" / ", use_labels=True
) -> str:
    """
    Return a formatted variant name from its option values.

    Args:
        variant: A ``ProductVariant`` instance with M2M populated.
        separator: String used to join option value labels.
        use_labels: If True, use the ``label`` field; otherwise ``value``.

    Returns:
        Formatted name string (e.g., ``"Medium / Red"``).
    """
    option_vals = (
        variant.option_values.select_related("option_type")
        .order_by("option_type__display_order", "display_order")
    )
    if use_labels:
        parts = [ov.label or ov.value for ov in option_vals]
    else:
        parts = [ov.value for ov in option_vals]
    return separator.join(parts)
