# Accounting API Documentation

> **Module:** Chart of Accounts  
> **Base URL:** `/api/v1/accounting/`  
> **Authentication:** JWT Bearer Token (required for all endpoints)  
> **Content-Type:** `application/json`

---

## Overview

The Accounting API provides endpoints for managing the Chart of Accounts (COA), including CRUD operations on accounts, hierarchical tree views, account type configuration, and COA initialization from templates.

### Key Features

- Full CRUD for accounts with automatic code validation
- Hierarchical tree structure via MPTT
- Filtering, searching, and ordering
- COA initialization from default or custom templates
- Soft-delete (archive) instead of hard-delete
- System account protection

---

## Endpoints

| Method | Path                    | Description                       |
| ------ | ----------------------- | --------------------------------- |
| GET    | `/accounts/`            | List all accounts                 |
| POST   | `/accounts/`            | Create a new account              |
| GET    | `/accounts/{id}/`       | Retrieve account details          |
| PUT    | `/accounts/{id}/`       | Full update of an account         |
| PATCH  | `/accounts/{id}/`       | Partial update of an account      |
| DELETE | `/accounts/{id}/`       | Archive an account (soft-delete)  |
| GET    | `/accounts/tree/`       | Get hierarchical tree of accounts |
| GET    | `/accounts/types/`      | List account type configurations  |
| POST   | `/accounts/initialize/` | Initialize Chart of Accounts      |

---

## Authentication

All endpoints require a valid JWT Bearer token in the `Authorization` header.

```
Authorization: Bearer <access_token>
```

### Obtaining a Token

```http
POST /api/auth/token/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your_password"
}
```

**Response:**

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## Accounts

### List Accounts

```http
GET /api/v1/accounting/accounts/
```

#### Query Parameters

| Parameter        | Type    | Description                                                                  |
| ---------------- | ------- | ---------------------------------------------------------------------------- |
| `account_type`   | string  | Filter by type: `asset`, `liability`, `equity`, `revenue`, `expense`         |
| `category`       | string  | Filter by category: `CURRENT`, `NON_CURRENT`, `OPERATING`, etc.              |
| `status`         | string  | Filter by status: `ACTIVE`, `INACTIVE`, `ARCHIVED`                           |
| `parent`         | uuid    | Filter by parent account ID                                                  |
| `parent__isnull` | boolean | `true` for root accounts only                                                |
| `is_active`      | boolean | Filter active/inactive accounts                                              |
| `is_header`      | boolean | Filter header accounts                                                       |
| `is_system`      | boolean | Filter system accounts                                                       |
| `search`         | string  | Search in code, name, description                                            |
| `ordering`       | string  | Order by: `code`, `name`, `account_type`, `created_on` (prefix `-` for desc) |
| `page`           | integer | Page number for pagination                                                   |

#### Example Response

```json
{
  "count": 69,
  "next": "http://example.com/api/v1/accounting/accounts/?page=2",
  "previous": null,
  "results": [
    {
      "id": "a6587802-1234-5678-9abc-def012345678",
      "code": "1000",
      "name": "Assets",
      "account_type": "asset",
      "account_type_config": "a1b2c3d4-...",
      "category": "OTHER",
      "status": "ACTIVE",
      "parent": null,
      "description": "All asset accounts",
      "is_active": true,
      "is_system": true,
      "is_header": true,
      "currency": "LKR",
      "opening_balance": "0.00",
      "current_balance": "0.00",
      "children_count": 5,
      "created_on": "2025-07-18T10:00:00Z",
      "updated_on": "2025-07-18T10:00:00Z"
    }
  ]
}
```

---

### Create Account

```http
POST /api/v1/accounting/accounts/
Content-Type: application/json
```

#### Request Body

| Field          | Type    | Required | Description                                                  |
| -------------- | ------- | -------- | ------------------------------------------------------------ |
| `code`         | string  | Yes      | Numeric string, min 4 digits, unique per tenant              |
| `name`         | string  | Yes      | Account name (max 200 chars)                                 |
| `account_type` | string  | Yes      | One of: `asset`, `liability`, `equity`, `revenue`, `expense` |
| `category`     | string  | No       | Account category (default: `OTHER`)                          |
| `parent`       | uuid    | No       | Parent account ID for hierarchy                              |
| `description`  | string  | No       | Account description                                          |
| `is_header`    | boolean | No       | Header/group account flag (default: `false`)                 |
| `is_system`    | boolean | No       | System-protected account flag (default: `false`)             |

#### Example

```json
{
  "code": "1100",
  "name": "Current Assets",
  "account_type": "asset",
  "category": "CURRENT",
  "parent": "a6587802-1234-5678-9abc-def012345678",
  "description": "Assets convertible to cash within one year",
  "is_header": true
}
```

#### Validation Rules

- `code` must be numeric (digits only), at least 4 characters
- `code` must be unique within the tenant
- `code` must fall within the valid range for the specified `account_type`:
  - Asset: 1000–1999
  - Liability: 2000–2999
  - Equity: 3000–3999
  - Revenue: 4000–4999
  - Expense: 5000–5999

**Response:** `201 Created`

---

### Retrieve Account

```http
GET /api/v1/accounting/accounts/{id}/
```

Returns the full account object as shown in the List response.

**Response:** `200 OK`

---

### Update Account

```http
PUT /api/v1/accounting/accounts/{id}/
```

Full replacement update. All required fields must be provided.

> **Note:** System accounts (`is_system=true`) cannot have their `code` or `account_type` changed.

**Response:** `200 OK`

---

### Partial Update

```http
PATCH /api/v1/accounting/accounts/{id}/
```

Update only the provided fields.

**Response:** `200 OK`

---

### Delete (Archive) Account

```http
DELETE /api/v1/accounting/accounts/{id}/
```

Archives the account instead of permanently deleting it. Sets `status` to `ARCHIVED`.

- System accounts with active journal entries cannot be archived.
- Accounts with child accounts may be blocked from archiving depending on configuration.

**Response:** `204 No Content`

---

## Tree Endpoint

### Get Account Tree

```http
GET /api/v1/accounting/accounts/tree/
```

Returns all root-level accounts with their complete nested children hierarchy using recursive serialization.

#### Example Response

```json
[
  {
    "id": "a6587802-...",
    "code": "1000",
    "name": "Assets",
    "account_type": "asset",
    "children": [
      {
        "id": "b7698913-...",
        "code": "1100",
        "name": "Current Assets",
        "account_type": "asset",
        "children": [
          {
            "id": "c8709024-...",
            "code": "1101",
            "name": "Cash on Hand",
            "account_type": "asset",
            "children": []
          }
        ]
      }
    ]
  }
]
```

**Response:** `200 OK`

---

## Account Types Endpoint

### List Account Type Configurations

```http
GET /api/v1/accounting/accounts/types/
```

Returns all account type configurations ordered by display order.

#### Example Response

```json
[
  {
    "id": 1,
    "type_name": "ASSET",
    "normal_balance": "DEBIT",
    "code_start": 1000,
    "code_end": 1999,
    "display_order": 1,
    "description": "Assets represent resources owned...",
    "code_range_display": "1000 - 1999"
  },
  {
    "id": 2,
    "type_name": "LIABILITY",
    "normal_balance": "CREDIT",
    "code_start": 2000,
    "code_end": 2999,
    "display_order": 2,
    "description": "Liabilities represent obligations...",
    "code_range_display": "2000 - 2999"
  }
]
```

**Response:** `200 OK`

---

## Initialize COA Endpoint

### Initialize Chart of Accounts

```http
POST /api/v1/accounting/accounts/initialize/
Content-Type: application/json
```

Populates the tenant's Chart of Accounts from a template or the default account set.

#### Request Body

| Field         | Type    | Required | Description                                                            |
| ------------- | ------- | -------- | ---------------------------------------------------------------------- |
| `template_id` | uuid    | No       | COA template ID. If omitted, uses default accounts.                    |
| `force`       | boolean | No       | If `true`, deletes existing accounts before loading. Default: `false`. |

#### Example — Default Initialization

```json
{}
```

#### Example — From Template

```json
{
  "template_id": "d9810135-...",
  "force": false
}
```

#### Response Codes

| Status                      | Description                                            |
| --------------------------- | ------------------------------------------------------ |
| `201 Created`               | COA initialized successfully                           |
| `400 Bad Request`           | Invalid template ID or template is inactive            |
| `409 Conflict`              | Accounts already exist (use `force: true` to override) |
| `500 Internal Server Error` | Unexpected initialization failure                      |

#### Success Response

```json
{
  "status": "initialized",
  "accounts_created": 69
}
```

#### Conflict Response (409)

```json
{
  "error": "Tenant already has accounts. Use force=true to reinitialize.",
  "accounts_count": 69
}
```

---

## Error Responses

### Validation Error (400)

```json
{
  "code": ["Account code must be a numeric string of at least 4 digits. Got: 'ABC'."],
  "account_type": ["\"invalid\" is not a valid choice."]
}
```

### Authentication Error (401)

```json
{
  "detail": "Authentication credentials were not provided."
}
```

### Not Found (404)

```json
{
  "detail": "Not found."
}
```

---

## Filtering & Search Examples

### Filter by Account Type

```
GET /api/v1/accounting/accounts/?account_type=asset
```

### Search by Name or Code

```
GET /api/v1/accounting/accounts/?search=cash
```

### Root Accounts Only

```
GET /api/v1/accounting/accounts/?parent__isnull=true
```

### Active Header Accounts

```
GET /api/v1/accounting/accounts/?is_header=true&is_active=true
```

### Order by Name Descending

```
GET /api/v1/accounting/accounts/?ordering=-name
```

---

## Usage Examples

### cURL

```bash
# List all asset accounts
curl -H "Authorization: Bearer $TOKEN" \
  "https://api.example.com/api/v1/accounting/accounts/?account_type=asset"

# Create a new account
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"code": "1100", "name": "Current Assets", "account_type": "asset", "is_header": true}' \
  "https://api.example.com/api/v1/accounting/accounts/"

# Initialize default COA
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}' \
  "https://api.example.com/api/v1/accounting/accounts/initialize/"
```

### Python (requests)

```python
import requests

BASE = "https://api.example.com/api/v1/accounting"
headers = {"Authorization": f"Bearer {token}"}

# List accounts
resp = requests.get(f"{BASE}/accounts/", headers=headers)
accounts = resp.json()

# Get tree
resp = requests.get(f"{BASE}/accounts/tree/", headers=headers)
tree = resp.json()

# Initialize COA
resp = requests.post(
    f"{BASE}/accounts/initialize/",
    headers=headers,
    json={"force": False},
)
```

### JavaScript (fetch)

```javascript
const BASE = "https://api.example.com/api/v1/accounting";
const headers = {
  Authorization: `Bearer ${token}`,
  "Content-Type": "application/json",
};

// List accounts
const resp = await fetch(`${BASE}/accounts/?account_type=asset`, { headers });
const data = await resp.json();

// Create account
const created = await fetch(`${BASE}/accounts/`, {
  method: "POST",
  headers,
  body: JSON.stringify({
    code: "1100",
    name: "Current Assets",
    account_type: "asset",
    is_header: true,
  }),
});
```

---

## Data Models

### Account Fields

| Field                 | Type      | Description                                   |
| --------------------- | --------- | --------------------------------------------- |
| `id`                  | UUID      | Primary key                                   |
| `code`                | string    | Numeric account code (unique per tenant)      |
| `name`                | string    | Account display name                          |
| `account_type`        | string    | Asset, Liability, Equity, Revenue, or Expense |
| `account_type_config` | UUID/null | FK to AccountTypeConfig                       |
| `category`            | string    | Sub-classification (CURRENT, OPERATING, etc.) |
| `status`              | string    | ACTIVE, INACTIVE, or ARCHIVED                 |
| `parent`              | UUID/null | Parent account for hierarchy                  |
| `description`         | string    | Account description                           |
| `is_active`           | boolean   | Active flag                                   |
| `is_system`           | boolean   | System-protected flag                         |
| `is_header`           | boolean   | Header/group account flag                     |
| `currency`            | string    | ISO currency code (default: LKR)              |
| `opening_balance`     | decimal   | Opening balance amount                        |
| `current_balance`     | decimal   | Current calculated balance                    |
| `children_count`      | integer   | Number of direct child accounts (read-only)   |
| `created_on`          | datetime  | Record creation timestamp                     |
| `updated_on`          | datetime  | Last update timestamp                         |

### AccountTypeConfig Fields

| Field                | Type    | Description                                |
| -------------------- | ------- | ------------------------------------------ |
| `id`                 | integer | Primary key                                |
| `type_name`          | string  | ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE |
| `normal_balance`     | string  | DEBIT or CREDIT                            |
| `code_start`         | integer | Start of code range                        |
| `code_end`           | integer | End of code range                          |
| `display_order`      | integer | Display sequence                           |
| `description`        | string  | Type description                           |
| `code_range_display` | string  | Formatted range (read-only)                |

---

## Changelog

| Date       | Version | Changes                                                            |
| ---------- | ------- | ------------------------------------------------------------------ |
| 2025-07-18 | 1.0.0   | Initial API release — Full CRUD, tree, types, initialize endpoints |
