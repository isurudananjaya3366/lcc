"""
Warehouse dashboard data service.

Aggregates statistics for a warehouse into a JSON-serialisable dictionary
suitable for front-end dashboard rendering.
"""

import logging

from django.core.cache import cache
from django.db.models import Count, Q

logger = logging.getLogger(__name__)


class WarehouseDashboard:
    """Aggregate warehouse statistics for dashboard display."""

    CACHE_TIMEOUT = 300  # 5 minutes

    def get_warehouse_stats(self, warehouse):
        """
        Return a dict of key dashboard metrics for *warehouse*.
        """
        cache_key = f"wh_dashboard_{warehouse.pk}"
        stats = cache.get(cache_key)
        if stats is not None:
            return stats

        from apps.inventory.warehouses.models import (
            StorageLocation,
            WarehouseCapacity,
            WarehouseZone,
        )

        locations = StorageLocation.objects.filter(warehouse=warehouse)
        zones = WarehouseZone.objects.filter(warehouse=warehouse)

        active_count = locations.filter(is_active=True).count()
        inactive_count = locations.filter(is_active=False).count()

        # Capacity
        capacity_pct = 0.0
        alerts = []
        try:
            cap = WarehouseCapacity.objects.get(warehouse=warehouse)
            capacity_pct = cap.utilization_percentage
            alerts = cap.check_capacity_alerts()
        except WarehouseCapacity.DoesNotExist:
            pass

        # Top locations by scan activity
        top_locations = list(
            locations.filter(scans__isnull=False)
            .annotate(scan_count=Count("scans"))
            .order_by("-scan_count")
            .values("code", "scan_count")[:10]
        )

        stats = {
            "warehouse_code": warehouse.code,
            "warehouse_name": warehouse.name,
            "total_locations": locations.count(),
            "active_locations": active_count,
            "inactive_locations": inactive_count,
            "zone_count": zones.count(),
            "capacity_percentage": round(capacity_pct, 1),
            "alerts": alerts,
            "top_locations_by_activity": top_locations,
        }

        cache.set(cache_key, stats, self.CACHE_TIMEOUT)
        return stats

    def get_zone_breakdown(self, warehouse):
        """Return location counts per zone for *warehouse*."""
        from apps.inventory.warehouses.models import WarehouseZone

        zones = WarehouseZone.objects.filter(warehouse=warehouse, is_active=True)
        return list(
            zones.annotate(location_count=Count("locations")).values(
                "code", "name", "purpose", "location_count"
            )
        )

    def get_capacity_trend(self, warehouse, days=30):
        """
        Placeholder for historical capacity trend.

        Returns an empty list until a CapacityHistory model or scheduled
        snapshots are implemented.
        """
        return []
