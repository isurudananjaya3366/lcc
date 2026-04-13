# API Integration Guide

## Overview

The frontend communicates with the Django backend API at `NEXT_PUBLIC_API_URL` (default: `http://localhost:8000/api/v1`).

## Configuration

```typescript
import { env } from '@/lib/env';

// Client-side: uses public URL
const apiUrl = env.NEXT_PUBLIC_API_URL;

// Server-side: uses internal Docker URL for performance
const serverApiUrl = env.API_BASE_URL; // http://backend:8000/api/v1
```

## Request Headers

Every API request includes:

| Header          | Value                  | Purpose                |
| --------------- | ---------------------- | ---------------------- |
| `Authorization` | `Bearer {jwt_token}`   | Authentication         |
| `Content-Type`  | `application/json`     | Request format         |
| `X-Tenant-ID`   | `{tenant_id}`          | Multi-tenant isolation |
| `Accept`        | `application/json`     | Response format        |

## Response Format

### Success Response

```json
{
  "data": { ... },
  "message": "Success",
  "meta": { "page": 1, "total": 100, "page_size": 20 }
}
```

### Error Response

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": { "email": ["This field is required."] }
  }
}
```

## Common Endpoints

| Method   | Endpoint                  | Purpose            |
| -------- | ------------------------- | ------------------ |
| `POST`   | `/auth/login/`            | Login              |
| `POST`   | `/auth/logout/`           | Logout             |
| `POST`   | `/auth/token/refresh/`    | Refresh JWT        |
| `GET`    | `/auth/me/`               | Current user       |
| `GET`    | `/health/`                | Health check       |

## Error Handling

| Status | Meaning            | Action                       |
| ------ | ------------------ | ---------------------------- |
| 400    | Bad Request        | Show validation errors       |
| 401    | Unauthorized       | Redirect to login            |
| 403    | Forbidden          | Show permission denied       |
| 404    | Not Found          | Show not found page          |
| 422    | Validation Error   | Show field-level errors      |
| 500    | Server Error       | Show generic error message   |

## Retry Strategy

- **Retry on:** Network errors, 502, 503, 504
- **Max retries:** 3
- **Backoff:** Exponential (1s, 2s, 4s)
- **No retry on:** 400, 401, 403, 404, 422

## Timeout

Default: 30 seconds (configurable via `API_TIMEOUT` env var)

## TypeScript Integration

```typescript
// Generic API response type
interface ApiResponse<T> {
  data: T;
  message?: string;
  meta?: PaginationMeta;
}

// Paginated response
interface PaginatedResponse<T> {
  data: T[];
  meta: {
    page: number;
    per_page: number;
    total: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
  links: {
    next: string | null;
    prev: string | null;
  };
}
```

## Caching Strategies

| Data Type        | Cache Duration | Invalidation Trigger        |
| ---------------- | -------------- | --------------------------- |
| User profile     | 5 min          | Profile update, login       |
| Tenant info      | 10 min         | Tenant switch               |
| List data        | 2 min          | Create/update/delete        |
| Static config    | 1 hour         | App restart                 |
| Real-time data   | No cache       | N/A                         |

## Multi-Tenant Considerations

- Every API request must include `X-Tenant-ID` header
- Tenant context provided via `useTenant()` hook
- Switching tenants clears all cached data
- Server Components read tenant from cookies/headers

## Request Interceptors

1. **Auth token:** Attach JWT from cookie/store
2. **Tenant ID:** Attach `X-Tenant-ID` from tenant context
3. **Custom headers:** Accept-Language, timezone
4. **Dev logging:** Log request details in development

## Response Interceptors

1. **Success handling:** Extract data from response wrapper
2. **Error transformation:** Convert API errors to typed Error objects
3. **401 handling:** Clear auth state, redirect to login
4. **Dev logging:** Log response times and status

## Request Patterns

```typescript
// GET — Fetch a list
const products = await api.get<Product[]>('/products/');

// POST — Create
const product = await api.post<Product>('/products/', newData);

// PUT — Full update
await api.put<Product>(`/products/${id}/`, updatedData);

// PATCH — Partial update
await api.patch<Product>(`/products/${id}/`, partialData);

// DELETE — Remove
await api.delete(`/products/${id}/`);
```

## Testing API Integration

- Use **MSW (Mock Service Worker)** for API mocking in tests
- Test both success and error scenarios
- Verify loading states during requests
- Test token refresh flow with expired tokens
- Test tenant header propagation
