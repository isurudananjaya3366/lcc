# Troubleshooting Guide — Exception Handling

Common issues and solutions when working with the LankaCommerce exception system.

---

## 1. Exception not returning JSON envelope

**Symptom:** You raise a custom exception but get DRF's default HTML error page or plain-text response.

**Cause:** The custom exception handler is not registered in settings.

**Fix:** Ensure `REST_FRAMEWORK` settings include:

```python
REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "apps.core.exceptions.handlers.custom_exception_handler",
}
```

---

## 2. `error_code` is `API_ERROR` instead of a specific code

**Symptom:** The response shows `"error_code": "API_ERROR"` for a standard DRF exception.

**Cause:** The exception's HTTP status code isn't in the handler's `_DRF_STATUS_MAP`.

**Fix:** The map covers 400, 401, 403, 404, 405, and 429. For other status codes, either:

- Raise one of our custom exception classes instead, or
- Extend `_DRF_STATUS_MAP` in `handlers.py`.

---

## 3. `details` field missing from the response

**Symptom:** You passed data but `details` is not in the error envelope.

**Cause:** `ErrorResponse.to_dict()` only includes `details` when the value is truthy (not `None`, not empty dict/list).

**Fix:** Ensure you're passing a non-empty value to the `details` parameter:

```python
# This will NOT include details (empty dict is falsy):
raise ValidationException(details={})

# This WILL include details:
raise ValidationException(details={"email": ["Required"]})
```

---

## 4. `Retry-After` header not appearing

**Symptom:** You raised `RateLimitException(retry_after=60)` but the header is missing.

**Cause:** `ErrorResponse.to_response()` only adds the header when `retry_after is not None`.

**Fix:** Pass an integer value:

```python
raise RateLimitException(retry_after=60)  # header added
raise RateLimitException()                 # no header
```

---

## 5. Django `ValidationError` not converted properly

**Symptom:** A Django `ValidationError` (from model `clean()`) results in a 500 or unexpected format.

**Cause:** The handler checks `hasattr(exc, 'message_dict')` first. If the `ValidationError` was raised with a plain string or list, it uses `exc.messages` instead.

**Fix:** This is expected behaviour. For dict-based errors, raise with a dict:

```python
from django.core.exceptions import ValidationError
raise ValidationError({"name": ["This field is required."]})
```

---

## 6. Unhandled exception returns HTML in DEBUG mode

**Symptom:** In development (`DEBUG=True`), unexpected exceptions produce the default Django debug page instead of JSON.

**Cause:** The handler intentionally delegates to DRF's default handler in DEBUG mode so you get the full traceback page.

**Fix:** This is by design. In production (`DEBUG=False`), a clean JSON 500 envelope is always returned.

---

## 7. Business rule violation logged at wrong level

**Symptom:** Business rule violations appear as ERROR in logs.

**Cause:** You're using `log_exception()` instead of `log_business_rule_violation()`.

**Fix:** Use the dedicated function:

```python
from apps.core.exceptions.logging import log_business_rule_violation

log_business_rule_violation(
    rule_code="ORDER_ALREADY_SHIPPED",
    message="Cannot modify a shipped order.",
    request=request,
)
```

This logs at `WARNING` level, which is appropriate for expected domain constraints.

---

## 8. `required_permission` not showing in response

**Symptom:** You pass `required_permission` to `PermissionDeniedException` but it doesn't appear in `details`.

**Cause:** If you also pass an explicit `details` dict, the `required_permission` convenience logic is skipped.

**Fix:** Either use `required_permission` without `details`, or include it in your `details` dict manually:

```python
# Automatic:
raise PermissionDeniedException(required_permission="orders.approve")
# -> details = {"required_permission": "orders.approve"}

# Manual:
raise PermissionDeniedException(
    details={"required_permission": "orders.approve", "extra": "info"}
)
```

---

## 9. Import errors when using exceptions

**Symptom:** `ImportError` or `ModuleNotFoundError` when importing exceptions.

**Fix:** Import from the package root:

```python
from apps.core.exceptions import ValidationException, NotFoundException
```

Or from individual modules:

```python
from apps.core.exceptions.client import ValidationException
from apps.core.exceptions.auth import AuthenticationException
from apps.core.exceptions.server import BusinessRuleException
```
