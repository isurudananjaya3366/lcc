"""
Authentication and authorisation exceptions.

These cover token validation failures, permission denials, and
multi-tenant access issues.
"""

from __future__ import annotations

from typing import Any

from rest_framework import status

from apps.core.exceptions.base import APIException


# ------------------------------------------------------------------
# Auth 401 / 403
# ------------------------------------------------------------------


class AuthenticationException(APIException):
    """Raised when the request lacks valid authentication credentials."""

    status_code = status.HTTP_401_UNAUTHORIZED
    default_error_code = "AUTHENTICATION_FAILED"
    default_message = "Authentication credentials were not provided or are invalid."


class PermissionDeniedException(APIException):
    """Raised when the authenticated user lacks the required permissions."""

    status_code = status.HTTP_403_FORBIDDEN
    default_error_code = "PERMISSION_DENIED"
    default_message = "You do not have permission to perform this action."

    def __init__(
        self,
        message: str | None = None,
        error_code: str | None = None,
        details: dict[str, Any] | list | None = None,
        required_permission: str | None = None,
    ) -> None:
        if required_permission and details is None:
            details = {"required_permission": required_permission}
        super().__init__(message=message, error_code=error_code, details=details)
        self.required_permission = required_permission


# ------------------------------------------------------------------
# Token errors
# ------------------------------------------------------------------


class InvalidTokenException(APIException):
    """Raised when a JWT / access token cannot be decoded or verified."""

    status_code = status.HTTP_401_UNAUTHORIZED
    default_error_code = "INVALID_TOKEN"
    default_message = "The provided token is invalid."


class TokenExpiredException(APIException):
    """Raised when a JWT / access token has passed its expiry time."""

    status_code = status.HTTP_401_UNAUTHORIZED
    default_error_code = "TOKEN_EXPIRED"
    default_message = "The provided token has expired."


# ------------------------------------------------------------------
# Tenant errors
# ------------------------------------------------------------------


class TenantNotFoundException(APIException):
    """Raised when the resolved tenant does not exist."""

    status_code = status.HTTP_404_NOT_FOUND
    default_error_code = "TENANT_NOT_FOUND"
    default_message = "The specified tenant could not be found."


class TenantInactiveException(APIException):
    """Raised when the resolved tenant exists but is inactive / suspended."""

    status_code = status.HTTP_403_FORBIDDEN
    default_error_code = "TENANT_INACTIVE"
    default_message = "The specified tenant account is inactive."
