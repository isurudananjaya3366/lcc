"""
Warehouse model manager and queryset.

Provides chainable query methods for common warehouse operations
such as filtering by status, type, district, and default lookup.
"""

from django.db import models

from apps.inventory.warehouses.constants import (
    WAREHOUSE_STATUS_ACTIVE,
    WAREHOUSE_STATUS_INACTIVE,
)


class WarehouseQuerySet(models.QuerySet):
    """Chainable query methods for Warehouse."""

    def active(self):
        """Return warehouses with ACTIVE status."""
        return self.filter(status=WAREHOUSE_STATUS_ACTIVE)

    def inactive(self):
        """Return warehouses with INACTIVE status."""
        return self.filter(status=WAREHOUSE_STATUS_INACTIVE)

    def by_type(self, warehouse_type):
        """Filter by warehouse type."""
        return self.filter(warehouse_type=warehouse_type)

    def by_district(self, district):
        """Filter by Sri Lankan district."""
        return self.filter(district=district)

    def defaults(self):
        """Return warehouses marked as default."""
        return self.filter(is_default=True)


class WarehouseManager(models.Manager):
    """Custom manager for the Warehouse model."""

    def get_queryset(self):
        return WarehouseQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def inactive(self):
        return self.get_queryset().inactive()

    def by_type(self, warehouse_type):
        return self.get_queryset().by_type(warehouse_type)

    def by_district(self, district):
        return self.get_queryset().by_district(district)

    def get_default(self):
        """
        Return the default warehouse for the current tenant.

        Raises Warehouse.DoesNotExist if no default is configured.
        """
        return self.get_queryset().get(is_default=True)

    def get_by_code(self, code):
        """
        Look up a warehouse by its code (case-insensitive).

        Returns the Warehouse instance or None.
        """
        try:
            return self.get_queryset().get(code=code.upper())
        except self.model.DoesNotExist:
            return None
