"""
Bulk location generator for warehouse storage hierarchies.

Creates a predefined hierarchy of storage locations for a warehouse
in a single operation, following the Zone → Aisle → Rack → Shelf → Bin
structure.
"""

from apps.inventory.warehouses.constants import (
    LOCATION_TYPE_AISLE,
    LOCATION_TYPE_BIN,
    LOCATION_TYPE_RACK,
    LOCATION_TYPE_SHELF,
    LOCATION_TYPE_ZONE,
)
from apps.inventory.warehouses.models.storage_location import StorageLocation


def generate_locations(
    warehouse,
    zones=1,
    aisles_per_zone=2,
    racks_per_aisle=4,
    shelves_per_rack=4,
    bins_per_shelf=2,
    zone_prefix="",
):
    """
    Bulk-create a hierarchical location tree for *warehouse*.

    Returns the list of all created ``StorageLocation`` instances.

    Args:
        warehouse: Warehouse instance to create locations in.
        zones: Number of zones (default 1). Named A, B, C, ...
        aisles_per_zone: Aisles per zone.
        racks_per_aisle: Racks per aisle.
        shelves_per_rack: Shelves per rack.
        bins_per_shelf: Bins per shelf.
        zone_prefix: Optional prefix for zone codes.
    """
    created = []

    for z in range(zones):
        zone_letter = chr(ord("A") + z)
        zone_code = f"{zone_prefix}{zone_letter}" if zone_prefix else zone_letter
        zone = StorageLocation.objects.create(
            warehouse=warehouse,
            location_type=LOCATION_TYPE_ZONE,
            name=f"Zone {zone_code}",
            code=zone_code,
            parent=None,
        )
        created.append(zone)

        for a in range(1, aisles_per_zone + 1):
            aisle_code = f"{zone_code}{a:02d}"
            aisle = StorageLocation.objects.create(
                warehouse=warehouse,
                location_type=LOCATION_TYPE_AISLE,
                name=f"Aisle {aisle_code}",
                code=aisle_code,
                parent=zone,
            )
            created.append(aisle)

            for r in range(1, racks_per_aisle + 1):
                rack_code = f"{aisle_code}-R{r:02d}"
                rack = StorageLocation.objects.create(
                    warehouse=warehouse,
                    location_type=LOCATION_TYPE_RACK,
                    name=f"Rack {rack_code}",
                    code=rack_code,
                    parent=aisle,
                )
                created.append(rack)

                for s in range(1, shelves_per_rack + 1):
                    shelf_code = f"{rack_code}-S{s:02d}"
                    shelf = StorageLocation.objects.create(
                        warehouse=warehouse,
                        location_type=LOCATION_TYPE_SHELF,
                        name=f"Shelf {shelf_code}",
                        code=shelf_code,
                        parent=rack,
                    )
                    created.append(shelf)

                    for b in range(1, bins_per_shelf + 1):
                        bin_code = f"{shelf_code}-B{b:02d}"
                        bin_loc = StorageLocation.objects.create(
                            warehouse=warehouse,
                            location_type=LOCATION_TYPE_BIN,
                            name=f"Bin {bin_code}",
                            code=bin_code,
                            parent=shelf,
                        )
                        created.append(bin_loc)

    return created
