"""
Warehouse constants and choices.

Defines status values, types, and Sri Lankan district choices used
across the warehouse submodule in the multi-tenant inventory system.
"""

# ════════════════════════════════════════════════════════════════════════
# Warehouse Status Constants
# ════════════════════════════════════════════════════════════════════════

WAREHOUSE_STATUS_ACTIVE = "active"  # Operational, can receive/ship
WAREHOUSE_STATUS_INACTIVE = "inactive"  # Disabled, no operations allowed
WAREHOUSE_STATUS_MAINTENANCE = "maintenance"  # Temporary closure for maintenance

WAREHOUSE_STATUS_CHOICES = (
    (WAREHOUSE_STATUS_ACTIVE, "Active"),
    (WAREHOUSE_STATUS_INACTIVE, "Inactive"),
    (WAREHOUSE_STATUS_MAINTENANCE, "Maintenance"),
)

# ════════════════════════════════════════════════════════════════════════
# Warehouse Type Constants
# ════════════════════════════════════════════════════════════════════════

WAREHOUSE_TYPE_MAIN = "main"  # Primary central warehouse
WAREHOUSE_TYPE_DISTRIBUTION = "distribution"  # Regional fulfillment centers
WAREHOUSE_TYPE_RETAIL = "retail"  # Store-attached warehouse
WAREHOUSE_TYPE_RETURNS = "returns"  # Dedicated RMA/returns processing

WAREHOUSE_TYPE_CHOICES = (
    (WAREHOUSE_TYPE_MAIN, "Main Warehouse"),
    (WAREHOUSE_TYPE_DISTRIBUTION, "Distribution Center"),
    (WAREHOUSE_TYPE_RETAIL, "Retail Store Warehouse"),
    (WAREHOUSE_TYPE_RETURNS, "Returns Processing"),
)

# ════════════════════════════════════════════════════════════════════════
# Sri Lanka District Choices (25 districts across 9 provinces)
# ════════════════════════════════════════════════════════════════════════

# -- Western Province --
DISTRICT_COLOMBO = "colombo"
DISTRICT_GAMPAHA = "gampaha"
DISTRICT_KALUTARA = "kalutara"

# -- Central Province --
DISTRICT_KANDY = "kandy"
DISTRICT_MATALE = "matale"
DISTRICT_NUWARA_ELIYA = "nuwara_eliya"

# -- Southern Province --
DISTRICT_GALLE = "galle"
DISTRICT_MATARA = "matara"
DISTRICT_HAMBANTOTA = "hambantota"

# -- Northern Province --
DISTRICT_JAFFNA = "jaffna"
DISTRICT_KILINOCHCHI = "kilinochchi"
DISTRICT_MANNAR = "mannar"
DISTRICT_VAVUNIYA = "vavuniya"
DISTRICT_MULLAITIVU = "mullaitivu"

# -- Eastern Province --
DISTRICT_BATTICALOA = "batticaloa"
DISTRICT_AMPARA = "ampara"
DISTRICT_TRINCOMALEE = "trincomalee"

# -- North Western Province --
DISTRICT_KURUNEGALA = "kurunegala"
DISTRICT_PUTTALAM = "puttalam"

# -- North Central Province --
DISTRICT_ANURADHAPURA = "anuradhapura"
DISTRICT_POLONNARUWA = "polonnaruwa"

# -- Uva Province --
DISTRICT_BADULLA = "badulla"
DISTRICT_MONARAGALA = "monaragala"

# -- Sabaragamuwa Province --
DISTRICT_RATNAPURA = "ratnapura"
DISTRICT_KEGALLE = "kegalle"

# ════════════════════════════════════════════════════════════════════════
# Storage Location Type Constants
# Five-level hierarchy: Zone → Aisle → Rack → Shelf → Bin
# ════════════════════════════════════════════════════════════════════════

LOCATION_TYPE_ZONE = "zone"  # Logical warehouse area (depth 0)
LOCATION_TYPE_AISLE = "aisle"  # Physical walkway/corridor (depth 1)
LOCATION_TYPE_RACK = "rack"  # Vertical storage structure (depth 2)
LOCATION_TYPE_SHELF = "shelf"  # Horizontal level on rack (depth 3)
LOCATION_TYPE_BIN = "bin"  # Smallest storage unit (depth 4)

LOCATION_TYPE_CHOICES = (
    (LOCATION_TYPE_ZONE, "Zone"),
    (LOCATION_TYPE_AISLE, "Aisle"),
    (LOCATION_TYPE_RACK, "Rack"),
    (LOCATION_TYPE_SHELF, "Shelf"),
    (LOCATION_TYPE_BIN, "Bin"),
)

# Maps location type to hierarchy depth (0 = root)
LOCATION_DEPTH_MAP = {
    LOCATION_TYPE_ZONE: 0,
    LOCATION_TYPE_AISLE: 1,
    LOCATION_TYPE_RACK: 2,
    LOCATION_TYPE_SHELF: 3,
    LOCATION_TYPE_BIN: 4,
}

# Maps each type to its required parent type (None = root)
LOCATION_PARENT_RULES = {
    LOCATION_TYPE_ZONE: None,
    LOCATION_TYPE_AISLE: LOCATION_TYPE_ZONE,
    LOCATION_TYPE_RACK: LOCATION_TYPE_AISLE,
    LOCATION_TYPE_SHELF: LOCATION_TYPE_RACK,
    LOCATION_TYPE_BIN: LOCATION_TYPE_SHELF,
}

# ════════════════════════════════════════════════════════════════════════
# Location Barcode Format Constants
# Format: LOC-{TENANT_PREFIX}-{WAREHOUSE_CODE}-{LOCATION_CODE}-{CHECK_DIGIT}
# Example: LOC-ABC-WHCMB01-A03R02S01B05-7
# ════════════════════════════════════════════════════════════════════════

BARCODE_PREFIX_LOCATION = "LOC"
BARCODE_SEPARATOR = "-"
BARCODE_TENANT_PREFIX_LENGTH = 3
BARCODE_WAREHOUSE_CODE_LENGTH = 6
BARCODE_LOCATION_CODE_LENGTH = 15  # max
CHECK_DIGIT_LENGTH = 1
BARCODE_MAX_LENGTH = 100
BARCODE_CHECK_ALGORITHM = "luhn"

# ════════════════════════════════════════════════════════════════════════
# Barcode Scan Type Constants
# ════════════════════════════════════════════════════════════════════════

SCAN_TYPE_RECEIVING = "RECEIVING"
SCAN_TYPE_PICKING = "PICKING"
SCAN_TYPE_INVENTORY_COUNT = "INVENTORY_COUNT"
SCAN_TYPE_TRANSFER = "TRANSFER"
SCAN_TYPE_INQUIRY = "INQUIRY"

SCAN_TYPE_CHOICES = (
    (SCAN_TYPE_RECEIVING, "Receiving"),
    (SCAN_TYPE_PICKING, "Picking"),
    (SCAN_TYPE_INVENTORY_COUNT, "Inventory Count"),
    (SCAN_TYPE_TRANSFER, "Transfer"),
    (SCAN_TYPE_INQUIRY, "Inquiry"),
)

# ════════════════════════════════════════════════════════════════════════
# Warehouse Zone Purpose Constants
# ════════════════════════════════════════════════════════════════════════

ZONE_PURPOSE_RECEIVING = "receiving"
ZONE_PURPOSE_STORAGE = "storage"
ZONE_PURPOSE_PICKING = "picking"
ZONE_PURPOSE_SHIPPING = "shipping"
ZONE_PURPOSE_RETURNS = "returns"
ZONE_PURPOSE_QUARANTINE = "quarantine"

ZONE_PURPOSE_CHOICES = (
    (ZONE_PURPOSE_RECEIVING, "Receiving"),
    (ZONE_PURPOSE_STORAGE, "Storage"),
    (ZONE_PURPOSE_PICKING, "Picking"),
    (ZONE_PURPOSE_SHIPPING, "Shipping"),
    (ZONE_PURPOSE_RETURNS, "Returns"),
    (ZONE_PURPOSE_QUARANTINE, "Quarantine"),
)

# ════════════════════════════════════════════════════════════════════════
# Location Utilization Status Constants
# ════════════════════════════════════════════════════════════════════════

UTILIZATION_EMPTY = "empty"
UTILIZATION_PARTIAL = "partial"
UTILIZATION_FULL = "full"

UTILIZATION_STATUS_CHOICES = (
    (UTILIZATION_EMPTY, "Empty"),
    (UTILIZATION_PARTIAL, "Partial"),
    (UTILIZATION_FULL, "Full"),
)

# ════════════════════════════════════════════════════════════════════════
# Capacity Alert Thresholds (percentage)
# ════════════════════════════════════════════════════════════════════════

CAPACITY_THRESHOLD_GREEN = 80
CAPACITY_THRESHOLD_YELLOW = 90
CAPACITY_THRESHOLD_ORANGE = 95
CAPACITY_THRESHOLD_RED = 100

# ════════════════════════════════════════════════════════════════════════
# Default Warehouse Config Scope
# ════════════════════════════════════════════════════════════════════════

CONFIG_SCOPE_TENANT = "tenant_default"
CONFIG_SCOPE_USER = "user_default"

CONFIG_SCOPE_CHOICES = (
    (CONFIG_SCOPE_TENANT, "Tenant Default"),
    (CONFIG_SCOPE_USER, "User Default"),
)

# ════════════════════════════════════════════════════════════════════════
# Sri Lanka District Choices (25 districts across 9 provinces)
# ════════════════════════════════════════════════════════════════════════

SRI_LANKA_DISTRICTS = (
    # Western Province
    (DISTRICT_COLOMBO, "Colombo"),
    (DISTRICT_GAMPAHA, "Gampaha"),
    (DISTRICT_KALUTARA, "Kalutara"),
    # Central Province
    (DISTRICT_KANDY, "Kandy"),
    (DISTRICT_MATALE, "Matale"),
    (DISTRICT_NUWARA_ELIYA, "Nuwara Eliya"),
    # Southern Province
    (DISTRICT_GALLE, "Galle"),
    (DISTRICT_MATARA, "Matara"),
    (DISTRICT_HAMBANTOTA, "Hambantota"),
    # Northern Province
    (DISTRICT_JAFFNA, "Jaffna"),
    (DISTRICT_KILINOCHCHI, "Kilinochchi"),
    (DISTRICT_MANNAR, "Mannar"),
    (DISTRICT_VAVUNIYA, "Vavuniya"),
    (DISTRICT_MULLAITIVU, "Mullaitivu"),
    # Eastern Province
    (DISTRICT_BATTICALOA, "Batticaloa"),
    (DISTRICT_AMPARA, "Ampara"),
    (DISTRICT_TRINCOMALEE, "Trincomalee"),
    # North Western Province
    (DISTRICT_KURUNEGALA, "Kurunegala"),
    (DISTRICT_PUTTALAM, "Puttalam"),
    # North Central Province
    (DISTRICT_ANURADHAPURA, "Anuradhapura"),
    (DISTRICT_POLONNARUWA, "Polonnaruwa"),
    # Uva Province
    (DISTRICT_BADULLA, "Badulla"),
    (DISTRICT_MONARAGALA, "Monaragala"),
    # Sabaragamuwa Province
    (DISTRICT_RATNAPURA, "Ratnapura"),
    (DISTRICT_KEGALLE, "Kegalle"),
)
