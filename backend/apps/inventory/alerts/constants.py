"""
Constants for the stock alerts and reordering system.

Defines threshold types, stock statuses, alert types, alert statuses,
visibility overrides, and reorder suggestion statuses.
"""

# ── Threshold Type Constants ────────────────────────────────────
# Inheritance chain: Global → Category → Product
# Product overrides Category overrides Global.

THRESHOLD_TYPE_GLOBAL = "global"
THRESHOLD_TYPE_CATEGORY = "category"
THRESHOLD_TYPE_PRODUCT = "product"

THRESHOLD_TYPE_CHOICES = [
    (THRESHOLD_TYPE_GLOBAL, "Global"),
    (THRESHOLD_TYPE_CATEGORY, "Category"),
    (THRESHOLD_TYPE_PRODUCT, "Product"),
]

# ── Stock Status Constants ──────────────────────────────────────
# Priority: OUT_OF_STOCK > CRITICAL > LOW > NORMAL
#
# Calculation order:
#   if available_quantity <= 0: OUT_OF_STOCK
#   elif stock <= (low_stock_threshold * 0.5): CRITICAL
#   elif stock <= low_stock_threshold: LOW
#   else: NORMAL

STOCK_STATUS_NORMAL = "normal"
STOCK_STATUS_LOW = "low"
STOCK_STATUS_CRITICAL = "critical"
STOCK_STATUS_OUT_OF_STOCK = "out_of_stock"

STOCK_STATUS_CHOICES = [
    (STOCK_STATUS_NORMAL, "Normal"),
    (STOCK_STATUS_LOW, "Low Stock"),
    (STOCK_STATUS_CRITICAL, "Critical Stock"),
    (STOCK_STATUS_OUT_OF_STOCK, "Out of Stock"),
]

# ── Webstore Visibility Override Constants ──────────────────────

VISIBILITY_AUTO = "auto"
VISIBILITY_ALWAYS_SHOW = "always_show"
VISIBILITY_ALWAYS_HIDE = "always_hide"

VISIBILITY_CHOICES = [
    (VISIBILITY_AUTO, "Automatic"),
    (VISIBILITY_ALWAYS_SHOW, "Always Show"),
    (VISIBILITY_ALWAYS_HIDE, "Always Hide"),
]

# ── Alert Type Constants ────────────────────────────────────────

ALERT_TYPE_LOW_STOCK = "low_stock"
ALERT_TYPE_CRITICAL_STOCK = "critical_stock"
ALERT_TYPE_OUT_OF_STOCK = "out_of_stock"
ALERT_TYPE_BACK_IN_STOCK = "back_in_stock"

ALERT_TYPE_CHOICES = [
    (ALERT_TYPE_LOW_STOCK, "Low Stock"),
    (ALERT_TYPE_CRITICAL_STOCK, "Critical Stock"),
    (ALERT_TYPE_OUT_OF_STOCK, "Out of Stock"),
    (ALERT_TYPE_BACK_IN_STOCK, "Back in Stock"),
]

# Priority mapping: higher = more urgent
ALERT_TYPE_PRIORITY = {
    ALERT_TYPE_BACK_IN_STOCK: 1,
    ALERT_TYPE_LOW_STOCK: 2,
    ALERT_TYPE_CRITICAL_STOCK: 3,
    ALERT_TYPE_OUT_OF_STOCK: 4,
}

# Color mapping for UI
ALERT_TYPE_COLORS = {
    ALERT_TYPE_LOW_STOCK: "#FFC107",
    ALERT_TYPE_CRITICAL_STOCK: "#FF9800",
    ALERT_TYPE_OUT_OF_STOCK: "#F44336",
    ALERT_TYPE_BACK_IN_STOCK: "#4CAF50",
}

# ── Alert Status Constants ──────────────────────────────────────

ALERT_STATUS_ACTIVE = "active"
ALERT_STATUS_ACKNOWLEDGED = "acknowledged"
ALERT_STATUS_RESOLVED = "resolved"
ALERT_STATUS_SNOOZED = "snoozed"

ALERT_STATUS_CHOICES = [
    (ALERT_STATUS_ACTIVE, "Active"),
    (ALERT_STATUS_ACKNOWLEDGED, "Acknowledged"),
    (ALERT_STATUS_RESOLVED, "Resolved"),
    (ALERT_STATUS_SNOOZED, "Snoozed"),
]

VALID_TRANSITIONS = {
    ALERT_STATUS_ACTIVE: [ALERT_STATUS_ACKNOWLEDGED, ALERT_STATUS_SNOOZED, ALERT_STATUS_RESOLVED],
    ALERT_STATUS_ACKNOWLEDGED: [ALERT_STATUS_SNOOZED, ALERT_STATUS_RESOLVED],
    ALERT_STATUS_SNOOZED: [ALERT_STATUS_ACTIVE],
    ALERT_STATUS_RESOLVED: [],
}

ALERT_STATUS_ICONS = {
    ALERT_STATUS_ACTIVE: "alert-circle",
    ALERT_STATUS_ACKNOWLEDGED: "check-circle",
    ALERT_STATUS_RESOLVED: "check-circle-fill",
    ALERT_STATUS_SNOOZED: "clock",
}

# Common snooze duration presets (hours)
SNOOZE_PRESETS = [
    (1, "1 Hour"),
    (4, "4 Hours"),
    (8, "8 Hours"),
    (24, "1 Day"),
    (72, "3 Days"),
    (168, "1 Week"),
]

# ── Reorder Suggestion Status Constants ─────────────────────────

SUGGESTION_STATUS_PENDING = "pending"
SUGGESTION_STATUS_CONVERTED = "converted_to_po"
SUGGESTION_STATUS_DISMISSED = "dismissed"
SUGGESTION_STATUS_EXPIRED = "expired"

SUGGESTION_STATUS_CHOICES = [
    (SUGGESTION_STATUS_PENDING, "Pending"),
    (SUGGESTION_STATUS_CONVERTED, "Converted to PO"),
    (SUGGESTION_STATUS_DISMISSED, "Dismissed"),
    (SUGGESTION_STATUS_EXPIRED, "Expired"),
]

# ── Auto-Reorder Urgency Choices ────────────────────────────────

AUTO_REORDER_URGENCY_CHOICES = [
    ("critical", "Critical Only"),
    ("high", "High and Critical"),
    ("medium", "Medium and above"),
]

# ── Suggestion Urgency Constants ────────────────────────────────

URGENCY_LOW = "low"
URGENCY_MEDIUM = "medium"
URGENCY_HIGH = "high"
URGENCY_CRITICAL = "critical"

URGENCY_CHOICES = [
    (URGENCY_LOW, "Low"),
    (URGENCY_MEDIUM, "Medium"),
    (URGENCY_HIGH, "High"),
    (URGENCY_CRITICAL, "Critical"),
]

# ── Monitoring Frequency Constants ──────────────────────────────

FREQUENCY_HOURLY = "hourly"
FREQUENCY_EVERY_2_HOURS = "every_2_hours"
FREQUENCY_EVERY_4_HOURS = "every_4_hours"
FREQUENCY_TWICE_DAILY = "twice_daily"
FREQUENCY_DAILY = "daily"
FREQUENCY_WEEKLY = "weekly"

FREQUENCY_CHOICES = [
    (FREQUENCY_HOURLY, "Every Hour"),
    (FREQUENCY_EVERY_2_HOURS, "Every 2 Hours"),
    (FREQUENCY_EVERY_4_HOURS, "Every 4 Hours"),
    (FREQUENCY_TWICE_DAILY, "Twice Daily"),
    (FREQUENCY_DAILY, "Daily"),
    (FREQUENCY_WEEKLY, "Weekly"),
]

# ── Monitoring Batch Size ───────────────────────────────────────

MONITORING_BATCH_SIZE = 100
