"""
API Documentation Schemas.

Reusable OpenAPI schema components for error responses, pagination,
authentication tokens, and other common response shapes used across
the LankaCommerce Cloud API.

These serializers are *not* used at runtime — they exist solely to
generate accurate OpenAPI component schemas so that consumers of the
documentation can understand the exact shape of every response.

Usage with ``drf-spectacular``::

    from drf_spectacular.utils import extend_schema
    from apps.core.api_docs.schemas import ValidationErrorResponseSerializer

    class MyView(APIView):
        @extend_schema(responses={400: ValidationErrorResponseSerializer})
        def post(self, request): ...
"""

from __future__ import annotations

from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers


# ═══════════════════════════════════════════════════════════════════════
# Base error envelope
# ═══════════════════════════════════════════════════════════════════════


class ErrorResponseSerializer(serializers.Serializer):
    """
    Standard error response envelope.

    Every error returned by the API conforms to this shape.
    """

    error_code = serializers.CharField(
        help_text="Machine-readable error code (e.g. ``VALIDATION_ERROR``).",
    )
    message = serializers.CharField(
        help_text="Human-readable error description.",
    )
    details = serializers.DictField(
        required=False,
        allow_null=True,
        help_text="Optional field-level or contextual error details.",
    )


# ═══════════════════════════════════════════════════════════════════════
# Specific error responses
# ═══════════════════════════════════════════════════════════════════════


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Validation Error",
            value={
                "error_code": "VALIDATION_ERROR",
                "message": "Invalid input data.",
                "details": {
                    "price": ["Ensure this value is greater than 0."],
                },
            },
            response_only=True,
            status_codes=["400"],
        ),
    ],
)
class ValidationErrorResponseSerializer(serializers.Serializer):
    """Validation error response (HTTP 400)."""

    error_code = serializers.CharField(
        default="VALIDATION_ERROR",
        help_text="Machine-readable error code.",
    )
    message = serializers.CharField(
        default="Invalid input data.",
        help_text="Human-readable error summary.",
    )
    details = serializers.DictField(
        help_text="Field-level validation errors keyed by field name.",
    )


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Authentication Error",
            value={
                "error_code": "AUTHENTICATION_FAILED",
                "message": "Authentication credentials were not provided.",
            },
            response_only=True,
            status_codes=["401"],
        ),
    ],
)
class AuthenticationErrorResponseSerializer(serializers.Serializer):
    """Authentication error response (HTTP 401)."""

    error_code = serializers.CharField(
        default="AUTHENTICATION_FAILED",
        help_text="Machine-readable error code.",
    )
    message = serializers.CharField(
        default="Authentication credentials were not provided.",
        help_text="Human-readable error description.",
    )


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Permission Denied",
            value={
                "error_code": "PERMISSION_DENIED",
                "message": "You do not have permission to perform this action.",
            },
            response_only=True,
            status_codes=["403"],
        ),
    ],
)
class PermissionDeniedResponseSerializer(serializers.Serializer):
    """Permission denied response (HTTP 403)."""

    error_code = serializers.CharField(
        default="PERMISSION_DENIED",
        help_text="Machine-readable error code.",
    )
    message = serializers.CharField(
        default="You do not have permission to perform this action.",
        help_text="Human-readable error description.",
    )


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Not Found",
            value={
                "error_code": "NOT_FOUND",
                "message": "The requested resource was not found.",
            },
            response_only=True,
            status_codes=["404"],
        ),
    ],
)
class NotFoundResponseSerializer(serializers.Serializer):
    """Not found response (HTTP 404)."""

    error_code = serializers.CharField(
        default="NOT_FOUND",
        help_text="Machine-readable error code.",
    )
    message = serializers.CharField(
        default="The requested resource was not found.",
        help_text="Human-readable error description.",
    )


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Rate Limit Exceeded",
            value={
                "error_code": "RATE_LIMIT_EXCEEDED",
                "message": "API rate limit exceeded. Please wait before retrying.",
                "details": {
                    "retry_after": 3600,
                    "limit": 1000,
                    "reset_at": "2024-01-15T15:00:00Z",
                },
            },
            response_only=True,
            status_codes=["429"],
        ),
    ],
)
class RateLimitExceededResponseSerializer(serializers.Serializer):
    """Rate limit exceeded response (HTTP 429)."""

    error_code = serializers.CharField(
        default="RATE_LIMIT_EXCEEDED",
        help_text="Machine-readable error code.",
    )
    message = serializers.CharField(
        default="API rate limit exceeded. Please wait before retrying.",
        help_text="Human-readable error description.",
    )
    details = serializers.DictField(
        help_text="Rate-limit context (retry_after, limit, reset_at).",
    )


# ═══════════════════════════════════════════════════════════════════════
# Authentication token schemas
# ═══════════════════════════════════════════════════════════════════════


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Token Pair",
            value={
                "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9…",
                "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9…",
            },
            response_only=True,
            status_codes=["200"],
        ),
    ],
)
class TokenResponseSerializer(serializers.Serializer):
    """JWT token pair returned by ``/api/token/``."""

    access = serializers.CharField(
        help_text="Short-lived JWT access token (60 min).",
    )
    refresh = serializers.CharField(
        help_text="Long-lived JWT refresh token (24 hours).",
    )


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Refreshed Access Token",
            value={
                "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9…",
            },
            response_only=True,
            status_codes=["200"],
        ),
    ],
)
class TokenRefreshResponseSerializer(serializers.Serializer):
    """Refreshed access token returned by ``/api/token/refresh/``."""

    access = serializers.CharField(
        help_text="New short-lived JWT access token.",
    )


# ═══════════════════════════════════════════════════════════════════════
# Pagination schema
# ═══════════════════════════════════════════════════════════════════════


class PaginatedResponseSerializer(serializers.Serializer):
    """
    Pagination wrapper returned by all list endpoints.

    The ``results`` key contains an array of resource objects whose
    shape depends on the specific endpoint.
    """

    count = serializers.IntegerField(
        help_text="Total number of results across all pages.",
    )
    next = serializers.URLField(
        required=False,
        allow_null=True,
        help_text="URL of the next page (``null`` on the last page).",
    )
    previous = serializers.URLField(
        required=False,
        allow_null=True,
        help_text="URL of the previous page (``null`` on the first page).",
    )
    results = serializers.ListField(
        child=serializers.DictField(),
        help_text="Array of resource objects for the current page.",
    )
