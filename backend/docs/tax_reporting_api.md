# Tax Reporting API Documentation

> **Module:** SP12 — Tax Reporting & Compliance  
> **Base URL:** `/api/v1/accounting/tax/`

---

## Authentication

All endpoints require `Authorization: Bearer <token>` header.

---

## 1. Tax Configuration

### GET `/tax/config/`

List all tax configurations.

### GET `/tax/config/{id}/`

Retrieve a single configuration.

### PUT `/tax/config/{id}/`

Update tax registration details.

**Request body:**

```json
{
  "vat_registration_no": "123456789-7000",
  "is_svat_registered": false,
  "vat_filing_period": "MONTHLY",
  "epf_registration_no": "E/123456",
  "etf_registration_no": "654321",
  "tin_number": "987654321"
}
```

---

## 2. Tax Periods

### GET `/tax/periods/`

List tax filing periods (filterable by `tax_type`, `year`, `filing_status`).

### POST `/tax/periods/`

Create a new tax period.

**Request body:**

```json
{
  "tax_configuration": "<uuid>",
  "tax_type": "VAT",
  "period_type": "MONTHLY",
  "year": 2026,
  "period_number": 1,
  "start_date": "2026-01-01",
  "end_date": "2026-01-31",
  "due_date": "2026-02-20"
}
```

---

## 3. VAT Returns

### GET `/tax/vat-returns/`

List VAT returns.

### POST `/tax/vat-returns/`

Create/record a VAT return.

**Request body:**

```json
{
  "period": "<uuid>",
  "output_vat": "18000.00",
  "input_vat": "9000.00",
  "line_items": {
    "sales": [{ "description": "Standard rated sales", "amount": "100000.00", "vat": "18000.00" }],
    "purchases": [{ "description": "Business purchases", "amount": "50000.00", "vat": "9000.00" }]
  }
}
```

**Response** (auto-calculated fields):

```json
{
  "id": "<uuid>",
  "reference_number": "VAT-202601-00001",
  "output_vat": "18000.00",
  "input_vat": "9000.00",
  "net_vat_payable": "9000.00",
  "is_refund_position": false,
  "status": "GENERATED"
}
```

### GET `/tax/vat-returns/{id}/csv/`

Export VAT return as CSV download.

### GET `/tax/vat-returns/{id}/pdf/`

Get VAT return rendered as PDF HTML.

---

## 4. PAYE Returns

### GET `/tax/paye-returns/`

List PAYE returns.

### POST `/tax/paye-returns/`

Create a PAYE return.

**Request body:**

```json
{
  "tax_period": "<uuid>",
  "total_employees": 25,
  "total_remuneration": "2500000.00",
  "total_paye_deducted": "125000.00",
  "employee_details": [{ "name": "John Doe", "epf_no": "E/100001", "gross_salary": "100000.00", "paye": "5000.00" }]
}
```

---

## 5. EPF Returns (C-Form)

### GET `/tax/epf-returns/`

List EPF returns.

### POST `/tax/epf-returns/`

Create an EPF return.

**Contribution rates:** Employee 8% + Employer 12% = 20% total.

**Request body:**

```json
{
  "tax_period": "<uuid>",
  "total_employees": 20,
  "total_employee_contribution": "80000.00",
  "total_employer_contribution": "120000.00",
  "employee_schedule": [
    { "name": "Jane Smith", "basic_salary": "100000.00", "employee_8pct": "8000.00", "employer_12pct": "12000.00" }
  ]
}
```

Auto-calculated: `total_contribution = employee + employer = 200000.00`

---

## 6. ETF Returns

### GET `/tax/etf-returns/`

List ETF returns.

### POST `/tax/etf-returns/`

Create an ETF return.

**Contribution rate:** Employer-only 3%.

**Request body:**

```json
{
  "tax_period": "<uuid>",
  "total_employees": 20,
  "total_contribution": "30000.00",
  "total_gross_salary": "1000000.00"
}
```

---

## 7. Tax Submissions

### GET `/tax/submissions/`

List filed tax submissions.

### POST `/tax/submissions/`

Record a new filing submission.

**Request body:**

```json
{
  "tax_period": "<uuid>",
  "submitted_by": "<user-uuid>",
  "submission_reference": "VAT-2026-001234",
  "submitted_at": "2026-02-18T10:30:00Z",
  "status": "SUBMITTED",
  "notes": "Filed via IRD e-portal"
}
```

**Statuses:** `SUBMITTED`, `ACCEPTED`, `REJECTED`, `UNDER_REVIEW`

---

## 8. Tax Calendar

### GET `/tax/calendar/`

Overview of upcoming filing deadlines.

**Response:**

```json
{
  "current_month": "February 2026",
  "deadlines": [
    {
      "tax_type": "PAYE",
      "period": "2026/01",
      "due_date": "2026-02-15",
      "status": "PENDING",
      "days_remaining": 5
    },
    {
      "tax_type": "VAT",
      "period": "2026/01",
      "due_date": "2026-02-20",
      "status": "PENDING",
      "days_remaining": 10
    }
  ],
  "overdue": []
}
```

---

## 9. Reminders Widget

### GET `/tax/reminders/`

Dashboard widget data with urgency indicators.

**Response:**

```json
{
  "pending_filings": [
    {
      "period_id": "<uuid>",
      "tax_type": "VAT",
      "period": "2026/01",
      "due_date": "2026-02-20",
      "days_remaining": 3,
      "urgency": "warning",
      "status": "PENDING"
    }
  ],
  "summary": {
    "pending_count": 4,
    "overdue": 1,
    "urgent": 0,
    "warning": 1,
    "upcoming": 2
  },
  "recent_submissions": [
    {
      "tax_type": "EPF",
      "period": "2025/12",
      "submitted_at": "2026-01-28T10:30:00Z",
      "status": "Accepted & Processed"
    }
  ],
  "last_updated": "2026-02-10T08:00:00Z"
}
```

**Urgency levels:**

| Level    | Days Remaining | Color  |
| -------- | -------------- | ------ |
| overdue  | < 0            | Red    |
| urgent   | 0–1            | Orange |
| warning  | 2–3            | Yellow |
| upcoming | 4–7            | Blue   |
| normal   | > 7            | Green  |

---

## Sri Lankan Tax Deadlines

| Tax  | Due Date                             | Authority           |
| ---- | ------------------------------------ | ------------------- |
| VAT  | 20th of following month              | Inland Revenue Dept |
| PAYE | 15th of following month              | Inland Revenue Dept |
| EPF  | Last business day of following month | Central Bank (CBSL) |
| ETF  | Last business day of following month | ETF Board           |

---

## Export Formats

- **CSV:** Available on VAT returns via `/{id}/csv/` action
- **PDF:** HTML rendering via `/{id}/pdf/` action (use wkhtmltopdf or similar for final PDF)
