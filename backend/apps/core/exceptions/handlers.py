"""
Global DRF exception handler.

Plug into Django REST Framework via settings::

    REST_FRAMEWORK = {
        "EXCEPTION_HANDLER": "apps.core.exceptions.handlers.custom_exception_handler",
    }

This handler converts *all* exceptions — both DRF-native and custom
:class:`APIException` subclasses — into a consistent JSON error envelope
produced by :class:`~apps.core.exceptions.response.ErrorResponse`.
"""

from __future__ import annotations

import logging
from typing import Any

from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import (
    APIException as DRFAPIException,
    AuthenticationFailed,
    NotAuthenticated,
    NotFound,
    PermissionDenied as DRFPermissionDenied,
    ValidationError as DRFValidationError,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from apps.core.exceptions.base import APIException
from apps.core.exceptions.response import ErrorResponse

logger = logging.getLogger("apps.core.exceptions")


# ------------------------------------------------------------------
# Mapping of DRF / Django built-in exceptions → our error codes
# ------------------------------------------------------------------

_DRF_STATUS_MAP: dict[int, str] = {
    status.HTTP_400_BAD_REQUEST: "VALIDATION_ERROR",
    status.HTTP_401_UNAUTHORIZED: "AUTHENTICATION_FAILED",
    status.HTTP_403_FORBIDDEN: "PERMISSION_DENIED",
    status.HTTP_404_NOT_FOUND: "NOT_FOUND",
    status.HTTP_405_METHOD_NOT_ALLOWED: "METHOD_NOT_ALLOWED",
    status.HTTP_429_TOO_MANY_REQUESTS: "RATE_LIMIT_EXCEEDED",
}


def custom_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """
    Custom exception handler for Django REST Framework.

    Parameters
    ----------
    exc : Exception
        The exception that was raised.
    context : dict
        DRF context containing the view, request, etc.

    Returns
    -------
    Response or None
        A DRF ``Response`` with standardised error envelope, or ``None``
        if the exception should propagate (should not normally happen).
    """

    # ------------------------------------------------------------------
    # 1.  Convert Django core exceptions to DRF equivalents
    # ------------------------------------------------------------------
    if isinstance(exc, Http404):
        exc = NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = DRFPermissionDenied()
    elif isinstance(exc, DjangoValidationError):
        # Django's own ValidationError → DRF ValidationError
        if hasattr(exc, "message_dict"):
            exc = DRFValidationError(detail=exc.message_dict)
        else:
            exc = DRFValidationError(detail=exc.messages)

    # ------------------------------------------------------------------
    # 2.  Our custom APIException subclasses (preferred path)
    # ------------------------------------------------------------------
    if isinstance(exc, APIException):
        _log_exception(exc, context)
        return ErrorResponse(exc).to_response()

    # ------------------------------------------------------------------
    # 3.  Standard DRF exceptions
    # ------------------------------------------------------------------
    if isinstance(exc, DRFAPIException):
        error_code = _DRF_STATUS_MAP.get(exc.status_code, "API_ERROR")
        message = _extract_message(exc)

        api_exc = APIException(
            message=message,
            error_code=error_code,
            details=_extract_details(exc),
            status_code=exc.status_code,
        )
        _log_exception(api_exc, context)
        return ErrorResponse(api_exc).to_response()

    # ------------------------------------------------------------------
    # 4.  Unhandled / unexpected exceptions
    # ------------------------------------------------------------------
    # In DEBUG mode let DRF raise its default error page.
    if getattr(settings, "DEBUG", False):
        response = drf_exception_handler(exc, context)
        if response is not None:
            return response

    # Production: return a generic 500 envelope and log the real error.
    logger.exception(
        "Unhandled exception in %s: %s",
        _view_name(context),
        exc,
    )
    api_exc = APIException(
        message="An internal server error occurred.",
        error_code="INTERNAL_SERVER_ERROR",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
    return ErrorResponse(api_exc).to_response()


# ------------------------------------------------------------------
# Private helpers
# ------------------------------------------------------------------


def _extract_message(exc: DRFAPIException) -> str:
    """Pull a single human-readable string from a DRF exception."""
    detail = exc.detail
    if isinstance(detail, str):
        return detail
    if isinstance(detail, list):
        return "; ".join(str(d) for d in detail)
    if isinstance(detail, dict):
        # Flatten {"field": ["error"]} → "field: error; …"
        parts: list[str] = []
        for field, errors in detail.items():
            if isinstance(errors, list):
                for e in errors:
                    parts.append(f"{field}: {e}")
            else:
                parts.append(f"{field}: {errors}")
        return "; ".join(parts) if parts else str(detail)
    return str(detail)


def _extract_details(exc: DRFAPIException) -> dict[str, Any] | list | None:
    """Pull structured details from a DRF exception if available."""
    detail = exc.detail
    if isinstance(detail, (dict, list)):
        return detail  # type: ignore[return-value]
    return None


def _view_name(context: dict[str, Any]) -> str:
    """Resolve a human-readable view name from DRF context."""
    view = context.get("view")
    if view is None:
        return "<unknown>"
    cls = getattr(view, "__class__", None)
    if cls:
        return f"{cls.__module__}.{cls.__name__}"
    return str(view)


def _log_exception(exc: APIException, context: dict[str, Any]) -> None:
    """Log the exception at an appropriate level."""
    view_name = _view_name(context)
    if exc.status_code >= 500:
        logger.error(
            "[%s] %s in %s | details=%s",
            exc.error_code,
            exc.message,
            view_name,
            exc.details,
        )
    elif exc.status_code >= 400:
        logger.warning(
            "[%s] %s in %s | details=%s",
            exc.error_code,
            exc.message,
            view_name,
            exc.details,
        )
