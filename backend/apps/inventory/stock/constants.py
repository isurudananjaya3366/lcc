"""
Stock constants for the inventory stock submodule.

Defines stock status values, movement types, movement reasons,
and other constants used across the stock tracking system.
"""

# ════════════════════════════════════════════════════════════════════════
# Stock Status Constants
# ════════════════════════════════════════════════════════════════════════
# Status is determined dynamically based on available_quantity vs reorder_point:
#   IN_STOCK:     available_quantity > reorder_point
#   LOW_STOCK:    0 < available_quantity <= reorder_point
#   OUT_OF_STOCK: available_quantity <= 0

IN_STOCK = "in_stock"
LOW_STOCK = "low_stock"
OUT_OF_STOCK = "out_of_stock"

STOCK_STATUS_CHOICES = [
    (IN_STOCK, "In Stock"),
    (LOW_STOCK, "Low Stock"),
    (OUT_OF_STOCK, "Out of Stock"),
]

STOCK_STATUS_COLORS = {
    IN_STOCK: "green",
    LOW_STOCK: "orange",
    OUT_OF_STOCK: "red",
}

STOCK_STATUS_ICONS = {
    IN_STOCK: "✓",
    LOW_STOCK: "⚠",
    OUT_OF_STOCK: "✗",
}

# ════════════════════════════════════════════════════════════════════════
# Movement Type Constants
# ════════════════════════════════════════════════════════════════════════

MOVEMENT_TYPE_STOCK_IN = "stock_in"
MOVEMENT_TYPE_STOCK_OUT = "stock_out"
MOVEMENT_TYPE_TRANSFER = "transfer"
MOVEMENT_TYPE_ADJUSTMENT = "adjustment"
MOVEMENT_TYPE_RESERVED = "reserved"
MOVEMENT_TYPE_RELEASED = "released"

MOVEMENT_TYPE_CHOICES = [
    (MOVEMENT_TYPE_STOCK_IN, "Stock In"),
    (MOVEMENT_TYPE_STOCK_OUT, "Stock Out"),
    (MOVEMENT_TYPE_TRANSFER, "Transfer"),
    (MOVEMENT_TYPE_ADJUSTMENT, "Adjustment"),
    (MOVEMENT_TYPE_RESERVED, "Reserved"),
    (MOVEMENT_TYPE_RELEASED, "Released"),
]

# ════════════════════════════════════════════════════════════════════════
# Movement Reason Constants
# ════════════════════════════════════════════════════════════════════════

REASON_PURCHASE = "purchase"
REASON_SALE = "sale"
REASON_RETURN = "return"
REASON_RETURN_FROM_CUSTOMER = "return_from_customer"
REASON_RETURN_TO_SUPPLIER = "return_to_supplier"
REASON_DAMAGE = "damage"
REASON_THEFT = "theft"
REASON_CORRECTION = "correction"
REASON_EXPIRED = "expired"
REASON_PRODUCTION = "production"
REASON_INITIAL = "initial"
REASON_STOCK_TAKE = "stock_take"
REASON_FOUND = "found"
REASON_LOST = "lost"
REASON_TRANSFER = "transfer"
REASON_WRITE_OFF = "write_off"
REASON_OTHER = "other"

# Reservation reasons
REASON_ORDER_PLACED = "order_placed"
REASON_ORDER_CANCELLED = "order_cancelled"
REASON_ORDER_TIMEOUT = "order_timeout"
REASON_MANUAL_RELEASE = "manual_release"

MOVEMENT_REASON_CHOICES = [
    (REASON_PURCHASE, "Purchase"),
    (REASON_SALE, "Sale"),
    (REASON_RETURN, "Return"),
    (REASON_RETURN_FROM_CUSTOMER, "Return from Customer"),
    (REASON_RETURN_TO_SUPPLIER, "Return to Supplier"),
    (REASON_DAMAGE, "Damage"),
    (REASON_THEFT, "Theft"),
    (REASON_CORRECTION, "Correction"),
    (REASON_EXPIRED, "Expired"),
    (REASON_PRODUCTION, "Production"),
    (REASON_INITIAL, "Initial Stock"),
    (REASON_STOCK_TAKE, "Stock Take"),
    (REASON_FOUND, "Found"),
    (REASON_LOST, "Lost"),
    (REASON_TRANSFER, "Transfer"),
    (REASON_WRITE_OFF, "Write-Off"),
    (REASON_OTHER, "Other"),
    (REASON_ORDER_PLACED, "Order Placed"),
    (REASON_ORDER_CANCELLED, "Order Cancelled"),
    (REASON_ORDER_TIMEOUT, "Order Timeout"),
    (REASON_MANUAL_RELEASE, "Manual Release"),
]

# ════════════════════════════════════════════════════════════════════════
# Reference Type Constants
# ════════════════════════════════════════════════════════════════════════

REFERENCE_TYPE_ORDER = "order"
REFERENCE_TYPE_PO = "purchase_order"
REFERENCE_TYPE_ADJUSTMENT = "adjustment"
REFERENCE_TYPE_TRANSFER = "transfer"
REFERENCE_TYPE_STOCK_TAKE = "stock_take"
REFERENCE_TYPE_MANUAL = "manual"

REFERENCE_TYPE_CHOICES = [
    (REFERENCE_TYPE_ORDER, "Order"),
    (REFERENCE_TYPE_PO, "Purchase Order"),
    (REFERENCE_TYPE_ADJUSTMENT, "Adjustment"),
    (REFERENCE_TYPE_TRANSFER, "Transfer"),
    (REFERENCE_TYPE_STOCK_TAKE, "Stock Take"),
    (REFERENCE_TYPE_MANUAL, "Manual"),
]

# ════════════════════════════════════════════════════════════════════════
# Valid Reason-Type Combinations
# ════════════════════════════════════════════════════════════════════════

VALID_REASON_COMBINATIONS = {
    MOVEMENT_TYPE_STOCK_IN: [
        REASON_PURCHASE, REASON_RETURN, REASON_RETURN_FROM_CUSTOMER,
        REASON_PRODUCTION, REASON_INITIAL, REASON_FOUND, REASON_OTHER,
    ],
    MOVEMENT_TYPE_STOCK_OUT: [
        REASON_SALE, REASON_DAMAGE, REASON_THEFT, REASON_EXPIRED,
        REASON_RETURN_TO_SUPPLIER, REASON_LOST, REASON_WRITE_OFF, REASON_OTHER,
    ],
    MOVEMENT_TYPE_TRANSFER: [REASON_TRANSFER, REASON_OTHER],
    MOVEMENT_TYPE_ADJUSTMENT: [
        REASON_CORRECTION, REASON_STOCK_TAKE, REASON_FOUND, REASON_LOST,
        REASON_DAMAGE, REASON_OTHER,
    ],
    MOVEMENT_TYPE_RESERVED: [REASON_ORDER_PLACED],
    MOVEMENT_TYPE_RELEASED: [
        REASON_ORDER_CANCELLED, REASON_ORDER_TIMEOUT, REASON_MANUAL_RELEASE,
    ],
}

# ════════════════════════════════════════════════════════════════════════
# Stock Take Status Constants
# ════════════════════════════════════════════════════════════════════════

STOCK_TAKE_DRAFT = "draft"
STOCK_TAKE_IN_PROGRESS = "in_progress"
STOCK_TAKE_COUNTING = "counting"
STOCK_TAKE_REVIEW = "review"
STOCK_TAKE_COMPLETED = "completed"
STOCK_TAKE_CANCELLED = "cancelled"

STOCK_TAKE_STATUS_CHOICES = [
    (STOCK_TAKE_DRAFT, "Draft"),
    (STOCK_TAKE_IN_PROGRESS, "In Progress"),
    (STOCK_TAKE_COUNTING, "Counting"),
    (STOCK_TAKE_REVIEW, "Review"),
    (STOCK_TAKE_COMPLETED, "Completed"),
    (STOCK_TAKE_CANCELLED, "Cancelled"),
]

# ════════════════════════════════════════════════════════════════════════
# Stock Take Scope Constants
# ════════════════════════════════════════════════════════════════════════

STOCK_TAKE_SCOPE_FULL = "full"
STOCK_TAKE_SCOPE_PARTIAL = "partial"
STOCK_TAKE_SCOPE_CYCLE = "cycle"

STOCK_TAKE_SCOPE_CHOICES = [
    (STOCK_TAKE_SCOPE_FULL, "Full Count"),
    (STOCK_TAKE_SCOPE_PARTIAL, "Partial Count"),
    (STOCK_TAKE_SCOPE_CYCLE, "Cycle Count"),
]

# ════════════════════════════════════════════════════════════════════════
# Stock Take Item Status Constants
# ════════════════════════════════════════════════════════════════════════

STOCK_TAKE_ITEM_PENDING = "pending"
STOCK_TAKE_ITEM_COUNTED = "counted"
STOCK_TAKE_ITEM_VERIFIED = "verified"
STOCK_TAKE_ITEM_ADJUSTED = "adjusted"

STOCK_TAKE_ITEM_STATUS_CHOICES = [
    (STOCK_TAKE_ITEM_PENDING, "Pending"),
    (STOCK_TAKE_ITEM_COUNTED, "Counted"),
    (STOCK_TAKE_ITEM_VERIFIED, "Verified"),
    (STOCK_TAKE_ITEM_ADJUSTED, "Adjusted"),
]

# ════════════════════════════════════════════════════════════════════════
# Approval Status Constants
# ════════════════════════════════════════════════════════════════════════

APPROVAL_NOT_REQUIRED = "not_required"
APPROVAL_PENDING = "pending"
APPROVAL_APPROVED = "approved"
APPROVAL_REJECTED = "rejected"

APPROVAL_STATUS_CHOICES = [
    (APPROVAL_NOT_REQUIRED, "Not Required"),
    (APPROVAL_PENDING, "Pending"),
    (APPROVAL_APPROVED, "Approved"),
    (APPROVAL_REJECTED, "Rejected"),
]

# ════════════════════════════════════════════════════════════════════════
# Variance Classification Thresholds
# ════════════════════════════════════════════════════════════════════════

VARIANCE_MINOR_THRESHOLD = 2    # percentage
VARIANCE_MODERATE_THRESHOLD = 5  # percentage
VARIANCE_SIGNIFICANT_THRESHOLD = 10  # percentage

# ════════════════════════════════════════════════════════════════════════
# Threshold Defaults
# ════════════════════════════════════════════════════════════════════════

DEFAULT_REORDER_POINT = 10
ADJUSTMENT_AUTHORIZATION_THRESHOLD = 100  # Value above which manager approval needed

# ════════════════════════════════════════════════════════════════════════
# Transit Status Constants (Task 43)
# ════════════════════════════════════════════════════════════════════════

TRANSIT_PENDING = "pending"
TRANSIT_DISPATCHED = "dispatched"
TRANSIT_IN_TRANSIT = "in_transit"
TRANSIT_RECEIVED = "received"
TRANSIT_CANCELLED = "cancelled"

TRANSIT_STATUS_CHOICES = [
    (TRANSIT_PENDING, "Pending"),
    (TRANSIT_DISPATCHED, "Dispatched"),
    (TRANSIT_IN_TRANSIT, "In Transit"),
    (TRANSIT_RECEIVED, "Received"),
    (TRANSIT_CANCELLED, "Cancelled"),
]

# ════════════════════════════════════════════════════════════════════════
# Costing Method Constants (Task 55)
# ════════════════════════════════════════════════════════════════════════

COSTING_METHOD_WAC = "wac"
COSTING_METHOD_FIFO = "fifo"
COSTING_METHOD_LIFO = "lifo"

COSTING_METHOD_CHOICES = [
    (COSTING_METHOD_WAC, "Weighted Average Cost"),
    (COSTING_METHOD_FIFO, "First In, First Out"),
    (COSTING_METHOD_LIFO, "Last In, First Out"),
]

# ════════════════════════════════════════════════════════════════════════
# Lot Status Constants (Task 55)
# ════════════════════════════════════════════════════════════════════════

LOT_STATUS_ACTIVE = "active"
LOT_STATUS_DEPLETED = "depleted"
LOT_STATUS_EXPIRED = "expired"
LOT_STATUS_ON_HOLD = "on_hold"

LOT_STATUS_CHOICES = [
    (LOT_STATUS_ACTIVE, "Active"),
    (LOT_STATUS_DEPLETED, "Depleted"),
    (LOT_STATUS_EXPIRED, "Expired"),
    (LOT_STATUS_ON_HOLD, "On Hold"),
]

# ════════════════════════════════════════════════════════════════════════
# ABC Classification Constants (Task 72)
# ════════════════════════════════════════════════════════════════════════

ABC_CLASS_A = "A"
ABC_CLASS_B = "B"
ABC_CLASS_C = "C"

ABC_CLASSIFICATION_CHOICES = [
    (ABC_CLASS_A, "A - High Value / High Frequency"),
    (ABC_CLASS_B, "B - Medium Value / Medium Frequency"),
    (ABC_CLASS_C, "C - Low Value / Low Frequency"),
]

# Default cycle count intervals (days) by ABC class
CYCLE_COUNT_INTERVAL_A = 30   # Monthly
CYCLE_COUNT_INTERVAL_B = 90   # Quarterly
CYCLE_COUNT_INTERVAL_C = 180  # Semi-annually

# ════════════════════════════════════════════════════════════════════════
# Cycle Count Schedule Status Constants (Task 72)
# ════════════════════════════════════════════════════════════════════════

SCHEDULE_ACTIVE = "active"
SCHEDULE_PAUSED = "paused"
SCHEDULE_COMPLETED = "completed"

SCHEDULE_STATUS_CHOICES = [
    (SCHEDULE_ACTIVE, "Active"),
    (SCHEDULE_PAUSED, "Paused"),
    (SCHEDULE_COMPLETED, "Completed"),
]

# ════════════════════════════════════════════════════════════════════════
# Per-Item Approval Thresholds (Task 69)
# ════════════════════════════════════════════════════════════════════════

ITEM_APPROVAL_THRESHOLD_MINOR = 5     # percentage – auto-approve
ITEM_APPROVAL_THRESHOLD_MAJOR = 20    # percentage – requires manager
ITEM_APPROVAL_THRESHOLD_CRITICAL = 50  # percentage – requires director
