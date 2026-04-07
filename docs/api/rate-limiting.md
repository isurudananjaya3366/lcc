# API Rate Limiting

> Throttle limits, response headers, and retry guidance.

**Navigation:** [API Overview](overview.md) · [Errors](errors.md) · [Docs Index](../index.md)

---

## Overview

LankaCommerce Cloud API enforces **rate limiting** (throttling) to protect the service from abuse and ensure fair usage across all clients. Different limits apply to anonymous and authenticated requests.

---

## Rate Limits

| Client Type       | Limit                   | Scope            |
| ----------------- | ----------------------- | ---------------- |
| **Anonymous**     | 100 requests per hour   | Per IP address   |
| **Authenticated** | 1,000 requests per hour | Per user account |

These limits are configured in `REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]` in the Django settings.

---

## Rate Limit Headers

When rate limiting is active, the API includes standard headers in every response:

| Header                  | Description                                             |
| ----------------------- | ------------------------------------------------------- |
| `X-RateLimit-Limit`     | Maximum requests allowed in the window                  |
| `X-RateLimit-Remaining` | Requests remaining in the current window                |
| `X-RateLimit-Reset`     | Unix timestamp when the rate limit window resets        |
| `Retry-After`           | Seconds to wait before retrying (only on 429 responses) |

---

## Exceeding the Limit

When a client exceeds the rate limit, the API responds with:

| Field                | Value                                                       |
| -------------------- | ----------------------------------------------------------- |
| HTTP Status          | `429 Too Many Requests`                                     |
| `detail`             | `"Request was throttled. Expected available in X seconds."` |
| `Retry-After` header | Number of seconds to wait                                   |

---

## Retry Strategy

| Approach                  | Description                                                                 |
| ------------------------- | --------------------------------------------------------------------------- |
| **Respect `Retry-After`** | Always wait the indicated number of seconds before retrying                 |
| **Exponential backoff**   | For repeated 429s, double the wait time on each retry                       |
| **Jitter**                | Add a random delay (0–1 second) to prevent thundering herd                  |
| **Max retries**           | Limit automatic retries to 3–5 attempts, then surface the error to the user |

### Recommended Retry Flow

1. Receive a 429 response
2. Read the `Retry-After` header value
3. Wait for that duration plus a small random jitter
4. Retry the request
5. If 429 again, double the wait time
6. After 3–5 retries, stop and report the error

---

## Endpoint-Specific Limits

Some endpoints may have stricter limits to prevent abuse:

| Endpoint                      | Limit                   | Reason                             |
| ----------------------------- | ----------------------- | ---------------------------------- |
| `/api/v1/auth/token/`         | 20 per hour (anonymous) | Prevent brute-force login attempts |
| `/api/v1/auth/token/refresh/` | 60 per hour             | Prevent token rotation abuse       |
| Report generation endpoints   | 10 per hour             | Resource-intensive operations      |

> These limits will be enforced as the respective modules are implemented.

---

## Best Practices

| Practice              | Recommendation                                                         |
| --------------------- | ---------------------------------------------------------------------- |
| Cache responses       | Cache GET responses client-side to reduce unnecessary requests         |
| Batch operations      | Use bulk endpoints where available instead of many individual requests |
| Monitor usage         | Track your rate limit headers to avoid hitting limits                  |
| Authenticate requests | Authenticated users get 10× the rate limit of anonymous clients        |
| Handle 429 gracefully | Show a user-friendly "please wait" message rather than an error        |

---

## Related Documentation

- [API Overview](overview.md) — API architecture and entry points
- [Errors Documentation](errors.md) — Error response formats
- [Authentication](authentication.md) — JWT flows and token management
- [Docs Index](../index.md) — Documentation hub
