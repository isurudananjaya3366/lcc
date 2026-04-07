# API Documentation

> **Module:** `apps.core.api_docs`
> **Framework:** [drf-spectacular](https://drf-spectacular.readthedocs.io/)
> **Spec:** OpenAPI 3.0

---

## Overview

The LankaCommerce Cloud API documentation system uses **drf-spectacular** to
automatically generate an OpenAPI 3.0 schema from Django REST Framework code.
Three interfaces are provided:

| Interface      | URL            | Purpose                                  |
| -------------- | -------------- | ---------------------------------------- |
| **Swagger UI** | `/api/docs/`   | Interactive API explorer with Try-It-Out |
| **ReDoc**      | `/api/redoc/`  | Read-only three-panel reference docs     |
| **Raw Schema** | `/api/schema/` | JSON/YAML download for codegen tools     |

### Architecture

```
┌────────────────────────────────────────┐
│  Django REST Framework Views / ViewSets │
│  (with @extend_schema decorators)      │
└──────────────┬─────────────────────────┘
               │
               ▼
┌────────────────────────────────────────┐
│   drf-spectacular Schema Generator     │
│   + custom_preprocessing_hook          │
└──────────────┬─────────────────────────┘
               │
               ▼
┌────────────────────────────────────────┐
│       OpenAPI 3.0 Schema (JSON/YAML)   │
└──────────────┬─────────────────────────┘
               │
         ┌─────┴──────┐
         ▼            ▼
   Swagger UI      ReDoc
```

---

## Accessing the Documentation

### Development

```
http://localhost:8000/api/docs/       # Swagger UI
http://localhost:8000/api/redoc/      # ReDoc
http://localhost:8000/api/schema/     # JSON schema
http://localhost:8000/api/schema/?format=yaml  # YAML schema
```

### Production

```
https://api.lankacommerce.com/api/docs/
https://api.lankacommerce.com/api/redoc/
https://api.lankacommerce.com/api/schema/
```

### Authenticating in Swagger UI

1. Click the **Authorize** button (top-right).
2. Enter: `Bearer <your_access_token>`.
3. Click **Authorize** → **Close**.
4. All subsequent requests include the JWT header.

Obtain a token:

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user@example.com", "password": "password"}'
```

---

## Module Structure

```
apps/core/api_docs/
├── __init__.py       # Package exports (__all__)
├── urls.py           # URL patterns (schema, docs, redoc)
├── extensions.py     # Preprocessing hook, description supplements
├── schemas.py        # Response serializers (9 classes)
└── examples.py       # OpenApiExample instances (18 examples)
```

### Configuration

Settings live in `config/settings/api_docs.py` and are merged into
Django settings via `SPECTACULAR_SETTINGS`.

Key settings:

| Setting                   | Value                         | Purpose                        |
| ------------------------- | ----------------------------- | ------------------------------ |
| `TITLE`                   | LankaCommerce Cloud API       | Schema title                   |
| `VERSION`                 | 1.0.0                         | API version                    |
| `SCHEMA_PATH_PREFIX`      | `/api/v[0-9]`                 | Only document versioned routes |
| `PREPROCESSING_HOOKS`     | `[custom_preprocessing_hook]` | Filter endpoints               |
| `COMPONENT_SPLIT_REQUEST` | `True`                        | Separate input/output schemas  |

---

## For Developers

### Documenting a New Endpoint

Use `@extend_schema` on your view method:

```python
from drf_spectacular.utils import extend_schema
from apps.core.api_docs.schemas import (
    ValidationErrorResponseSerializer,
    NotFoundResponseSerializer,
)

class ProductViewSet(viewsets.ModelViewSet):
    @extend_schema(
        summary="Create a new product",
        description="Create a product in the tenant's catalogue.",
        request=ProductCreateSerializer,
        responses={
            201: ProductSerializer,
            400: ValidationErrorResponseSerializer,
        },
        tags=["Products"],
    )
    def create(self, request, *args, **kwargs):
        ...
```

### Adding Request / Response Examples

Add `OpenApiExample` instances to `apps/core/api_docs/examples.py`:

```python
from drf_spectacular.utils import OpenApiExample

MY_EXAMPLE = OpenApiExample(
    name="My Example",
    value={"key": "value"},
    request_only=True,  # or response_only=True
    summary="Short description",
)
```

Then register in `__init__.py` → `__all__`.

### Using Shared Error Schemas

Import from `apps.core.api_docs.schemas`:

```python
from apps.core.api_docs.schemas import (
    ErrorResponseSerializer,              # generic
    ValidationErrorResponseSerializer,    # 400
    AuthenticationErrorResponseSerializer,# 401
    PermissionDeniedResponseSerializer,   # 403
    NotFoundResponseSerializer,           # 404
    RateLimitExceededResponseSerializer,  # 429
)
```

---

## Testing

### Run API docs tests

```bash
pytest tests/core/test_api_docs.py -v
```

### Validate schema in CI

```bash
python manage.py validate_schema
python manage.py validate_schema --strict
python manage.py validate_schema --format json --output schema.json
```

The `validate_schema` command:

- Generates the OpenAPI schema
- Validates JSON and YAML serialisation
- Checks for required top-level keys (`openapi`, `info`, `paths`)
- Returns exit code **0** on success, **1** on failure

---

## Troubleshooting

| Symptom                              | Cause                                     | Fix                                            |
| ------------------------------------ | ----------------------------------------- | ---------------------------------------------- |
| Endpoint missing from docs           | Not under `/api/v{N}/` prefix             | Check `SCHEMA_PATH_PREFIX`                     |
| Endpoint shows in docs but shouldn't | Path doesn't start with `/api/_internal/` | Add to preprocessing hook filter               |
| "No schema found" error              | Serializer missing or misconfigured       | Add `@extend_schema` to the view               |
| Examples not showing                 | Example not in `__all__`                  | Export from `__init__.py`                      |
| Auth button missing                  | Security scheme not configured            | Check `COMPONENT_SECURITY_SCHEMES`             |
| CI check failing                     | Schema generation error                   | Run `python manage.py validate_schema` locally |

---

## Further Reading

- [drf-spectacular docs](https://drf-spectacular.readthedocs.io/)
- [OpenAPI 3.0 spec](https://spec.openapis.org/oas/v3.0.3)
- [Decorator guide](../../docs/api_docs/decorators.md)
- [Extension guide](../../docs/api_docs/extensions.md)
