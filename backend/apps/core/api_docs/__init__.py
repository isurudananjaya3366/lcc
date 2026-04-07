"""
API Documentation Module.

This module provides OpenAPI 3.0 schema generation and documentation
interfaces (Swagger UI, ReDoc) for the LankaCommerce Cloud API.

Powered by drf-spectacular — see https://drf-spectacular.readthedocs.io/

Sub-modules
-----------
urls
    URL patterns for /api/schema/, /api/docs/, /api/redoc/
extensions
    Custom preprocessing hooks and description supplements.
schemas
    Reusable serializers for error responses, tokens, and pagination.
examples
    ``OpenApiExample`` instances for request / response documentation.
"""

# ── Preprocessing hooks ──────────────────────────────────────────────
from apps.core.api_docs.extensions import (  # noqa: E402
    DESCRIPTION_SUPPLEMENT,
    TENANT_HEADER_PARAMETER,
    custom_preprocessing_hook,
)

# ── Reusable response schemas ────────────────────────────────────────
from apps.core.api_docs.schemas import (  # noqa: E402
    AuthenticationErrorResponseSerializer,
    ErrorResponseSerializer,
    NotFoundResponseSerializer,
    PaginatedResponseSerializer,
    PermissionDeniedResponseSerializer,
    RateLimitExceededResponseSerializer,
    TokenRefreshResponseSerializer,
    TokenResponseSerializer,
    ValidationErrorResponseSerializer,
)

# ── Request / response examples ──────────────────────────────────────
from apps.core.api_docs.examples import (  # noqa: E402
    AUTHENTICATION_ERROR_RESPONSE_EXAMPLE,
    CREATE_CUSTOMER_REQUEST_EXAMPLE,
    CREATE_ORDER_REQUEST_EXAMPLE,
    CREATE_PRODUCT_REQUEST_EXAMPLE,
    LOGIN_REQUEST_EXAMPLE,
    LOGIN_RESPONSE_EXAMPLE,
    NOT_FOUND_RESPONSE_EXAMPLE,
    ORDER_RESPONSE_EXAMPLE,
    PERMISSION_DENIED_RESPONSE_EXAMPLE,
    PRODUCT_LIST_RESPONSE_EXAMPLE,
    PRODUCT_RESPONSE_EXAMPLE,
    RATE_LIMIT_RESPONSE_EXAMPLE,
    TOKEN_REFRESH_REQUEST_EXAMPLE,
    TOKEN_REFRESH_RESPONSE_EXAMPLE,
    UPDATE_PRODUCT_REQUEST_EXAMPLE,
    VALIDATION_ERROR_RESPONSE_EXAMPLE,
)

__all__: list[str] = [
    # Preprocessing
    "custom_preprocessing_hook",
    "DESCRIPTION_SUPPLEMENT",
    "TENANT_HEADER_PARAMETER",
    # Schemas
    "ErrorResponseSerializer",
    "ValidationErrorResponseSerializer",
    "AuthenticationErrorResponseSerializer",
    "PermissionDeniedResponseSerializer",
    "NotFoundResponseSerializer",
    "RateLimitExceededResponseSerializer",
    "TokenResponseSerializer",
    "TokenRefreshResponseSerializer",
    "PaginatedResponseSerializer",
    # Examples — requests
    "LOGIN_REQUEST_EXAMPLE",
    "TOKEN_REFRESH_REQUEST_EXAMPLE",
    "CREATE_PRODUCT_REQUEST_EXAMPLE",
    "UPDATE_PRODUCT_REQUEST_EXAMPLE",
    "CREATE_ORDER_REQUEST_EXAMPLE",
    "CREATE_CUSTOMER_REQUEST_EXAMPLE",
    # Examples — responses
    "LOGIN_RESPONSE_EXAMPLE",
    "TOKEN_REFRESH_RESPONSE_EXAMPLE",
    "PRODUCT_RESPONSE_EXAMPLE",
    "PRODUCT_LIST_RESPONSE_EXAMPLE",
    "ORDER_RESPONSE_EXAMPLE",
    "VALIDATION_ERROR_RESPONSE_EXAMPLE",
    "AUTHENTICATION_ERROR_RESPONSE_EXAMPLE",
    "PERMISSION_DENIED_RESPONSE_EXAMPLE",
    "NOT_FOUND_RESPONSE_EXAMPLE",
    "RATE_LIMIT_RESPONSE_EXAMPLE",
]
