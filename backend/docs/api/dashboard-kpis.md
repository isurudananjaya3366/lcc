# Dashboard KPIs API Documentation

> **Module:** Dashboard & KPIs  
> **Base URL:** `/api/v1/dashboard/`  
> **Authentication:** Required (JWT Bearer Token)

---

## Overview

The Dashboard API provides real-time KPI metrics across four business categories: Sales, Inventory, Financial, and HR. It also supports user-specific layout customization and configurable threshold alerts.

---

## Endpoints

### 1. Sales KPIs

**GET** `/api/v1/dashboard/sales/`

Retrieve sales performance metrics.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| period | string | month | Period: today, week, month, quarter, year |
| refresh | boolean | false | Force cache refresh |

**Response:** `200 OK`

```json
{
  "todays_sales": {
    "value": 125000.0,
    "label": "Today's Sales",
    "change": 15.5,
    "extra": { "order_count": 42 }
  },
  "monthly_sales": {
    "value": 3250000.0,
    "label": "Monthly Sales",
    "change": 8.2,
    "extra": {}
  },
  "average_order_value": {
    "value": 2976.19,
    "label": "Average Order Value",
    "change": -2.1,
    "extra": {}
  }
}
```

---

### 2. Inventory KPIs

**GET** `/api/v1/dashboard/inventory/`

Retrieve inventory and stock metrics.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| period | string | month | Period for turnover calculations |
| refresh | boolean | false | Force cache refresh |

**Response:** `200 OK`

```json
{
  "stock_value": {
    "value": 15750000.00,
    "label": "Total Stock Value",
    "extra": {"product_count": 1250}
  },
  "low_stock_items": {
    "value": 23,
    "label": "Low Stock Items",
    "extra": {"items": [...]}
  },
  "out_of_stock": {
    "value": 5,
    "label": "Out of Stock",
    "extra": {"items": [...]}
  }
}
```

---

### 3. Financial KPIs

**GET** `/api/v1/dashboard/financial/`

Retrieve financial performance metrics.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| period | string | month | Period: month, quarter, year |
| refresh | boolean | false | Force cache refresh |

**Response:** `200 OK`

```json
{
  "revenue": {
    "value": 4500000.0,
    "label": "Total Revenue",
    "change": 12.3,
    "extra": { "previous_period": 4006000.0 }
  },
  "expenses": {
    "value": 3200000.0,
    "label": "Total Expenses",
    "change": 5.1,
    "extra": {}
  },
  "net_income": {
    "value": 1300000.0,
    "label": "Net Income",
    "change": 28.7,
    "extra": {}
  }
}
```

---

### 4. HR KPIs

**GET** `/api/v1/dashboard/hr/`

Retrieve human resources metrics.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| period | string | month | Period for turnover/hiring metrics |
| refresh | boolean | false | Force cache refresh |

**Response:** `200 OK`

```json
{
  "total_employees": {
    "value": 85,
    "label": "Total Active Employees",
    "extra": {
      "by_department": [
        { "department": "Sales", "count": 25 },
        { "department": "Operations", "count": 20 }
      ]
    }
  },
  "attendance_rate": {
    "value": 94.5,
    "label": "Attendance Rate (%)",
    "extra": { "today_rate": 96.2 }
  },
  "pending_leave_requests": {
    "value": 7,
    "label": "Pending Leave Requests",
    "extra": { "oldest_pending_days": 3 }
  }
}
```

---

### 5. All KPIs (Combined)

**GET** `/api/v1/dashboard/all/`

Retrieve all KPI categories in a single request.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| period | string | month | Period for all calculations |
| refresh | boolean | false | Force cache refresh |

**Response:** `200 OK`

```json
{
  "sales": { "todays_sales": {...}, "monthly_sales": {...} },
  "inventory": { "stock_value": {...}, "low_stock_items": {...} },
  "financial": { "revenue": {...}, "expenses": {...} },
  "hr": { "total_employees": {...}, "attendance_rate": {...} },
  "alerts": [
    {
      "id": 1,
      "kpi_name": "Low Stock Items",
      "kpi_code": "STOCK_LOW",
      "warning_threshold": "10.00",
      "critical_threshold": "5.00",
      "comparison": "gt",
      "is_active": true
    }
  ]
}
```

---

### 6. Active Alerts

**GET** `/api/v1/dashboard/alerts/`

Retrieve all active KPI alerts.

**Response:** `200 OK`

```json
[
  {
    "id": 1,
    "kpi": 3,
    "kpi_name": "Low Stock Items",
    "kpi_code": "STOCK_LOW",
    "warning_threshold": "10.00",
    "critical_threshold": "5.00",
    "comparison": "gt",
    "notify_email": true,
    "notify_dashboard": true,
    "is_active": true,
    "last_triggered": "2025-01-15T14:30:00Z"
  }
]
```

---

### 7. Dashboard Layout

**GET** `/api/v1/dashboard/layout/`

Retrieve user's dashboard layout. Returns default if none saved.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| reset | boolean | false | Reset to default layout |

**Response:** `200 OK`

```json
{
  "id": 1,
  "name": "My Dashboard",
  "widgets": {
    "widgets": [
      {
        "kpi_code": "SALES_TODAY",
        "widget_type": "NUMBER",
        "position": { "x": 0, "y": 0, "w": 3, "h": 1 }
      }
    ]
  },
  "is_default": true,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

---

**PUT** `/api/v1/dashboard/layout/`

Save or update user's dashboard layout.

**Request Body:**

```json
{
  "name": "Custom Dashboard",
  "widgets": {
    "widgets": [
      {
        "kpi_code": "SALES_TODAY",
        "widget_type": "NUMBER",
        "position": { "x": 0, "y": 0, "w": 3, "h": 1 },
        "config": { "show_trend": true }
      },
      {
        "kpi_code": "STOCK_VALUE",
        "widget_type": "GAUGE",
        "position": { "x": 3, "y": 0, "w": 3, "h": 1 }
      }
    ]
  }
}
```

**Response:** `201 Created` (new) or `200 OK` (updated)

---

## Caching

All KPI endpoints use Redis caching with period-based TTLs:

- `today` period: 5 minutes
- `week` / `month`: 10 minutes
- `quarter` / `year`: 30 minutes

Use `?refresh=true` to bypass cache.

---

## Error Responses

| Status | Description                        |
| ------ | ---------------------------------- |
| 401    | Authentication required            |
| 403    | Insufficient permissions           |
| 404    | Endpoint not found                 |
| 500    | Server error (logged with details) |

---

## Periodic Alert Checking

A Celery beat task (`check_kpi_alerts`) runs every 30 minutes to evaluate all active alerts against current KPI values.

- Triggered alerts are logged and update `last_triggered` timestamp
- Supports comparison operators: `lt`, `gt`, `lte`, `gte`
- Two severity levels: `warning` and `critical`
