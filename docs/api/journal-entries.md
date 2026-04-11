# Journal Entries API Documentation

> **Module:** Journal Entries (SP09)  
> **Base URL:** `/api/v1/accounting/`  
> **Authentication:** JWT Bearer Token (required for all endpoints)  
> **Content-Type:** `application/json`

---

## Overview

The Journal Entries API provides endpoints for managing double-entry journal entries, including full CRUD operations, workflow actions (post, void, approve), nested line items, and filtering/search capabilities.

### Key Features

- Full CRUD for journal entries with nested line items
- Automatic entry numbering (`JE-YYYY-NNNNN`)
- Workflow actions: post, void, approve
- Balanced entry validation (total debits = total credits)
- Minimum 2 lines per entry
- Automatic cached totals
- Filtering by status, type, and source
- Search by entry number, reference, and description

---

## Endpoints

| Method | Path                     | Description                            |
| ------ | ------------------------ | -------------------------------------- |
| GET    | `/entries/`              | List all journal entries               |
| POST   | `/entries/`              | Create a new journal entry             |
| GET    | `/entries/{id}/`         | Retrieve a journal entry               |
| PUT    | `/entries/{id}/`         | Full update of a journal entry         |
| PATCH  | `/entries/{id}/`         | Partial update of a journal entry      |
| DELETE | `/entries/{id}/`         | Delete a draft journal entry           |
| POST   | `/entries/{id}/post/`    | Post a draft or approved entry         |
| POST   | `/entries/{id}/void/`    | Void a posted entry (creates reversal) |
| POST   | `/entries/{id}/approve/` | Approve a pending entry                |

---

## Authentication

All endpoints require a valid JWT Bearer token in the `Authorization` header.

```
Authorization: Bearer <access_token>
```

---

## Entry Status Workflow

```
DRAFT → PENDING_APPROVAL → APPROVED → POSTED → VOID
```

- **DRAFT**: Entry is editable. Can be posted directly or submitted for approval.
- **PENDING_APPROVAL**: Awaiting approval. Not editable.
- **APPROVED**: Approved entry. Can be posted.
- **POSTED**: Entry is finalized and affects account balances. Cannot be edited.
- **VOID**: Entry has been voided via a reversal entry. Cannot be modified.

Only **DRAFT** entries can be edited or deleted.

---

## Enumerations

### Entry Types

| Value       | Label           | Description                                  |
| ----------- | --------------- | -------------------------------------------- |
| `MANUAL`    | Manual Entry    | User-created entries                         |
| `AUTO`      | Auto-Generated  | System-generated from business transactions  |
| `ADJUSTING` | Adjusting Entry | Period-end adjustments (accruals, deferrals) |
| `REVERSING` | Reversing Entry | Auto-generated to reverse adjusting entries  |

### Entry Statuses

| Value              | Label            |
| ------------------ | ---------------- |
| `DRAFT`            | Draft            |
| `PENDING_APPROVAL` | Pending Approval |
| `APPROVED`         | Approved         |
| `POSTED`           | Posted           |
| `VOID`             | Void             |

### Entry Sources

| Value        | Label        | Description            |
| ------------ | ------------ | ---------------------- |
| `SALES`      | Sales        | Sales transactions     |
| `PURCHASE`   | Purchase     | Purchase transactions  |
| `PAYROLL`    | Payroll      | Payroll processing     |
| `INVENTORY`  | Inventory    | Inventory adjustments  |
| `BANKING`    | Banking      | Banking transactions   |
| `MANUAL`     | Manual Entry | Manual journal entries |
| `ADJUSTMENT` | Adjustment   | Period-end adjustments |

---

## Journal Entries

### List Entries

```http
GET /api/v1/accounting/entries/
```

#### Query Parameters

| Parameter      | Type    | Description                                                                 |
| -------------- | ------- | --------------------------------------------------------------------------- |
| `entry_status` | string  | Filter by status: `DRAFT`, `PENDING_APPROVAL`, `APPROVED`, `POSTED`, `VOID` |
| `entry_type`   | string  | Filter by type: `MANUAL`, `AUTO`, `ADJUSTING`, `REVERSING`                  |
| `entry_source` | string  | Filter by source: `SALES`, `PURCHASE`, `PAYROLL`, etc.                      |
| `search`       | string  | Search in entry_number, reference, description                              |
| `ordering`     | string  | Order by: `entry_date`, `entry_number`, `total_debit` (prefix `-` for desc) |
| `page`         | integer | Page number for pagination                                                  |

#### Example Response

```json
{
  "count": 15,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "entry_number": "JE-2025-00001",
      "entry_date": "2025-01-15",
      "entry_type": "MANUAL",
      "entry_status": "DRAFT",
      "entry_source": "MANUAL",
      "reference": "INV-2025-001",
      "description": "Record sales invoice",
      "total_debit": "15000.00",
      "total_credit": "15000.00",
      "lines": [
        {
          "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
          "account": "c3d4e5f6-a7b8-9012-cdef-123456789012",
          "account_code": "1100",
          "account_name": "Accounts Receivable",
          "debit_amount": "15000.00",
          "credit_amount": "0.00",
          "description": "Customer receivable",
          "sort_order": 0
        },
        {
          "id": "d4e5f6a7-b8c9-0123-defa-234567890123",
          "account": "e5f6a7b8-c9d0-1234-efab-345678901234",
          "account_code": "4100",
          "account_name": "Sales Revenue",
          "debit_amount": "0.00",
          "credit_amount": "15000.00",
          "description": "Sales revenue",
          "sort_order": 1
        }
      ],
      "created_by": "f6a7b8c9-d0e1-2345-fabc-456789012345",
      "created_by_email": "accountant@example.com",
      "posted_by": null,
      "posted_by_email": null,
      "posted_at": null,
      "reversal_of": null,
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

---

### Create Entry

```http
POST /api/v1/accounting/entries/
```

Creates a new journal entry in `DRAFT` status with nested line items.

#### Request Body

| Field          | Type   | Required | Description                            |
| -------------- | ------ | -------- | -------------------------------------- |
| `entry_date`   | date   | Yes      | Date of the journal entry (YYYY-MM-DD) |
| `entry_type`   | string | Yes      | Entry type enum value                  |
| `entry_source` | string | Yes      | Entry source enum value                |
| `reference`    | string | No       | External reference number              |
| `description`  | string | No       | Description of the entry               |
| `reversal_of`  | uuid   | No       | ID of the entry this reverses          |
| `lines`        | array  | Yes      | Array of line items (minimum 2)        |

#### Line Item Fields

| Field           | Type    | Required | Description                              |
| --------------- | ------- | -------- | ---------------------------------------- |
| `account`       | uuid    | Yes      | Account ID to debit or credit            |
| `debit_amount`  | decimal | Yes      | Debit amount (0.00 if credit line)       |
| `credit_amount` | decimal | Yes      | Credit amount (0.00 if debit line)       |
| `description`   | string  | No       | Line-level description                   |
| `sort_order`    | integer | No       | Display order (auto-assigned if omitted) |

#### Example Request

```json
{
  "entry_date": "2025-01-15",
  "entry_type": "MANUAL",
  "entry_source": "MANUAL",
  "reference": "INV-2025-001",
  "description": "Record sales invoice",
  "lines": [
    {
      "account": "c3d4e5f6-a7b8-9012-cdef-123456789012",
      "debit_amount": "15000.00",
      "credit_amount": "0.00",
      "description": "Customer receivable"
    },
    {
      "account": "e5f6a7b8-c9d0-1234-efab-345678901234",
      "debit_amount": "0.00",
      "credit_amount": "15000.00",
      "description": "Sales revenue"
    }
  ]
}
```

#### Example Response (201 Created)

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "entry_number": "JE-2025-00001",
  "entry_date": "2025-01-15",
  "entry_type": "MANUAL",
  "entry_status": "DRAFT",
  "entry_source": "MANUAL",
  "reference": "INV-2025-001",
  "description": "Record sales invoice",
  "total_debit": "15000.00",
  "total_credit": "15000.00",
  "lines": [
    {
      "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "account": "c3d4e5f6-a7b8-9012-cdef-123456789012",
      "account_code": "1100",
      "account_name": "Accounts Receivable",
      "debit_amount": "15000.00",
      "credit_amount": "0.00",
      "description": "Customer receivable",
      "sort_order": 0
    },
    {
      "id": "d4e5f6a7-b8c9-0123-defa-234567890123",
      "account": "e5f6a7b8-c9d0-1234-efab-345678901234",
      "account_code": "4100",
      "account_name": "Sales Revenue",
      "debit_amount": "0.00",
      "credit_amount": "15000.00",
      "description": "Sales revenue",
      "sort_order": 1
    }
  ],
  "created_by": "f6a7b8c9-d0e1-2345-fabc-456789012345",
  "created_by_email": "accountant@example.com",
  "posted_by": null,
  "posted_by_email": null,
  "posted_at": null,
  "reversal_of": null,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

---

### Retrieve Entry

```http
GET /api/v1/accounting/entries/{id}/
```

Returns a single journal entry with all nested lines.

---

### Update Entry

```http
PUT /api/v1/accounting/entries/{id}/
PATCH /api/v1/accounting/entries/{id}/
```

Update an existing journal entry. Only **DRAFT** entries can be updated.

When `lines` are provided, all existing lines are replaced with the new set (full replacement).

#### Error Response (non-draft entry)

```json
{
  "detail": "Entry JE-2025-00001 is not editable."
}
```

---

### Delete Entry

```http
DELETE /api/v1/accounting/entries/{id}/
```

Delete a journal entry. Only **DRAFT** entries can be deleted.

**Response:** `204 No Content`

---

## Workflow Actions

### Post Entry

```http
POST /api/v1/accounting/entries/{id}/post/
```

Posts a `DRAFT` or `APPROVED` entry, changing its status to `POSTED`. The posting user and timestamp are recorded.

#### Preconditions

- Entry must be in `DRAFT` or `APPROVED` status.
- Entry must be balanced (total_debit == total_credit).
- Entry must have at least 2 lines.
- All line accounts must be active.

#### Request Body

None required.

#### Success Response (200 OK)

Returns the updated entry with `entry_status: "POSTED"`.

#### Error Response (400 Bad Request)

```json
{
  "detail": "Entry JE-2025-00001 cannot be posted: status is VOID."
}
```

---

### Void Entry

```http
POST /api/v1/accounting/entries/{id}/void/
```

Voids a `POSTED` entry by creating an automatic reversal entry. The original entry status changes to `VOID`.

#### Request Body

| Field    | Type   | Required | Description                  |
| -------- | ------ | -------- | ---------------------------- |
| `reason` | string | No       | Reason for voiding the entry |

#### Example Request

```json
{
  "reason": "Duplicate entry, voiding for correction"
}
```

#### Success Response (200 OK)

```json
{
  "voided_entry": {
    "id": "a1b2c3d4-...",
    "entry_number": "JE-2025-00001",
    "entry_status": "VOID",
    "...": "..."
  },
  "reversal_entry": {
    "id": "f6a7b8c9-...",
    "entry_number": "JE-2025-00002",
    "entry_type": "REVERSING",
    "entry_status": "POSTED",
    "reversal_of": "a1b2c3d4-...",
    "description": "Reversal of JE-2025-00001",
    "...": "..."
  }
}
```

#### Error Response (400 Bad Request)

```json
{
  "detail": "Entry JE-2025-00001 cannot be voided: status is DRAFT."
}
```

---

### Approve Entry

```http
POST /api/v1/accounting/entries/{id}/approve/
```

Approves a `PENDING_APPROVAL` entry, changing its status to `APPROVED`.

#### Preconditions

- Entry must be in `PENDING_APPROVAL` status.
- Approver must be different from the entry creator (segregation of duties).

#### Request Body

None required.

#### Success Response (200 OK)

Returns the updated entry with `entry_status: "APPROVED"`.

#### Error Response (400 Bad Request)

```json
{
  "detail": "Cannot approve own entry (segregation of duties)."
}
```

---

## Validation Rules

### Entry-Level Validation

| Rule             | Description                                           |
| ---------------- | ----------------------------------------------------- |
| Balanced totals  | `total_debit` must equal `total_credit`               |
| Minimum lines    | At least 2 line items required                        |
| Non-zero amounts | Total debit and credit must be greater than zero      |
| Active period    | Entry date must fall within an open accounting period |
| Active accounts  | All line accounts must have `ACTIVE` status           |

### Line-Level Validation

| Rule                 | Description                                                      |
| -------------------- | ---------------------------------------------------------------- |
| Single-sided amounts | A line should have either a debit or a credit, not both non-zero |
| Non-negative amounts | Debit and credit amounts must be >= 0                            |
| Valid account        | Account UUID must reference an existing active account           |

---

## Error Responses

### Standard Error Format

```json
{
  "detail": "Error description message."
}
```

### Common HTTP Status Codes

| Code | Description                                          |
| ---- | ---------------------------------------------------- |
| 200  | Success                                              |
| 201  | Created (new entry)                                  |
| 204  | No Content (successful delete)                       |
| 400  | Bad Request (validation error or workflow violation) |
| 401  | Unauthorized (missing or invalid token)              |
| 403  | Forbidden (insufficient permissions)                 |
| 404  | Not Found (entry does not exist)                     |

### Validation Error Response

```json
{
  "entry_date": ["This field is required."],
  "lines": [
    {
      "account": ["This field is required."]
    }
  ]
}
```

---

## Related Services

The API internally uses the following services for workflow operations:

| Service                 | Purpose                                          |
| ----------------------- | ------------------------------------------------ |
| `JournalEntryService`   | Create, post, and void entries atomically        |
| `ApprovalService`       | Approval workflow with segregation of duties     |
| `TemplateService`       | Create entries from templates                    |
| `RecurringService`      | Process recurring entry schedules (Celery tasks) |
| `AdjustingEntryService` | Create accrual and deferral entries              |
| `ReversingEntryService` | Create reversal entries                          |
| `AutoEntryGenerator`    | Generate entries from business events            |

---

## Usage Examples

### Complete Workflow: Create → Post → Void

```bash
# 1. Create a draft entry
curl -X POST /api/v1/accounting/entries/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "entry_date": "2025-01-15",
    "entry_type": "MANUAL",
    "entry_source": "MANUAL",
    "description": "Monthly rent payment",
    "lines": [
      {"account": "<expense-account-id>", "debit_amount": "50000.00", "credit_amount": "0.00"},
      {"account": "<bank-account-id>", "debit_amount": "0.00", "credit_amount": "50000.00"}
    ]
  }'

# 2. Post the entry
curl -X POST /api/v1/accounting/entries/<entry-id>/post/ \
  -H "Authorization: Bearer <token>"

# 3. Void the entry (if needed)
curl -X POST /api/v1/accounting/entries/<entry-id>/void/ \
  -H "Authorization: Bearer <token>" \
  -d '{"reason": "Incorrect amount, creating correction"}'
```

### Approval Workflow

```bash
# 1. Create entry (creates as DRAFT)
# 2. Request approval (entry status changes to PENDING_APPROVAL via service)
# 3. Different user approves
curl -X POST /api/v1/accounting/entries/<entry-id>/approve/ \
  -H "Authorization: Bearer <approver-token>"

# 4. Post the approved entry
curl -X POST /api/v1/accounting/entries/<entry-id>/post/ \
  -H "Authorization: Bearer <token>"
```
