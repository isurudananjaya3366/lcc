"""
LankaCommerce Cloud – Redis & Cache Settings (SP09)

Redis database allocation:
    DB 0  – Celery broker / results
    DB 1  – Default application cache
    DB 2  – WebSocket channel layers
    DB 3  – Session storage
    DB 4  – Rate-limit counters
    DB 5-15 – Reserved
"""
from config.env import env

# ── Redis Connection ──────────────────────────────────────────────────
REDIS_URL = env("REDIS_URL", default="redis://redis:6379")

# Per-purpose Redis URLs (different DB numbers)
REDIS_CACHE_URL = env("REDIS_CACHE_URL", default=f"{REDIS_URL}/1")
REDIS_SESSION_URL = env("REDIS_SESSION_URL", default=f"{REDIS_URL}/3")
REDIS_RATELIMIT_URL = env("REDIS_RATELIMIT_URL", default=f"{REDIS_URL}/4")

# ── Connection Pool ───────────────────────────────────────────────────
REDIS_MAX_CONNECTIONS = env.int("REDIS_MAX_CONNECTIONS", default=10)
REDIS_SOCKET_TIMEOUT = env.float("REDIS_SOCKET_TIMEOUT", default=5.0)
REDIS_SOCKET_CONNECT_TIMEOUT = env.float("REDIS_SOCKET_CONNECT_TIMEOUT", default=5.0)
REDIS_RETRY_ON_TIMEOUT = env.bool("REDIS_RETRY_ON_TIMEOUT", default=True)
REDIS_HEALTH_CHECK_INTERVAL = env.int("REDIS_HEALTH_CHECK_INTERVAL", default=30)

# ── Django CACHES ─────────────────────────────────────────────────────
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_CACHE_URL,
        "TIMEOUT": 300,  # 5 minutes
        "KEY_PREFIX": "lcc",
        "VERSION": 1,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": REDIS_SOCKET_CONNECT_TIMEOUT,
            "SOCKET_TIMEOUT": REDIS_SOCKET_TIMEOUT,
            "RETRY_ON_TIMEOUT": REDIS_RETRY_ON_TIMEOUT,
            "MAX_CONNECTIONS": REDIS_MAX_CONNECTIONS,
            "PARSER_CLASS": "redis.connection.HiredisParser",
            "CONNECTION_POOL_KWARGS": {
                "health_check_interval": REDIS_HEALTH_CHECK_INTERVAL,
            },
        },
    },
    "sessions": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_SESSION_URL,
        "TIMEOUT": 86400,  # 1 day
        "KEY_PREFIX": "lcc:sess",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": REDIS_SOCKET_CONNECT_TIMEOUT,
            "SOCKET_TIMEOUT": REDIS_SOCKET_TIMEOUT,
            "MAX_CONNECTIONS": 10,
            "PARSER_CLASS": "redis.connection.HiredisParser",
        },
    },
    "ratelimit": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_RATELIMIT_URL,
        "TIMEOUT": 300,
        "KEY_PREFIX": "lcc:rl",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "MAX_CONNECTIONS": 5,
        },
    },
}

# ── Session via cache ─────────────────────────────────────────────────
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "sessions"
SESSION_COOKIE_AGE = 86400  # 1 day in seconds
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

# ── Cache Timeout Constants (also available from apps.core.cache.constants) ──
CACHE_TTL_SHORT = 300       # 5 minutes  – volatile data (dashboard stats)
CACHE_TTL_MEDIUM = 3600     # 1 hour     – standard data (product lists)
CACHE_TTL_LONG = 86400      # 1 day      – stable data (tax rates, configs)

# ── Cache Timeout Constants ───────────────────────────────────────────
CACHE_TTL_SHORT = 300       # 5 minutes  – volatile data (dashboard stats)
CACHE_TTL_MEDIUM = 3600     # 1 hour     – standard data (product lists)
CACHE_TTL_LONG = 86400      # 1 day      – stable data (tax rates, configs)
