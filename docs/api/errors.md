# API Errors

> Error response formats, HTTP status codes, and troubleshooting guidance.

**Navigation:** [API Overview](overview.md) · [Authentication](authentication.md) · [Docs Index](../index.md)

---

## Overview

LankaCommerce Cloud API returns consistent, machine-readable error responses. All errors use standard HTTP status codes and include a structured JSON body to help clients handle failures gracefully.

---

## Error Response Format

### Standard Error

| Field    | Type   | Description                  |
| -------- | ------ | ---------------------------- |
| `detail` | string | Human-readable error message |

### Validation Error

| Field              | Type  | Description                          |
| ------------------ | ----- | ------------------------------------ |
| `<field_name>`     | array | List of error messages for the field |
| `non_field_errors` | array | Errors not tied to a specific field  |

### Multiple Validation Errors

| Field    | Type  | Description                                         |
| -------- | ----- | --------------------------------------------------- |
| `field1` | array | `["This field is required."]`                       |
| `field2` | array | `["Ensure this value has at most 255 characters."]` |

---

## HTTP Status Codes

### Success Codes

| Code | Meaning    | Typical Use                             |
| ---- | ---------- | --------------------------------------- |
| 200  | OK         | Successful GET, PUT, PATCH              |
| 201  | Created    | Successful POST that creates a resource |
| 204  | No Content | Successful DELETE                       |

### Client Error Codes

| Code | Meaning              | Description                                                 |
| ---- | -------------------- | ----------------------------------------------------------- |
| 400  | Bad Request          | Invalid request body or parameters                          |
| 401  | Unauthorized         | Missing or invalid authentication token                     |
| 403  | Forbidden            | Authenticated but lacking required permissions              |
| 404  | Not Found            | Resource does not exist or is not accessible                |
| 405  | Method Not Allowed   | HTTP method not supported for this endpoint                 |
| 409  | Conflict             | Resource state conflict (e.g., duplicate entry)             |
| 422  | Unprocessable Entity | Request is well-formed but semantically invalid             |
| 429  | Too Many Requests    | Rate limit exceeded — see [Rate Limiting](rate-limiting.md) |

### Server Error Codes

| Code | Meaning               | Description                                |
| ---- | --------------------- | ------------------------------------------ |
| 500  | Internal Server Error | Unexpected server failure                  |
| 502  | Bad Gateway           | Upstream service unavailable               |
| 503  | Service Unavailable   | Server is temporarily down for maintenance |

---

## Common Error Scenarios

### Authentication Errors (401)

| Scenario             | `detail` Message                                |
| -------------------- | ----------------------------------------------- |
| No token provided    | `Authentication credentials were not provided.` |
| Invalid token        | `Given token not valid for any token type.`     |
| Expired access token | `Token is invalid or expired.`                  |

**Resolution:** Obtain a new access token via the refresh endpoint. See [Authentication](authentication.md).

### Permission Errors (403)

| Scenario          | `detail` Message                                     |
| ----------------- | ---------------------------------------------------- |
| Insufficient role | `You do not have permission to perform this action.` |
| Wrong tenant      | `You do not have access to this tenant's resources.` |

**Resolution:** Verify the user has the correct role or tenant membership.

### Validation Errors (400)

| Scenario               | Response Body                                        |
| ---------------------- | ---------------------------------------------------- |
| Missing required field | `{"name": ["This field is required."]}`              |
| Invalid format         | `{"email": ["Enter a valid email address."]}`        |
| Unique constraint      | `{"sku": ["product with this sku already exists."]}` |

**Resolution:** Correct the request body and retry.

### Not Found (404)

| Scenario                | `detail` Message |
| ----------------------- | ---------------- |
| Resource does not exist | `Not found.`     |
| Soft-deleted resource   | `Not found.`     |

**Resolution:** Verify the resource ID and that the resource has not been deleted.

### Rate Limiting (429)

| Header        | Description                     |
| ------------- | ------------------------------- |
| `Retry-After` | Seconds to wait before retrying |

**Resolution:** Wait for the indicated period and retry. See [Rate Limiting](rate-limiting.md).

---

## Error Handling Best Practices

| Practice                  | Recommendation                                                     |
| ------------------------- | ------------------------------------------------------------------ |
| Check status codes        | Always check the HTTP status code before parsing the response body |
| Handle 401 gracefully     | Automatically attempt token refresh on 401 responses               |
| Display validation errors | Map field-level errors to form fields in the UI                    |
| Retry on 429              | Respect the `Retry-After` header and implement exponential backoff |
| Log 5xx errors            | Report server errors to your monitoring system                     |
| Never expose internals    | API never leaks stack traces or internal details in production     |

---

## Related Documentation

- [API Overview](overview.md) — API architecture and entry points
- [Authentication](authentication.md) — JWT flows and token management
- [Rate Limiting](rate-limiting.md) — Throttle limits and retry guidance
- [Docs Index](../index.md) — Documentation hub
