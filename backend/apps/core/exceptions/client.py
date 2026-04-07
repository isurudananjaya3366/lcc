"""
Client-side error exceptions (HTTP 4xx).

These exceptions represent errors caused by the client's request, such as
invalid input, missing resources, or conflicts with existing state.
"""

from __future__ import annotations

from typing import Any

from rest_framework import status

from apps.core.exceptions.base import APIException


class ValidationException(APIException):
    """
    Raised when request data fails validation.

    ``details`` typically contains a mapping of field names to error lists,
    mirroring DRF's serializer error structure::

        raise ValidationException(
            message="Invalid input.",
            details={"email": ["Enter a valid email address."]},
        )
    """

    status_code = status.HTTP_400_BAD_REQUEST
    default_error_code = "VALIDATION_ERROR"
    default_message = "Invalid input data."

    def __init__(
        self,
        message: str | None = None,
        error_code: str | None = None,
        details: dict[str, Any] | list | None = None,
        field_errors: dict[str, list[str]] | None = None,
    ) -> None:
        if field_errors and details is None:
            details = field_errors
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
        self.field_errors = field_errors or {}


class NotFoundException(APIException):
    """
    Raised when a requested resource cannot be found.

    Example::

        raise NotFoundException(
            message="Product not found.",
            details={"product_id": "abc-123"},
        )
    """

    status_code = status.HTTP_404_NOT_FOUND
    default_error_code = "NOT_FOUND"
    default_message = "The requested resource was not found."


class ConflictException(APIException):
    """
    Raised when the request conflicts with existing state.

    Common scenarios include duplicate unique keys, concurrent modification
    of the same record, or status transitions that are no longer valid.
    """

    status_code = status.HTTP_409_CONFLICT
    default_error_code = "CONFLICT"
    default_message = "The request conflicts with the current state of the resource."


class RateLimitException(APIException):
    """
    Raised when a client exceeds the allowed request rate.

    Handlers should include ``Retry-After`` headers when surfacing this
    exception.
    """

    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_error_code = "RATE_LIMIT_EXCEEDED"
    default_message = "Too many requests. Please try again later."

    def __init__(
        self,
        message: str | None = None,
        error_code: str | None = None,
        details: dict[str, Any] | list | None = None,
        retry_after: int | None = None,
    ) -> None:
        super().__init__(message=message, error_code=error_code, details=details)
        self.retry_after = retry_after
