# Financial Reports API

## Overview

The Financial Reports API provides endpoints for generating standard financial statements including Trial Balance, Profit & Loss, Balance Sheet, Cash Flow Statement, and General Ledger.

**Base URL:** `/api/v1/accounting/reports/`

---

## Available Reports

```
GET /api/v1/accounting/reports/
```

Returns a list of available report types.

**Response:**

```json
{
  "reports": [
    { "type": "trial_balance", "name": "Trial Balance" },
    { "type": "profit_loss", "name": "Profit & Loss" },
    { "type": "balance_sheet", "name": "Balance Sheet" },
    { "type": "cash_flow", "name": "Cash Flow" },
    { "type": "general_ledger", "name": "General Ledger" }
  ]
}
```

---

## Common Query Parameters

All report endpoints accept the following parameters:

| Parameter               | Type   | Required | Description                                     |
| ----------------------- | ------ | -------- | ----------------------------------------------- |
| `start_date`            | date   | Varies   | Period start date (YYYY-MM-DD)                  |
| `end_date`              | date   | Varies   | Period end date (YYYY-MM-DD)                    |
| `as_of_date`            | date   | Varies   | Point-in-time date for balance reports          |
| `detail_level`          | string | No       | `SUMMARY` (default) or `DETAIL`                 |
| `include_comparison`    | bool   | No       | Enable period comparison (default: false)       |
| `include_zero_balances` | bool   | No       | Include zero-balance accounts (default: false)  |
| `comparison_start_date` | date   | No       | Comparison period start                         |
| `comparison_end_date`   | date   | No       | Comparison period end                           |
| `comparison_as_of_date` | date   | No       | Comparison as-of date                           |
| `format`                | string | No       | Output format: `json` (default), `pdf`, `excel` |

---

## Trial Balance

```
GET /api/v1/accounting/reports/trial-balance/
```

Generates a Trial Balance showing opening, period, and closing debit/credit balances for all accounts.

**Required Parameters:** None (uses as_of_date or end_date)

**Example:**

```
GET /reports/trial-balance/?start_date=2026-01-01&end_date=2026-12-31
```

**Response:**

```json
{
  "status": "success",
  "report_type": "trial_balance",
  "data": {
    "title": "Trial Balance",
    "period": { "start_date": "2026-01-01", "end_date": "2026-12-31" },
    "account_groups": [
      {
        "account_type": "asset",
        "display_name": "Assets",
        "accounts": [
          {
            "account_code": "1100",
            "account_name": "Cash in Hand",
            "opening_debit": 50000.0,
            "opening_credit": 0.0,
            "period_debit": 200000.0,
            "period_credit": 180000.0,
            "closing_debit": 70000.0,
            "closing_credit": 0.0
          }
        ],
        "subtotals": { "opening_debit": 50000.0, "...": "..." }
      }
    ],
    "grand_totals": { "opening_debit": 100000.0, "opening_credit": 100000.0, "...": "..." },
    "is_balanced": true,
    "validation": { "is_balanced": true, "errors": [] }
  }
}
```

---

## Profit & Loss Statement

```
GET /api/v1/accounting/reports/profit-loss/
```

Generates an Income Statement showing revenue, COGS, operating expenses, and net income.

**Required Parameters:** `start_date`, `end_date`

**Example:**

```
GET /reports/profit-loss/?start_date=2026-01-01&end_date=2026-12-31
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "title": "Profit & Loss Statement",
    "revenue": { "accounts": [...], "total": 1000000.0 },
    "cost_of_goods_sold": { "accounts": [...], "total": 600000.0 },
    "gross_profit": { "amount": 400000.0, "margin_percentage": 40.0 },
    "operating_expenses": { "accounts": [...], "total": 200000.0 },
    "operating_income": { "amount": 200000.0, "margin_percentage": 20.0 },
    "other_income": { "accounts": [...], "total": 10000.0 },
    "other_expenses": { "accounts": [...], "total": 5000.0 },
    "net_income": { "amount": 205000.0, "margin_percentage": 20.5 }
  }
}
```

---

## Balance Sheet

```
GET /api/v1/accounting/reports/balance-sheet/
```

Generates a Statement of Financial Position showing Assets = Liabilities + Equity.

**Required Parameters:** `as_of_date` or `end_date`

**Example:**

```
GET /reports/balance-sheet/?as_of_date=2026-12-31
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "title": "Balance Sheet",
    "as_of_date": "2026-12-31",
    "assets": {
      "current_assets": { "accounts": [...], "total": 500000.0 },
      "fixed_assets": { "accounts": [...], "total_gross": 300000.0 },
      "accumulated_depreciation": { "accounts": [...], "total": 50000.0 },
      "net_fixed_assets": 250000.0,
      "total_assets": 750000.0
    },
    "liabilities": {
      "current_liabilities": { "accounts": [...], "total": 200000.0 },
      "long_term_liabilities": { "accounts": [...], "total": 100000.0 },
      "total_liabilities": 300000.0
    },
    "equity": {
      "total_equity": 450000.0,
      "current_net_income": 205000.0
    },
    "total_liabilities_equity": 750000.0,
    "is_balanced": true
  }
}
```

---

## Cash Flow Statement

```
GET /api/v1/accounting/reports/cash-flow/
```

Generates a Cash Flow Statement using the indirect method.

**Required Parameters:** `start_date`, `end_date`

**Example:**

```
GET /reports/cash-flow/?start_date=2026-01-01&end_date=2026-12-31
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "title": "Cash Flow Statement",
    "operating_activities": {
      "net_income": 205000.0,
      "adjustments": [...],
      "working_capital_changes": [...],
      "total": 250000.0
    },
    "investing_activities": { "items": [...], "total": -100000.0 },
    "financing_activities": { "items": [...], "total": 50000.0 },
    "net_cash_change": 200000.0,
    "beginning_cash": 300000.0,
    "ending_cash": 500000.0
  }
}
```

---

## General Ledger

```
GET /api/v1/accounting/reports/general-ledger/
```

Generates a detailed transaction log with running balances.

**Additional Parameters:**

| Parameter      | Type   | Description                 |
| -------------- | ------ | --------------------------- |
| `account_code` | string | Filter to single account    |
| `code_from`    | string | Start of account code range |
| `code_to`      | string | End of account code range   |

**Required Parameters:** `start_date`, `end_date`

**Example:**

```
GET /reports/general-ledger/?start_date=2026-01-01&end_date=2026-12-31&account_code=1100
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "title": "General Ledger",
    "filter": "Account: 1100",
    "accounts": [
      {
        "account_code": "1100",
        "account_name": "Cash in Hand",
        "opening_balance": 50000.0,
        "transactions": [
          {
            "date": "2026-01-15",
            "entry_number": "JE-2026-00001",
            "description": "Cash sale",
            "debit_amount": 5000.0,
            "credit_amount": 0.0,
            "running_balance": 55000.0
          }
        ],
        "closing_balance": 70000.0
      }
    ],
    "summary": {
      "total_accounts": 1,
      "total_transactions": 45,
      "total_debits": 220000.0,
      "total_credits": 200000.0
    }
  }
}
```

---

## Export Formats

### PDF Export

```
GET /reports/trial-balance/?start_date=2026-01-01&end_date=2026-12-31&format=pdf
```

Returns a PDF file with `Content-Disposition: attachment`.

### Excel Export

```
GET /reports/trial-balance/?start_date=2026-01-01&end_date=2026-12-31&format=excel
```

Returns an `.xlsx` file with `Content-Disposition: attachment`.

---

## Error Responses

```json
{
  "status": "error",
  "message": "start_date and end_date are required for Profit & Loss."
}
```

**HTTP Status Codes:**

- `200` — Report generated successfully
- `400` — Invalid parameters or report generation error
- `401` — Authentication required
- `501` — Export format not available (missing dependency)

---

## Comparison Mode

Enable comparison by setting `include_comparison=true` and providing comparison date parameters. Response includes additional `comparison` and `variances` keys with variance classification (favorable/unfavorable) and materiality flags.

```
GET /reports/trial-balance/?start_date=2026-01-01&end_date=2026-12-31&include_comparison=true&comparison_start_date=2025-01-01&comparison_end_date=2025-12-31
```
