"""
Cache timeout constants and key-related constants.
"""

# ── Timeout Presets (seconds) ─────────────────────────────────────────
CACHE_TTL_SHORT: int = 300       # 5 minutes  – dashboard stats, inventory counts
CACHE_TTL_MEDIUM: int = 3600     # 1 hour     – product lists, category trees
CACHE_TTL_LONG: int = 86400      # 1 day      – tax rates, static config

# ── Key Prefixes ──────────────────────────────────────────────────────
KEY_PREFIX = "lcc"
TENANT_KEY_TEMPLATE = "{prefix}:tenant:{schema}:{key}"
SHARED_KEY_TEMPLATE = "{prefix}:shared:{key}"

# ── Maximum key length before hashing ─────────────────────────────────
MAX_KEY_LENGTH: int = 200
