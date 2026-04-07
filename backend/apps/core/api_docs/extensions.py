"""
API Documentation Extensions.

Custom OpenAPI schema preprocessing and enhancements for the
LankaCommerce Cloud API documentation.  Includes multi-tenant header
documentation, authentication flow descriptions, and rate-limit /
versioning metadata injected into the generated OpenAPI 3.0 schema.

The main entry-point consumed by drf-spectacular is
:func:`custom_preprocessing_hook`, registered via::

    SPECTACULAR_SETTINGS["PREPROCESSING_HOOKS"] = [
        "apps.core.api_docs.extensions.custom_preprocessing_hook",
    ]
"""

from __future__ import annotations

import logging
from typing import Any

from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiResponse
from rest_framework import serializers, status

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════
# Preprocessing hooks
# ═══════════════════════════════════════════════════════════════════════


def custom_preprocessing_hook(
    endpoints: list[tuple[str, str, str, Any]],
    **kwargs: Any,
) -> list[tuple[str, str, str, Any]]:
    """
    Custom OpenAPI schema preprocessing hook.

    Called by drf-spectacular during schema generation.  The function
    receives a list of endpoint tuples and returns the (optionally
    modified) list.

    Current enhancements:

    * Filters out internal / non-public endpoints (paths starting with
      ``/api/public/`` are left untouched; everything else is kept as-is
      but eligible for tenant-header injection at the schema level).
    * Provides a single place to add future path-level manipulations.

    Parameters
    ----------
    endpoints:
        List of ``(path, path_regex, method, callback)`` tuples
        discovered by drf-spectacular.

    Returns
    -------
    list
        Filtered / modified endpoint list.
    """
    processed: list[tuple[str, str, str, Any]] = []

    for path, path_regex, method, callback in endpoints:
        # Skip any internal debug endpoints that should not appear in
        # the public API documentation.
        if path.startswith("/api/_internal/"):
            continue

        processed.append((path, path_regex, method, callback))

    logger.debug(
        "custom_preprocessing_hook: %d → %d endpoints",
        len(endpoints),
        len(processed),
    )
    return processed


# ═══════════════════════════════════════════════════════════════════════
# Global OpenAPI parameters
# ═══════════════════════════════════════════════════════════════════════

# X-Tenant-ID header — required on every tenant-scoped request.
TENANT_HEADER_PARAMETER = OpenApiParameter(
    name="X-Tenant-ID",
    type=str,
    location=OpenApiParameter.HEADER,
    required=True,
    description=(
        "Tenant identifier (UUID) for multi-tenant data isolation. "
        "Every request to a tenant-scoped endpoint must include this "
        "header.  Contact support to obtain your tenant ID."
    ),
    examples=[
        OpenApiExample(
            name="Tenant ID",
            value="550e8400-e29b-41d4-a716-446655440000",
        ),
    ],
)


# ═══════════════════════════════════════════════════════════════════════
# Authentication documentation helpers
# ═══════════════════════════════════════════════════════════════════════

AUTHENTICATION_DESCRIPTION = """\

## Authentication

The API uses **JWT (JSON Web Token)** authentication.

### 1. Obtain tokens

```http
POST /api/token/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**Response (200 OK)**

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc…",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc…"
}
```

### 2. Use the access token

Include the access token in the `Authorization` header of every request:

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc…
```

### 3. Token expiry & refresh

| Token   | Lifetime | Purpose                         |
|---------|----------|---------------------------------|
| Access  | 60 min   | Authenticate API requests       |
| Refresh | 24 hours | Obtain a new access token       |

When the access token expires the API responds with **401 Unauthorized**.
Use the refresh token to obtain a new access token without
re-authenticating:

```http
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc…"
}
```

**Response (200 OK)**

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc…"
}
```

When the refresh token itself expires (after 24 hours), the user must
log in again with their credentials.

> **Security note:** store refresh tokens securely and never expose them
> in client-side code or URLs.
"""

# ═══════════════════════════════════════════════════════════════════════
# Error responses documentation
# ═══════════════════════════════════════════════════════════════════════

ERROR_RESPONSES_DESCRIPTION = """\

## Error Responses

All errors follow a consistent JSON envelope:

```json
{
  "error_code": "MACHINE_READABLE_CODE",
  "message": "Human-readable description.",
  "details": {
    "field_name": ["Specific validation error."]
  }
}
```

### Common HTTP status codes

| Code | Meaning              | Typical cause                  |
|------|----------------------|--------------------------------|
| 400  | Bad Request          | Validation errors              |
| 401  | Unauthorized         | Missing or invalid JWT token   |
| 403  | Forbidden            | Insufficient permissions       |
| 404  | Not Found            | Resource does not exist        |
| 429  | Too Many Requests    | Rate limit exceeded            |
| 500  | Internal Server Error| Unexpected server failure      |
"""

# ═══════════════════════════════════════════════════════════════════════
# Pagination documentation
# ═══════════════════════════════════════════════════════════════════════

PAGINATION_DESCRIPTION = """\

## Pagination

List endpoints use **page-number pagination**.

### Query parameters

| Parameter   | Type    | Default | Max | Description            |
|-------------|---------|---------|-----|------------------------|
| `page`      | integer | 1       | —   | Page number            |
| `page_size` | integer | 20      | 100 | Results per page       |

### Response structure

```json
{
  "count": 150,
  "next": "https://api.lankacommerce.com/api/v1/products/?page=3",
  "previous": "https://api.lankacommerce.com/api/v1/products/?page=1",
  "results": [ … ]
}
```

| Field      | Type          | Description                          |
|------------|---------------|--------------------------------------|
| `count`    | integer       | Total number of results              |
| `next`     | string / null | URL of the next page                 |
| `previous` | string / null | URL of the previous page             |
| `results`  | array         | Items for the current page           |
"""

# ═══════════════════════════════════════════════════════════════════════
# Filtering documentation
# ═══════════════════════════════════════════════════════════════════════

FILTERING_DESCRIPTION = """\

## Filtering

List endpoints support field-based filtering via query parameters.

### Syntax

```
GET /api/v1/products/?category=electronics&price__gte=100
```

### Operators

| Suffix         | SQL equivalent | Example                          |
|----------------|---------------|----------------------------------|
| *(none)*       | `=`           | `?status=active`                 |
| `__icontains`  | `ILIKE %…%`  | `?name__icontains=phone`         |
| `__gt`         | `>`           | `?price__gt=100`                 |
| `__gte`        | `>=`          | `?price__gte=100`                |
| `__lt`         | `<`           | `?price__lt=1000`                |
| `__lte`        | `<=`          | `?price__lte=1000`               |
| `__in`         | `IN (…)`      | `?status__in=active,pending`     |

### Search

Most list endpoints also accept a free-text `search` parameter:

```
GET /api/v1/products/?search=wireless+mouse
```
"""

# ═══════════════════════════════════════════════════════════════════════
# Ordering documentation
# ═══════════════════════════════════════════════════════════════════════

ORDERING_DESCRIPTION = """\

## Ordering

Use the `ordering` query parameter to sort results.

| Format                      | Meaning                            |
|-----------------------------|------------------------------------|
| `?ordering=field`           | Ascending                          |
| `?ordering=-field`          | Descending                         |
| `?ordering=field1,-field2`  | Multiple fields                    |

### Example

```
GET /api/v1/products/?category=electronics&ordering=-price
```

Returns electronics sorted by price, highest first.

### Defaults

Most list endpoints default to `-created_at` (newest first) when no
`ordering` parameter is supplied.
"""

# ═══════════════════════════════════════════════════════════════════════
# Rate limiting documentation
# ═══════════════════════════════════════════════════════════════════════

RATE_LIMIT_DESCRIPTION = """\

## Rate Limiting

The API enforces per-user rate limits to ensure fair usage.

### Limits

| User type       | Requests / hour | Requests / day |
|-----------------|-----------------|----------------|
| Anonymous       | 100             | 1 000          |
| Authenticated   | 1 000           | 10 000         |
| Premium         | 5 000           | 50 000         |
| Enterprise      | Custom          | Custom         |

### Response headers

Every response includes rate-limit information:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 956
X-RateLimit-Reset: 1640995200
```

| Header                   | Description                               |
|--------------------------|-------------------------------------------|
| `X-RateLimit-Limit`      | Max requests in the current time window  |
| `X-RateLimit-Remaining`  | Requests remaining in the current window |
| `X-RateLimit-Reset`      | Unix timestamp when the window resets    |

### 429 Too Many Requests

```json
{
  "error_code": "RATE_LIMIT_EXCEEDED",
  "message": "API rate limit exceeded. Please wait before retrying.",
  "details": {
    "retry_after": 3600,
    "limit": 1000,
    "reset_at": "2024-01-15T15:00:00Z"
  }
}
```

### Per-endpoint limits

| Endpoint                   | Limit      | Reason                  |
|----------------------------|------------|-------------------------|
| `/api/token/`              | 10 / hour  | Prevent brute-force     |
| `/api/reports/export/`     | 5 / hour   | Resource-intensive      |
| `/api/bulk-import/`        | 3 / hour   | Large data processing   |

### Best practices

1. **Monitor headers** — check `X-RateLimit-Remaining` proactively.
2. **Exponential back-off** — retry with increasing delays on `429`.
3. **Cache responses** — avoid redundant requests for static data.
4. **Use webhooks** — subscribe to events instead of polling.
"""

# ═══════════════════════════════════════════════════════════════════════
# Versioning documentation
# ═══════════════════════════════════════════════════════════════════════

VERSIONING_DESCRIPTION = """\

## API Versioning

The version is embedded in the URL path:

```
https://api.lankacommerce.com/api/v1/products/
```

### Semantic versioning

**MAJOR.MINOR.PATCH** — the current release is **v1.0.0**.

| Segment | Meaning                                     |
|---------|---------------------------------------------|
| MAJOR   | Breaking changes (new URL prefix)           |
| MINOR   | New features, backward-compatible           |
| PATCH   | Bug-fixes, backward-compatible              |

### Lifecycle

| Stage      | Duration   | Description                           |
|------------|------------|---------------------------------------|
| Active     | Current    | Fully supported, receives updates     |
| Deprecated | 12 months  | Functional but migration encouraged   |
| End-of-Life| —          | Removed after deprecation period      |

Deprecated endpoints include the headers:

```
Deprecation: true
Sunset: Sat, 15 Dec 2025 23:59:59 GMT
```

### Backward-compatibility guarantee

Within the same major version:

* New **optional** fields may appear in responses.
* New **optional** query parameters may be added.
* New endpoints may be introduced.
* Existing behaviour will **not** change.
"""

# ═══════════════════════════════════════════════════════════════════════
# Changelog documentation
# ═══════════════════════════════════════════════════════════════════════

CHANGELOG_DESCRIPTION = """\

## Changelog

### v1.0.0 — 2024-01-15 (Initial release)

#### Added
- JWT authentication with access & refresh tokens
- Multi-tenant architecture with `X-Tenant-ID` header
- Product catalogue management
- Order management and POS integration
- Customer / CRM endpoints
- Inventory management
- Financial & accounting endpoints (LKR)
- Webstore / e-commerce endpoints
- Page-number pagination (default 20, max 100)
- Filtering via Django Filter Backend
- Ordering on all list endpoints
- OpenAPI 3.0 schema with Swagger UI and ReDoc
- Rate limiting (1 000 req/hour for authenticated users)
- Sri Lanka localisation (LKR, Sinhala, Asia/Colombo)

#### Security
- JWT token-based authentication
- Tenant data isolation
- HTTPS enforcement in production
- Rate limiting to prevent abuse

---

*Future releases will follow the format below:*

```
### vX.Y.Z — YYYY-MM-DD

#### Added
- …

#### Changed
- **BREAKING**: …

#### Deprecated
- …

#### Fixed
- …

#### Security
- …
```

**Stay updated**

- Documentation — https://docs.lankacommerce.com/changelog
- Email — subscribe at https://lankacommerce.com/api-updates
"""


# ═══════════════════════════════════════════════════════════════════════
# Composed DESCRIPTION supplement
# ═══════════════════════════════════════════════════════════════════════
# This single string is appended to the base DESCRIPTION in
# SPECTACULAR_SETTINGS so all supplementary sections appear in the
# rendered Swagger UI / ReDoc description area.

DESCRIPTION_SUPPLEMENT: str = (
    AUTHENTICATION_DESCRIPTION
    + ERROR_RESPONSES_DESCRIPTION
    + PAGINATION_DESCRIPTION
    + FILTERING_DESCRIPTION
    + ORDERING_DESCRIPTION
    + RATE_LIMIT_DESCRIPTION
    + VERSIONING_DESCRIPTION
    + CHANGELOG_DESCRIPTION
)
