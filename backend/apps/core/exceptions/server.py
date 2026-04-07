"""
Server-side and business-logic exceptions.

Server errors (5xx) indicate the failure is on the server, not the client.
Business-rule violations are semantically distinct from validation errors
and use HTTP 422 (Unprocessable Entity).
"""

from __future__ import annotations

from typing import Any

from rest_framework import status

from apps.core.exceptions.base import APIException


# ------------------------------------------------------------------
# 5xx server errors
# ------------------------------------------------------------------


class ServerException(APIException):
    """Generic internal server error."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_error_code = "INTERNAL_SERVER_ERROR"
    default_message = "An internal server error occurred."


class ServiceUnavailableException(APIException):
    """Raised when a required external service is unreachable."""

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_error_code = "SERVICE_UNAVAILABLE"
    default_message = "The service is temporarily unavailable. Please try again later."

    def __init__(
        self,
        message: str | None = None,
        error_code: str | None = None,
        details: dict[str, Any] | list | None = None,
        service_name: str | None = None,
        retry_after: int | None = None,
    ) -> None:
        if service_name and details is None:
            details = {"service": service_name}
        super().__init__(message=message, error_code=error_code, details=details)
        self.service_name = service_name
        self.retry_after = retry_after


# ------------------------------------------------------------------
# Business-rule errors
# ------------------------------------------------------------------


class BusinessRuleException(APIException):
    """
    Raised when a business rule is violated.

    These are distinct from validation errors — the data is well-formed
    but violates a domain invariant (e.g. "Cannot delete a user with
    open orders").

    Uses HTTP 422 Unprocessable Entity.
    """

    status_code = 422  # HTTP_422_UNPROCESSABLE_ENTITY (not in older DRF)
    default_error_code = "BUSINESS_RULE_VIOLATION"
    default_message = "A business rule has been violated."

    def __init__(
        self,
        message: str | None = None,
        error_code: str | None = None,
        details: dict[str, Any] | list | None = None,
        rule_code: str | None = None,
    ) -> None:
        if rule_code:
            details = details or {}
            if isinstance(details, dict):
                details["rule_code"] = rule_code
        super().__init__(message=message, error_code=error_code, details=details)
        self.rule_code = rule_code


class ResourceExistsException(APIException):
    """
    Raised when an attempt is made to create a resource that already exists.

    This is a specialised form of :class:`ConflictException` that carries
    the identity of the existing resource for easier client handling.
    """

    status_code = status.HTTP_409_CONFLICT
    default_error_code = "RESOURCE_EXISTS"
    default_message = "The resource already exists."

    def __init__(
        self,
        message: str | None = None,
        error_code: str | None = None,
        details: dict[str, Any] | list | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
    ) -> None:
        if resource_type and details is None:
            details = {
                "resource_type": resource_type,
                "resource_id": resource_id,
            }
        super().__init__(message=message, error_code=error_code, details=details)
        self.resource_type = resource_type
        self.resource_id = resource_id
