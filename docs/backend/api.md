# Backend API

> API architecture, conventions, and endpoint reference for LankaCommerce Cloud.

**Navigation:** [Docs Index](../index.md) · [Backend README](../../backend/README.md) · [Apps](apps.md) · [Models](models.md)

---

## Overview

The LankaCommerce Cloud backend exposes a RESTful API built with **Django REST Framework (DRF)**. The API follows a versioned, resource-oriented design with consistent authentication, permissions, and response formats across all endpoints.

---

## API Architecture

### Layers

The API is structured in layers, each with a clear responsibility:

| Layer                | Location                                                       | Responsibility                                  |
| -------------------- | -------------------------------------------------------------- | ----------------------------------------------- |
| **URL Routing**      | `config/urls.py`, `apps/<app>/urls.py`                         | Maps URLs to views, version prefixing           |
| **Views / ViewSets** | `apps/<app>/views.py` or `apps/<app>/api/views.py`             | Request handling, business logic orchestration  |
| **Serializers**      | `apps/<app>/serializers.py` or `apps/<app>/api/serializers.py` | Data validation, transformation, and formatting |
| **Permissions**      | `apps/<app>/permissions.py`                                    | Access control and authorization checks         |
| **Filters**          | `apps/<app>/filters.py`                                        | Query parameter filtering and search            |
| **Models**           | `apps/<app>/models.py`                                         | Data persistence and business rules             |

### Request Flow

1. Client sends HTTP request to a versioned endpoint
2. URL router dispatches to the correct viewset or view
3. Authentication middleware validates the JWT token
4. Permission classes check user authorization
5. Serializer validates and deserializes the request body
6. View executes business logic and interacts with models
7. Serializer formats the response data
8. View returns the HTTP response

---

## API Versioning

All endpoints are prefixed with a version number:

| Version | Prefix     | Status           |
| ------- | ---------- | ---------------- |
| v1      | `/api/v1/` | Active (current) |

Version is included in the URL path. When breaking changes are needed, a new version prefix will be introduced while maintaining backward compatibility on the existing version.

---

## Authentication

The API uses **JWT (JSON Web Token)** authentication via `djangorestframework-simplejwt`.

| Endpoint                      | Method | Description                      |
| ----------------------------- | ------ | -------------------------------- |
| `/api/v1/auth/token/`         | POST   | Obtain access and refresh tokens |
| `/api/v1/auth/token/refresh/` | POST   | Refresh an expired access token  |
| `/api/v1/auth/token/verify/`  | POST   | Verify a token is valid          |

**Token usage:** Include the access token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

**Token lifetime defaults:**

- Access token: 30 minutes
- Refresh token: 7 days

### Public Endpoints

The following endpoints do not require authentication:

| Endpoint                     | Purpose                                            |
| ---------------------------- | -------------------------------------------------- |
| `/health/`                   | Application health check (database, Redis, Celery) |
| `/api/v1/auth/token/`        | Token acquisition                                  |
| `/api/v1/auth/register/`     | New user registration _(planned)_                  |
| `/api/v1/webstore/products/` | Public product catalog _(planned)_                 |

---

## Permissions

DRF permission classes control access at the view level:

| Permission        | Usage                                                   |
| ----------------- | ------------------------------------------------------- |
| `IsAuthenticated` | Default — requires a valid JWT token                    |
| `IsAdminUser`     | Restricts to staff/admin users                          |
| `IsTenantAdmin`   | Restricts to the admin of the current tenant _(custom)_ |
| `IsTenantMember`  | Restricts to members of the current tenant _(custom)_   |
| `AllowAny`        | Public access (health check, registration)              |

Permissions are set per viewset or per action using `permission_classes` and `get_permissions()`.

---

## Serializers

Serializers handle data validation and transformation between JSON and Django model instances.

### Conventions

| Convention                               | Example                                                 |
| ---------------------------------------- | ------------------------------------------------------- |
| Name matches model + "Serializer" suffix | `ProductSerializer`, `SalesOrderSerializer`             |
| List serializers use minimal fields      | `ProductListSerializer` (id, name, price)               |
| Detail serializers include nested data   | `ProductDetailSerializer` (full fields + category)      |
| Create/Update serializers validate input | `ProductCreateSerializer` (writable fields only)        |
| Read-only fields are explicit            | `read_only_fields = ["id", "created_at", "updated_at"]` |

### Nested Serialization

- Use nested serializers for read operations (expand related objects)
- Use primary key fields for write operations (accept IDs)
- Limit nesting depth to 2 levels maximum

---

## Response Format

All API responses follow a consistent structure:

### Success Response

```json
{
  "count": 25,
  "next": "http://localhost:8000/api/v1/products/?page=2",
  "previous": null,
  "results": [{ "id": "...", "name": "..." }]
}
```

### Error Response

```json
{
  "detail": "Authentication credentials were not provided.",
  "code": "not_authenticated"
}
```

### Validation Error

```json
{
  "name": ["This field is required."],
  "price": ["Ensure this value is greater than 0."]
}
```

---

## Pagination

Default pagination uses **PageNumberPagination**:

| Setting              | Value       |
| -------------------- | ----------- |
| Page size            | 20          |
| Max page size        | 100         |
| Page query parameter | `page`      |
| Size query parameter | `page_size` |

Configured globally in `config/settings/base.py` under `REST_FRAMEWORK`.

---

## Filtering and Search

Filtering is powered by `django-filters`:

| Feature         | Query Parameter   | Example                 |
| --------------- | ----------------- | ----------------------- |
| Field filtering | `?field=value`    | `?status=active`        |
| Search          | `?search=term`    | `?search=laptop`        |
| Ordering        | `?ordering=field` | `?ordering=-created_at` |

Each viewset declares its filterable fields in `filterset_fields` and searchable fields in `search_fields`.

---

## Interactive API Documentation

When the development server is running, interactive documentation is available:

| Tool           | URL                                 | Description                   |
| -------------- | ----------------------------------- | ----------------------------- |
| Swagger UI     | `http://localhost:8000/api/docs/`   | Interactive API explorer      |
| ReDoc          | `http://localhost:8000/api/redoc/`  | Clean read-only documentation |
| OpenAPI Schema | `http://localhost:8000/api/schema/` | Raw OpenAPI 3.0 JSON/YAML     |

Documentation is auto-generated by **drf-spectacular** from the DRF viewsets and serializers. All three endpoints are publicly accessible (no authentication required) to allow developers to explore the API without a token.

The schema, Swagger UI, and ReDoc routes are configured in `config/urls.py` and the drf-spectacular settings in `config/settings/base.py` under `SPECTACULAR_SETTINGS`.

> For the full API reference, see the [API Documentation](../api/overview.md) — including [authentication](../api/authentication.md), [errors](../api/errors.md), [pagination](../api/pagination.md), [rate limiting](../api/rate-limiting.md), and [versioning](../api/versioning.md).

---

## Endpoint Reference by Module

| Module     | Base Path             | Key Endpoints                  |
| ---------- | --------------------- | ------------------------------ |
| Auth       | `/api/v1/auth/`       | token, refresh, register       |
| Users      | `/api/v1/users/`      | profile, preferences           |
| Products   | `/api/v1/products/`   | CRUD, categories, search       |
| Inventory  | `/api/v1/inventory/`  | stock, warehouses, movements   |
| Sales      | `/api/v1/sales/`      | orders, payments, receipts     |
| Customers  | `/api/v1/customers/`  | profiles, groups, loyalty      |
| Vendors    | `/api/v1/vendors/`    | profiles, purchase orders      |
| HR         | `/api/v1/hr/`         | employees, attendance, payroll |
| Accounting | `/api/v1/accounting/` | accounts, invoices, journals   |
| Reports    | `/api/v1/reports/`    | analytics, exports             |
| Webstore   | `/api/v1/webstore/`   | catalog, cart, checkout        |
| Tenants    | `/api/v1/tenants/`    | registration, settings         |

> Endpoint details will be documented as each module is implemented.

---

## Related Documentation

- [Backend README](../../backend/README.md) — Setup and development guide
- [Apps Documentation](apps.md) — App responsibilities and structure
- [Models Documentation](models.md) — Base models and conventions
- [API Reference](../api/) — Full endpoint documentation _(planned)_
- [Docs Index](../index.md) — Full documentation hub
