# Reorder Suggestions & Auto-Reorder

> Intelligent reorder calculations, suggestion management, and optional
> automated purchase order creation.

---

## Reorder Calculation Pipeline

```
SalesVelocityService                    ReorderCalculator
  ├─ calculate_velocity()         ──►   ├─ calculate_days_until_stockout()
  ├─ calculate_daily_velocity()         ├─ determine_urgency()
  ├─ detect_trend()                     ├─ simplified_safety_stock()
  ├─ detect_seasonality()               ├─ calculate_eoq()
  └─ get_seasonal_factor()              ├─ get_reorder_point()
                                        ├─ calculate_estimated_cost()
                                        └─ calculate_reorder_suggestion()
```

### Sales Velocity

`SalesVelocityService` queries `OrderItem` history to compute demand rates.

**Fallback chain** (when no recent data):

1. Extend to 90 days
2. Use category average from sibling products
3. Return zero velocity

**Seasonality:** `detect_seasonality()` checks coefficient of variation on
monthly totals (>30% = seasonal). `get_seasonal_factor()` returns a multiplier
for the current month vs. yearly average.

### Urgency Levels

| Days Until Stockout | Urgency  |
| ------------------- | -------- |
| < 5                 | Critical |
| 5 – 14              | High     |
| 15 – 29             | Medium   |
| ≥ 30                | Low      |

### EOQ (Economic Order Quantity)

Uses the Wilson formula:

$$EOQ = \sqrt{\frac{2 \times D \times S}{H}}$$

Where $D$ = annual demand, $S$ = ordering cost (LKR), $H$ = holding cost per
unit per year.

---

## Suggestion Lifecycle

```
  ┌─────────┐  convert_to_po  ┌───────────┐
  │ PENDING ├─────────────────►│ CONVERTED │
  └────┬────┘                  └───────────┘
       │ dismiss
       ▼
  ┌───────────┐
  │ DISMISSED │
  └───────────┘
       │ expire (30d)
       ▼
  ┌─────────┐
  │ EXPIRED │
  └─────────┘
```

---

## Celery Tasks

| Task                           | Schedule | Purpose                            |
| ------------------------------ | -------- | ---------------------------------- |
| `generate_reorder_suggestions` | Daily    | Create/update suggestions          |
| `mark_expired_suggestions`     | Daily    | Expire old pending suggestions     |
| `process_auto_reorders`        | Daily    | Convert eligible → PO (if enabled) |
| `send_weekly_reorder_report`   | Weekly   | Email summary report               |

---

## Auto-Reorder

When `GlobalStockSettings.enable_auto_reorder = True`:

1. `process_auto_reorders` finds pending suggestions meeting minimum urgency.
2. Validates budget limits and supplier availability.
3. Creates purchase order stubs.
4. Marks suggestions as `converted_to_po`.

Controlled by `auto_reorder_min_urgency` (default: high).

---

## Supplier Lead Time Tracking

`SupplierLeadTimeLog` records actual delivery performance:

| Field           | Purpose                              |
| --------------- | ------------------------------------ |
| `supplier`      | FK to vendor                         |
| `product`       | FK to product                        |
| `ordered_date`  | When PO was placed                   |
| `received_date` | When goods arrived                   |
| `expected_date` | Expected delivery date               |
| `days_taken`    | Auto-calculated (received − ordered) |
| `days_late`     | Auto-calculated (actual − expected)  |
| `on_time`       | Boolean (days_late ≤ 0)              |

`SupplierLeadTimeManager` provides:

- `for_supplier(supplier_id)` — All logs for a supplier
- `for_product(product_id)` — All logs for a product
- `get_supplier_stats(supplier_id)` — Aggregate stats
- `get_lead_time_for_product(product_id, supplier_id)` — Average lead time

---

## API Endpoints

| Method | Path                                         | Purpose                    |
| ------ | -------------------------------------------- | -------------------------- |
| `GET`  | `/api/v1/alerts/reorder/`                    | List suggestions           |
| `GET`  | `/api/v1/alerts/reorder/{id}/`               | Retrieve suggestion        |
| `POST` | `/api/v1/alerts/reorder/{id}/dismiss/`       | Dismiss with reason        |
| `POST` | `/api/v1/alerts/reorder/{id}/convert_to_po/` | Convert to purchase order  |
| `POST` | `/api/v1/alerts/reorder/bulk_convert/`       | Bulk convert to POs        |
| `GET`  | `/api/v1/alerts/reorder/summary/`            | Urgency summary            |
| `GET`  | `/api/v1/alerts/reorder/report/`             | JSON/CSV/Excel export      |
| `POST` | `/api/v1/alerts/reorder/email_report/`       | Email report to recipients |
| `GET`  | `/api/v1/alerts/reorder/{id}/calendar/`      | Calendar view data         |

Filters: `urgency`, `status`, `warehouse`, `product`, `estimated_cost_min/max`.
