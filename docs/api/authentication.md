# API Authentication

> JWT authentication flows, token management, and security best practices.

**Navigation:** [API Overview](overview.md) · [Errors](errors.md) · [Docs Index](../index.md)

---

## Overview

LankaCommerce Cloud uses **JSON Web Tokens (JWT)** for API authentication, implemented via `djangorestframework-simplejwt`. All authenticated endpoints require a valid access token in the `Authorization` header.

---

## Authentication Flow

1. **Obtain tokens** — Send credentials to the token endpoint
2. **Use access token** — Include it in the `Authorization` header for API requests
3. **Refresh token** — When the access token expires, use the refresh token to get a new pair
4. **Logout** — Blacklist the refresh token to invalidate the session

---

## Token Endpoints

| Endpoint                      | Method | Description                      |
| ----------------------------- | ------ | -------------------------------- |
| `/api/v1/auth/token/`         | POST   | Obtain access and refresh tokens |
| `/api/v1/auth/token/refresh/` | POST   | Refresh an expired access token  |
| `/api/v1/auth/token/verify/`  | POST   | Verify a token is still valid    |

### Obtain Tokens

**Request:**

| Field      | Type   | Required | Description        |
| ---------- | ------ | -------- | ------------------ |
| `email`    | string | Yes      | User email address |
| `password` | string | Yes      | User password      |

**Response:**

| Field     | Type   | Description                    |
| --------- | ------ | ------------------------------ |
| `access`  | string | JWT access token (short-lived) |
| `refresh` | string | JWT refresh token (long-lived) |

### Refresh Token

**Request:**

| Field     | Type   | Required | Description           |
| --------- | ------ | -------- | --------------------- |
| `refresh` | string | Yes      | Current refresh token |

**Response:**

| Field     | Type   | Description                             |
| --------- | ------ | --------------------------------------- |
| `access`  | string | New JWT access token                    |
| `refresh` | string | New refresh token (if rotation enabled) |

---

## Token Configuration

| Setting                  | Value                     | Description                                         |
| ------------------------ | ------------------------- | --------------------------------------------------- |
| Access Token Lifetime    | 30 minutes (configurable) | Set via `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` env var |
| Refresh Token Lifetime   | 7 days (configurable)     | Set via `JWT_REFRESH_TOKEN_LIFETIME_DAYS` env var   |
| Algorithm                | HS256                     | HMAC-SHA256 signing                                 |
| Token Rotation           | Configurable              | Set via `JWT_ROTATE_REFRESH_TOKENS` env var         |
| Blacklist After Rotation | Configurable              | Set via `JWT_BLACKLIST_AFTER_ROTATION` env var      |
| Header Type              | `Bearer`                  | Prefix for the Authorization header                 |

---

## Using Tokens

Include the access token in every authenticated request:

| Header          | Value                   |
| --------------- | ----------------------- |
| `Authorization` | `Bearer <access_token>` |

---

## Permission Levels

| Permission        | Description                                   |
| ----------------- | --------------------------------------------- |
| `IsAuthenticated` | Default — any authenticated user              |
| `IsAdminUser`     | Django admin users only                       |
| `IsTenantAdmin`   | Tenant administrator (Phase 2)                |
| `IsTenantMember`  | Any member of the current tenant (Phase 2)    |
| `AllowAny`        | Public endpoints — no authentication required |

---

## Public Endpoints

The following endpoints do not require authentication:

| Endpoint                      | Description                         |
| ----------------------------- | ----------------------------------- |
| `/health/`                    | Health check                        |
| `/api/v1/auth/token/`         | Token obtain                        |
| `/api/v1/auth/token/refresh/` | Token refresh                       |
| `/api/schema/`                | OpenAPI schema download             |
| `/api/docs/`                  | Swagger UI                          |
| `/api/redoc/`                 | ReDoc documentation                 |
| `/api/v1/store/*`             | Public webstore endpoints (Phase 8) |

---

## Security Best Practices

| Practice       | Recommendation                                                         |
| -------------- | ---------------------------------------------------------------------- |
| Token storage  | Store tokens in memory or `httpOnly` cookies — never in `localStorage` |
| HTTPS only     | Always transmit tokens over HTTPS in production                        |
| Token refresh  | Refresh proactively before expiry to avoid interrupted user sessions   |
| Logout cleanup | Blacklist the refresh token on logout                                  |
| Minimal scope  | Request only the permissions your client needs                         |
| Error handling | Never expose token content in error messages or logs                   |

---

## Related Documentation

- [API Overview](overview.md) — API architecture and entry points
- [Errors Documentation](errors.md) — Error response formats
- [Backend API Guide](../backend/api.md) — Full API architecture reference
- [Docs Index](../index.md) — Documentation hub
