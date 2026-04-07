"""
Tests for the global DRF exception handler.

Tasks 80-81: Tests for custom_exception_handler in
apps.core.exceptions.handlers.
"""

from unittest.mock import patch, MagicMock

from django.core.exceptions import (
    PermissionDenied as DjangoPermissionDenied,
    ValidationError as DjangoValidationError,
)
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import (
    AuthenticationFailed,
    NotFound,
    PermissionDenied as DRFPermissionDenied,
    Throttled,
    ValidationError as DRFValidationError,
)
from rest_framework.test import APIRequestFactory

from apps.core.exceptions.handlers import custom_exception_handler
from apps.core.exceptions.base import APIException
from apps.core.exceptions.client import (
    NotFoundException,
    ValidationException,
    RateLimitException,
)
from apps.core.exceptions.auth import (
    AuthenticationException,
    PermissionDeniedException,
)
from apps.core.exceptions.server import (
    ServerException,
    BusinessRuleException,
    ServiceUnavailableException,
)


def _make_context(view_name: str = "TestView") -> dict:
    """Build a minimal DRF handler context."""
    factory = APIRequestFactory()
    request = factory.get("/test/")
    mock_view = MagicMock()
    mock_view.__class__.__name__ = view_name
    mock_view.__class__.__module__ = "tests"
    return {"view": mock_view, "request": request}


# ------------------------------------------------------------------ #
# Our custom APIException subclasses
# ------------------------------------------------------------------ #


class TestHandlerCustomExceptions:
    """Verify handler processes our custom exception hierarchy."""

    def test_validation_exception(self):
        exc = ValidationException(message="Bad input")
        resp = custom_exception_handler(exc, _make_context())
        assert resp.status_code == 400
        assert resp.data["success"] is False
        assert resp.data["error"]["error_code"] == "VALIDATION_ERROR"

    def test_not_found_exception(self):
        exc = NotFoundException()
        resp = custom_exception_handler(exc, _make_context())
        assert resp.status_code == 404
        assert resp.data["error"]["error_code"] == "NOT_FOUND"

    def test_authentication_exception(self):
        exc = AuthenticationException()
        resp = custom_exception_handler(exc, _make_context())
        assert resp.status_code == 401

    def test_permission_denied_exception(self):
        exc = PermissionDeniedException(required_permission="edit_order")
        resp = custom_exception_handler(exc, _make_context())
        assert resp.status_code == 403
        assert resp.data["error"]["error_code"] == "PERMISSION_DENIED"

    def test_rate_limit_exception(self):
        exc = RateLimitException(retry_after=30)
        resp = custom_exception_handler(exc, _make_context())
        assert resp.status_code == 429
        assert resp["Retry-After"] == "30"

    def test_server_exception(self):
        exc = ServerException()
        resp = custom_exception_handler(exc, _make_context())
        assert resp.status_code == 500

    def test_business_rule_exception(self):
        exc = BusinessRuleException(rule_code="MAX_QTY_EXCEEDED")
        resp = custom_exception_handler(exc, _make_context())
        assert resp.status_code == 422
        assert resp.data["error"]["error_code"] == "BUSINESS_RULE_VIOLATION"

    def test_service_unavailable_exception(self):
        exc = ServiceUnavailableException(service_name="redis", retry_after=60)
        resp = custom_exception_handler(exc, _make_context())
        assert resp.status_code == 503
        assert resp["Retry-After"] == "60"


# ------------------------------------------------------------------ #
# Django core exceptions converted by the handler
# ------------------------------------------------------------------ #


class TestHandlerDjangoExceptions:
    """Verify Django exceptions are converted to structured responses."""

    def test_http404_converted(self):
        exc = Http404("Page not found")
        resp = custom_exception_handler(exc, _make_context())
        assert resp is not None
        assert resp.status_code == 404
        assert resp.data["success"] is False

    def test_django_permission_denied(self):
        exc = DjangoPermissionDenied("Forbidden")
        resp = custom_exception_handler(exc, _make_context())
        assert resp is not None
        assert resp.status_code == 403

    def test_django_validation_error_list(self):
        exc = DjangoValidationError(["Field is required."])
        resp = custom_exception_handler(exc, _make_context())
        assert resp is not None
        assert resp.status_code == 400

    def test_django_validation_error_dict(self):
        exc = DjangoValidationError({"email": ["Enter a valid email."]})
        resp = custom_exception_handler(exc, _make_context())
        assert resp is not None
        assert resp.status_code == 400


# ------------------------------------------------------------------ #
# DRF native exceptions
# ------------------------------------------------------------------ #


class TestHandlerDRFExceptions:
    """Verify DRF native exceptions are wrapped in our envelope."""

    def test_drf_authentication_failed(self):
        exc = AuthenticationFailed()
        resp = custom_exception_handler(exc, _make_context())
        assert resp is not None
        assert resp.status_code == 401
        assert resp.data["success"] is False

    def test_drf_permission_denied(self):
        exc = DRFPermissionDenied()
        resp = custom_exception_handler(exc, _make_context())
        assert resp.status_code == 403

    def test_drf_not_found(self):
        exc = NotFound()
        resp = custom_exception_handler(exc, _make_context())
        assert resp.status_code == 404

    def test_drf_validation_error(self):
        exc = DRFValidationError({"name": ["This field is required."]})
        resp = custom_exception_handler(exc, _make_context())
        assert resp.status_code == 400
        assert resp.data["error"]["error_code"] == "VALIDATION_ERROR"

    def test_drf_throttled(self):
        exc = Throttled(wait=45)
        resp = custom_exception_handler(exc, _make_context())
        assert resp.status_code == 429


# ------------------------------------------------------------------ #
# Unhandled exceptions → 500
# ------------------------------------------------------------------ #


class TestHandlerUnhandledExceptions:
    """Unhandled exceptions should produce a generic 500 response."""

    @patch("apps.core.exceptions.handlers.settings", DEBUG=False)
    def test_unhandled_exception_returns_500(self, _mock_settings):
        exc = RuntimeError("Something broke")
        resp = custom_exception_handler(exc, _make_context())
        assert resp is not None
        assert resp.status_code == 500
        assert resp.data["success"] is False
        assert resp.data["error"]["error_code"] == "INTERNAL_SERVER_ERROR"


# ------------------------------------------------------------------ #
# Response structure
# ------------------------------------------------------------------ #


class TestHandlerResponseStructure:
    """The response envelope must always contain the standard keys."""

    def test_envelope_keys(self):
        exc = NotFoundException()
        resp = custom_exception_handler(exc, _make_context())
        data = resp.data
        assert "success" in data
        assert "error" in data
        error = data["error"]
        assert "error_code" in error
        assert "message" in error
        assert "timestamp" in error

    def test_success_is_false(self):
        exc = ValidationException()
        resp = custom_exception_handler(exc, _make_context())
        assert resp.data["success"] is False
