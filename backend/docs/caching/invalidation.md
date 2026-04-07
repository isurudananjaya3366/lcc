# Cache Invalidation Guide

> How to keep cached data fresh when the database changes.

---

## Overview

The caching layer provides three invalidation strategies:

| Strategy           | When to use                                 |
| ------------------ | ------------------------------------------- |
| **Manual**         | Targeted invalidation from service code     |
| **Signal-based**   | Automatic invalidation on model save/delete |
| **Management cmd** | Operational cache flush via CLI             |

All strategies work through `TenantCache.delete_pattern()`, which requires a `django-redis` backend in production. In test environments (`LocMemCache`), pattern deletes are no-ops.

---

## 1. `CacheInvalidator` — Manual Invalidation

Located in `apps.core.cache.invalidation`.

### `invalidate_model(model_class)`

Deletes **all** cache keys for a model.

```python
from apps.core.cache.invalidation import CacheInvalidator
from apps.products.models import Product

CacheInvalidator.invalidate_model(Product)
# Deletes pattern: "products_product:*"
```

### `invalidate_list(model_class)`

Deletes only list/collection caches.

```python
CacheInvalidator.invalidate_list(Product)
# Deletes pattern: "products_product:list*"
```

### `invalidate_detail(model_class, instance_id)`

Deletes detail caches for a specific instance.

```python
CacheInvalidator.invalidate_detail(Product, instance_id=42)
# Deletes pattern: "products_product:detail:42*"
```

### `invalidate_related(model_class, instance, related_models=None)`

Invalidates the model **and** its related models.

```python
# Explicit related models
CacheInvalidator.invalidate_related(
    Order, order_instance,
    related_models=[OrderItem, Payment],
)

# Auto-discover from _meta.related_objects
CacheInvalidator.invalidate_related(Order, order_instance)
```

When `related_models` is `None`, the method inspects `model_class._meta.related_objects` to find FK and M2M relations automatically.

### `invalidate_tenant_cache()`

Nuclear option — clears the **entire** cache for the current tenant.

```python
CacheInvalidator.invalidate_tenant_cache()
# Deletes pattern: "*" (scoped to current tenant via TenantCache)
```

### Key naming convention

The pattern used for invalidation is derived from `model._meta.label_lower` with dots replaced by underscores:

| Model                     | Pattern prefix            |
| ------------------------- | ------------------------- |
| `products.Product`        | `products_product`        |
| `orders.OrderItem`        | `orders_orderitem`        |
| `inventory.StockMovement` | `inventory_stockmovement` |

For invalidation to work, your **cache keys must follow this naming convention** when storing data.

---

## 2. Signal Handlers — Automatic Invalidation

### `cache_post_save_handler`

Connected to `post_save`. On every save it:

1. Calls `CacheInvalidator.invalidate_list(sender)` — clears list caches.
2. If the instance has a `pk`, calls `CacheInvalidator.invalidate_detail(sender, instance.pk)`.

### `cache_post_delete_handler`

Connected to `post_delete`. Calls `CacheInvalidator.invalidate_model(sender)` — clears all caches for the model.

### Connecting signals

In your app's `ready()` method:

```python
# apps/products/apps.py
from django.apps import AppConfig
from django.db.models.signals import post_save, post_delete


class ProductsConfig(AppConfig):
    name = "apps.products"

    def ready(self):
        from apps.core.cache.invalidation import (
            cache_post_save_handler,
            cache_post_delete_handler,
        )
        from apps.products.models import Product

        post_save.connect(cache_post_save_handler, sender=Product)
        post_delete.connect(cache_post_delete_handler, sender=Product)
```

### Error handling

Both signal handlers wrap their logic in `try/except`. If the cache is down, the signal handler logs the error and **does not** re-raise — your save/delete operation still succeeds.

---

## 3. `CacheMixin` — Model Mixin

A convenience mixin that declares which related models should be invalidated.

```python
from django.db import models
from apps.core.cache.invalidation import CacheMixin


class Order(CacheMixin, models.Model):
    class CacheMeta:
        invalidate_related = [OrderItem, Payment]

    # ... fields ...
```

Access the related list programmatically:

```python
Order._get_invalidation_related()
# [OrderItem, Payment]
```

If `CacheMeta` is not defined, `_get_invalidation_related()` returns `[]`.

> **Note:** `CacheMixin` is abstract (`class Meta: abstract = True`). It does **not** auto-connect signals; you must still wire them in `ready()` or use a custom signal-connection mechanism.

---

## 4. Management Command — `clearcache`

Flush caches from the command line.

```bash
# Clear the default cache
python manage.py clearcache

# Clear a specific alias
python manage.py clearcache --alias sessions

# Delete keys matching a pattern (tenant-scoped)
python manage.py clearcache --pattern "products:*"

# Clear ALL cache aliases
python manage.py clearcache --all
```

### Flags

| Flag        | Description                                             |
| ----------- | ------------------------------------------------------- |
| `--alias`   | Cache alias to target (default: `"default"`)            |
| `--pattern` | Glob pattern for selective deletion                     |
| `--all`     | Iterate over every configured alias and call `.clear()` |

The `--all` flag ignores `--alias` and `--pattern` and wipes everything.

---

## Invalidation Best Practices

1. **Connect signals only for models you cache.** Don't blanket-connect every model — it adds overhead.
2. **Use `invalidate_list` + `invalidate_detail`** for surgical cache updates after a save; reserve `invalidate_model` for bulk changes.
3. **Prefer `invalidate_related`** when a parent model save should also flush child caches (e.g. Order → OrderItem).
4. **Name your cache keys consistently** using the `{app}_{model}:{type}:{id}` convention so pattern invalidation works.
5. **Test invalidation paths** — the test suite includes mock-based tests for every `CacheInvalidator` method.
6. **Run `clearcache --all` after deployments** that change serialisation formats to avoid stale/corrupt entries.
