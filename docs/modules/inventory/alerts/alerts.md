# Stock Alerts System

> Automated alert lifecycle: creation, escalation, acknowledgement,
> snoozing, and resolution.

---

## Alert Types

| Type             | Priority | Trigger                     | Color   |
| ---------------- | -------- | --------------------------- | ------- |
| `back_in_stock`  | 1 (Info) | Restocked after OOS         | #4CAF50 |
| `low_stock`      | 2        | Stock ≤ low threshold & > 0 | #FFC107 |
| `critical_stock` | 3        | Stock ≤ critical threshold  | #FF9800 |
| `out_of_stock`   | 4 (Crit) | Stock ≤ 0                   | #F44336 |

Critical threshold = `low_stock_threshold × critical_threshold_multiplier`
(default multiplier: 0.5).

---

## Alert Lifecycle

```
  ┌─────────┐  acknowledge   ┌──────────────┐
  │  ACTIVE ├───────────────►│ ACKNOWLEDGED │
  └────┬────┘                └──────┬───────┘
       │ snooze                     │ resolve
       ▼                            ▼
  ┌─────────┐  un-snooze     ┌──────────┐
  │ SNOOZED ├────────────────►│ RESOLVED │
  └─────────┘   (auto via    └──────────┘
               expired check)
```

- **Active** — New alert requiring attention.
- **Acknowledged** — User has seen it; still tracked.
- **Snoozed** — Muted until `snoozed_until` timestamp.
  A Celery task (`check_expired_snoozes`) reactivates expired snoozes.
- **Resolved** — Stock recovered above threshold (auto) or manually
  resolved via API.

---

## Alert Creation & Deduplication

`StockAlert.create_or_update()` handles deduplication:

1. Checks for an existing active alert of the same type/product/warehouse.
2. If found and stock changed ≥ 5 units, updates the existing alert.
3. If none found and not within cooldown window, creates a new alert.
4. Returns `(alert, created)` tuple.

---

## Throttling

Prevents alert spam during rapid stock fluctuations.

| Alert Type       | Default Throttle |
| ---------------- | ---------------- |
| `low_stock`      | 24 hours         |
| `critical_stock` | 12 hours         |
| `out_of_stock`   | 6 hours          |
| `back_in_stock`  | 24 hours         |

Throttle bypass occurs when stock drops ≥ 50% since the last alert.

---

## Escalation

When a product drops from LOW_STOCK to CRITICAL_STOCK:

1. Existing LOW_STOCK alerts are auto-resolved.
2. A new CRITICAL_STOCK alert is created.
3. `_check_escalation_needed()` flags `needs_escalation=True`.

Similarly, OOS alerts resolve any existing LOW/CRITICAL alerts.

---

## Severity Calculation

`check_low_stock()` returns a severity float (0.0 → 1.0):

```
severity = 1.0 - (current_stock / threshold)
```

| Severity Range | Level    |
| -------------- | -------- |
| ≥ 0.75         | Critical |
| ≥ 0.50         | High     |
| ≥ 0.25         | Medium   |
| < 0.25         | Low      |

---

## API Endpoints

| Method | Path                                      | Purpose                   |
| ------ | ----------------------------------------- | ------------------------- |
| `GET`  | `/api/v1/alerts/alerts/`                  | List all alerts           |
| `GET`  | `/api/v1/alerts/alerts/{id}/`             | Retrieve single alert     |
| `POST` | `/api/v1/alerts/alerts/{id}/acknowledge/` | Acknowledge an alert      |
| `POST` | `/api/v1/alerts/alerts/{id}/snooze/`      | Snooze with duration      |
| `POST` | `/api/v1/alerts/alerts/{id}/resolve/`     | Resolve manually          |
| `POST` | `/api/v1/alerts/alerts/bulk_acknowledge/` | Bulk acknowledge          |
| `GET`  | `/api/v1/alerts/alerts/statistics/`       | Summary statistics        |
| `GET`  | `/api/v1/alerts/products/{id}/alerts/`    | Per-product alert summary |

Filters: `alert_type`, `status`, `warehouse`, `priority`, `product`.
