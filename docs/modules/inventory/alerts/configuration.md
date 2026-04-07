# Configuration Guide

> Multi-level stock threshold and monitoring configuration.

---

## Configuration Hierarchy

The alerts module uses a layered configuration that resolves in order of
specificity:

```
Global → Category → Product → Product+Warehouse
```

The `ConfigResolver.resolve_for_product(product)` method walks this chain and
returns a merged dict with keys like `low_stock_threshold`, `reorder_point`,
`reorder_quantity`, `lead_time_days`, `critical_threshold_multiplier`,
and `source` / `sources`.

---

## 1. Global Settings (`GlobalStockSettings`)

Singleton model created per tenant. Stores system-wide defaults.

| Field                         | Type    | Default | Purpose                            |
| ----------------------------- | ------- | ------- | ---------------------------------- |
| `default_low_threshold`       | Decimal | 10.000  | Default low stock threshold        |
| `default_reorder_point`       | Decimal | 15.000  | Default reorder trigger point      |
| `default_reorder_qty`         | Decimal | 50.000  | Default reorder quantity           |
| `enable_auto_reorder`         | Boolean | False   | Enable auto PO creation            |
| `monitoring_frequency`        | Choice  | hourly  | Celery Beat schedule frequency     |
| `monitoring_start_hour`       | Integer | 6       | Monitoring window start (24h)      |
| `monitoring_end_hour`         | Integer | 22      | Monitoring window end (24h)        |
| `ordering_cost_lkr`           | Decimal | 5000.00 | Per-order cost for EOQ calculation |
| `holding_cost_percent`        | Decimal | 0.25    | Annual holding cost % for EOQ      |
| `reorder_suggestions_enabled` | Boolean | True    | Enable suggestion generation       |

**API:** `GET/PUT /api/v1/alerts/global-settings/`

---

## 2. Category Config (`CategoryStockConfig`)

Override thresholds for an entire product category.

| Field                 | Type    | Purpose                  |
| --------------------- | ------- | ------------------------ |
| `category`            | FK      | Target category          |
| `low_stock_threshold` | Decimal | Category-level threshold |
| `reorder_point`       | Decimal | Category reorder trigger |
| `reorder_quantity`    | Decimal | Category reorder qty     |
| `lead_time_days`      | Integer | Supplier lead time       |

---

## 3. Product Config (`ProductStockConfig`)

Most granular level. Optionally scoped to a specific warehouse.

| Field                     | Type    | Purpose                             |
| ------------------------- | ------- | ----------------------------------- |
| `product`                 | FK      | Target product                      |
| `warehouse`               | FK      | Optional warehouse scope (nullable) |
| `low_stock_threshold`     | Decimal | Product-level threshold             |
| `reorder_point`           | Decimal | Product reorder trigger             |
| `reorder_quantity`        | Decimal | Product reorder qty                 |
| `monitoring_enabled`      | Boolean | Enable/disable monitoring           |
| `exclude_from_monitoring` | Boolean | Temporary exclusion flag            |
| `exclusion_start_date`    | Date    | Exclusion window start              |
| `exclusion_end_date`      | Date    | Exclusion window end                |
| `auto_hide_when_oos`      | Boolean | Hide from webstore when OOS         |

**API:** `GET/POST/PATCH/DELETE /api/v1/alerts/stock-config/`

**Special endpoints:**

- `POST /stock-config/{id}/reset_to_defaults/` — Reset to global defaults
- `POST /stock-config/bulk/` — Bulk update multiple configs
- `POST /stock-config/bulk_exclude/` — Bulk toggle monitoring exclusion
- `GET  /stock-config/summary/` — Summary statistics

---

## Best Practices

1. Set global defaults first, then override only where needed.
2. Use category configs for product families with similar turnover.
3. Use product+warehouse config for location-specific thresholds.
4. Leverage `exclude_from_monitoring` for seasonal or discontinued products.
