"""
Tests for ErrorResponse.

Task 81: Tests for apps.core.exceptions.response.ErrorResponse.
"""

from apps.core.exceptions.base import APIException
from apps.core.exceptions.client import RateLimitException, ValidationException
from apps.core.exceptions.response import ErrorResponse
from apps.core.exceptions.server import ServiceUnavailableException


class TestErrorResponseToDict:
    """Tests for ErrorResponse.to_dict()."""

    def test_envelope_structure(self):
        exc = APIException(message="Oops", error_code="TEST_ERROR")
        d = ErrorResponse(exc).to_dict()
        assert d["success"] is False
        assert "error" in d
        error = d["error"]
        assert error["error_code"] == "TEST_ERROR"
        assert error["message"] == "Oops"
        assert "timestamp" in error

    def test_details_included_when_present(self):
        exc = ValidationException(field_errors={"name": ["Required."]})
        d = ErrorResponse(exc).to_dict()
        assert d["error"]["details"] == {"name": ["Required."]}

    def test_details_absent_when_none(self):
        exc = APIException()
        d = ErrorResponse(exc).to_dict()
        assert "details" not in d["error"]

    def test_timestamp_is_iso_string(self):
        exc = APIException()
        d = ErrorResponse(exc).to_dict()
        ts = d["error"]["timestamp"]
        assert isinstance(ts, str)
        # ISO timestamps contain "T"
        assert "T" in ts


class TestErrorResponseToResponse:
    """Tests for ErrorResponse.to_response()."""

    def test_returns_drf_response(self):
        from rest_framework.response import Response

        exc = APIException()
        resp = ErrorResponse(exc).to_response()
        assert isinstance(resp, Response)

    def test_status_code_matches(self):
        exc = APIException(status_code=422)
        resp = ErrorResponse(exc).to_response()
        assert resp.status_code == 422

    def test_retry_after_header_for_rate_limit(self):
        exc = RateLimitException(retry_after=90)
        resp = ErrorResponse(exc).to_response()
        assert resp["Retry-After"] == "90"

    def test_retry_after_header_for_service_unavailable(self):
        exc = ServiceUnavailableException(retry_after=300)
        resp = ErrorResponse(exc).to_response()
        assert resp["Retry-After"] == "300"

    def test_no_retry_after_header_when_none(self):
        exc = APIException()
        resp = ErrorResponse(exc).to_response()
        assert resp.get("Retry-After") is None


class TestErrorResponseFromValues:
    """Tests for ErrorResponse.from_values() factory method."""

    def test_creates_error_response(self):
        er = ErrorResponse.from_values(
            error_code="CUSTOM", message="Custom error", status_code=400
        )
        assert isinstance(er, ErrorResponse)

    def test_from_values_to_dict(self):
        er = ErrorResponse.from_values(
            error_code="MY_CODE", message="Something failed", status_code=503
        )
        d = er.to_dict()
        assert d["error"]["error_code"] == "MY_CODE"
        assert d["error"]["message"] == "Something failed"
        assert d["success"] is False

    def test_from_values_status_code(self):
        er = ErrorResponse.from_values(
            error_code="E", message="m", status_code=502
        )
        resp = er.to_response()
        assert resp.status_code == 502

    def test_from_values_with_details(self):
        details = {"info": "extra"}
        er = ErrorResponse.from_values(
            error_code="E", message="m", details=details
        )
        d = er.to_dict()
        assert d["error"]["details"] == details

    def test_from_values_default_status_code(self):
        er = ErrorResponse.from_values(error_code="E", message="m")
        resp = er.to_response()
        assert resp.status_code == 500
