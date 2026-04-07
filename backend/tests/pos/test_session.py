"""
Tests for POSSession model: creation, lifecycle (open/close/suspend/resume),
cash reconciliation, session number generation, and edge cases.
"""

from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from apps.pos.constants import (
    SESSION_STATUS_CLOSED,
    SESSION_STATUS_FORCE_CLOSED,
    SESSION_STATUS_OPEN,
    SESSION_STATUS_SUSPENDED,
    TERMINAL_STATUS_INACTIVE,
)

pytestmark = pytest.mark.django_db


# ── Session Creation ─────────────────────────────────────────────────


class TestPOSSessionCreation:
    def test_session_created_with_valid_data(self, session):
        assert session.pk is not None
        assert session.status == SESSION_STATUS_OPEN
        assert session.opening_cash_amount == Decimal("10000.00")

    def test_session_requires_terminal(self, session, terminal):
        assert session.terminal == terminal

    def test_session_requires_user(self, session, cashier):
        assert session.user == cashier

    def test_session_number_auto_generated(self, session):
        assert session.session_number is not None
        assert session.session_number.startswith("SESS-")

    def test_session_opened_at_auto_populated(self, session):
        assert session.opened_at is not None

    def test_session_closed_at_null_on_creation(self, session):
        assert session.closed_at is None

    def test_session_defaults_to_zero_totals(self, session):
        assert session.total_sales == Decimal("0.00")
        assert session.total_refunds == Decimal("0.00")
        assert session.transaction_count == 0

    def test_session_str_representation(self, session):
        assert session.session_number in str(session)
        assert session.terminal.name in str(session)


# ── Open Session ─────────────────────────────────────────────────────


class TestOpenSession:
    def test_open_session_success(self, terminal, cashier):
        from apps.pos.terminal.models import POSSession

        session_num = POSSession.generate_session_number(terminal)
        sess = POSSession(
            terminal=terminal,
            user=cashier,
            session_number=session_num,
            opening_cash_amount=Decimal("5000.00"),
        )
        sess.open_session()
        assert sess.status == SESSION_STATUS_OPEN
        assert sess.pk is not None

    def test_open_session_zero_opening_balance(self, terminal2, cashier2):
        from apps.pos.terminal.models import POSSession

        session_num = POSSession.generate_session_number(terminal2)
        sess = POSSession(
            terminal=terminal2,
            user=cashier2,
            session_number=session_num,
            opening_cash_amount=Decimal("0.00"),
        )
        sess.open_session()
        assert sess.status == SESSION_STATUS_OPEN

    def test_open_session_inactive_terminal_raises(self, inactive_terminal, cashier):
        from apps.pos.terminal.models import POSSession

        session_num = POSSession.generate_session_number(inactive_terminal)
        sess = POSSession(
            terminal=inactive_terminal,
            user=cashier,
            session_number=session_num,
            opening_cash_amount=Decimal("1000.00"),
        )
        with pytest.raises(ValidationError, match="Terminal is"):
            sess.open_session()

    def test_open_session_duplicate_raises(self, session, terminal, cashier2):
        """Cannot open second session on same terminal."""
        from apps.pos.terminal.models import POSSession

        session_num = POSSession.generate_session_number(terminal)
        sess2 = POSSession(
            terminal=terminal,
            user=cashier2,
            session_number=session_num,
            opening_cash_amount=Decimal("1000.00"),
        )
        with pytest.raises(ValidationError, match="already has an open session"):
            sess2.open_session()

    def test_open_session_negative_cash_raises(self, terminal2, cashier2):
        from apps.pos.terminal.models import POSSession

        session_num = POSSession.generate_session_number(terminal2)
        sess = POSSession(
            terminal=terminal2,
            user=cashier2,
            session_number=session_num,
            opening_cash_amount=Decimal("-100.00"),
        )
        with pytest.raises(ValidationError, match="negative"):
            sess.open_session()


# ── Close Session ────────────────────────────────────────────────────


class TestCloseSession:
    def test_close_session_success(self, session):
        session.close_session(actual_cash_amount=Decimal("10000.00"))
        assert session.status == SESSION_STATUS_CLOSED
        assert session.closed_at is not None

    def test_close_session_records_actual_cash(self, session):
        session.close_session(actual_cash_amount=Decimal("9500.00"))
        assert session.actual_cash_amount == Decimal("9500.00")

    def test_close_session_calculates_expected_cash(self, session):
        session.total_sales = Decimal("5000.00")
        session.total_refunds = Decimal("500.00")
        session.save()

        session.close_session(actual_cash_amount=Decimal("14500.00"))
        expected = Decimal("10000.00") + Decimal("5000.00") - Decimal("500.00")
        assert session.expected_cash == expected

    def test_close_session_positive_variance(self, session):
        """Cash over: actual > expected."""
        session.close_session(actual_cash_amount=Decimal("11000.00"))
        assert session.cash_variance == Decimal("1000.00")

    def test_close_session_negative_variance(self, session):
        """Cash short: actual < expected."""
        session.close_session(actual_cash_amount=Decimal("9000.00"))
        assert session.cash_variance == Decimal("-1000.00")

    def test_close_session_zero_variance(self, session):
        """Balanced: actual == expected."""
        session.close_session(actual_cash_amount=Decimal("10000.00"))
        assert session.cash_variance == Decimal("0.00")

    def test_close_already_closed_raises(self, closed_session):
        with pytest.raises(ValidationError, match="Only open sessions"):
            closed_session.close_session(actual_cash_amount=Decimal("5000.00"))

    def test_close_session_none_amount_raises(self, session):
        with pytest.raises(ValidationError, match="required"):
            session.close_session(actual_cash_amount=None)

    def test_close_session_negative_amount_raises(self, session):
        with pytest.raises(ValidationError, match="negative"):
            session.close_session(actual_cash_amount=Decimal("-100.00"))

    def test_close_session_with_notes(self, session):
        session.close_session(
            actual_cash_amount=Decimal("10000.00"), notes="All good"
        )
        assert session.status == SESSION_STATUS_CLOSED


# ── Suspend / Resume ─────────────────────────────────────────────────


class TestSessionSuspendResume:
    def test_suspend_open_session(self, session):
        session.suspend_session()
        assert session.status == SESSION_STATUS_SUSPENDED

    def test_suspend_closed_raises(self, closed_session):
        with pytest.raises(ValidationError, match="Only open sessions"):
            closed_session.suspend_session()

    def test_resume_suspended_session(self, session):
        session.suspend_session()
        session.resume_session()
        assert session.status == SESSION_STATUS_OPEN

    def test_resume_open_raises(self, session):
        with pytest.raises(ValidationError, match="Only suspended sessions"):
            session.resume_session()

    def test_force_close_open_session(self, session):
        session.force_close()
        assert session.status == SESSION_STATUS_FORCE_CLOSED
        assert session.closed_at is not None

    def test_force_close_suspended_session(self, session):
        session.suspend_session()
        session.force_close()
        assert session.status == SESSION_STATUS_FORCE_CLOSED


# ── Session Number Generation ────────────────────────────────────────


class TestSessionNumberGeneration:
    def test_session_number_format(self, session, terminal):
        assert session.session_number.startswith(f"SESS-{terminal.code}-")

    def test_session_number_uniqueness(self, terminal, cashier):
        from apps.pos.terminal.models import POSSession

        nums = set()
        for _ in range(3):
            num = POSSession.generate_session_number(terminal)
            nums.add(num)
        assert len(nums) == 3


# ── Session Filtering & Queries ──────────────────────────────────────


class TestSessionQueries:
    def test_filter_by_status(self, session, closed_session):
        from apps.pos.terminal.models import POSSession

        open_sessions = POSSession.objects.filter(status=SESSION_STATUS_OPEN)
        assert session in open_sessions
        assert closed_session not in open_sessions

    def test_multiple_sequential_sessions(self, terminal, cashier):
        """Terminal can have sequential sessions (not concurrent)."""
        from apps.pos.terminal.models import POSSession

        # First session: open and close
        num1 = POSSession.generate_session_number(terminal)
        s1 = POSSession(
            terminal=terminal,
            user=cashier,
            session_number=num1,
            opening_cash_amount=Decimal("1000.00"),
        )
        s1.open_session()
        s1.close_session(actual_cash_amount=Decimal("1000.00"))

        # Second session: open
        num2 = POSSession.generate_session_number(terminal)
        s2 = POSSession(
            terminal=terminal,
            user=cashier,
            session_number=num2,
            opening_cash_amount=Decimal("2000.00"),
        )
        s2.open_session()
        assert s2.status == SESSION_STATUS_OPEN

    def test_session_duration_property(self, closed_session):
        assert closed_session.duration is not None

    def test_session_no_transactions_totals(self, session):
        assert session.total_sales == Decimal("0.00")
        assert session.transaction_count == 0
