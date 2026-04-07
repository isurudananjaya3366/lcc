# API Reference

> Complete REST API reference for the Stock Alerts & Reordering module.

**Base URL:** `/api/v1/alerts/`

All endpoints require authentication (JWT or session). Responses use standard
DRF pagination.

---

## Product Stock Config

### `GET /stock-config/`

List product stock configurations. Supports filtering and search.

**Query Parameters:**
| Param | Type | Description |
| ----------- | ---- | -------------------------- |
| `warehouse` | UUID | Filter by warehouse |
| `search` | str | Search by product name/SKU |

### `POST /stock-config/`

Create a new product stock config.

**Body:**

```json
{
  "product_id": "uuid",
  "warehouse": "uuid (optional)",
  "low_stock_threshold": "25.000",
  "reorder_point": "60.000",
  "reorder_quantity": "250.000"
}
```

### `PATCH /stock-config/{id}/`

Update an existing config.

### `DELETE /stock-config/{id}/`

Delete a config.

### `POST /stock-config/{id}/reset_to_defaults/`

Reset config to global default values.

### `GET /stock-config/summary/`

Summary statistics for all configs.

### `POST /stock-config/bulk/`

Bulk update multiple configs.

**Body:**

```json
{
  "config_ids": ["uuid1", "uuid2"],
  "low_stock_threshold": "30.000"
}
```

### `POST /stock-config/bulk_exclude/`

Toggle monitoring exclusion for multiple products.

---

## Global Settings

### `GET /global-settings/`

Read global stock settings (singleton per tenant).

### `PUT /global-settings/{id}/`

Update global settings.

---

## Stock Alerts

### `GET /alerts/`

List alerts with filtering.

**Query Parameters:**
| Param | Type | Description |
| ----------- | ------ | ------------------------------ |
| `alert_type`| string | low_stock, critical_stock, etc |
| `status` | string | active, acknowledged, etc |
| `warehouse` | UUID | Filter by warehouse |
| `priority` | int | Filter by priority level |

### `GET /alerts/{id}/`

Retrieve a single alert.

### `POST /alerts/{id}/acknowledge/`

Mark alert as acknowledged.

### `POST /alerts/{id}/snooze/`

Snooze an alert.

**Body:**

```json
{
  "snoozed_until": "2024-01-15T18:00:00Z"
}
```

### `POST /alerts/{id}/resolve/`

Manually resolve an alert.

### `POST /alerts/bulk_acknowledge/`

Bulk acknowledge multiple alerts.

**Body:**

```json
{
  "alert_ids": ["uuid1", "uuid2", "uuid3"]
}
```

### `GET /alerts/statistics/`

Alert statistics by type and status.

---

## Product Alerts

### `GET /products/{product_id}/alerts/`

Aggregated alert data for a specific product.

**Response:**

```json
{
  "active_alerts": [...],
  "recent_history": [...],
  "reorder_suggestions": [...],
  "statistics": {
    "by_type": { "low_stock": 2, "critical_stock": 1 },
    "avg_resolution_time_hours": 4.5
  }
}
```

---

## Reorder Suggestions

### `GET /reorder/`

List reorder suggestions.

**Query Parameters:**
| Param | Type | Description |
| ------------------- | ------ | ------------------------ |
| `urgency` | string | critical, high, etc |
| `status` | string | pending, converted, etc |
| `warehouse` | UUID | Filter by warehouse |
| `estimated_cost_min`| number | Min estimated cost (LKR) |
| `estimated_cost_max`| number | Max estimated cost (LKR) |

### `GET /reorder/{id}/`

Retrieve a single suggestion.

### `POST /reorder/{id}/dismiss/`

Dismiss a suggestion.

**Body:**

```json
{
  "reason": "Already ordered from another supplier"
}
```

### `POST /reorder/{id}/convert_to_po/`

Convert suggestion to purchase order.

### `POST /reorder/bulk_convert/`

Bulk convert multiple suggestions.

### `GET /reorder/summary/`

Summary of pending suggestions by urgency.

### `GET /reorder/report/`

Export reorder report.

**Query Parameters:**
| Param | Type | Options |
| --------------- | ------ | --------------------- |
| `export_format` | string | json, csv, excel |

### `POST /reorder/email_report/`

Email a reorder report.

### `GET /reorder/{id}/calendar/`

Calendar view for reorder scheduling.

---

## Dashboard & Health

### `GET /dashboard/`

Alert dashboard with summary counts and recent alerts.
Response is cached for 5 minutes.

### `GET /health/`

Inventory health score (0–100) with breakdown.

**Query Parameters:**
| Param | Type | Description |
| ---------- | ---- | ------------------- |
| `warehouse`| UUID | Filter by warehouse |
| `category` | UUID | Filter by category |

Response is cached for 10 minutes.

**Response:**

```json
{
  "health_score": "85.50",
  "total_products": 150,
  "healthy_count": 128,
  "low_stock_count": 12,
  "critical_count": 5,
  "oos_count": 5,
  "trend": "stable"
}
```
