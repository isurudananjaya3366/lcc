"""
Base API Exception.

All custom exceptions in the LankaCommerce Cloud API inherit from
:class:`APIException`.  It mirrors the DRF ``APIException`` interface while
adding structured ``error_code`` and ``details`` attributes so that
exception handlers can build consistent JSON error envelopes.
"""

from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.exceptions import APIException as DRFAPIException


class APIException(DRFAPIException):
    """
    Base exception for all LankaCommerce API errors.

    Attributes
    ----------
    default_error_code : str
        Machine-readable error code (e.g. ``"VALIDATION_ERROR"``).
    default_message : str
        Human-readable description shown when no explicit message is given.
    status_code : int
        HTTP status code.  Subclasses override this.
    """

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_error_code: str = "API_ERROR"
    default_message: str = "An unexpected error occurred."

    def __init__(
        self,
        message: str | None = None,
        error_code: str | None = None,
        details: dict[str, Any] | list | None = None,
        status_code: int | None = None,
    ) -> None:
        self.error_code: str = error_code or self.default_error_code
        self.message: str = message or self.default_message
        self.details: dict[str, Any] | list | None = details

        if status_code is not None:
            self.status_code = status_code

        # DRF expects ``detail`` (singular) for serialisation.
        super().__init__(detail=self.message, code=self.error_code)

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable dictionary of the error."""
        payload: dict[str, Any] = {
            "error_code": self.error_code,
            "message": self.message,
        }
        if self.details:
            payload["details"] = self.details
        return payload

    def __str__(self) -> str:  # pragma: no cover
        return f"[{self.error_code}] {self.message}"

    def __repr__(self) -> str:  # pragma: no cover
        cls = type(self).__name__
        return (
            f"{cls}(error_code={self.error_code!r}, "
            f"message={self.message!r}, "
            f"status_code={self.status_code})"
        )
