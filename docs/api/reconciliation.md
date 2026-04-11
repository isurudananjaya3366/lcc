# Account Reconciliation API

## Endpoints

### Bank Accounts

| Method | Endpoint                              | Description           |
| ------ | ------------------------------------- | --------------------- |
| GET    | `/api/accounting/bank-accounts/`      | List bank accounts    |
| POST   | `/api/accounting/bank-accounts/`      | Create bank account   |
| GET    | `/api/accounting/bank-accounts/{id}/` | Retrieve bank account |
| PUT    | `/api/accounting/bank-accounts/{id}/` | Update bank account   |
| PATCH  | `/api/accounting/bank-accounts/{id}/` | Partial update        |
| DELETE | `/api/accounting/bank-accounts/{id}/` | Delete bank account   |

### Reconciliations

| Method | Endpoint                                | Description             |
| ------ | --------------------------------------- | ----------------------- |
| GET    | `/api/accounting/reconciliations/`      | List reconciliations    |
| POST   | `/api/accounting/reconciliations/`      | Create reconciliation   |
| GET    | `/api/accounting/reconciliations/{id}/` | Retrieve reconciliation |
| PUT    | `/api/accounting/reconciliations/{id}/` | Update reconciliation   |
| DELETE | `/api/accounting/reconciliations/{id}/` | Delete reconciliation   |

#### Custom Actions

| Method | Endpoint                                                 | Description                                        |
| ------ | -------------------------------------------------------- | -------------------------------------------------- |
| POST   | `/api/accounting/reconciliations/{id}/start/`            | Start reconciliation                               |
| POST   | `/api/accounting/reconciliations/{id}/auto_match/`       | Run auto-matching                                  |
| POST   | `/api/accounting/reconciliations/{id}/match_items/`      | Manually match a statement line to a journal entry |
| POST   | `/api/accounting/reconciliations/{id}/unmatch_items/`    | Remove a match                                     |
| POST   | `/api/accounting/reconciliations/{id}/complete/`         | Complete reconciliation                            |
| POST   | `/api/accounting/reconciliations/{id}/cancel/`           | Cancel reconciliation                              |
| GET    | `/api/accounting/reconciliations/{id}/get_suggestions/`  | Get match suggestions for a statement line         |
| POST   | `/api/accounting/reconciliations/{id}/import_statement/` | Upload/import bank statement file                  |
| GET    | `/api/accounting/reconciliations/{id}/summary/`          | Get reconciliation summary                         |
| GET    | `/api/accounting/reconciliations/{id}/report/`           | Generate reconciliation report                     |

### Matching Rules

| Method | Endpoint                               | Description            |
| ------ | -------------------------------------- | ---------------------- |
| GET    | `/api/accounting/matching-rules/`      | List matching rules    |
| POST   | `/api/accounting/matching-rules/`      | Create matching rule   |
| GET    | `/api/accounting/matching-rules/{id}/` | Retrieve matching rule |
| PUT    | `/api/accounting/matching-rules/{id}/` | Update matching rule   |
| PATCH  | `/api/accounting/matching-rules/{id}/` | Partial update         |
| DELETE | `/api/accounting/matching-rules/{id}/` | Delete matching rule   |

---

## Request/Response Schemas

### Bank Account

```json
{
  "id": "uuid",
  "account_name": "string",
  "account_number": "string",
  "bank_name": "string",
  "branch_name": "string | null",
  "branch_code": "string | null",
  "account_type": "CHECKING | SAVINGS | CREDIT_CARD | CASH",
  "gl_account": "uuid",
  "currency": "string (default: LKR)",
  "last_reconciled_date": "date | null",
  "last_reconciled_balance": "decimal | null",
  "is_active": "boolean",
  "created_by": "uuid",
  "updated_by": "uuid | null"
}
```

### Start Reconciliation

**POST** `/api/accounting/reconciliations/{id}/start/`

```json
{
  "bank_account_id": "uuid",
  "statement_id": "uuid (optional)"
}
```

**Response:**

```json
{
  "id": "uuid",
  "bank_account": "uuid",
  "bank_statement": "uuid | null",
  "start_date": "date",
  "end_date": "date",
  "statement_balance": "decimal",
  "book_balance": "decimal",
  "difference": "decimal",
  "status": "IN_PROGRESS",
  "created_by": "uuid"
}
```

### Match Items

**POST** `/api/accounting/reconciliations/{id}/match_items/`

```json
{
  "statement_line_id": "uuid",
  "journal_entry_id": "uuid",
  "notes": "string (optional)"
}
```

### Unmatch Items

**POST** `/api/accounting/reconciliations/{id}/unmatch_items/`

```json
{
  "item_id": "uuid"
}
```

### Complete Reconciliation

**POST** `/api/accounting/reconciliations/{id}/complete/`

```json
{
  "force_complete": false
}
```

### Get Suggestions

**GET** `/api/accounting/reconciliations/{id}/get_suggestions/?statement_line_id={uuid}`

**Response:**

```json
[
  {
    "journal_entry": { "id": "uuid", "entry_date": "date", "description": "string" },
    "score": 0.95,
    "quality": "excellent",
    "confidence": "high",
    "explanation": "string"
  }
]
```

### Import Statement

**POST** `/api/accounting/reconciliations/{id}/import_statement/` (multipart/form-data)

| Field    | Type   | Description                    |
| -------- | ------ | ------------------------------ |
| `file`   | File   | Bank statement file (CSV, OFX) |
| `format` | string | `CSV` or `OFX`                 |

### Summary

**GET** `/api/accounting/reconciliations/{id}/summary/`

```json
{
  "matched_count": 5,
  "unmatched_statement_count": 2,
  "unmatched_journal_count": 1,
  "total_matched_amount": "50000.00",
  "difference": "5000.00",
  "statement_balance": "125000.00",
  "book_balance": "120000.00"
}
```

### Report

**GET** `/api/accounting/reconciliations/{id}/report/`

Returns a JSON report with `header`, `summary`, `matched_items`, `unmatched_items`, and `adjustments` sections.

### Matching Rule

```json
{
  "id": "uuid",
  "bank_account": "uuid | null",
  "name": "string",
  "priority": "integer (1-100)",
  "amount_tolerance": "decimal",
  "date_range_days": "integer (0-365)",
  "match_reference": "boolean",
  "description_pattern": "string (regex, optional)",
  "pattern_flags": "string (default: i)",
  "is_active": "boolean"
}
```

---

## Workflow

1. **Create bank account** → link to GL account
2. **Import statement** → upload CSV/OFX file via `import_statement`
3. **Start reconciliation** → creates in-progress session with statement
4. **Auto-match** → engine applies matching rules by priority
5. **Review suggestions** → get unmatched lines + suggestions
6. **Manual match** → match remaining items manually
7. **Create adjustments** → enter bank charges, interest, etc.
8. **Complete** → finalize when difference is zero (or force)

---

## Error Codes

| Status | Meaning                                                                |
| ------ | ---------------------------------------------------------------------- |
| 400    | Validation error (missing fields, invalid data)                        |
| 404    | Resource not found                                                     |
| 409    | Status conflict (e.g., completing an already-completed reconciliation) |
