# Caching Patterns & Usage

> Practical recipes for using the caching layer in everyday code.

---

## 1. Direct `TenantCache` Usage

The lowest-level API. Use it when decorators don't fit your use case.

```python
from apps.core.cache.tenant_cache import TenantCache
from apps.core.cache.constants import CACHE_TTL_SHORT

cache = TenantCache()                   # uses 'default' alias
cache = TenantCache("sessions")         # uses 'sessions' alias

# Basic CRUD
cache.set("products:list", product_data, timeout=CACHE_TTL_SHORT)
data = cache.get("products:list")       # returns None on miss
cache.delete("products:list")

# Shared (cross-tenant) key
cache.set("exchange_rates", rates, timeout=CACHE_TTL_LONG, shared=True)
rates = cache.get("exchange_rates", shared=True)

# Bulk operations
cache.set_many({"a": 1, "b": 2}, timeout=300)
result = cache.get_many(["a", "b"])     # {"a": 1, "b": 2}

# Counters
cache.incr("api:hits")                  # initialises to 1 if missing
cache.decr("stock:item:42")

# Pattern delete (requires django-redis backend)
cache.delete_pattern("products:*")
```

### Factory shortcut

```python
from apps.core.cache.tenant_cache import get_tenant_cache

cache = get_tenant_cache()              # equivalent to TenantCache()
cache = get_tenant_cache("sessions")
```

---

## 2. `cache_response` Decorator (Views / DRF)

Caches the response of a view function or DRF action.

```python
from apps.core.cache.decorators import cache_response
from apps.core.cache.constants import CACHE_TTL_SHORT

class ProductViewSet(viewsets.ModelViewSet):

    @cache_response(timeout=CACHE_TTL_SHORT)
    def list(self, request):
        ...

    @cache_response(cache_key="products:featured", timeout=3600)
    def featured(self, request):
        ...
```

### Options

| Parameter        | Default            | Description                                   |
| ---------------- | ------------------ | --------------------------------------------- |
| `cache_key`      | `None` (auto)      | Static string, or callable `(request) -> str` |
| `timeout`        | `CACHE_TTL_MEDIUM` | TTL in seconds                                |
| `cache_alias`    | `"default"`        | Django cache alias                            |
| `vary_on_tenant` | `True`             | `False` → stores in shared key space          |
| `vary_on_user`   | `False`            | `True` → appends `:u:<user_pk>` to key        |

### Behaviour

- **Cache miss**: calls the view, caches `response.data` (DRF) or the response object.
- **Cache hit**: returns the cached value immediately — the view is **not** called.
- **Error responses** (status ≥ 300): never cached.

### Dynamic key via callable

```python
@cache_response(cache_key=lambda req: f"search:{req.query_params.get('q')}")
def search(self, request):
    ...
```

---

## 3. `cache_method` Decorator (Service Methods)

Caches the return value of any method or function.

```python
from apps.core.cache.decorators import cache_method

class ReportService:
    @cache_method(timeout=3600)
    def get_monthly_summary(self, year, month):
        ...
```

- A unique key is auto-generated from `method.__qualname__`.
- When `**kwargs` differ, the key includes an MD5 hash of the sorted keyword arguments, so different arguments produce different cache entries.

---

## 4. `cache_queryset` Decorator

Caches the result of a function that returns a Django queryset. The queryset is **evaluated to a list** before caching (querysets are not serialisable).

```python
from apps.core.cache.decorators import cache_queryset

@cache_queryset(cache_key="products:active", timeout=3600)
def get_active_products():
    return Product.objects.filter(is_active=True)
```

---

## 5. `cache_get_or_set` Utility

Get-or-compute in a single call — the callback runs only on a cache miss.

```python
from apps.core.cache.utils import cache_get_or_set
from apps.core.cache.constants import CACHE_TTL_SHORT

data = cache_get_or_set(
    "dashboard:stats",
    lambda: compute_dashboard_stats(),
    timeout=CACHE_TTL_SHORT,
)
```

Parameters: `key`, `callback`, `timeout`, `cache_alias`, `shared`.

---

## 6. `make_cache_key` Utility

Build a properly scoped key from parts without manually constructing template strings.

```python
from apps.core.cache.utils import make_cache_key

key = make_cache_key("products", "list")
# => "lcc:tenant:acme:products:list"

key = make_cache_key("rates", shared=True)
# => "lcc:shared:rates"
```

---

## 7. `clear_cache` Utility

Programmatically wipe the cache.

```python
from apps.core.cache.utils import clear_cache

clear_cache()                           # clears entire 'default' cache
clear_cache(pattern="products:*")       # pattern delete (tenant-scoped)
clear_cache(cache_alias="sessions")     # clear a specific alias
```

---

## 8. `cache_stats` Utility

Returns memory usage and key count from Redis.

```python
from apps.core.cache.utils import cache_stats

stats = cache_stats()
# {
#     "used_memory": "1.5M",
#     "total_keys": 128,
#     "max_memory": "100M",
#     "hit_rate": 4500,
#     "miss_rate": 120,
# }
```

Returns an empty dict if the backend is not `django-redis` (e.g. in tests with `LocMemCache`).

---

## 9. `hash_key` Utility

Get an MD5 hex digest of a string — handy when you need a deterministic short identifier.

```python
from apps.core.cache.utils import hash_key

digest = hash_key("some:very:long:key:here")
# "a3f5b8..."  (32-char hex string)
```

---

## Tips & Best Practices

1. **Prefer decorators** over direct `TenantCache` calls for readability.
2. **Always set a timeout**. Unbounded keys cause memory leaks.
3. **Use `shared=True`** only for data that is truly global (exchange rates, feature flags).
4. **Combine short TTL + proactive invalidation** for frequently changing data.
5. **Test with `LocMemCache`** — the same API works without Redis.
6. **Monitor with `cache_stats()`** in admin dashboards or health checks.
