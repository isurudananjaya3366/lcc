"""
Core Exception Classes

Provides the exception hierarchy for the LankaCommerce Cloud API.

Exception Hierarchy:
    APIException (base)
    ├── Client Errors (4xx)
    │   ├── ValidationException (400)
    │   ├── AuthenticationException (401)
    │   ├── PermissionDeniedException (403)
    │   ├── NotFoundException (404)
    │   ├── ConflictException (409)
    │   └── RateLimitException (429)
    ├── Auth / Token Errors
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

Utilities:
    ErrorResponse: Standardised error response builder.
    custom_exception_handler: DRF-compatible global handler.
    log_exception: Context-enriched error logging.
"""

from apps.core.exceptions.base import APIException
from apps.core.exceptions.client import (
    ConflictException,
    NotFoundException,
    RateLimitException,
    ValidationException,
)
from apps.core.exceptions.auth import (
    AuthenticationException,
    InvalidTokenException,
    PermissionDeniedException,
    TenantInactiveException,
    TenantNotFoundException,
    TokenExpiredException,
)
from apps.core.exceptions.server import (
    BusinessRuleException,
    ResourceExistsException,
    ServerException,
    ServiceUnavailableException,
)
from apps.core.exceptions.handlers import custom_exception_handler
from apps.core.exceptions.response import ErrorResponse

__all__ = [
    # Base
    "APIException",
    # Client errors
    "ValidationException",
    "NotFoundException",
    "ConflictException",
    "RateLimitException",
    # Auth errors
    "AuthenticationException",
    "PermissionDeniedException",
    "InvalidTokenException",
    "TokenExpiredException",
    "TenantNotFoundException",
    "TenantInactiveException",
    # Server errors
    "ServerException",
    "ServiceUnavailableException",
    "BusinessRuleException",
    "ResourceExistsException",
    # Utilities
    "ErrorResponse",
    "custom_exception_handler",
]
