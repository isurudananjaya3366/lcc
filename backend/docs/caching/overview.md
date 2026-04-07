# Caching Layer Overview

> **Module path:** `apps.core.cache`
> **Redis client:** `django-redis` via Django's cache framework
> **Isolation:** automatic per-tenant key prefixing

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Application Code                   │
│  (Views · Services · Tasks · Management commands)    │
├─────────────┬──────────────┬────────────────────────┤
│  Decorators │   Utilities  │    CacheInvalidator    │
│  (cache_    │ (make_cache  │  (invalidate_model,    │
│   response, │  _key,       │   signal handlers,     │
│   cache_    │  cache_get   │   CacheMixin)          │
│   method,   │  _or_set,    │                        │
│   cache_    │  clear_cache │                        │
│   queryset) │  cache_stats)│                        │
├─────────────┴──────────────┴────────────────────────┤
│                    TenantCache                       │
│  (get · set · delete · delete_pattern ·              │
│   get_many · set_many · incr · decr)                 │
├─────────────────────────────────────────────────────┤
│              Django Cache Framework                   │
│            (django.core.cache.caches)                │
├─────────────────────────────────────────────────────┤
│                    Redis Server                      │
│  DB 1 – default  │  DB 3 – sessions  │  DB 4 – RL   │
└─────────────────────────────────────────────────────┘
```

All application code interacts with the cache through `TenantCache` or the convenience decorators/utilities built on top of it. `TenantCache` wraps Django's cache framework and transparently prefixes every key with the current tenant's schema name, guaranteeing data isolation in a multi-tenant deployment.

---

## Key Format

Every cache key follows one of two templates defined in `apps.core.cache.constants`:

| Scope  | Template                         | Example                         |
| ------ | -------------------------------- | ------------------------------- |
| Tenant | `{prefix}:tenant:{schema}:{key}` | `lcc:tenant:acme:products:list` |
| Shared | `{prefix}:shared:{key}`          | `lcc:shared:exchange_rates`     |

- **Prefix** (`lcc`) prevents collisions with other applications sharing the same Redis instance.
- **Schema** is the current tenant's `schema_name` from `django-tenants`.
- When a key exceeds **200 characters**, it is replaced with an MD5 hash: `lcc:h:<md5hex>`.

---

## TTL Guidelines

| Constant           | Value    | Intended Use                                    |
| ------------------ | -------- | ----------------------------------------------- |
| `CACHE_TTL_SHORT`  | 300 s    | Dashboard stats, inventory counts, live totals  |
| `CACHE_TTL_MEDIUM` | 3 600 s  | Product lists, category trees, search results   |
| `CACHE_TTL_LONG`   | 86 400 s | Tax rates, static configuration, exchange rates |

Choose the shortest TTL that is acceptable for your data freshness requirements. Combine short TTLs with proactive invalidation for the best user experience.

---

## Redis Database Allocation

| DB   | Purpose               |
| ---- | --------------------- |
| 0    | Celery broker/results |
| 1    | Default app cache     |
| 2    | WebSocket channels    |
| 3    | Session storage       |
| 4    | Rate-limit counters   |
| 5–15 | Reserved              |

Configured in `config/settings/cache.py` via environment variables (`REDIS_CACHE_URL`, `REDIS_SESSION_URL`, `REDIS_RATELIMIT_URL`).

---

## Tenant Isolation

`TenantCache._get_tenant_schema()` reads `django.db.connection.tenant.schema_name` at runtime. If no tenant is active (e.g. during management commands or public-schema requests), the schema falls back to `"public"`.

This means:

1. A `cache.set("products:list", data)` call in tenant **acme** writes to key `lcc:tenant:acme:products:list`.
2. The same call in tenant **beta** writes to `lcc:tenant:beta:products:list`.
3. A shared call `cache.set("rates", data, shared=True)` writes to `lcc:shared:rates` regardless of the active tenant.

No additional middleware or context managers are needed — isolation is automatic.

---

## Test Configuration

In `config/settings/test.py`, all cache aliases use `django.core.cache.backends.locmem.LocMemCache`. This avoids a Redis dependency during CI while still exercising the caching logic.

Note that `LocMemCache` does **not** support `delete_pattern`. The `TenantCache.delete_pattern` method gracefully returns `0` in this case.

---

## Module Layout

```
apps/core/cache/
├── __init__.py
├── constants.py         # TTL presets, key templates, MAX_KEY_LENGTH
├── tenant_cache.py      # TenantCache class + get_tenant_cache factory
├── decorators.py        # cache_response, cache_method, cache_queryset
├── utils.py             # make_cache_key, hash_key, cache_get_or_set, clear_cache, cache_stats
└── invalidation.py      # CacheInvalidator, signal handlers, CacheMixin

apps/core/management/commands/
└── clearcache.py        # `python manage.py clearcache` command

config/settings/
└── cache.py             # CACHES dict, Redis connection settings
```
