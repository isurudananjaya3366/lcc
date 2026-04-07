# Schema Decorator Guide

> **Task 80 — SP11 Group F**
> How to use drf-spectacular decorators to document LankaCommerce Cloud API endpoints.

---

## Table of Contents

1. [@extend_schema](#extend_schema)
2. [@extend_schema_view](#extend_schema_view)
3. [OpenApiParameter](#openapiparameter)
4. [OpenApiExample](#openapiexample)
5. [@extend_schema_serializer](#extend_schema_serializer)
6. [Common Patterns](#common-patterns)

---

## @extend_schema

The primary decorator for documenting a single view method.

### Import

```python
from drf_spectacular.utils import extend_schema
```

### Basic Usage

```python
from drf_spectacular.utils import extend_schema

class ProductViewSet(viewsets.ModelViewSet):
    @extend_schema(
        summary="List all products",
        description="Returns a paginated list of products for the current tenant.",
        tags=["Products"],
    )
    def list(self, request, *args, **kwargs):
        ...
```

### Full Signature

```python
@extend_schema(
    # ── Metadata ──────────────────────────────
    summary="Short one-line summary",
    description="Longer markdown description.",
    tags=["TagName"],
    operation_id="customOperationId",
    deprecated=False,

    # ── Request body ──────────────────────────
    request=MyInputSerializer,          # or inline dict / OpenApiTypes

    # ── Responses ─────────────────────────────
    responses={
        200: MyOutputSerializer,
        400: ValidationErrorResponseSerializer,
        401: AuthenticationErrorResponseSerializer,
        404: NotFoundResponseSerializer,
    },

    # ── Parameters ────────────────────────────
    parameters=[
        OpenApiParameter("search", str, description="Search term"),
    ],

    # ── Examples ──────────────────────────────
    examples=[
        MY_REQUEST_EXAMPLE,
        MY_RESPONSE_EXAMPLE,
    ],

    # ── Auth ──────────────────────────────────
    auth=None,  # Override default security; [] = no auth required

    # ── Exclude ───────────────────────────────
    exclude=False,  # True to hide this endpoint
)
```

### Response Shortcuts

```python
# Single response
@extend_schema(responses=ProductSerializer)

# Multiple status codes
@extend_schema(responses={
    200: ProductSerializer,
    404: NotFoundResponseSerializer,
})

# No response body (204)
@extend_schema(responses={204: None})

# Inline response
@extend_schema(responses={200: {"type": "object", "properties": {"ok": {"type": "boolean"}}}})
```

---

## @extend_schema_view

Apply `@extend_schema` to multiple ViewSet actions at once, without
decorating each method individually.

### Import

```python
from drf_spectacular.utils import extend_schema_view
```

### Usage

```python
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    list=extend_schema(
        summary="List products",
        tags=["Products"],
    ),
    create=extend_schema(
        summary="Create product",
        tags=["Products"],
    ),
    retrieve=extend_schema(
        summary="Get product detail",
        tags=["Products"],
    ),
    update=extend_schema(
        summary="Update product",
        tags=["Products"],
    ),
    partial_update=extend_schema(
        summary="Patch product",
        tags=["Products"],
    ),
    destroy=extend_schema(
        summary="Delete product",
        tags=["Products"],
    ),
)
class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
```

---

## OpenApiParameter

Define custom query, path, header, or cookie parameters.

### Import

```python
from drf_spectacular.utils import OpenApiParameter
```

### Query Parameter

```python
OpenApiParameter(
    name="search",
    type=str,
    location=OpenApiParameter.QUERY,
    description="Free-text search across product name and description.",
    required=False,
)
```

### Path Parameter

```python
OpenApiParameter(
    name="product_id",
    type=int,
    location=OpenApiParameter.PATH,
    description="Product primary key.",
    required=True,
)
```

### Header Parameter

```python
from apps.core.api_docs.extensions import TENANT_HEADER_PARAMETER

# The TENANT_HEADER_PARAMETER is pre-built:
#   name="X-Tenant-ID", location=HEADER, required=True

@extend_schema(parameters=[TENANT_HEADER_PARAMETER])
def my_view(request): ...
```

### Enum Parameter

```python
OpenApiParameter(
    name="status",
    type=str,
    enum=["active", "inactive", "archived"],
    description="Filter by product status.",
)
```

---

## OpenApiExample

Provide realistic request/response examples.

### Import

```python
from drf_spectacular.utils import OpenApiExample
```

### Request Example

```python
CREATE_PRODUCT_EXAMPLE = OpenApiExample(
    name="Create Product",
    value={
        "name": "Ceylon Tea 100g",
        "sku": "TEA-001",
        "price": "850.00",
        "category": "beverages",
    },
    request_only=True,
    summary="Create a new product",
)
```

### Response Example

```python
PRODUCT_DETAIL_EXAMPLE = OpenApiExample(
    name="Product Detail",
    value={
        "id": "550e8400-e29b-41d4-a716-446655440010",
        "name": "Ceylon Tea 100g",
        "price": "850.00",
        "currency": "LKR",
    },
    response_only=True,
    status_codes=["200", "201"],
    summary="Single product resource",
)
```

### Attach to a View

```python
@extend_schema(
    examples=[CREATE_PRODUCT_EXAMPLE, PRODUCT_DETAIL_EXAMPLE],
)
def create(self, request, *args, **kwargs): ...
```

---

## @extend_schema_serializer

Attach metadata (examples, descriptions) directly to a serializer class so
every endpoint using it inherits the decoration.

### Import

```python
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
```

### Usage

```python
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Validation Error",
            value={
                "error_code": "VALIDATION_ERROR",
                "message": "Invalid input data.",
                "details": {"price": ["Must be > 0."]},
            },
            response_only=True,
            status_codes=["400"],
        ),
    ],
)
class ValidationErrorResponseSerializer(serializers.Serializer):
    error_code = serializers.CharField()
    message = serializers.CharField()
    details = serializers.DictField()
```

---

## Common Patterns

### Unauthenticated Endpoint

```python
@extend_schema(auth=[], summary="Health check")
def health(request):
    return Response({"status": "ok"})
```

### Hide an Endpoint

```python
@extend_schema(exclude=True)
def internal_debug(request): ...
```

### File Upload

```python
from drf_spectacular.utils import extend_schema, OpenApiTypes

@extend_schema(
    request={"multipart/form-data": {
        "type": "object",
        "properties": {
            "file": {"type": "string", "format": "binary"},
        },
    }},
    responses={201: ImageSerializer},
)
def upload(self, request): ...
```

### Pagination Override

```python
from apps.core.api_docs.schemas import PaginatedResponseSerializer

@extend_schema(responses={200: PaginatedResponseSerializer})
def list(self, request): ...
```

### Multiple Tags

```python
@extend_schema(tags=["Products", "Inventory"])
def stock_transfer(self, request): ...
```

---

## LankaCommerce Conventions

1. **Always tag endpoints** — use the tag names from `SPECTACULAR_SETTINGS["TAGS"]`.
2. **Always specify error responses** — at minimum 400 and 401.
3. **Use shared schemas** — import from `apps.core.api_docs.schemas`.
4. **Use LKR examples** — all monetary values in Sri Lankan Rupees.
5. **Include the tenant header** — use `TENANT_HEADER_PARAMETER` for tenant-scoped endpoints.
6. **Export new examples** — add to `examples.py` and `__init__.py.__all__`.

---

## Further Reading

- [drf-spectacular docs](https://drf-spectacular.readthedocs.io/)
- [OpenAPI 3.0 specification](https://spec.openapis.org/oas/v3.0.3)
- [Extension Guide](extensions.md)
- [API Docs README](../../apps/core/api_docs/README.md)
