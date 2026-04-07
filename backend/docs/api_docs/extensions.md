# Extension Guide

> **Task 81 — SP11 Group F**
> How to extend and customise the LankaCommerce Cloud API documentation system.

---

## Table of Contents

1. [Custom Preprocessing Hooks](#custom-preprocessing-hooks)
2. [Description Supplements](#description-supplements)
3. [Custom Schema Serializers](#custom-schema-serializers)
4. [Adding New Examples](#adding-new-examples)
5. [Custom OpenAPI Parameters](#custom-openapi-parameters)
6. [Post-processing Hooks](#post-processing-hooks)

---

## Custom Preprocessing Hooks

Preprocessing hooks run during schema generation and can filter or
modify the list of discovered endpoints before the schema is built.

### How It Works

drf-spectacular calls every function listed in
`SPECTACULAR_SETTINGS["PREPROCESSING_HOOKS"]` with the full list of
endpoint tuples.

Each tuple has the shape:

```python
(path: str, path_regex: str, method: str, callback: Any)
```

### Existing Hook

```python
# apps/core/api_docs/extensions.py

def custom_preprocessing_hook(endpoints, **kwargs):
    """Filter out internal debug endpoints."""
    processed = []
    for path, path_regex, method, callback in endpoints:
        if path.startswith("/api/_internal/"):
            continue
        processed.append((path, path_regex, method, callback))
    return processed
```

### Adding a New Filter

To exclude additional paths (e.g. deprecated v0 endpoints):

```python
# Add to custom_preprocessing_hook or create a new hook

def exclude_deprecated_v0(endpoints, **kwargs):
    """Remove deprecated v0 endpoints from the schema."""
    return [
        ep for ep in endpoints
        if not ep[0].startswith("/api/v0/")
    ]
```

Register in `config/settings/api_docs.py`:

```python
SPECTACULAR_SETTINGS = {
    "PREPROCESSING_HOOKS": [
        "apps.core.api_docs.extensions.custom_preprocessing_hook",
        "apps.core.api_docs.extensions.exclude_deprecated_v0",  # new
    ],
}
```

### Modifying Endpoints

You can also transform endpoints (e.g. inject tags or rewrite paths):

```python
def add_tenant_tag(endpoints, **kwargs):
    """Inject 'Multi-Tenant' tag for tenant-scoped endpoints."""
    processed = []
    for path, path_regex, method, callback in endpoints:
        # You can attach metadata via callback attributes
        if hasattr(callback, 'cls') and hasattr(callback.cls, 'tenant_scoped'):
            # Metadata can be read by @extend_schema later
            pass
        processed.append((path, path_regex, method, callback))
    return processed
```

---

## Description Supplements

The `DESCRIPTION_SUPPLEMENT` string is appended to the main API
description in `SPECTACULAR_SETTINGS["DESCRIPTION"]` and rendered at the
top of Swagger UI / ReDoc.

### Existing Sections

| Section         | Constant                      | Content                      |
| --------------- | ----------------------------- | ---------------------------- |
| Authentication  | `AUTHENTICATION_DESCRIPTION`  | JWT flow, token endpoints    |
| Error Responses | `ERROR_RESPONSES_DESCRIPTION` | Error envelope, status codes |
| Pagination      | `PAGINATION_DESCRIPTION`      | Page-number pagination       |
| Filtering       | `FILTERING_DESCRIPTION`       | Query parameter filters      |
| Ordering        | `ORDERING_DESCRIPTION`        | Sort results                 |
| Rate Limiting   | `RATE_LIMIT_DESCRIPTION`      | Per-user rate limits         |
| Versioning      | `VERSIONING_DESCRIPTION`      | URL path versioning          |
| Changelog       | `CHANGELOG_DESCRIPTION`       | Release history              |

### Adding a New Section

1. Define the section in `apps/core/api_docs/extensions.py`:

````python
WEBHOOKS_DESCRIPTION = """\

## Webhooks

The API supports webhooks for real-time event notifications.

### Supported Events

| Event | Trigger |
|-------|---------|
| `order.created` | New order placed |
| `order.updated` | Order status change |
| `inventory.low` | Stock below threshold |

### Payload Format

```json
{
  "event": "order.created",
  "timestamp": "2024-01-15T14:30:00+05:30",
  "data": { ... }
}
````

"""

````

2. Append to the `DESCRIPTION_SUPPLEMENT` composition:

```python
DESCRIPTION_SUPPLEMENT: str = (
    AUTHENTICATION_DESCRIPTION
    + ERROR_RESPONSES_DESCRIPTION
    + PAGINATION_DESCRIPTION
    + FILTERING_DESCRIPTION
    + ORDERING_DESCRIPTION
    + RATE_LIMIT_DESCRIPTION
    + VERSIONING_DESCRIPTION
    + CHANGELOG_DESCRIPTION
    + WEBHOOKS_DESCRIPTION         # ← add here
)
````

3. The new section will automatically appear in Swagger UI and ReDoc.

---

## Custom Schema Serializers

Schema serializers live in `apps/core/api_docs/schemas.py`. They are
**not** used at runtime — they exist only to produce accurate OpenAPI
component schemas.

### Creating a New Schema

```python
# apps/core/api_docs/schemas.py

from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Conflict Error",
            value={
                "error_code": "CONFLICT",
                "message": "A resource with this SKU already exists.",
                "details": {"sku": "MOUSE-WL-001"},
            },
            response_only=True,
            status_codes=["409"],
        ),
    ],
)
class ConflictErrorResponseSerializer(serializers.Serializer):
    """Conflict error response (HTTP 409)."""

    error_code = serializers.CharField(
        default="CONFLICT",
        help_text="Machine-readable error code.",
    )
    message = serializers.CharField(
        default="A resource with this identifier already exists.",
        help_text="Human-readable error description.",
    )
    details = serializers.DictField(
        required=False,
        help_text="Conflicting resource details.",
    )
```

### Registering the New Schema

1. Import in `apps/core/api_docs/__init__.py`:

```python
from apps.core.api_docs.schemas import ConflictErrorResponseSerializer
```

2. Add to `__all__`:

```python
__all__ = [
    ...
    "ConflictErrorResponseSerializer",
]
```

3. Use in views:

```python
@extend_schema(responses={409: ConflictErrorResponseSerializer})
def create(self, request): ...
```

---

## Adding New Examples

Examples live in `apps/core/api_docs/examples.py` as module-level
`OpenApiExample` instances.

### Step-by-Step

1. **Define the example:**

```python
# apps/core/api_docs/examples.py

CREATE_INVOICE_REQUEST_EXAMPLE = OpenApiExample(
    name="Create Invoice",
    value={
        "customer_id": "550e8400-e29b-41d4-a716-446655440001",
        "items": [
            {"description": "Web Development", "amount": "150000.00"},
        ],
        "currency": "LKR",
        "due_date": "2024-02-15",
    },
    request_only=True,
    summary="Create a new invoice",
)

INVOICE_RESPONSE_EXAMPLE = OpenApiExample(
    name="Invoice Detail",
    value={
        "id": "550e8400-e29b-41d4-a716-446655440030",
        "invoice_number": "INV-2024-0001",
        "status": "draft",
        "total": "150000.00",
        "currency": "LKR",
        "created_at": "2024-01-15T10:00:00+05:30",
    },
    response_only=True,
    status_codes=["200", "201"],
    summary="Single invoice resource",
)
```

2. **Export from `__init__.py`:**

```python
from apps.core.api_docs.examples import (
    CREATE_INVOICE_REQUEST_EXAMPLE,
    INVOICE_RESPONSE_EXAMPLE,
)

__all__ = [
    ...
    "CREATE_INVOICE_REQUEST_EXAMPLE",
    "INVOICE_RESPONSE_EXAMPLE",
]
```

3. **Attach to a view:**

```python
@extend_schema(
    examples=[CREATE_INVOICE_REQUEST_EXAMPLE, INVOICE_RESPONSE_EXAMPLE],
)
def create(self, request): ...
```

### Example Conventions

- **Monetary values** — always use `"LKR"` currency, string amounts (`"850.00"`).
- **Phone numbers** — use `"+94"` prefix (Sri Lanka).
- **Timestamps** — use `"+05:30"` timezone (Asia/Colombo).
- **UUIDs** — use realistic UUID4 values, not placeholder text.
- **Request examples** — set `request_only=True`.
- **Response examples** — set `response_only=True` and `status_codes`.

---

## Custom OpenAPI Parameters

Global or reusable parameters are defined in
`apps/core/api_docs/extensions.py`.

### Existing Parameters

| Name                      | Location | Required | Purpose                |
| ------------------------- | -------- | -------- | ---------------------- |
| `TENANT_HEADER_PARAMETER` | Header   | Yes      | Multi-tenant isolation |

### Creating a New Parameter

```python
# apps/core/api_docs/extensions.py

ACCEPT_LANGUAGE_PARAMETER = OpenApiParameter(
    name="Accept-Language",
    type=str,
    location=OpenApiParameter.HEADER,
    required=False,
    description="Preferred response language (en, si, ta).",
    examples=[
        OpenApiExample(name="English", value="en"),
        OpenApiExample(name="Sinhala", value="si"),
        OpenApiExample(name="Tamil", value="ta"),
    ],
)
```

Export from `__init__.py` and use in views:

```python
@extend_schema(parameters=[ACCEPT_LANGUAGE_PARAMETER])
def my_view(request): ...
```

---

## Post-processing Hooks

drf-spectacular also supports **post-processing hooks** that run after
the schema is fully generated. Use these for global transformations.

### Registration

```python
# config/settings/api_docs.py

SPECTACULAR_SETTINGS = {
    "POSTPROCESSING_HOOKS": [
        "apps.core.api_docs.extensions.custom_postprocessing_hook",
    ],
}
```

### Example: Inject Global Headers

```python
def custom_postprocessing_hook(result, generator, request, public):
    """Add global response headers to every operation."""
    for path_item in result.get("paths", {}).values():
        for operation in path_item.values():
            if isinstance(operation, dict) and "responses" in operation:
                for response in operation["responses"].values():
                    if isinstance(response, dict):
                        response.setdefault("headers", {})
                        response["headers"]["X-Request-ID"] = {
                            "description": "Unique request identifier",
                            "schema": {"type": "string", "format": "uuid"},
                        }
    return result
```

---

## CI Validation

The `validate_schema` management command checks schema integrity:

```bash
python manage.py validate_schema           # JSON + YAML
python manage.py validate_schema --strict  # treat warnings as errors
python manage.py validate_schema --output schema.json
```

Add to your CI pipeline:

```yaml
- name: Validate API Schema
  run: python manage.py validate_schema --strict
```

---

## Further Reading

- [Decorator Guide](decorators.md)
- [API Docs README](../../apps/core/api_docs/README.md)
- [drf-spectacular customisation](https://drf-spectacular.readthedocs.io/en/latest/customization.html)
