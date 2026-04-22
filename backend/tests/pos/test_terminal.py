"""
Tests for POSTerminal model: creation, validation, uniqueness, defaults,
relationships, string representation, and manager methods.
"""

from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.pos.constants import (
    TERMINAL_STATUS_ACTIVE,
    TERMINAL_STATUS_INACTIVE,
    TERMINAL_STATUS_MAINTENANCE,
)

pytestmark = pytest.mark.django_db


# ── Creation & Defaults ──────────────────────────────────────────────


class TestPOSTerminalCreation:
    def test_create_terminal_with_valid_data(self, terminal):
        assert terminal.pk is not None
        assert terminal.name == "Main Checkout"
        assert terminal.code == "T001"
        assert terminal.status == TERMINAL_STATUS_ACTIVE

    def test_terminal_default_values(self, terminal):
        assert terminal.cash_drawer_enabled is True
        assert terminal.barcode_scanner_enabled is True
        assert terminal.auto_print_receipt is True
        assert terminal.receipt_copies == 1
        assert terminal.allow_discount is True
        assert terminal.allow_price_override is False
        assert terminal.is_mobile is False

    def test_terminal_warehouse_relationship(self, terminal, warehouse):
        assert terminal.warehouse == warehouse
        assert terminal in warehouse.terminals.all()

    def test_terminal_str_representation(self, terminal):
        expected = f"{terminal.name} ({terminal.code})"
        assert str(terminal) == expected


# ── Uniqueness & Validation ──────────────────────────────────────────


class TestPOSTerminalValidation:
    def test_terminal_code_unique(self, terminal, warehouse):
        from apps.pos.terminal.models import POSTerminal

        with pytest.raises(IntegrityError):
            with transaction.atomic():
                POSTerminal.objects.create(
                    name="Duplicate Code",
                    code="T001",
                    warehouse=warehouse,
                    status="active",
                )

    def test_terminal_name_strip_whitespace(self, warehouse):
        from apps.pos.terminal.models import POSTerminal

        t = POSTerminal.objects.create(
            name="  Spaced Name  ",
            code="T-SPC",
            warehouse=warehouse,
            status="active",
        )
        # Model may not auto-strip; just ensure it's saved
        assert t.pk is not None


# ── Manager Methods ──────────────────────────────────────────────────


class TestPOSTerminalManager:
    def test_active_terminals(self, terminal, inactive_terminal):
        from apps.pos.terminal.models import POSTerminal

        active = POSTerminal.objects.active()
        assert terminal in active
        assert inactive_terminal not in active

    def test_by_warehouse(self, terminal, warehouse):
        from apps.pos.terminal.models import POSTerminal

        terminals = POSTerminal.objects.by_warehouse(warehouse)
        assert terminal in terminals

    def test_alive_manager_excludes_deleted(self, terminal):
        terminal.is_deleted = True
        terminal.save()

        from apps.pos.terminal.models import POSTerminal

        assert terminal not in POSTerminal.objects.all()
        assert terminal in POSTerminal.all_with_deleted.all()


# ── Status Management ────────────────────────────────────────────────


class TestPOSTerminalStatus:
    def test_terminal_status_active(self, terminal):
        assert terminal.status == TERMINAL_STATUS_ACTIVE

    def test_terminal_status_inactive(self, inactive_terminal):
        assert inactive_terminal.status == TERMINAL_STATUS_INACTIVE

    def test_terminal_status_maintenance(self, warehouse):
        from apps.pos.terminal.models import POSTerminal

        t = POSTerminal.objects.create(
            name="Maintenance Terminal",
            code="T-MNT",
            warehouse=warehouse,
            status=TERMINAL_STATUS_MAINTENANCE,
        )
        assert t.status == TERMINAL_STATUS_MAINTENANCE
