"""
Tests for exception logging utilities.

Task 82: Tests for apps.core.exceptions.logging (log_exception,
log_business_rule_violation, get_client_ip).
"""

import logging
from unittest.mock import patch, MagicMock

from django.http import HttpRequest

from apps.core.exceptions.logging import (
    get_client_ip,
    log_business_rule_violation,
    log_exception,
)
from apps.core.exceptions.base import APIException


LOGGER_PATH = "apps.core.exceptions.logging.logger"


# ------------------------------------------------------------------ #
# get_client_ip
# ------------------------------------------------------------------ #


class TestGetClientIP:
    """Tests for get_client_ip()."""

    def test_x_forwarded_for_single(self):
        request = HttpRequest()
        request.META["HTTP_X_FORWARDED_FOR"] = "1.2.3.4"
        assert get_client_ip(request) == "1.2.3.4"

    def test_x_forwarded_for_multiple(self):
        request = HttpRequest()
        request.META["HTTP_X_FORWARDED_FOR"] = "10.0.0.1, 192.168.1.1, 172.16.0.1"
        assert get_client_ip(request) == "10.0.0.1"

    def test_remote_addr_fallback(self):
        request = HttpRequest()
        request.META["REMOTE_ADDR"] = "127.0.0.1"
        assert get_client_ip(request) == "127.0.0.1"

    def test_unknown_when_no_headers(self):
        request = HttpRequest()
        assert get_client_ip(request) == "unknown"


# ------------------------------------------------------------------ #
# log_exception
# ------------------------------------------------------------------ #


class TestLogException:
    """Tests for log_exception()."""

    @patch(LOGGER_PATH)
    def test_logs_at_error_by_default(self, mock_logger):
        exc = APIException(message="Kaboom")
        log_exception(exc)
        mock_logger.log.assert_called_once()
        call_args = mock_logger.log.call_args
        assert call_args[0][0] == logging.ERROR

    @patch(LOGGER_PATH)
    def test_logs_at_custom_level(self, mock_logger):
        exc = APIException()
        log_exception(exc, level=logging.WARNING)
        call_args = mock_logger.log.call_args
        assert call_args[0][0] == logging.WARNING

    @patch(LOGGER_PATH)
    def test_includes_error_code_in_message(self, mock_logger):
        exc = APIException(error_code="MY_CODE", message="test msg")
        log_exception(exc)
        logged_msg_args = mock_logger.log.call_args[0]
        # The format string contains %s placeholders for error_code and message
        assert "MY_CODE" in str(logged_msg_args)
        assert "test msg" in str(logged_msg_args)

    @patch(LOGGER_PATH)
    def test_includes_request_context(self, mock_logger):
        exc = APIException()
        request = HttpRequest()
        request.META["REMOTE_ADDR"] = "10.0.0.5"
        request.method = "POST"
        request.path = "/api/test/"
        log_exception(exc, request=request)
        call_args = mock_logger.log.call_args
        # Context dict is the last positional arg
        ctx = call_args[0][-1]
        assert "10.0.0.5" in str(ctx)

    @patch(LOGGER_PATH)
    def test_extra_merged_into_context(self, mock_logger):
        exc = APIException()
        log_exception(exc, extra={"order_id": "999"})
        call_args = mock_logger.log.call_args
        ctx = call_args[0][-1]
        assert ctx.get("order_id") == "999"

    @patch(LOGGER_PATH)
    def test_exc_info_true_for_error_level(self, mock_logger):
        exc = APIException()
        log_exception(exc, level=logging.ERROR)
        call_kwargs = mock_logger.log.call_args[1]
        assert call_kwargs.get("exc_info") is True

    @patch(LOGGER_PATH)
    def test_exc_info_false_for_warning_level(self, mock_logger):
        exc = APIException()
        log_exception(exc, level=logging.WARNING)
        call_kwargs = mock_logger.log.call_args[1]
        assert call_kwargs.get("exc_info") is False

    @patch(LOGGER_PATH)
    def test_non_api_exception(self, mock_logger):
        exc = ValueError("bad value")
        log_exception(exc)
        logged_msg_args = mock_logger.log.call_args[0]
        assert "ValueError" in str(logged_msg_args)


# ------------------------------------------------------------------ #
# log_business_rule_violation
# ------------------------------------------------------------------ #


class TestLogBusinessRuleViolation:
    """Tests for log_business_rule_violation()."""

    @patch(LOGGER_PATH)
    def test_logs_at_warning(self, mock_logger):
        log_business_rule_violation("MAX_QTY", "Quantity exceeded")
        mock_logger.warning.assert_called_once()

    @patch(LOGGER_PATH)
    def test_includes_rule_code(self, mock_logger):
        log_business_rule_violation("ORDER_SHIPPED", "Cannot cancel")
        call_args = mock_logger.warning.call_args[0]
        assert "ORDER_SHIPPED" in str(call_args)

    @patch(LOGGER_PATH)
    def test_includes_message(self, mock_logger):
        log_business_rule_violation("X", "The message text")
        call_args = mock_logger.warning.call_args[0]
        assert "The message text" in str(call_args)

    @patch(LOGGER_PATH)
    def test_includes_request_context(self, mock_logger):
        request = HttpRequest()
        request.META["REMOTE_ADDR"] = "192.168.1.10"
        request.method = "DELETE"
        request.path = "/api/orders/1/"
        log_business_rule_violation("X", "msg", request=request)
        call_args = mock_logger.warning.call_args[0]
        assert "192.168.1.10" in str(call_args)

    @patch(LOGGER_PATH)
    def test_extra_included(self, mock_logger):
        log_business_rule_violation("X", "msg", extra={"tenant": "abc"})
        call_args = mock_logger.warning.call_args[0]
        ctx = call_args[-1]
        assert ctx.get("tenant") == "abc"
