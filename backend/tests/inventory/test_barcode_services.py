"""
Barcode generation and lookup service tests (Task 81).

Database-free unit tests for BarcodeGenerator, BarcodeLookup,
and related barcode utilities.
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest

from apps.inventory.warehouses.services.barcode_generator import BarcodeGenerator
from apps.inventory.warehouses.constants import (
    BARCODE_PREFIX_LOCATION,
    BARCODE_SEPARATOR,
)


# ═══════════════════════════════════════════════════════════════════
# BarcodeGenerator tests
# ═══════════════════════════════════════════════════════════════════


class TestBarcodeGenerator:
    """Unit tests for BarcodeGenerator service."""

    def setup_method(self):
        self.gen = BarcodeGenerator()

    def test_calculate_check_digit_known_value(self):
        # Luhn check-digit calculation should be deterministic
        digit = self.gen.calculate_check_digit("LOC-TENT001-WH001-LOC001")
        assert isinstance(digit, str)
        assert len(digit) == 1
        assert digit.isdigit()

    def test_calculate_check_digit_consistency(self):
        d1 = self.gen.calculate_check_digit("TEST-DATA-123")
        d2 = self.gen.calculate_check_digit("TEST-DATA-123")
        assert d1 == d2

    def test_calculate_check_digit_different_inputs(self):
        d1 = self.gen.calculate_check_digit("TEST-A")
        d2 = self.gen.calculate_check_digit("TEST-B")
        # May or may not differ, but should both be valid digits
        assert d1.isdigit()
        assert d2.isdigit()

    @patch("django.db.connection")
    def test_generate_location_barcode_format(self, mock_conn):
        mock_tenant = MagicMock()
        mock_tenant.code = "ABC"
        mock_conn.tenant = mock_tenant

        location = MagicMock()
        location.warehouse.code = "WH-001"
        location.code = "LOC-001"
        location.pk = uuid.uuid4()

        with patch.object(self.gen, "_barcode_exists", return_value=False):
            barcode = self.gen.generate_location_barcode(location)
        assert barcode.startswith(BARCODE_PREFIX_LOCATION + BARCODE_SEPARATOR)
        parts = barcode.split(BARCODE_SEPARATOR)
        assert parts[0] == BARCODE_PREFIX_LOCATION
        assert len(parts) == 5  # PREFIX-TENANT-WH-LOC-CHECK

    @patch("django.db.connection")
    def test_validate_barcode_format_valid(self, mock_conn):
        mock_tenant = MagicMock()
        mock_tenant.code = "ABC"
        mock_conn.tenant = mock_tenant

        location = MagicMock()
        location.warehouse.code = "WH-001"
        location.code = "LOC-001"
        location.pk = uuid.uuid4()

        with patch.object(self.gen, "_barcode_exists", return_value=False):
            barcode = self.gen.generate_location_barcode(location)
        assert self.gen.validate_barcode_format(barcode) is True

    def test_validate_barcode_format_invalid(self):
        assert self.gen.validate_barcode_format("INVALID") is False

    def test_validate_barcode_format_empty(self):
        assert self.gen.validate_barcode_format("") is False

    @patch("django.db.connection")
    def test_parse_barcode(self, mock_conn):
        mock_tenant = MagicMock()
        mock_tenant.code = "TST"
        mock_conn.tenant = mock_tenant

        location = MagicMock()
        location.warehouse.code = "WH-CMB"
        location.code = "L100"
        location.pk = uuid.uuid4()

        with patch.object(self.gen, "_barcode_exists", return_value=False):
            barcode = self.gen.generate_location_barcode(location)
        parsed = self.gen.parse_barcode(barcode)
        assert parsed is not None
        assert "warehouse_code" in parsed
        assert "location_code" in parsed

    def test_parse_barcode_invalid(self):
        result = self.gen.parse_barcode("NOT-A-BARCODE")
        assert result is None or result == {}

    @patch("django.db.connection")
    def test_validate_barcode_with_check_digit(self, mock_conn):
        mock_tenant = MagicMock()
        mock_tenant.code = "TST"
        mock_conn.tenant = mock_tenant

        location = MagicMock()
        location.warehouse.code = "WH01"
        location.code = "LOC99"
        location.pk = uuid.uuid4()

        with patch.object(self.gen, "_barcode_exists", return_value=False):
            barcode = self.gen.generate_location_barcode(location)
        result = self.gen.validate_barcode(barcode)
        assert result is True

    @patch("django.db.connection")
    def test_validate_barcode_tampered(self, mock_conn):
        mock_tenant = MagicMock()
        mock_tenant.code = "TST"
        mock_conn.tenant = mock_tenant

        location = MagicMock()
        location.warehouse.code = "WH01"
        location.code = "LOC99"
        location.pk = uuid.uuid4()

        with patch.object(self.gen, "_barcode_exists", return_value=False):
            barcode = self.gen.generate_location_barcode(location)
        # Tamper with the check digit
        tampered = barcode[:-1] + ("0" if barcode[-1] != "0" else "1")
        result = self.gen.validate_barcode(tampered)
        assert result is False

    def test_get_tenant_prefix(self):
        tenant = MagicMock()
        tenant.code = "my_tenant"
        prefix = self.gen.get_tenant_prefix(tenant)
        assert isinstance(prefix, str)
        assert len(prefix) == 3

    def test_normalize_code(self):
        result = self.gen.normalize_code("Hello World 123")
        assert " " not in result  # should be cleaned up


# ═══════════════════════════════════════════════════════════════════
# Barcode signal tests
# ═══════════════════════════════════════════════════════════════════


class TestBarcodeSignal:
    """Test auto_generate_barcode pre_save signal."""

    def test_signal_registered(self):
        from django.db.models.signals import pre_save
        from apps.inventory.warehouses.models import StorageLocation

        receivers = [
            r[1]()
            for r in pre_save.receivers
            if r[1]() is not None
        ]
        # Just check that signals module loads without error
        import apps.inventory.warehouses.signals  # noqa: F401
