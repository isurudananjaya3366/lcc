"""
Standardised error response builder.

:class:`ErrorResponse` wraps exception data into a consistent JSON envelope
that the global exception handler returns to clients.

Envelope format::

    {
        "success": false,
        "error": {
            "error_code": "VALIDATION_ERROR",
            "message": "Invalid input data.",
            "details": {"email": ["Enter a valid email address."]},
            "timestamp": "2025-01-15T10:30:00Z"
        }
    }
"""

from __future__ import annotations

from typing import Any

from django.utils import timezone
from rest_framework.response import Response

from apps.core.exceptions.base import APIException


class ErrorResponse:
    """
    Build a DRF :class:`Response` from an :class:`APIException`.

    Usage::

        exc = ValidationException(details={"field": ["required"]})
        return ErrorResponse(exc).to_response()

    Or build from raw values::

        resp = ErrorResponse.from_values(
            error_code="CUSTOM",
            message="Something went wrong.",
            status_code=400,
        )
    """

    def __init__(self, exception: APIException) -> None:
        self.exception = exception

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Return the full envelope as a JSON-serialisable dict."""
        error_payload: dict[str, Any] = {
            "error_code": self.exception.error_code,
            "message": self.exception.message,
            "timestamp": timezone.now().isoformat(),
        }
        if self.exception.details:
            error_payload["details"] = self.exception.details
        return {
            "success": False,
            "error": error_payload,
        }

    def to_response(self) -> Response:
        """Return a DRF ``Response`` ready to be returned from a view."""
        headers: dict[str, str] = {}

        # Add Retry-After header when applicable.
        retry_after = getattr(self.exception, "retry_after", None)
        if retry_after is not None:
            headers["Retry-After"] = str(retry_after)

        return Response(
            data=self.to_dict(),
            status=self.exception.status_code,
            headers=headers or None,
        )

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def from_values(
        cls,
        error_code: str,
        message: str,
        status_code: int = 500,
        details: dict[str, Any] | list | None = None,
    ) -> "ErrorResponse":
        """Create an :class:`ErrorResponse` from raw values."""
        exc = APIException(
            message=message,
            error_code=error_code,
            details=details,
            status_code=status_code,
        )
        return cls(exception=exc)
