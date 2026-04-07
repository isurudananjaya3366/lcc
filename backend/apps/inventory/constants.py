"""
Inventory constants module.

Defines choices, status values, and other constants used across
the inventory application models.
"""

# ════════════════════════════════════════════════════════════════════════
# Location Type Choices
# ════════════════════════════════════════════════════════════════════════

LOCATION_TYPE_WAREHOUSE = "warehouse"
LOCATION_TYPE_STORE = "store"
LOCATION_TYPE_TRANSIT = "transit"
LOCATION_TYPE_VIRTUAL = "virtual"

LOCATION_TYPE_CHOICES = [
    (LOCATION_TYPE_WAREHOUSE, "Central Warehouse"),
    (LOCATION_TYPE_STORE, "Retail Store"),
    (LOCATION_TYPE_TRANSIT, "In-Transit"),
    (LOCATION_TYPE_VIRTUAL, "Virtual / Dropship"),
]

# Default location type for new locations
DEFAULT_LOCATION_TYPE = LOCATION_TYPE_WAREHOUSE

# ════════════════════════════════════════════════════════════════════════
# Movement Type Choices
# ════════════════════════════════════════════════════════════════════════

MOVEMENT_TYPE_IN = "in"
MOVEMENT_TYPE_OUT = "out"
MOVEMENT_TYPE_TRANSFER = "transfer"
MOVEMENT_TYPE_ADJUSTMENT = "adjustment"
MOVEMENT_TYPE_RETURN = "return"

MOVEMENT_TYPE_CHOICES = [
    (MOVEMENT_TYPE_IN, "Stock Received"),
    (MOVEMENT_TYPE_OUT, "Stock Sold / Consumed"),
    (MOVEMENT_TYPE_TRANSFER, "Transfer Between Locations"),
    (MOVEMENT_TYPE_ADJUSTMENT, "Manual Adjustment"),
    (MOVEMENT_TYPE_RETURN, "Customer Return"),
]
