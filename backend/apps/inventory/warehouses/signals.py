"""
Signals for warehouse location barcode management.

Auto-generates barcodes on StorageLocation save when the barcode
field is empty.
"""

import logging

from django.db.models.signals import pre_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(pre_save, sender="inventory.StorageLocation")
def auto_generate_barcode(sender, instance, **kwargs):
    """Generate a barcode for a StorageLocation if one is not already set."""
    if instance.barcode:
        return

    if not instance.warehouse_id or not instance.code:
        return

    try:
        from apps.inventory.warehouses.services.barcode_generator import (
            BarcodeGenerator,
        )

        generator = BarcodeGenerator()
        instance.barcode = generator.generate_location_barcode(instance)
        logger.info(
            "Auto-generated barcode %s for location %s",
            instance.barcode,
            instance.code,
        )
    except Exception:
        logger.exception(
            "Failed to auto-generate barcode for location %s", instance.code
        )
