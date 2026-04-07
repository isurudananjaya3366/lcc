"""
Offline Mode Constants.

All constants for POS offline mode including offline states, sync statuses,
conflict resolution strategies, sync types, sync directions, transaction
types, network quality levels, and data source types.
"""

# ── Offline Mode Status Constants ─────────────────────────────────────────
OFFLINE_MODE_ONLINE = "online"
OFFLINE_MODE_OFFLINE = "offline"
OFFLINE_MODE_SYNCING = "syncing"
OFFLINE_MODE_SYNC_ERROR = "sync_error"

OFFLINE_MODE_CHOICES = (
    (OFFLINE_MODE_ONLINE, "Online"),
    (OFFLINE_MODE_OFFLINE, "Offline"),
    (OFFLINE_MODE_SYNCING, "Syncing"),
    (OFFLINE_MODE_SYNC_ERROR, "Sync Error"),
)

# ── Sync Status Constants ─────────────────────────────────────────────────
SYNC_STATUS_PENDING = "pending"
SYNC_STATUS_IN_PROGRESS = "in_progress"
SYNC_STATUS_COMPLETED = "completed"
SYNC_STATUS_FAILED = "failed"
SYNC_STATUS_CONFLICT = "conflict"

SYNC_STATUS_CHOICES = (
    (SYNC_STATUS_PENDING, "Pending"),
    (SYNC_STATUS_IN_PROGRESS, "In Progress"),
    (SYNC_STATUS_COMPLETED, "Completed"),
    (SYNC_STATUS_FAILED, "Failed"),
    (SYNC_STATUS_CONFLICT, "Conflict"),
)

# ── Conflict Resolution Strategy Constants ────────────────────────────────
CONFLICT_RESOLUTION_SERVER_WINS = "server_wins"
CONFLICT_RESOLUTION_CLIENT_WINS = "client_wins"
CONFLICT_RESOLUTION_MERGE = "merge"
CONFLICT_RESOLUTION_MANUAL = "manual"

CONFLICT_RESOLUTION_CHOICES = (
    (CONFLICT_RESOLUTION_SERVER_WINS, "Server Wins"),
    (CONFLICT_RESOLUTION_CLIENT_WINS, "Client Wins"),
    (CONFLICT_RESOLUTION_MERGE, "Merge"),
    (CONFLICT_RESOLUTION_MANUAL, "Manual Resolution"),
)

# ── Sync Type Constants ───────────────────────────────────────────────────
SYNC_TYPE_PUSH = "push"
SYNC_TYPE_PULL = "pull"
SYNC_TYPE_FULL = "full"
SYNC_TYPE_AUTO = "auto"
SYNC_TYPE_MANUAL = "manual"

SYNC_TYPE_CHOICES = (
    (SYNC_TYPE_PUSH, "Push"),
    (SYNC_TYPE_PULL, "Pull"),
    (SYNC_TYPE_FULL, "Full Sync"),
    (SYNC_TYPE_AUTO, "Automatic"),
    (SYNC_TYPE_MANUAL, "Manual"),
)

# ── Sync Direction Constants ──────────────────────────────────────────────
SYNC_DIRECTION_PUSH = "push"
SYNC_DIRECTION_PULL = "pull"
SYNC_DIRECTION_BIDIRECTIONAL = "bidirectional"

SYNC_DIRECTION_CHOICES = (
    (SYNC_DIRECTION_PUSH, "Push (Client → Server)"),
    (SYNC_DIRECTION_PULL, "Pull (Server → Client)"),
    (SYNC_DIRECTION_BIDIRECTIONAL, "Bidirectional"),
)

# ── Offline Transaction Type Constants ────────────────────────────────────
TRANSACTION_TYPE_SALE = "sale"
TRANSACTION_TYPE_REFUND = "refund"
TRANSACTION_TYPE_EXCHANGE = "exchange"
TRANSACTION_TYPE_VOID = "void"
TRANSACTION_TYPE_ADJUSTMENT = "adjustment"

TRANSACTION_TYPE_CHOICES = (
    (TRANSACTION_TYPE_SALE, "Sale"),
    (TRANSACTION_TYPE_REFUND, "Refund"),
    (TRANSACTION_TYPE_EXCHANGE, "Exchange"),
    (TRANSACTION_TYPE_VOID, "Void"),
    (TRANSACTION_TYPE_ADJUSTMENT, "Adjustment"),
)

# ── Network Quality Constants ─────────────────────────────────────────────
NETWORK_QUALITY_EXCELLENT = "excellent"
NETWORK_QUALITY_GOOD = "good"
NETWORK_QUALITY_FAIR = "fair"
NETWORK_QUALITY_POOR = "poor"
NETWORK_QUALITY_UNKNOWN = "unknown"

NETWORK_QUALITY_CHOICES = (
    (NETWORK_QUALITY_EXCELLENT, "Excellent"),
    (NETWORK_QUALITY_GOOD, "Good"),
    (NETWORK_QUALITY_FAIR, "Fair"),
    (NETWORK_QUALITY_POOR, "Poor"),
    (NETWORK_QUALITY_UNKNOWN, "Unknown"),
)

# ── Data Source Constants ─────────────────────────────────────────────────
DATA_SOURCE_WEB_POS = "web-pos"
DATA_SOURCE_MOBILE_POS = "mobile-pos"
DATA_SOURCE_TABLET_POS = "tablet-pos"
DATA_SOURCE_KIOSK_POS = "kiosk-pos"

DATA_SOURCE_CHOICES = (
    (DATA_SOURCE_WEB_POS, "Web POS"),
    (DATA_SOURCE_MOBILE_POS, "Mobile POS"),
    (DATA_SOURCE_TABLET_POS, "Tablet POS"),
    (DATA_SOURCE_KIOSK_POS, "Kiosk POS"),
)

# ── Freshness Category Constants ──────────────────────────────────────────
FRESHNESS_REALTIME = "realtime"
FRESHNESS_NEAR_REALTIME = "near_realtime"
FRESHNESS_FRESH = "fresh"
FRESHNESS_ACCEPTABLE = "acceptable"
FRESHNESS_STALE_ACCEPTABLE = "stale_acceptable"

FRESHNESS_CHOICES = (
    (FRESHNESS_REALTIME, "Real-time (<5 min)"),
    (FRESHNESS_NEAR_REALTIME, "Near Real-time (5-30 min)"),
    (FRESHNESS_FRESH, "Fresh (30 min - 4 hours)"),
    (FRESHNESS_ACCEPTABLE, "Acceptable (4-24 hours)"),
    (FRESHNESS_STALE_ACCEPTABLE, "Stale Acceptable (>24 hours)"),
)

# ── Staleness Handling Strategy Constants ─────────────────────────────────
STALENESS_BLOCK = "block"
STALENESS_WARN = "warn"
STALENESS_ALLOW = "allow"
STALENESS_FALLBACK = "fallback"

STALENESS_HANDLING_CHOICES = (
    (STALENESS_BLOCK, "Block Operation"),
    (STALENESS_WARN, "Warn User"),
    (STALENESS_ALLOW, "Allow Silently"),
    (STALENESS_FALLBACK, "Use Fallback"),
)

# ── Default Sync Configuration Values ─────────────────────────────────────
DEFAULT_AUTO_SYNC_INTERVAL = 30  # minutes
DEFAULT_MAX_OFFLINE_TRANSACTIONS = 100
DEFAULT_SYNC_BATCH_SIZE = 50
DEFAULT_MAX_RETRY_ATTEMPTS = 3
DEFAULT_RETRY_BACKOFF_MINUTES = 5
DEFAULT_CONFLICT_RESOLUTION_TIMEOUT_HOURS = 24
DEFAULT_CONFLICT_ARCHIVE_DAYS = 90

# Cache TTL defaults (in minutes)
DEFAULT_CACHE_TTL_PRODUCTS = 240
DEFAULT_CACHE_TTL_PRICES = 120
DEFAULT_CACHE_TTL_CUSTOMERS = 480
DEFAULT_CACHE_TTL_CATEGORIES = 1440
DEFAULT_CACHE_TTL_SETTINGS = 60
