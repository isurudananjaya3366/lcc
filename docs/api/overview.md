# API Overview

> Architecture, entry points, and getting started with the LankaCommerce Cloud REST API.

**Navigation:** [Docs Index](../index.md) · [Backend API Guide](../backend/api.md) · [Authentication](authentication.md) · [Errors](errors.md)

---

## Introduction

The LankaCommerce Cloud API is a RESTful JSON API built with **Django REST Framework** and documented via **drf-spectacular** (OpenAPI 3.0). It powers both the ERP dashboard and the customer-facing webstore.

---

## Base URL

All API endpoints are served under a versioned prefix:

| Environment       | Base URL                               |
| ----------------- | -------------------------------------- |
| Local Development | `http://localhost:8000/api/v1/`        |
| Production        | `https://api.lankacommerce.lk/api/v1/` |

---

## Interactive Documentation

| Tool           | URL            | Description                                      |
| -------------- | -------------- | ------------------------------------------------ |
| Swagger UI     | `/api/docs/`   | Interactive API explorer — try requests directly |
| ReDoc          | `/api/redoc/`  | Clean, read-only API reference                   |
| OpenAPI Schema | `/api/schema/` | Download the raw OpenAPI 3.0 schema (YAML)       |

These endpoints are publicly accessible and do not require authentication.

---

## Request Format

All requests must use **JSON** for request bodies:

| Header          | Value                                                 |
| --------------- | ----------------------------------------------------- |
| `Content-Type`  | `application/json`                                    |
| `Accept`        | `application/json`                                    |
| `Authorization` | `Bearer <access_token>` (for authenticated endpoints) |

---

## Response Format

### Success Response

| Field        | Type       | Description         |
| ------------ | ---------- | ------------------- |
| `id`         | string/int | Resource identifier |
| `...`        | various    | Resource fields     |
| `created_at` | string     | ISO 8601 timestamp  |
| `updated_at` | string     | ISO 8601 timestamp  |

### List Response (Paginated)

| Field      | Type        | Description               |
| ---------- | ----------- | ------------------------- |
| `count`    | integer     | Total number of results   |
| `next`     | string/null | URL for the next page     |
| `previous` | string/null | URL for the previous page |
| `results`  | array       | Array of resource objects |

### Error Response

| Field    | Type   | Description                  |
| -------- | ------ | ---------------------------- |
| `detail` | string | Human-readable error message |
| `code`   | string | Machine-readable error code  |

> See [Errors Documentation](errors.md) for the full error format reference.

---

## API Modules

| Module     | Base Path             | Status            | Description                              |
| ---------- | --------------------- | ----------------- | ---------------------------------------- |
| Auth       | `/api/v1/auth/`       | Planned (Phase 3) | User authentication and token management |
| Tenants    | `/api/v1/tenants/`    | Planned (Phase 2) | Tenant registration and management       |
| Users      | `/api/v1/users/`      | Planned (Phase 3) | User profiles and preferences            |
| Products   | `/api/v1/products/`   | Planned (Phase 4) | Product catalog and categories           |
| Inventory  | `/api/v1/inventory/`  | Planned (Phase 4) | Stock levels and warehouse management    |
| Vendors    | `/api/v1/vendors/`    | Planned (Phase 4) | Supplier management                      |
| Sales      | `/api/v1/sales/`      | Planned (Phase 5) | Orders, invoicing, and POS               |
| Customers  | `/api/v1/customers/`  | Planned (Phase 5) | Customer CRM                             |
| HR         | `/api/v1/hr/`         | Planned (Phase 6) | Human resources                          |
| Accounting | `/api/v1/accounting/` | Planned (Phase 6) | Financial transactions                   |
| Reports    | `/api/v1/reports/`    | Planned (Phase 6) | Analytics and reporting                  |
| Webstore   | `/api/v1/store/`      | Planned (Phase 8) | Public storefront API                    |
| Health     | `/health/`            | Active            | Health check endpoint                    |

---

## Key Concepts

- **Authentication:** JWT-based with access and refresh tokens — see [Authentication](authentication.md)
- **Pagination:** Page-number pagination with configurable page size — see [Pagination](pagination.md)
- **Errors:** Consistent error format with HTTP status codes — see [Errors](errors.md)
- **Rate Limiting:** Throttle limits for anonymous and authenticated users — see [Rate Limiting](rate-limiting.md)
- **Versioning:** URL-based versioning with deprecation policy — see [Versioning](versioning.md)

---

## Related Documentation

- [Backend API Guide](../backend/api.md) — Detailed API architecture and conventions
- [Backend README](../../backend/README.md) — Backend setup and development guide
- [Docs Index](../index.md) — Full documentation hub
