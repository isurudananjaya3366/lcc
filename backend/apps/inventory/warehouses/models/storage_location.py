"""
StorageLocation model for hierarchical warehouse locations.

Defines the StorageLocation model representing individual storage
positions within warehouses. Uses a self-referential ForeignKey
for the five-level hierarchy: Zone → Aisle → Rack → Shelf → Bin.
Tenant scoping is enforced via django-tenants schema isolation.
"""

from django.core.exceptions import ValidationError
from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin
from apps.inventory.warehouses.constants import (
    LOCATION_DEPTH_MAP,
    LOCATION_PARENT_RULES,
    LOCATION_TYPE_AISLE,
    LOCATION_TYPE_BIN,
    LOCATION_TYPE_CHOICES,
    LOCATION_TYPE_RACK,
    LOCATION_TYPE_SHELF,
    LOCATION_TYPE_ZONE,
    UTILIZATION_EMPTY,
    UTILIZATION_STATUS_CHOICES,
)
from apps.inventory.warehouses.managers.location_manager import StorageLocationManager


class StorageLocation(UUIDMixin, TimestampMixin, models.Model):
    """
    Hierarchical storage location within a warehouse.

    Supports five depth levels:
        0 – Zone (root, no parent)
        1 – Aisle (parent must be Zone)
        2 – Rack  (parent must be Aisle)
        3 – Shelf (parent must be Rack)
        4 – Bin   (parent must be Shelf)

    Cascade deletion: removing a parent removes all descendants.
    """

    # ── Relationships ───────────────────────────────────────────────
    warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.CASCADE,
        related_name="storage_locations",
        db_index=True,
        verbose_name="Warehouse",
        help_text="Warehouse containing this location.",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="children",
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Parent Location",
        help_text="Parent location in the hierarchy.",
    )
    zone = models.ForeignKey(
        "inventory.WarehouseZone",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="locations",
        verbose_name="Zone",
        help_text="Operational zone this location belongs to.",
    )

    # ── Identity ────────────────────────────────────────────────────
    location_type = models.CharField(
        max_length=20,
        choices=LOCATION_TYPE_CHOICES,
        db_index=True,
        verbose_name="Location Type",
        help_text="Hierarchy level: zone, aisle, rack, shelf, or bin.",
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Location Name",
        help_text='e.g., "Storage Zone A", "Aisle 3", "Rack 2"',
    )
    code = models.CharField(
        max_length=50,
        db_index=True,
        verbose_name="Location Code",
        help_text='Unique code like "A03-R02-S04-B01".',
    )
    barcode = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_index=True,
        verbose_name="Barcode",
        help_text="Scannable barcode for this location.",
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description",
        help_text="Additional location details or instructions.",
    )

    # ── Capacity ────────────────────────────────────────────────────
    max_weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Max Weight (kg)",
        help_text="Maximum weight capacity in kilograms.",
    )
    max_volume = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        blank=True,
        null=True,
        verbose_name="Max Volume (m³)",
        help_text="Maximum volume capacity in cubic metres.",
    )
    max_items = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Max Items",
        help_text="Maximum number of items/SKUs at this location.",
    )
    max_pallets = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name="Max Pallets",
        help_text="Maximum number of pallets at this location.",
    )
    capacity_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Capacity Notes",
        help_text="Additional notes about storage capacity or restrictions.",
    )

    # ── Operational Flags ───────────────────────────────────────────
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Active",
        help_text="Location is operational and can be used.",
    )
    is_pickable = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Pickable",
        help_text="Location can be used for order picking.",
    )
    is_receivable = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Receivable",
        help_text="Location can receive incoming goods.",
    )

    # ── Utilisation Tracking ────────────────────────────────────────
    utilization_status = models.CharField(
        max_length=10,
        choices=UTILIZATION_STATUS_CHOICES,
        default=UTILIZATION_EMPTY,
        db_index=True,
        verbose_name="Utilisation Status",
    )
    last_activity_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Last Activity",
        help_text="Timestamp of last stock movement at this location.",
    )

    # ── Managers ────────────────────────────────────────────────────
    objects = StorageLocationManager()

    class Meta:
        verbose_name = "Storage Location"
        verbose_name_plural = "Storage Locations"
        db_table = "inventory_storage_locations"
        ordering = ["warehouse", "code"]
        indexes = [
            models.Index(
                fields=["warehouse", "code"],
                name="idx_loc_wh_code",
            ),
            models.Index(
                fields=["warehouse", "location_type"],
                name="idx_loc_wh_type",
            ),
            models.Index(
                fields=["warehouse", "is_active"],
                name="idx_loc_wh_active",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["warehouse", "code"],
                name="uq_storage_location_warehouse_code",
            ),
            models.UniqueConstraint(
                fields=["barcode"],
                condition=models.Q(barcode__isnull=False),
                name="uq_storage_location_barcode",
            ),
        ]
        permissions = [
            ("can_deactivate_location", "Can deactivate a storage location"),
            ("can_bulk_create_locations", "Can bulk-create storage locations"),
        ]

    # ── String Representations ──────────────────────────────────────

    def __str__(self):
        return f"{self.code} ({self.name})"

    def __repr__(self):
        return (
            f"<StorageLocation id={self.pk} "
            f"type={self.location_type!r} code={self.code!r}>"
        )

    # ── Computed Properties ─────────────────────────────────────────

    @property
    def depth(self):
        """Hierarchy depth: 0=Zone, 1=Aisle, 2=Rack, 3=Shelf, 4=Bin."""
        return LOCATION_DEPTH_MAP.get(self.location_type, 0)

    @property
    def level_name(self):
        """Human-readable level name."""
        names = {0: "Zone", 1: "Aisle", 2: "Rack", 3: "Shelf", 4: "Bin"}
        return names.get(self.depth, "Unknown")

    @property
    def location_path(self):
        """
        Full hierarchy path from root to this location.

        Example: "Zone A > Aisle 03 > Rack 02 > Bin 01"
        """
        parts = []
        current = self
        seen = set()
        while current is not None:
            if current.pk in seen:
                break  # guard against circular references
            seen.add(current.pk)
            parts.append(current.name)
            current = current.parent if current.parent_id else None
        parts.reverse()
        return " > ".join(parts)

    # ── Hierarchy Navigation ────────────────────────────────────────

    def get_children(self, active_only=False):
        """Return direct child locations, ordered by code."""
        qs = self.children.all()
        if active_only:
            qs = qs.filter(is_active=True)
        return qs.order_by("code")

    def get_child_count(self):
        return self.children.count()

    def has_children(self):
        return self.children.exists()

    def get_all_descendants(self, active_only=False, depth_limit=None):
        """
        Return all descendant locations recursively.

        Uses iterative breadth-first traversal to avoid deep recursion.
        """
        descendants = []
        queue = list(self.get_children(active_only=active_only))
        current_depth = 0

        while queue:
            if depth_limit is not None and current_depth >= depth_limit:
                break
            next_queue = []
            for loc in queue:
                descendants.append(loc)
                next_queue.extend(loc.get_children(active_only=active_only))
            queue = next_queue
            current_depth += 1

        return descendants

    def get_descendant_count(self, active_only=False):
        return len(self.get_all_descendants(active_only=active_only))

    # Type-specific child accessors

    def get_aisles(self, active_only=True):
        """Child aisles (valid only for Zones)."""
        if self.location_type != LOCATION_TYPE_ZONE:
            return StorageLocation.objects.none()
        return self.get_children(active_only).filter(
            location_type=LOCATION_TYPE_AISLE
        )

    def get_racks(self, active_only=True):
        """Child racks (valid only for Aisles)."""
        if self.location_type != LOCATION_TYPE_AISLE:
            return StorageLocation.objects.none()
        return self.get_children(active_only).filter(
            location_type=LOCATION_TYPE_RACK
        )

    def get_shelves(self, active_only=True):
        """Child shelves (valid only for Racks)."""
        if self.location_type != LOCATION_TYPE_RACK:
            return StorageLocation.objects.none()
        return self.get_children(active_only).filter(
            location_type=LOCATION_TYPE_SHELF
        )

    def get_bins(self, active_only=True):
        """Child bins (valid only for Shelves)."""
        if self.location_type != LOCATION_TYPE_SHELF:
            return StorageLocation.objects.none()
        return self.get_children(active_only).filter(
            location_type=LOCATION_TYPE_BIN
        )

    # ── Validation ──────────────────────────────────────────────────

    def clean(self):
        """
        Validate hierarchy rules and field consistency.
        """
        super().clean()
        errors = {}

        # Code uppercase
        if self.code:
            self.code = self.code.upper()

        # Parent type rules
        expected_parent_type = LOCATION_PARENT_RULES.get(self.location_type)
        if expected_parent_type is None:
            # Zone must have no parent
            if self.parent_id is not None:
                errors["parent"] = "Zones cannot have a parent location."
        else:
            if self.parent_id is None:
                errors["parent"] = (
                    f"{self.get_location_type_display()} requires a parent "
                    f"of type {expected_parent_type}."
                )
            elif self.parent.location_type != expected_parent_type:
                errors["parent"] = (
                    f"{self.get_location_type_display()} parent must be "
                    f"{expected_parent_type}, not {self.parent.location_type}."
                )

        # Parent must be in the same warehouse
        if self.parent_id and hasattr(self.parent, "warehouse_id"):
            if self.parent.warehouse_id != self.warehouse_id:
                errors["parent"] = (
                    "Parent location must be in the same warehouse."
                )

        # Capacity: non-negative
        if self.max_weight is not None and self.max_weight < 0:
            errors["max_weight"] = "Max weight cannot be negative."
        if self.max_volume is not None and self.max_volume < 0:
            errors["max_volume"] = "Max volume cannot be negative."

        if errors:
            raise ValidationError(errors)
