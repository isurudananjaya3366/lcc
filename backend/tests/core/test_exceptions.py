"""
Tests for the core exception classes.

Tasks 75–79: Comprehensive tests for all exception classes in
apps.core.exceptions (base, client, auth, server).
"""

import pytest
from rest_framework import status

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


# ------------------------------------------------------------------ #
# Base APIException
# ------------------------------------------------------------------ #


class TestAPIException:
    """Tests for the base APIException class."""

    def test_default_values(self):
        exc = APIException()
        assert exc.error_code == "API_ERROR"
        assert exc.message == "An unexpected error occurred."
        assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc.details is None

    def test_custom_message(self):
        exc = APIException(message="Custom message")
        assert exc.message == "Custom message"

    def test_custom_error_code(self):
        exc = APIException(error_code="CUSTOM_CODE")
        assert exc.error_code == "CUSTOM_CODE"

    def test_custom_details(self):
        details = {"key": "value"}
        exc = APIException(details=details)
        assert exc.details == details

    def test_custom_status_code(self):
        exc = APIException(status_code=418)
        assert exc.status_code == 418

    def test_to_dict_minimal(self):
        exc = APIException()
        d = exc.to_dict()
        assert d == {"error_code": "API_ERROR", "message": "An unexpected error occurred."}

    def test_to_dict_with_details(self):
        details = {"field": "email"}
        exc = APIException(details=details)
        d = exc.to_dict()
        assert d["details"] == details

    def test_drf_detail_attribute(self):
        """DRF uses 'detail' (singular) for serialisation."""
        exc = APIException(message="Hello")
        assert exc.detail == "Hello"

    def test_drf_code_attribute(self):
        """DRF stores an error code as exc.default_code / 'code' kwarg."""
        exc = APIException(error_code="MY_CODE")
        # rest_framework stores the code via get_codes()
        assert exc.get_codes() == "MY_CODE"


# ------------------------------------------------------------------ #
# Client exceptions (4xx)
# ------------------------------------------------------------------ #


class TestValidationException:
    """Tests for ValidationException."""

    def test_defaults(self):
        exc = ValidationException()
        assert exc.status_code == 400
        assert exc.error_code == "VALIDATION_ERROR"
        assert exc.message == "Invalid input data."
        assert exc.field_errors == {}

    def test_custom_message(self):
        exc = ValidationException(message="Bad data")
        assert exc.message == "Bad data"

    def test_field_errors_kwarg(self):
        field_errors = {"email": ["Enter a valid email."]}
        exc = ValidationException(field_errors=field_errors)
        assert exc.field_errors == field_errors
        assert exc.details == field_errors

    def test_field_errors_does_not_override_explicit_details(self):
        details = {"custom": "value"}
        exc = ValidationException(details=details, field_errors={"a": ["b"]})
        assert exc.details == details

    def test_to_dict_includes_details(self):
        exc = ValidationException(field_errors={"name": ["Required."]})
        d = exc.to_dict()
        assert d["details"] == {"name": ["Required."]}

    def test_inherits_api_exception(self):
        exc = ValidationException()
        assert isinstance(exc, APIException)


class TestNotFoundException:
    """Tests for NotFoundException."""

    def test_defaults(self):
        exc = NotFoundException()
        assert exc.status_code == 404
        assert exc.error_code == "NOT_FOUND"
        assert exc.message == "The requested resource was not found."

    def test_custom_message(self):
        exc = NotFoundException(message="Product not found.")
        assert exc.message == "Product not found."

    def test_custom_details(self):
        exc = NotFoundException(details={"product_id": "abc"})
        assert exc.details["product_id"] == "abc"


class TestConflictException:
    """Tests for ConflictException."""

    def test_defaults(self):
        exc = ConflictException()
        assert exc.status_code == 409
        assert exc.error_code == "CONFLICT"
        assert "conflicts" in exc.message.lower()

    def test_custom_values(self):
        exc = ConflictException(message="Duplicate SKU", error_code="DUPLICATE_SKU")
        assert exc.message == "Duplicate SKU"
        assert exc.error_code == "DUPLICATE_SKU"


class TestRateLimitException:
    """Tests for RateLimitException."""

    def test_defaults(self):
        exc = RateLimitException()
        assert exc.status_code == 429
        assert exc.error_code == "RATE_LIMIT_EXCEEDED"
        assert exc.retry_after is None

    def test_retry_after(self):
        exc = RateLimitException(retry_after=60)
        assert exc.retry_after == 60

    def test_custom_message(self):
        exc = RateLimitException(message="Slow down")
        assert exc.message == "Slow down"


# ------------------------------------------------------------------ #
# Auth exceptions
# ------------------------------------------------------------------ #


class TestAuthenticationException:
    """Tests for AuthenticationException."""

    def test_defaults(self):
        exc = AuthenticationException()
        assert exc.status_code == 401
        assert exc.error_code == "AUTHENTICATION_FAILED"

    def test_custom_message(self):
        exc = AuthenticationException(message="Bad credentials")
        assert exc.message == "Bad credentials"


class TestPermissionDeniedException:
    """Tests for PermissionDeniedException."""

    def test_defaults(self):
        exc = PermissionDeniedException()
        assert exc.status_code == 403
        assert exc.error_code == "PERMISSION_DENIED"
        assert exc.required_permission is None

    def test_required_permission_kwarg(self):
        exc = PermissionDeniedException(required_permission="can_edit_orders")
        assert exc.required_permission == "can_edit_orders"
        assert exc.details == {"required_permission": "can_edit_orders"}

    def test_required_permission_does_not_override_explicit_details(self):
        details = {"custom": True}
        exc = PermissionDeniedException(
            details=details, required_permission="admin"
        )
        assert exc.details == details


class TestInvalidTokenException:
    """Tests for InvalidTokenException."""

    def test_defaults(self):
        exc = InvalidTokenException()
        assert exc.status_code == 401
        assert exc.error_code == "INVALID_TOKEN"
        assert exc.message == "The provided token is invalid."


class TestTokenExpiredException:
    """Tests for TokenExpiredException."""

    def test_defaults(self):
        exc = TokenExpiredException()
        assert exc.status_code == 401
        assert exc.error_code == "TOKEN_EXPIRED"
        assert exc.message == "The provided token has expired."


class TestTenantNotFoundException:
    """Tests for TenantNotFoundException."""

    def test_defaults(self):
        exc = TenantNotFoundException()
        assert exc.status_code == 404
        assert exc.error_code == "TENANT_NOT_FOUND"

    def test_custom_message(self):
        exc = TenantNotFoundException(message="Tenant xyz missing")
        assert exc.message == "Tenant xyz missing"


class TestTenantInactiveException:
    """Tests for TenantInactiveException."""

    def test_defaults(self):
        exc = TenantInactiveException()
        assert exc.status_code == 403
        assert exc.error_code == "TENANT_INACTIVE"


# ------------------------------------------------------------------ #
# Server / business-rule exceptions
# ------------------------------------------------------------------ #


class TestServerException:
    """Tests for ServerException."""

    def test_defaults(self):
        exc = ServerException()
        assert exc.status_code == 500
        assert exc.error_code == "INTERNAL_SERVER_ERROR"
        assert exc.message == "An internal server error occurred."


class TestServiceUnavailableException:
    """Tests for ServiceUnavailableException."""

    def test_defaults(self):
        exc = ServiceUnavailableException()
        assert exc.status_code == 503
        assert exc.error_code == "SERVICE_UNAVAILABLE"
        assert exc.service_name is None
        assert exc.retry_after is None

    def test_service_name_kwarg(self):
        exc = ServiceUnavailableException(service_name="payment-gateway")
        assert exc.service_name == "payment-gateway"
        assert exc.details == {"service": "payment-gateway"}

    def test_retry_after(self):
        exc = ServiceUnavailableException(retry_after=120)
        assert exc.retry_after == 120


class TestBusinessRuleException:
    """Tests for BusinessRuleException."""

    def test_defaults(self):
        exc = BusinessRuleException()
        assert exc.status_code == 422
        assert exc.error_code == "BUSINESS_RULE_VIOLATION"
        assert exc.rule_code is None

    def test_rule_code_kwarg(self):
        exc = BusinessRuleException(rule_code="ORDER_ALREADY_SHIPPED")
        assert exc.rule_code == "ORDER_ALREADY_SHIPPED"
        assert exc.details["rule_code"] == "ORDER_ALREADY_SHIPPED"

    def test_rule_code_merges_with_existing_details(self):
        exc = BusinessRuleException(
            details={"order_id": "123"}, rule_code="MAX_ITEMS"
        )
        assert exc.details["rule_code"] == "MAX_ITEMS"
        assert exc.details["order_id"] == "123"

    def test_custom_message(self):
        exc = BusinessRuleException(message="Cannot ship cancelled order")
        assert exc.message == "Cannot ship cancelled order"


class TestResourceExistsException:
    """Tests for ResourceExistsException."""

    def test_defaults(self):
        exc = ResourceExistsException()
        assert exc.status_code == 409
        assert exc.error_code == "RESOURCE_EXISTS"
        assert exc.resource_type is None
        assert exc.resource_id is None

    def test_resource_type_and_id(self):
        exc = ResourceExistsException(resource_type="Product", resource_id="42")
        assert exc.resource_type == "Product"
        assert exc.resource_id == "42"
        assert exc.details == {"resource_type": "Product", "resource_id": "42"}

    def test_explicit_details_not_overridden(self):
        details = {"custom": True}
        exc = ResourceExistsException(details=details, resource_type="X")
        assert exc.details == details


# ------------------------------------------------------------------ #
# Parametrized: default status codes
# ------------------------------------------------------------------ #


@pytest.mark.parametrize(
    "exc_class,expected_code,expected_error_code",
    [
        (APIException, 500, "API_ERROR"),
        (ValidationException, 400, "VALIDATION_ERROR"),
        (NotFoundException, 404, "NOT_FOUND"),
        (ConflictException, 409, "CONFLICT"),
        (RateLimitException, 429, "RATE_LIMIT_EXCEEDED"),
        (AuthenticationException, 401, "AUTHENTICATION_FAILED"),
        (PermissionDeniedException, 403, "PERMISSION_DENIED"),
        (InvalidTokenException, 401, "INVALID_TOKEN"),
        (TokenExpiredException, 401, "TOKEN_EXPIRED"),
        (TenantNotFoundException, 404, "TENANT_NOT_FOUND"),
        (TenantInactiveException, 403, "TENANT_INACTIVE"),
        (ServerException, 500, "INTERNAL_SERVER_ERROR"),
        (ServiceUnavailableException, 503, "SERVICE_UNAVAILABLE"),
        (BusinessRuleException, 422, "BUSINESS_RULE_VIOLATION"),
        (ResourceExistsException, 409, "RESOURCE_EXISTS"),
    ],
)
class TestExceptionStatusCodes:
    """Parametrized check that every exception has the right status/error code."""

    def test_status_code(self, exc_class, expected_code, expected_error_code):
        exc = exc_class()
        assert exc.status_code == expected_code

    def test_error_code(self, exc_class, expected_code, expected_error_code):
        exc = exc_class()
        assert exc.error_code == expected_error_code

    def test_is_api_exception(self, exc_class, expected_code, expected_error_code):
        exc = exc_class()
        assert isinstance(exc, APIException)

    def test_to_dict_structure(self, exc_class, expected_code, expected_error_code):
        exc = exc_class()
        d = exc.to_dict()
        assert "error_code" in d
        assert "message" in d
        assert d["error_code"] == expected_error_code
