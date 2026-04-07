"""
StorageLocation model manager and queryset.

Provides chainable query methods for storage location filtering
by warehouse, type, activity status, and operational flags.
"""

from django.db import models

from apps.inventory.warehouses.constants import (
    LOCATION_TYPE_BIN,
    LOCATION_TYPE_ZONE,
)


class StorageLocationQuerySet(models.QuerySet):
    """Chainable query methods for StorageLocation."""

    def active(self):
        return self.filter(is_active=True)

    def inactive(self):
        return self.filter(is_active=False)

    def for_warehouse(self, warehouse):
        return self.filter(warehouse=warehouse)

    def by_warehouse(self, warehouse):
        """Alias for for_warehouse (task-doc name)."""
        return self.for_warehouse(warehouse)

    def by_parent(self, parent):
        """Filter locations by parent."""
        return self.filter(parent=parent)

    def by_type(self, location_type):
        return self.filter(location_type=location_type)

    def zones(self):
        return self.filter(location_type=LOCATION_TYPE_ZONE)

    def bins(self):
        return self.filter(location_type=LOCATION_TYPE_BIN)

    def roots(self):
        """Locations with no parent (zones)."""
        return self.filter(parent__isnull=True)

    def root_locations(self):
        """Alias for roots (task-doc name)."""
        return self.roots()

    def pickable(self):
        return self.filter(is_pickable=True, is_active=True)

    def receivable(self):
        return self.filter(is_receivable=True, is_active=True)


class StorageLocationManager(models.Manager):
    """Custom manager for StorageLocation."""

    def get_queryset(self):
        return StorageLocationQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def inactive(self):
        return self.get_queryset().inactive()

    def for_warehouse(self, warehouse):
        return self.get_queryset().for_warehouse(warehouse)

    def by_warehouse(self, warehouse):
        return self.get_queryset().by_warehouse(warehouse)

    def by_parent(self, parent):
        return self.get_queryset().by_parent(parent)

    def by_type(self, location_type):
        return self.get_queryset().by_type(location_type)

    def zones(self):
        return self.get_queryset().zones()

    def bins(self):
        return self.get_queryset().bins()

    def roots(self):
        return self.get_queryset().roots()

    def root_locations(self):
        return self.get_queryset().root_locations()

    def pickable(self):
        return self.get_queryset().pickable()

    def receivable(self):
        return self.get_queryset().receivable()

    def get_by_barcode(self, barcode):
        """Look up a location by its barcode. Returns None if not found."""
        try:
            return self.get_queryset().get(barcode=barcode)
        except self.model.DoesNotExist:
            return None

    def get_by_code(self, warehouse, code):
        """Look up a location by warehouse and code. Returns None if not found."""
        try:
            return self.get_queryset().get(warehouse=warehouse, code=code)
        except self.model.DoesNotExist:
            return None
