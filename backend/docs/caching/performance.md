# Cache Performance Guidelines

> **SubPhase:** SP09 – Caching Layer  
> **Task:** 87 – Performance Guidelines

---

## Cache TTL Strategy

| Tier       | Constant           | Value          | Use Cases                                                       |
| ---------- | ------------------ | -------------- | --------------------------------------------------------------- |
| **SHORT**  | `CACHE_TTL_SHORT`  | 5 min (300s)   | Dashboard stats, inventory counts, active sessions              |
| **MEDIUM** | `CACHE_TTL_MEDIUM` | 1 hr (3600s)   | Product lists, category trees, search results, user permissions |
| **LONG**   | `CACHE_TTL_LONG`   | 1 day (86400s) | Tax rates, country lists, static config, payment methods        |

**Rule:** Always set a TTL. Never use `TIMEOUT=None` (infinite).

---

## Connection Pool Sizing

```
Formula: max_connections = (gunicorn_workers × threads) × 1.5 + buffer

Development:  1 × 1 × 1.5 + 3 = ~5
Staging:      2 × 2 × 1.5 + 2 = ~8
Production:   4 × 2 × 1.5 + 3 = ~15
High-load:    8 × 4 × 1.5 + 2 = ~50
```

Each cache alias gets its own pool. Session and ratelimit pools are smaller (5–10).

---

## Key Length

- Keys over 200 characters are automatically MD5-hashed by `TenantCache.make_key()`
- Keep keys concise: `products:list` not `all-active-products-that-are-visible-in-the-webstore`
- Use `hash_key()` from `apps.core.cache.utils` if you need to manually hash

---

## Serialisation

`django-redis` uses `pickle` by default. Considerations:

- **Avoid caching Django model instances** → cache dicts or serialised data instead
- **Avoid caching querysets directly** → use `list(qs)` or the `@cache_queryset` decorator
- **Prefer JSON-serialisable data** for portability

---

## Cache Stampede Prevention

When a popular cache key expires, many requests may simultaneously try to recompute it.

Mitigation strategies:

1. **Staggered TTLs** – Add small random jitter to TTLs:

   ```python
   import random
   timeout = CACHE_TTL_MEDIUM + random.randint(-60, 60)
   ```

2. **Lock-based recompute** – Use Redis SETNX to elect a single recomputer:

   ```python
   from django_redis import get_redis_connection
   conn = get_redis_connection("default")
   if conn.set(f"lock:{key}", 1, nx=True, ex=30):
       # This request recomputes
       ...
   ```

3. **Background refresh** – Use Celery tasks to refresh cache before expiry.

---

## Hot Key Mitigation

If a single key receives extremely high traffic:

- Use local in-process cache (e.g. `functools.lru_cache`) for the hottest keys
- Replicate across Redis read replicas
- Consider application-level memoisation for the 10-second window

---

## Memory Budget

Monitor with `cache_stats()` or the `clearcache` management command:

```python
from apps.core.cache.utils import cache_stats
stats = cache_stats("default")
print(stats)
# {'used_memory': '1.5M', 'total_keys': 2340, ...}
```

Set Redis `maxmemory` and `maxmemory-policy` in production:

```
maxmemory 256mb
maxmemory-policy allkeys-lru
```

---

## Network Latency

| Scenario            | Expected Latency | Recommendation                           |
| ------------------- | ---------------- | ---------------------------------------- |
| Same Docker network | < 1ms            | Socket timeout 5s                        |
| Same cloud region   | 1–5ms            | Socket timeout 5s                        |
| Cross-region        | 10–50ms          | Socket timeout 10s, consider local cache |

---

## What NOT to Cache

- Rapidly mutating counters (use Redis INCR/DECR directly)
- User-specific security tokens (use session store instead)
- Large binary blobs > 1MB (use file storage)
- Data that must be 100% consistent (e.g. payment states)

---

## Monitoring Checklist

- [ ] Redis `used_memory` stays within budget
- [ ] Cache hit rate > 80% in production
- [ ] No `TimeoutError` spikes in logs
- [ ] `delete_pattern` calls are fast (< 50ms)
- [ ] Connection pool utilisation < 80%
