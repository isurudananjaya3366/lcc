"""
Tests for Quote services.

Covers: QuoteNumberGenerator, QuoteCalculationService, QuoteService.
"""

import uuid
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from apps.quotes.constants import DiscountType, QuoteStatus

pytestmark = pytest.mark.django_db


# ── Helpers ──────────────────────────────────────────────────────


def make_quote(**kwargs):
    from apps.quotes.models import Quote

    defaults = {
        "id": uuid.uuid4(),
        "quote_number": f"QT-SVC-{uuid.uuid4().hex[:5].upper()}",
        "status": QuoteStatus.DRAFT,
        "issue_date": date.today(),
    }
    defaults.update(kwargs)
    return Quote.objects.create(**defaults)


def make_line_item(quote, **kwargs):
    from apps.quotes.models import QuoteLineItem

    defaults = {
        "product_name": "Test Product",
        "quantity": Decimal("2"),
        "unit_price": Decimal("100.00"),
    }
    defaults.update(kwargs)
    return QuoteLineItem.objects.create(quote=quote, **defaults)


# ═══════════════════════════════════════════════════════════════════
# QuoteNumberGenerator
# ═══════════════════════════════════════════════════════════════════


@pytest.mark.usefixtures("tenant_context")
class TestQuoteNumberGenerator:
    def test_generate_returns_string(self):
        from apps.quotes.services import QuoteNumberGenerator

        num = QuoteNumberGenerator.generate()
        assert isinstance(num, str)
        assert num.startswith("QT-")

    def test_sequential_numbers(self):
        from apps.quotes.services import QuoteNumberGenerator

        n1 = QuoteNumberGenerator.generate()
        n2 = QuoteNumberGenerator.generate()
        assert n1 != n2


# ═══════════════════════════════════════════════════════════════════
# QuoteCalculationService
# ═══════════════════════════════════════════════════════════════════


@pytest.mark.usefixtures("tenant_context")
class TestQuoteCalculationService:
    def test_calculate_all_empty_quote(self):
        from apps.quotes.services import QuoteCalculationService

        q = make_quote()
        QuoteCalculationService(q).calculate_all()
        assert q.subtotal == Decimal("0")
        assert q.total == Decimal("0")

    def test_calculate_all_with_items(self):
        from apps.quotes.services import QuoteCalculationService

        q = make_quote()
        make_line_item(q, quantity=Decimal("2"), unit_price=Decimal("50.00"))
        make_line_item(q, quantity=Decimal("1"), unit_price=Decimal("30.00"))
        QuoteCalculationService(q).calculate_all()
        assert q.subtotal == Decimal("130.00")
        assert q.total == Decimal("130.00")

    def test_calculate_with_header_discount_percentage(self):
        from apps.quotes.services import QuoteCalculationService

        q = make_quote(
            discount_type=DiscountType.PERCENTAGE,
            discount_value=Decimal("10"),
        )
        make_line_item(q, quantity=Decimal("1"), unit_price=Decimal("200.00"))
        QuoteCalculationService(q).calculate_all()
        assert q.discount_amount == Decimal("20.00")
        assert q.total == Decimal("180.00")

    def test_calculate_with_header_discount_fixed(self):
        from apps.quotes.services import QuoteCalculationService

        q = make_quote(
            discount_type=DiscountType.FIXED,
            discount_value=Decimal("15"),
        )
        make_line_item(q, quantity=Decimal("1"), unit_price=Decimal("100.00"))
        QuoteCalculationService(q).calculate_all()
        assert q.discount_amount == Decimal("15.00")

    def test_calculate_with_tax(self):
        from apps.quotes.services import QuoteCalculationService

        q = make_quote()
        make_line_item(
            q,
            quantity=Decimal("1"),
            unit_price=Decimal("100.00"),
            is_taxable=True,
            tax_rate=Decimal("15.00"),
        )
        QuoteCalculationService(q).calculate_all()
        assert q.tax_amount == Decimal("15.00")
        # line_total includes tax (100 + 15 = 115), subtotal = 115,
        # grand_total = subtotal - discount + tax = 115 - 0 + 15 = 130
        assert q.total == Decimal("130.00")

    def test_get_total_breakdown(self):
        from apps.quotes.services import QuoteCalculationService

        q = make_quote()
        make_line_item(q, quantity=Decimal("1"), unit_price=Decimal("100.00"))
        svc = QuoteCalculationService(q)
        svc.calculate_all()
        breakdown = svc.get_total_breakdown()
        assert "subtotal" in breakdown
        assert "grand_total" in breakdown


# ═══════════════════════════════════════════════════════════════════
# QuoteService
# ═══════════════════════════════════════════════════════════════════


@pytest.mark.usefixtures("tenant_context")
class TestQuoteService:
    def test_send_quote(self):
        from apps.quotes.services import QuoteService

        q = make_quote(status=QuoteStatus.DRAFT, guest_email="test@example.com")
        make_line_item(q)
        QuoteService.send_quote(q)
        q.refresh_from_db()
        assert q.status == QuoteStatus.SENT
        assert q.sent_at is not None

    def test_send_non_draft_raises(self):
        from apps.quotes.services import QuoteService
        from apps.quotes.services.quote_service import InvalidStatusTransition

        q = make_quote(status=QuoteStatus.EXPIRED)
        with pytest.raises(InvalidStatusTransition):
            QuoteService.send_quote(q)

    def test_accept_quote(self):
        from apps.quotes.services import QuoteService

        q = make_quote(status=QuoteStatus.SENT)
        QuoteService.accept_quote(q)
        q.refresh_from_db()
        assert q.status == QuoteStatus.ACCEPTED

    def test_reject_quote(self):
        from apps.quotes.services import QuoteService

        q = make_quote(status=QuoteStatus.SENT)
        QuoteService.reject_quote(q, reason="Too expensive")
        q.refresh_from_db()
        assert q.status == QuoteStatus.REJECTED
        assert q.rejection_reason == "Too expensive"

    def test_expire_quote(self):
        from apps.quotes.services import QuoteService

        q = make_quote(status=QuoteStatus.SENT)
        QuoteService.expire_quote(q)
        q.refresh_from_db()
        assert q.status == QuoteStatus.EXPIRED

    def test_duplicate_quote(self):
        from apps.quotes.services import QuoteService

        q = make_quote(title="Original", guest_name="Alice")
        make_line_item(q, product_name="Widget")
        dup = QuoteService.duplicate_quote(q)
        assert dup.pk != q.pk
        assert dup.status == QuoteStatus.DRAFT
        assert dup.guest_name == "Alice"
        assert dup.line_items.count() == 1

    def test_get_available_actions_draft(self):
        from apps.quotes.services import QuoteService

        q = make_quote(status=QuoteStatus.DRAFT)
        actions = QuoteService.get_available_actions(q)
        assert "send" in actions

    def test_get_available_actions_sent(self):
        from apps.quotes.services import QuoteService

        q = make_quote(status=QuoteStatus.SENT)
        actions = QuoteService.get_available_actions(q)
        assert "accept" in actions
        assert "reject" in actions

    def test_get_available_actions_terminal(self):
        from apps.quotes.services import QuoteService

        q = make_quote(status=QuoteStatus.EXPIRED)
        actions = QuoteService.get_available_actions(q)
        assert len(actions) == 0 or "duplicate" in actions

    def test_log_history(self):
        from apps.quotes.models import QuoteHistory
        from apps.quotes.services import QuoteService

        q = make_quote()
        QuoteService.log_history(q, "created", notes="test")
        assert QuoteHistory.objects.filter(quote=q, event_type="created").exists()
