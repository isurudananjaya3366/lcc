# Error Codes Reference

Complete reference of all machine-readable error codes returned by the LankaCommerce Cloud API.

---

## Client Errors (4xx)

| Error Code              | HTTP Status | Exception Class             | Description                                                                                                       |
| ----------------------- | ----------- | --------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `VALIDATION_ERROR`      | 400         | `ValidationException`       | Request data failed validation. `details` contains field-level errors.                                            |
| `AUTHENTICATION_FAILED` | 401         | `AuthenticationException`   | Missing or invalid authentication credentials.                                                                    |
| `INVALID_TOKEN`         | 401         | `InvalidTokenException`     | JWT / access token cannot be decoded or verified.                                                                 |
| `TOKEN_EXPIRED`         | 401         | `TokenExpiredException`     | JWT / access token has passed its expiry time.                                                                    |
| `PERMISSION_DENIED`     | 403         | `PermissionDeniedException` | Authenticated user lacks the required permission. `details.required_permission` may be set.                       |
| `TENANT_INACTIVE`       | 403         | `TenantInactiveException`   | The resolved tenant account is inactive or suspended.                                                             |
| `NOT_FOUND`             | 404         | `NotFoundException`         | The requested resource does not exist.                                                                            |
| `TENANT_NOT_FOUND`      | 404         | `TenantNotFoundException`   | The specified tenant could not be found.                                                                          |
| `CONFLICT`              | 409         | `ConflictException`         | Request conflicts with current resource state (e.g. duplicate unique key).                                        |
| `RESOURCE_EXISTS`       | 409         | `ResourceExistsException`   | Attempted to create a resource that already exists. `details.resource_type` and `details.resource_id` may be set. |
| `RATE_LIMIT_EXCEEDED`   | 429         | `RateLimitException`        | Client exceeded the allowed request rate. Response includes `Retry-After` header when `retry_after` is set.       |

## Business Logic Errors

| Error Code                | HTTP Status | Exception Class         | Description                                                                            |
| ------------------------- | ----------- | ----------------------- | -------------------------------------------------------------------------------------- |
| `BUSINESS_RULE_VIOLATION` | 422         | `BusinessRuleException` | A domain business rule was violated. `details.rule_code` identifies the specific rule. |

## Server Errors (5xx)

| Error Code              | HTTP Status | Exception Class               | Description                                                                                                                |
| ----------------------- | ----------- | ----------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `INTERNAL_SERVER_ERROR` | 500         | `ServerException`             | Generic internal server error. Also used for unhandled exceptions in production.                                           |
| `API_ERROR`             | 500         | `APIException`                | Base error code. Returned when no more specific code applies.                                                              |
| `SERVICE_UNAVAILABLE`   | 503         | `ServiceUnavailableException` | A required external service is unreachable. `details.service` identifies the service. `Retry-After` header may be present. |

## DRF Mapped Codes

When standard DRF exceptions are raised (not our custom classes), the handler maps them to these codes based on HTTP status:

| HTTP Status | Mapped Error Code       |
| ----------- | ----------------------- |
| 400         | `VALIDATION_ERROR`      |
| 401         | `AUTHENTICATION_FAILED` |
| 403         | `PERMISSION_DENIED`     |
| 404         | `NOT_FOUND`             |
| 405         | `METHOD_NOT_ALLOWED`    |
| 429         | `RATE_LIMIT_EXCEEDED`   |
| Other       | `API_ERROR`             |

## Response Envelope

All errors follow this structure:

```json
{
  "success": false,
  "error": {
    "error_code": "<ERROR_CODE>",
    "message": "<Human-readable message>",
    "details": {},
    "timestamp": "<ISO 8601>"
  }
}
```

- `details` is only present when the exception carries structured data.
- `timestamp` is the server time when the error was generated.
