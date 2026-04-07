"""
WarehouseZone model — logical area grouping within a warehouse.

Zones organise storage locations by operational function
(receiving, storage, picking, shipping, returns, quarantine).
"""

from django.db import models

from apps.core.mixins import TimestampMixin, UUIDMixin
from apps.inventory.warehouses.constants import ZONE_PURPOSE_CHOICES, ZONE_PURPOSE_STORAGE


class WarehouseZone(UUIDMixin, TimestampMixin, models.Model):
    """Logical zone within a warehouse (e.g. Receiving, Cold Storage)."""

    warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.CASCADE,
        related_name="zones",
    )

    name = models.CharField(max_length=100)

    code = models.CharField(
        max_length=20,
        help_text="Short identifier, unique per warehouse",
    )

    purpose = models.CharField(
        max_length=20,
        choices=ZONE_PURPOSE_CHOICES,
        default=ZONE_PURPOSE_STORAGE,
        db_index=True,
    )

    description = models.TextField(blank=True, default="")

    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        app_label = "inventory"
        db_table = "inventory_warehouse_zones"
        verbose_name = "Warehouse Zone"
        verbose_name_plural = "Warehouse Zones"
        ordering = ["warehouse", "code"]
        constraints = [
            models.UniqueConstraint(
                fields=["warehouse", "code"],
                name="uq_zone_warehouse_code",
            ),
        ]
        indexes = [
            models.Index(fields=["warehouse", "purpose"]),
        ]

    def __str__(self):
        return f"{self.warehouse.code} / {self.name}"
