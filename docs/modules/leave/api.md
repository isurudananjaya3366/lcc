# Leave Management API Reference

## Base URL

All endpoints are tenant-scoped and require authentication.

```
/api/leave/
```

## Endpoints

### Leave Types

| Method | Endpoint             | Description                 |
| ------ | -------------------- | --------------------------- |
| GET    | `/leave-types/`      | List all leave types        |
| POST   | `/leave-types/`      | Create a new leave type     |
| GET    | `/leave-types/{id}/` | Retrieve leave type details |
| PUT    | `/leave-types/{id}/` | Update a leave type         |
| PATCH  | `/leave-types/{id}/` | Partial update a leave type |
| DELETE | `/leave-types/{id}/` | Soft-delete a leave type    |

**Filters**: `category`, `is_active`, `is_paid`, `search` (name/code)

**Computed Fields**: `usage_count`, `is_active_display`

### Leave Balances

| Method | Endpoint             | Description                  |
| ------ | -------------------- | ---------------------------- |
| GET    | `/balances/`         | List balances (filterable)   |
| GET    | `/balances/{id}/`    | Retrieve balance details     |
| GET    | `/balances/my/`      | Current user's balances      |
| GET    | `/balances/summary/` | Balance summary for employee |

**Filters**: `employee`, `leave_type`, `year`, `is_active`

**Computed Fields**: `available_days`, `days_until_expiry`

### Leave Requests

| Method | Endpoint                  | Description                |
| ------ | ------------------------- | -------------------------- |
| GET    | `/requests/`              | List leave requests        |
| POST   | `/requests/`              | Create a draft request     |
| GET    | `/requests/{id}/`         | Retrieve request details   |
| PUT    | `/requests/{id}/`         | Update a draft request     |
| DELETE | `/requests/{id}/`         | Soft-delete a request      |
| POST   | `/requests/{id}/submit/`  | Submit for approval        |
| POST   | `/requests/{id}/approve/` | Approve a pending request  |
| POST   | `/requests/{id}/reject/`  | Reject a pending request   |
| POST   | `/requests/{id}/cancel/`  | Cancel a pending request   |
| POST   | `/requests/{id}/recall/`  | Recall an approved request |

**Filters**: `employee`, `leave_type`, `status`, `start_date`, `end_date`, `search`

**Permission Fields**: `can_approve`, `can_reject`, `can_recall`

### Holidays

| Method | Endpoint          | Description              |
| ------ | ----------------- | ------------------------ |
| GET    | `/holidays/`      | List holidays            |
| POST   | `/holidays/`      | Create a holiday         |
| GET    | `/holidays/{id}/` | Retrieve holiday details |
| PUT    | `/holidays/{id}/` | Update a holiday         |
| DELETE | `/holidays/{id}/` | Soft-delete a holiday    |

**Filters**: `holiday_type`, `applies_to`, `date_from`, `date_to`, `is_active`

## Authentication

All endpoints require JWT authentication via the `Authorization: Bearer <token>` header. Tenant resolution is handled via the `Host` header (django-tenants).

## Error Responses

Standard DRF error format:

```json
{
  "detail": "Error description.",
  "code": "error_code"
}
```

For validation errors:

```json
{
  "field_name": ["Error message 1", "Error message 2"]
}
```
