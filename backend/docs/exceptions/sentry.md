# Sentry Error Tracking & Context Enrichment

> **Tasks:** SP07-71, SP07-72, SP07-74

## Overview

LankaCommerce Cloud uses [Sentry](https://sentry.io) for real-time error
tracking, performance monitoring, and distributed tracing. The integration
consists of two parts:

| Component          | Location                                 | Purpose                                                                 |
| ------------------ | ---------------------------------------- | ----------------------------------------------------------------------- |
| SDK initialisation | `backend/config/settings/sentry.py`      | Configures `sentry_sdk.init()` with DSN, integrations, and sample rates |
| Context middleware | `backend/apps/core/middleware/sentry.py` | Enriches every event with user, tenant, and request metadata            |

---

## Configuration

### Environment Variables

| Variable                      | Required | Default      | Description                                                  |
| ----------------------------- | -------- | ------------ | ------------------------------------------------------------ |
| `SENTRY_DSN`                  | Yes      | —            | Project DSN from Sentry dashboard                            |
| `SENTRY_ENVIRONMENT`          | No       | `production` | Environment tag (`production`, `staging`, `development`)     |
| `SENTRY_TRACES_SAMPLE_RATE`   | No       | `0.1`        | Transaction sample rate (0.0–1.0)                            |
| `SENTRY_PROFILES_SAMPLE_RATE` | No       | `0.0`        | Profiling sample rate (0.0–1.0)                              |
| `SENTRY_RELEASE`              | No       | —            | Release identifier (e.g. git SHA)                            |
| `SENTRY_SEND_DEFAULT_PII`     | No       | `False`      | Send PII automatically (keep `False` unless legally cleared) |

### Activation

Sentry is initialised in production/staging settings by calling:

```python
# config/settings/production.py
from config.settings.sentry import configure_sentry
configure_sentry(env)
```

The `SentryContextMiddleware` is registered in `MIDDLEWARE` and will
silently no-op when the SDK is not installed or not initialised.

---

## Context Middleware (`SentryContextMiddleware`)

### What It Adds

#### User Context (`sentry_sdk.set_user`)

For **authenticated** requests:

| Key          | Source                            | Example               |
| ------------ | --------------------------------- | --------------------- |
| `id`         | `user.pk` (UUID)                  | `"a1b2c3d4-..."`      |
| `email`      | `user.email`                      | `"admin@example.com"` |
| `ip_address` | `X-Forwarded-For` / `REMOTE_ADDR` | `"192.168.1.10"`      |

For **anonymous** requests only `ip_address` is set.

> **Note:** `PlatformUser` is email-based (`USERNAME_FIELD = "email"`) and
> does **not** have a `username` field. The middleware safely checks for
> `username` via `getattr` and only includes it when present.

#### Tags (`sentry_sdk.set_tag`)

| Tag             | Source                       | Description                       |
| --------------- | ---------------------------- | --------------------------------- |
| `tenant_id`     | `request.tenant.pk`          | Current tenant primary key        |
| `tenant_domain` | `request.tenant.schema_name` | Tenant schema / domain            |
| `request_id`    | `X-Request-ID` header        | Correlation ID from reverse proxy |

Tags are **indexed** in Sentry and can be used to filter and search events.

#### Request Context (`sentry_sdk.set_context`)

Stored under the `"request_meta"` context key:

| Key            | Value                      |
| -------------- | -------------------------- |
| `method`       | HTTP method (GET, POST, …) |
| `path`         | Request path               |
| `content_type` | Content-Type header        |
| `user_agent`   | User-Agent header          |

### Middleware Order

The middleware is placed **after** `SecurityHeadersMiddleware` and
**before** `TimezoneMiddleware`:

```python
MIDDLEWARE = [
    ...
    "apps.core.middleware.security.SecurityHeadersMiddleware",
    "apps.core.middleware.sentry.SentryContextMiddleware",   # ← here
    "apps.core.middleware.timezone.TimezoneMiddleware",
    ...
]
```

It must run **after** `AuthenticationMiddleware` (so `request.user` is
available) and **after** `LCCTenantMiddleware` (so `request.tenant` is set).

---

## Graceful Degradation

The middleware is designed to work in any environment:

- **`sentry-sdk` not installed** → Import guard catches `ImportError`;
  middleware becomes a no-op.
- **Sentry not initialised** (no DSN) → `sentry_sdk.get_client().is_active()`
  returns `False`; middleware skips all work.
- **Attribute missing on user/tenant** → All attribute access uses `getattr`
  with safe defaults.

---

## SDK Integrations

The following integrations are enabled in `configure_sentry()`:

| Integration          | Purpose                                             |
| -------------------- | --------------------------------------------------- |
| `DjangoIntegration`  | Automatic transaction/span creation for views       |
| `CeleryIntegration`  | Track Celery task errors and monitor beat schedules |
| `LoggingIntegration` | Capture `ERROR`-level log entries as Sentry events  |
| `RedisIntegration`   | Trace Redis commands as spans                       |

### Event Filtering (`_before_send`)

The `_before_send` hook in `sentry.py`:

1. **Drops noisy exceptions** — `DisallowedHost`, `SuspiciousOperation`.
2. **Scrubs sensitive headers** — `Authorization`, `Cookie`, `X-CSRFToken`
   are replaced with `[Filtered]`.

---

## Testing Sentry Locally

### 1. Trigger a test event

```python
# In Django shell
import sentry_sdk
sentry_sdk.capture_message("Test event from local dev")
```

### 2. Verify context in the Sentry dashboard

After generating an error, check:

- **User** tab — should show `id`, `email`, `ip_address`.
- **Tags** sidebar — should show `tenant_id`, `tenant_domain`, `request_id`.
- **Context** section — should show `request_meta` with method, path, etc.

### 3. Unit-test the middleware without Sentry

```python
from unittest.mock import patch, MagicMock
from django.test import RequestFactory, TestCase

class SentryContextMiddlewareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.get_response = MagicMock(return_value=MagicMock(status_code=200))

    @patch("apps.core.middleware.sentry.sentry_sdk")
    @patch("apps.core.middleware.sentry._HAS_SENTRY", True)
    def test_sets_user_context_for_authenticated_user(self, mock_sentry):
        from apps.core.middleware.sentry import SentryContextMiddleware

        mock_sentry.get_client.return_value.is_active.return_value = True

        request = self.factory.get("/api/test/")
        request.user = MagicMock(
            is_authenticated=True,
            pk="abc-123",
            email="user@example.com",
            spec=["pk", "email", "is_authenticated"],
        )

        middleware = SentryContextMiddleware(self.get_response)
        middleware(request)

        mock_sentry.set_user.assert_called_once()
        user_data = mock_sentry.set_user.call_args[0][0]
        assert user_data["id"] == "abc-123"
        assert user_data["email"] == "user@example.com"
```

### 4. Smoke-test in staging

```bash
# Trigger a deliberate error
curl -X POST https://staging.lankacommerce.com/api/v1/debug-sentry/
```

---

## Troubleshooting

| Symptom                    | Cause                      | Fix                                             |
| -------------------------- | -------------------------- | ----------------------------------------------- |
| No events in Sentry        | `SENTRY_DSN` not set       | Add DSN to `.env`                               |
| Events missing user info   | Middleware order wrong     | Ensure it runs after `AuthenticationMiddleware` |
| Events missing tenant info | Middleware order wrong     | Ensure it runs after `LCCTenantMiddleware`      |
| `ImportError` in logs      | `sentry-sdk` not installed | `pip install sentry-sdk[django]`                |
| Too many events            | Sample rate too high       | Lower `SENTRY_TRACES_SAMPLE_RATE`               |

---

## References

- [Sentry Python SDK docs](https://docs.sentry.io/platforms/python/)
- [Django integration](https://docs.sentry.io/platforms/python/integrations/django/)
- [Enriching events](https://docs.sentry.io/platforms/python/enriching-events/)
- Internal: `backend/config/settings/sentry.py` — SDK initialisation
- Internal: `backend/apps/core/middleware/sentry.py` — Context middleware
