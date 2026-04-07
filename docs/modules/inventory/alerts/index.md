# Stock Alerts & Reordering Module

> **Module:** `apps.inventory.alerts`
> **Phase:** 04 — ERP Core Modules Part 1, SubPhase 10

---

## Overview

Comprehensive stock monitoring, automated alerting, and intelligent reorder
suggestions for the POS/ERP system.

### Features

| Feature              | Description                                        |
| -------------------- | -------------------------------------------------- |
| Multi-level config   | Global → category → product → warehouse thresholds |
| Automated monitoring | Celery-scheduled stock checks                      |
| Smart alerts         | Low stock, critical stock, out-of-stock detection  |
| Alert deduplication  | Prevents duplicate alerts for the same issue       |
| Notifications        | Email, SMS, dashboard, webhooks                    |
| Reorder calculations | EOQ, safety stock, velocity-based suggestions      |
| Demand forecasting   | Seasonality and trend detection                    |
| Auto-reorder         | Optional automated PO creation                     |
| Health scoring       | Inventory health metric 0 – 100                    |
| Reports              | JSON / CSV / Excel exports, email scheduling       |

---

## Architecture

```
Configuration Hierarchy
  GlobalStockSettings → CategoryStockConfig → ProductStockConfig (±warehouse)
                            │
                    ConfigResolver.resolve_for_product()
                            │
               ┌────────────┴────────────┐
               ▼                         ▼
     Celery Monitoring Tasks     Reorder Calculation
     (run_stock_monitoring)      (generate_reorder_suggestions)
               │                         │
               ▼                         ▼
         StockAlert  ◄──────────▶ ReorderSuggestion
         (lifecycle)              (convert / dismiss)
               │                         │
               ▼                         ▼
     AlertNotificationService     ReorderReportService
     (email, SMS, webhooks)       (CSV / Excel / email)
               │
               ▼
         DRF API Layer
         /api/v1/alerts/...
```

---

## Module Structure

```
apps/inventory/alerts/
├── models/
│   ├── global_settings.py     # Tenant-wide defaults (singleton)
│   ├── category_config.py     # Per-category overrides
│   ├── product_config.py      # Per-product (±warehouse) overrides
│   ├── stock_alert.py         # Alert model + manager
│   ├── reorder_suggestion.py  # Suggestion model + manager
│   └── monitoring_log.py      # Audit trail
├── constants.py               # Choice tuples and status constants
├── services/
│   ├── config_resolver.py     # Inheritance resolution
│   ├── notification.py        # Email / SMS dispatch
│   ├── webhook.py             # Webhook delivery
│   ├── sales_velocity.py      # Daily/weekly velocity
│   ├── reorder_calculator.py  # EOQ, safety stock, suggestions
│   ├── forecasting.py         # Demand forecast
│   └── reports.py             # Report & calendar services
├── tasks/
│   ├── stock_monitor.py       # run_stock_monitoring
│   ├── alert_resolution.py    # auto_resolve, snooze expiry
│   └── reorder_suggestions.py # generate, expire, auto-reorder
├── serializers/               # DRF serializers
├── views/                     # DRF viewsets & APIViews
├── urls.py                    # Router + extra paths
├── admin.py                   # Django admin integration
├── templates/                 # Email templates
└── tests/                     # pytest test suite
```

---

## Configuration Inheritance

Values resolve top-down; first non-null value wins:

1. **Warehouse-specific ProductStockConfig** (highest)
2. **Global ProductStockConfig** (warehouse = NULL)
3. **CategoryStockConfig** (with optional parent-category inheritance)
4. **GlobalStockSettings** (fallback)

```python
from apps.inventory.alerts.services import ConfigResolver

effective = ConfigResolver.resolve_for_product(product=p, warehouse=wh)
# → {"low_stock_threshold": 25, "reorder_point": 60, ..., "sources": {...}}
```

---

## Alert Lifecycle

```
 [Active]
    │──acknowledge(user)──▶ [Acknowledged]
    │                              │──resolve(user)──▶ [Resolved]
    │──resolve(user)───────────────────────────────────▶
    │──snooze(until, user)──▶ (paused until datetime)
```

### Alert Types

| Type             | Default priority | Trigger                                    |
| ---------------- | ---------------- | ------------------------------------------ |
| `low_stock`      | 5                | quantity < low threshold                   |
| `critical_stock` | 8                | quantity < threshold × critical multiplier |
| `out_of_stock`   | 9–10             | quantity = 0                               |
| `back_in_stock`  | 3                | quantity > threshold after OOS             |

---

## Reorder Calculations

### Economic Order Quantity (EOQ)

$$EOQ = \sqrt{\frac{2 \times D \times S}{H}}$$

- $D$ = annual demand (units)
- $S$ = ordering cost per order (LKR)
- $H$ = holding cost per unit per year (LKR)

### Safety Stock

$$SS = Z \times \sqrt{LT \times \sigma_d^2 + \bar{D}^2 \times \sigma_{LT}^2}$$

- $Z$ = service-level z-score (1.65 for 95 %)
- $LT$ = lead time (days)

### Urgency Levels

| Urgency  | Days until stockout |
| -------- | ------------------- |
| critical | ≤ 3                 |
| high     | 4 – 7               |
| medium   | 8 – 14              |
| low      | > 14                |

---

## API Endpoints

Base URL: `/api/v1/alerts/`

### Stock Configuration

| Method | Path                                    | Description      |
| ------ | --------------------------------------- | ---------------- |
| GET    | `/stock-config/`                        | List configs     |
| POST   | `/stock-config/`                        | Create config    |
| PATCH  | `/stock-config/{id}/`                   | Update config    |
| DELETE | `/stock-config/{id}/`                   | Delete config    |
| GET    | `/stock-config/summary/`                | Summary counts   |
| POST   | `/stock-config/{id}/reset_to_defaults/` | Reset to inherit |
| POST   | `/stock-config/bulk/`                   | Bulk update      |
| POST   | `/stock-config/bulk_exclude/`           | Bulk exclude     |

### Global Settings

| Method | Path                     | Description          |
| ------ | ------------------------ | -------------------- |
| GET    | `/global-settings/`      | Get / list singleton |
| PATCH  | `/global-settings/{id}/` | Update settings      |

### Alerts

| Method | Path                        | Description      |
| ------ | --------------------------- | ---------------- |
| GET    | `/alerts/`                  | List alerts      |
| GET    | `/alerts/{id}/`             | Retrieve alert   |
| POST   | `/alerts/{id}/acknowledge/` | Acknowledge      |
| POST   | `/alerts/{id}/snooze/`      | Snooze           |
| POST   | `/alerts/{id}/resolve/`     | Resolve          |
| POST   | `/alerts/bulk_acknowledge/` | Bulk acknowledge |
| GET    | `/alerts/statistics/`       | Statistics       |

### Reorder Suggestions

| Method | Path                           | Description             |
| ------ | ------------------------------ | ----------------------- |
| GET    | `/reorder/`                    | List suggestions        |
| GET    | `/reorder/{id}/`               | Retrieve                |
| POST   | `/reorder/{id}/convert_to_po/` | Convert to PO           |
| POST   | `/reorder/{id}/dismiss/`       | Dismiss                 |
| POST   | `/reorder/bulk_convert/`       | Bulk convert            |
| GET    | `/reorder/summary/`            | Summary stats           |
| GET    | `/reorder/report/`             | Report (JSON/CSV/Excel) |
| POST   | `/reorder/email_report/`       | Queue email report      |

### Dashboard & Health

| Method | Path          | Description        |
| ------ | ------------- | ------------------ |
| GET    | `/dashboard/` | Alert dashboard    |
| GET    | `/health/`    | Stock health score |

---

## Celery Tasks

| Task                           | Schedule                      | Description            |
| ------------------------------ | ----------------------------- | ---------------------- |
| `run_stock_monitoring`         | Configurable (hourly default) | Check all stock levels |
| `auto_resolve_alerts_task`     | Periodic                      | Resolve stale alerts   |
| `check_expired_snoozes`        | Every 15 min                  | Un-snooze expired      |
| `cleanup_old_monitoring_logs`  | Daily                         | Retention cleanup      |
| `generate_reorder_suggestions` | Daily                         | Create new suggestions |
| `mark_expired_suggestions`     | Daily                         | Expire old pending     |
| `process_auto_reorders`        | Daily                         | Auto-create POs        |
| `send_weekly_reorder_report`   | Weekly                        | Email summary          |

---

## Sri Lankan Context

- Currency: **LKR** (Sri Lankan Rupees)
- Timezone: **Asia/Colombo**
- Business hours: 8 AM – 6 PM
- Monitoring runs within business hours by default
- Supplier lead times account for local logistics
- Consider Poya days and monsoon seasons for safety stock

---

## Quick Start

```python
# 1. Configure global defaults
from apps.inventory.alerts.models import GlobalStockSettings
s = GlobalStockSettings.get_settings()
s.default_low_threshold = 20
s.default_reorder_point = 50
s.save()

# 2. Set product threshold
from apps.inventory.alerts.models import ProductStockConfig
ProductStockConfig.objects.create(
    product=my_product,
    low_stock_threshold=25,
    reorder_point=60,
    reorder_quantity=250,
)

# 3. Start Celery
# celery -A config beat --loglevel=info
# celery -A config worker --loglevel=info

# 4. Access alerts via API
# GET /api/v1/alerts/dashboard/
```

---

## Troubleshooting

| Issue                 | Check                                                        |
| --------------------- | ------------------------------------------------------------ |
| Alerts not generating | Celery Beat running? Monitoring frequency? Product excluded? |
| Wrong threshold used  | Inspect config inheritance chain via API                     |
| Snooze not expiring   | `check_expired_snoozes` task scheduled?                      |
| Report empty          | Verify pending suggestions exist                             |
