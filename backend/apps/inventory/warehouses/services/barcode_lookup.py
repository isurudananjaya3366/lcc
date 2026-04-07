"""
Service for looking up storage locations by barcode.

Provides cached lookup with optional scan logging integration.
"""

import logging

from django.core.cache import cache

from apps.inventory.warehouses.services.barcode_generator import BarcodeGenerator

logger = logging.getLogger(__name__)


class BarcodeLookup:
    """Fast location lookup by barcode with caching."""

    CACHE_TIMEOUT = 3600  # 1 hour

    def __init__(self):
        self.generator = BarcodeGenerator()

    def lookup_location(self, barcode, user=None, scan_type=None):
        """
        Find a StorageLocation by barcode.

        Validates format first, then checks cache, then queries the DB.
        Optionally logs the scan when *user* and *scan_type* are provided.

        Returns the StorageLocation instance or None.
        Raises ValueError for invalid barcode format.
        """
        if not self.generator.validate_barcode(barcode):
            raise ValueError(f"Invalid barcode format: {barcode}")

        cache_key = f"location_barcode_{barcode}"
        location = cache.get(cache_key)
        if location is not None:
            self._maybe_log_scan(location, barcode, user, scan_type)
            return location

        from apps.inventory.warehouses.models import StorageLocation

        try:
            location = StorageLocation.objects.select_related(
                "warehouse", "parent"
            ).get(barcode=barcode)
            cache.set(cache_key, location, self.CACHE_TIMEOUT)
            logger.info("Barcode lookup successful: %s", barcode)
        except StorageLocation.DoesNotExist:
            location = None
            logger.warning("Barcode lookup failed: %s", barcode)

        self._maybe_log_scan(location, barcode, user, scan_type)
        return location

    def lookup_product_in_location(self, barcode):
        """
        Find products stored at the location identified by *barcode*.

        Returns a list of dicts ``{'product', 'quantity', 'unit', 'location_bin'}``.
        Requires the StockLevel model from a future sub-phase; returns ``[]``
        until that model exists.
        """
        location = self.lookup_location(barcode)
        if not location:
            return []

        try:
            from apps.inventory.models import Stock

            stock_items = Stock.objects.filter(
                location=location,
            ).select_related("product")
            return [
                {
                    "product": item.product,
                    "quantity": item.quantity,
                    "location_bin": location.code,
                }
                for item in stock_items
            ]
        except Exception:
            # StockLevel model may not exist yet
            return []

    def invalidate_cache(self, barcode):
        cache.delete(f"location_barcode_{barcode}")

    # ── private helpers ───────────────────────────────────────────────

    def _maybe_log_scan(self, location, barcode, user, scan_type):
        if not user or not scan_type:
            return
        try:
            from apps.inventory.warehouses.models import BarcodeScan

            BarcodeScan.objects.create(
                location=location,
                user=user,
                scan_type=scan_type,
                scanned_barcode=barcode,
                success=location is not None,
            )
        except Exception:
            logger.exception("Failed to log barcode scan for %s", barcode)
