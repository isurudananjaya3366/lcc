# Analytics & Reports API

## Overview

The Analytics API provides endpoints for generating, managing, and scheduling
business intelligence reports. All endpoints require authentication and
return JSON responses.

**Base URL:** `/api/v1/analytics/`

---

## Endpoints

### List Available Reports

```
GET /api/v1/analytics/reports/
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|--------|-------------------------------------|
| category | string | Filter by category (SALES, INVENTORY, etc.) |
| search | string | Search report names |

**Response:** `200 OK`

```json
[
  {
    "id": "uuid",
    "code": "SALES_BY_PRODUCT",
    "name": "Sales by Product",
    "category": "SALES",
    "is_active": true
  }
]
```

---

### Get Report Definition Detail

```
GET /api/v1/analytics/reports/{code}/
```

**Response:** `200 OK`

```json
{
  "id": "uuid",
  "code": "SALES_BY_PRODUCT",
  "name": "Sales by Product",
  "description": "Sales breakdown by product with rankings.",
  "category": "SALES",
  "available_filters": {},
  "is_active": true,
  "default_format": "PDF",
  "allows_scheduling": true,
  "allows_export": true,
  "max_date_range_days": null,
  "estimated_time_seconds": 60,
  "created_on": "2026-01-01T00:00:00Z",
  "updated_on": "2026-01-01T00:00:00Z"
}
```

---

### Generate Report

```
POST /api/v1/analytics/generate/
```

**Request Body:**

```json
{
  "report_code": "SALES_BY_PRODUCT",
  "parameters": {
    "date_range": {
      "start_date": "2026-01-01",
      "end_date": "2026-01-31"
    }
  },
  "format": "JSON"
}
```

**Response:** `201 Created`

```json
{
  "id": "uuid",
  "report_definition": "uuid",
  "report_definition_name": "Sales by Product",
  "filter_parameters": {},
  "output_format": "JSON",
  "status": "COMPLETED",
  "report_data": {
    "report_type": "SALES_BY_PRODUCT",
    "report_title": "Sales By Product",
    "generated_at": "2026-01-31T12:00:00Z",
    "data": [],
    "totals": {},
    "row_count": 0
  }
}
```

**Error Response:** `400 Bad Request`

```json
{
  "report_code": ["No active report definition with code: INVALID"]
}
```

---

### List Report Instances

```
GET /api/v1/analytics/instances/
```

Returns the 50 most recent report instances for the authenticated user.

**Response:** `200 OK`

```json
[
  {
    "id": "uuid",
    "report_definition_name": "Sales by Product",
    "status": "COMPLETED",
    "output_format": "JSON",
    "generated_at": "2026-01-31T12:00:00Z",
    "generation_time_seconds": 2
  }
]
```

---

### Download Report File

```
GET /api/v1/analytics/download/{id}/
```

Returns the generated file as a download attachment. Only available for
completed reports that have a file attached.

**Response:** `200 OK` (file download)

**Error Responses:**

- `404 Not Found` — Instance not found or no file available

---

### Saved Reports

```
GET /api/v1/analytics/saved/
POST /api/v1/analytics/saved/
```

**GET** — List saved reports (owned by user or public).

**POST** — Create a new saved report configuration.

**Request Body (POST):**

```json
{
  "name": "My Monthly Sales",
  "description": "Monthly sales by product",
  "report_definition": "uuid",
  "filters_config": {
    "date_range": { "start_date": "2026-01-01", "end_date": "2026-01-31" }
  },
  "output_format": "PDF",
  "is_public": false
}
```

**Response:** `201 Created`

---

### Scheduled Reports

```
GET /api/v1/analytics/scheduled/
POST /api/v1/analytics/scheduled/
```

**GET** — List user's scheduled reports.

**POST** — Create a new schedule.

**Request Body (POST):**

```json
{
  "saved_report": "uuid",
  "frequency": "WEEKLY",
  "time_of_day": "09:00:00",
  "day_of_week": 0,
  "is_active": true,
  "recipients": ["user@example.com"],
  "email_subject": "{report_name} - {date}",
  "attach_pdf": true
}
```

---

### Schedule History

```
GET /api/v1/analytics/scheduled/{id}/history/
```

Returns the execution history for a specific scheduled report.

**Response:** `200 OK`

```json
[
  {
    "id": "uuid",
    "run_at": "2026-01-31T09:00:00Z",
    "status": "SUCCESS",
    "execution_time_seconds": "3.50",
    "email_sent": true,
    "recipients_count": 2
  }
]
```

---

## Report Categories

| Category  | Code      | Description                       |
| --------- | --------- | --------------------------------- |
| Sales     | SALES     | Revenue, transactions, sales      |
| Inventory | INVENTORY | Stock levels, movement, valuation |
| Purchase  | PURCHASE  | Vendor orders, receiving          |
| Customer  | CUSTOMER  | Customer analytics, CLV           |
| Staff     | STAFF     | Attendance, leave, overtime       |
| Financial | FINANCIAL | P&L, balance sheet, cash flow     |
| Tax       | TAX       | VAT, compliance, regulatory       |

## Report Formats

| Format | Extension | MIME Type                         |
| ------ | --------- | --------------------------------- |
| PDF    | .pdf      | application/pdf                   |
| EXCEL  | .xlsx     | application/vnd.openxmlformats-\* |
| CSV    | .csv      | text/csv                          |
| JSON   | .json     | application/json                  |
| HTML   | .html     | text/html                         |

## Available Report Generators

| Code                    | Category  | Description                    |
| ----------------------- | --------- | ------------------------------ |
| SALES_BY_PRODUCT        | SALES     | Product-level sales breakdown  |
| SALES_BY_CUSTOMER       | SALES     | Customer-level sales analysis  |
| SALES_BY_PERIOD         | SALES     | Time-series sales trends       |
| SALES_BY_CHANNEL        | SALES     | Channel comparison (POS/Web)   |
| SALES_BY_CASHIER        | SALES     | Cashier performance metrics    |
| STOCK_LEVEL             | INVENTORY | Current stock levels           |
| STOCK_MOVEMENT          | INVENTORY | Stock transaction history      |
| STOCK_VALUATION         | INVENTORY | Inventory valuation (FIFO/AVG) |
| PURCHASE_VENDOR         | PURCHASE  | Purchase orders by vendor      |
| PURCHASE_CATEGORY       | PURCHASE  | Purchases by category          |
| VENDOR_PERFORMANCE      | PURCHASE  | Vendor scoring and rating      |
| CUSTOMER_ACQUISITION    | CUSTOMER  | New customer analysis          |
| CUSTOMER_RETENTION      | CUSTOMER  | Retention and churn metrics    |
| CUSTOMER_LIFETIME_VALUE | CUSTOMER  | CLV calculation and tiers      |
| STAFF_ATTENDANCE        | STAFF     | Employee attendance tracking   |
| STAFF_LEAVE             | STAFF     | Leave balance and utilisation  |
| STAFF_OVERTIME          | STAFF     | Overtime hours and costs (LKR) |

## Authentication

All endpoints require a valid authentication token:

```
Authorization: Bearer <token>
```

## Error Codes

| Status | Meaning                             |
| ------ | ----------------------------------- |
| 400    | Validation error or invalid request |
| 401    | Authentication required             |
| 403    | Permission denied                   |
| 404    | Resource not found                  |
| 500    | Internal server error               |
