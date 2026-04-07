# API Error Guide

This guide explains how the LankaCommerce Cloud API handles errors and how to use the custom exception hierarchy in your views and serializers.

## Error Response Envelope

Every error response follows a consistent JSON structure:

```json
{
  "success": false,
  "error": {
    "error_code": "VALIDATION_ERROR",
    "message": "Invalid input data.",
    "details": { "email": ["Enter a valid email address."] },
    "timestamp": "2025-01-15T10:30:00+00:00"
  }
}
```

| Field              | Type                  | Description                                            |
| ------------------ | --------------------- | ------------------------------------------------------ |
| `success`          | `bool`                | Always `false` for errors.                             |
| `error.error_code` | `string`              | Machine-readable error code (e.g. `VALIDATION_ERROR`). |
| `error.message`    | `string`              | Human-readable description.                            |
| `error.details`    | `object\|array\|null` | Optional structured data (field errors, IDs, etc.).    |
| `error.timestamp`  | `string`              | ISO 8601 timestamp of the error.                       |

## Exception Hierarchy

All custom exceptions inherit from `APIException` (which itself extends DRF's `APIException`):

```
APIException (500)
├── Client Errors (4xx)
│   ├── ValidationException (400)
│   ├── NotFoundException (404)
│   ├── ConflictException (409)
│   └── RateLimitException (429)
├── Auth Errors
│   ├── AuthenticationException (401)
│   ├── PermissionDeniedException (403)
│   ├── InvalidTokenException (401)
│   ├── TokenExpiredException (401)
│   ├── TenantNotFoundException (404)
│   └── TenantInactiveException (403)
├── Server Errors (5xx)
│   ├── ServerException (500)
│   └── ServiceUnavailableException (503)
└── Business Errors
    ├── BusinessRuleException (422)
    └── ResourceExistsException (409)
```

## Usage Examples

### Raising a validation error

```python
from apps.core.exceptions import ValidationException

raise ValidationException(
    message="Invalid product data.",
    field_errors={"price": ["Price must be positive."]},
)
```

### Raising a not-found error

```python
from apps.core.exceptions import NotFoundException

raise NotFoundException(
    message="Product not found.",
    details={"product_id": product_id},
)
```

### Raising a permission error with required permission

```python
from apps.core.exceptions import PermissionDeniedException

raise PermissionDeniedException(
    message="Only managers can approve orders.",
    required_permission="orders.approve",
)
```

### Raising a business-rule violation

```python
from apps.core.exceptions import BusinessRuleException

raise BusinessRuleException(
    message="Cannot delete a customer with open orders.",
    rule_code="CUSTOMER_HAS_OPEN_ORDERS",
)
```

### Raising a rate-limit error

```python
from apps.core.exceptions import RateLimitException

raise RateLimitException(retry_after=60)
```

The handler automatically adds a `Retry-After` header to the HTTP response.

### Raising a service-unavailable error

```python
from apps.core.exceptions import ServiceUnavailableException

raise ServiceUnavailableException(
    service_name="payment-gateway",
    retry_after=120,
)
```

## Global Exception Handler

The custom handler is registered in DRF settings:

```python
REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "apps.core.exceptions.handlers.custom_exception_handler",
}
```

It handles:

1. **Django core exceptions** (`Http404`, `PermissionDenied`, `ValidationError`) — converted to DRF equivalents first.
2. **Our custom `APIException` subclasses** — wrapped in `ErrorResponse`.
3. **Standard DRF exceptions** — mapped to our error codes and wrapped.
4. **Unhandled exceptions** — logged and returned as a generic 500 error.

## Logging

Use the logging utilities for structured error logging:

```python
from apps.core.exceptions.logging import log_exception, log_business_rule_violation

# Log an exception with request context
log_exception(exc, request=request)

# Log a business rule violation (logged at WARNING)
log_business_rule_violation(
    rule_code="MAX_QTY_EXCEEDED",
    message="Quantity exceeds warehouse stock.",
    request=request,
)
```
