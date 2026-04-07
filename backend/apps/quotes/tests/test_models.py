"""
Tests for Quote models.

Covers: Quote, QuoteLineItem, QuoteTemplate, QuoteHistory, QuoteSettings, QuoteSequence.
"""

import uuid
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from apps.quotes.constants import (
    CurrencyChoice,
    DiscountType,
    EDITABLE_STATES,
    QuoteStatus,
    TERMINAL_STATES,
)

pytestmark = pytest.mark.django_db


# ── Helpers ──────────────────────────────────────────────────────


def make_quote(**kwargs):
    """Create a minimal Quote via the model directly."""
    from apps.quotes.models import Quote

    defaults = {
        "id": uuid.uuid4(),
        "quote_number": f"QT-TEST-{uuid.uuid4().hex[:5].upper()}",
        "status": QuoteStatus.DRAFT,
        "issue_date": date.today(),
    }
    defaults.update(kwargs)
    return Quote.objects.create(**defaults)


def make_line_item(quote, **kwargs):
    from apps.quotes.models import QuoteLineItem

    defaults = {
        "product_name": "Test Product",
        "quantity": Decimal("1"),
        "unit_price": Decimal("100.00"),
    }
    defaults.update(kwargs)
    return QuoteLineItem.objects.create(quote=quote, **defaults)


# ═══════════════════════════════════════════════════════════════════
# Quote Model
# ═══════════════════════════════════════════════════════════════════


@pytest.mark.usefixtures("tenant_context")
class TestQuoteModel:
    def test_create_draft_quote(self):
        q = make_quote(title="Test")
        assert q.pk is not None
        assert q.status == QuoteStatus.DRAFT
        assert q.quote_number.startswith("QT-")

    def test_auto_generates_uuid_and_number(self):
        from apps.quotes.models import Quote

        q = Quote(issue_date=date.today())
        q.save()
        assert q.id is not None
        assert q.quote_number is not None

    def test_str_representation(self):
        q = make_quote(quote_number="QT-2026-00001")
        assert str(q) == "QT-2026-00001"

    def test_repr(self):
        q = make_quote(quote_number="QT-2026-00002")
        assert "QT-2026-00002" in repr(q)

    def test_is_editable_for_draft(self):
        q = make_quote(status=QuoteStatus.DRAFT)
        assert q.is_editable is True

    def test_is_editable_false_for_sent(self):
        q = make_quote(status=QuoteStatus.SENT)
        assert q.is_editable is False

    def test_is_expired_property(self):
        q = make_quote(valid_until=date.today() - timedelta(days=1))
        assert q.is_expired is True

    def test_is_not_expired(self):
        q = make_quote(valid_until=date.today() + timedelta(days=30))
        assert q.is_expired is False

    def test_is_locked_for_non_draft(self):
        q = make_quote(status=QuoteStatus.SENT)
        assert q.is_locked is True

    def test_is_not_locked_for_draft(self):
        q = make_quote(status=QuoteStatus.DRAFT)
        assert q.is_locked is False

    def test_can_delete_draft(self):
        q = make_quote(status=QuoteStatus.DRAFT)
        assert q.can_delete() is True

    def test_cannot_delete_sent(self):
        q = make_quote(status=QuoteStatus.SENT)
        assert q.can_delete() is False

    def test_currency_symbol(self):
        q = make_quote(currency=CurrencyChoice.LKR)
        assert q.currency_symbol == "\u20A8"

    def test_customer_display_name_guest(self):
        q = make_quote(guest_name="John Doe")
        assert q.customer_display_name == "John Doe"

    def test_customer_display_name_fallback(self):
        q = make_quote()
        assert q.customer_display_name == "Unknown Customer"

    def test_days_until_expiry(self):
        q = make_quote(valid_until=date.today() + timedelta(days=10))
        assert q.days_until_expiry == 10

    def test_days_until_expiry_none(self):
        q = make_quote(valid_until=None)
        assert q.days_until_expiry is None

    def test_needs_regeneration_no_pdf(self):
        q = make_quote()
        assert q.needs_regeneration is True

    def test_calculate_valid_until(self):
        from apps.quotes.models import Quote

        result = Quote.calculate_valid_until(date(2026, 1, 1), 30)
        assert result == date(2026, 1, 31)

    def test_get_public_url_no_token(self):
        q = make_quote()
        assert q.get_public_url() is None

    def test_get_public_url_with_token(self):
        token = uuid.uuid4()
        q = make_quote(public_token=token)
        url = q.get_public_url()
        assert str(token) in url

    def test_manager_drafts(self):
        from apps.quotes.models import Quote

        make_quote(status=QuoteStatus.DRAFT)
        make_quote(status=QuoteStatus.SENT)
        assert Quote.objects.drafts().count() == 1

    def test_manager_active(self):
        from apps.quotes.models import Quote

        make_quote(status=QuoteStatus.DRAFT)
        make_quote(status=QuoteStatus.EXPIRED)
        assert Quote.objects.active().count() == 1


# ═══════════════════════════════════════════════════════════════════
# Line Item Model
# ═══════════════════════════════════════════════════════════════════


@pytest.mark.usefixtures("tenant_context")
class TestQuoteLineItemModel:
    def test_create_line_item(self):
        q = make_quote()
        item = make_line_item(q)
        assert item.pk is not None
        assert item.quote == q

    def test_auto_position(self):
        q = make_quote()
        i1 = make_line_item(q, product_name="A")
        i2 = make_line_item(q, product_name="B")
        assert i1.position == 1
        assert i2.position == 2

    def test_line_total_calculated(self):
        q = make_quote()
        item = make_line_item(q, quantity=Decimal("3"), unit_price=Decimal("50.00"))
        assert item.line_total == Decimal("150.00")

    def test_discount_amount_percentage(self):
        q = make_quote()
        item = make_line_item(
            q,
            quantity=Decimal("1"),
            unit_price=Decimal("200.00"),
            discount_type=DiscountType.PERCENTAGE,
            discount_value=Decimal("10"),
        )
        assert item.discount_amount == Decimal("20.00")

    def test_discount_amount_fixed(self):
        q = make_quote()
        item = make_line_item(
            q,
            quantity=Decimal("1"),
            unit_price=Decimal("200.00"),
            discount_type=DiscountType.FIXED,
            discount_value=Decimal("25.00"),
        )
        assert item.discount_amount == Decimal("25.00")

    def test_tax_calculated(self):
        q = make_quote()
        item = make_line_item(
            q,
            quantity=Decimal("1"),
            unit_price=Decimal("100.00"),
            is_taxable=True,
            tax_rate=Decimal("15.00"),
        )
        assert item.tax_amount == Decimal("15.00")

    def test_is_product_based(self):
        q = make_quote()
        item = make_line_item(q)
        # No product FK, but product_name set
        assert item.is_product_based is False

    def test_is_custom_item(self):
        q = make_quote()
        item = make_line_item(q, product_name="", custom_description="Custom work")
        assert item.is_custom_item is True

    def test_str_representation(self):
        q = make_quote(quote_number="QT-2026-00099")
        item = make_line_item(q, product_name="Widget")
        assert "Widget" in str(item)

    def test_recalculate(self):
        q = make_quote()
        item = make_line_item(q, quantity=Decimal("2"), unit_price=Decimal("50.00"))
        item.quantity = Decimal("5")
        item.recalculate()
        assert item.line_total == Decimal("250.00")


# ═══════════════════════════════════════════════════════════════════
# QuoteTemplate Model
# ═══════════════════════════════════════════════════════════════════


@pytest.mark.usefixtures("tenant_context")
class TestQuoteTemplateModel:
    def test_create_template(self):
        from apps.quotes.models import QuoteTemplate

        # QuoteTemplate has a tenant FK; use a placeholder approach
        tpl = QuoteTemplate(
            name="Test Template",
            is_default=True,
            primary_color="#2563eb",
        )
        assert tpl.name == "Test Template"
        assert tpl.is_default is True

    def test_str_repr(self):
        from apps.quotes.models import QuoteTemplate

        tpl = QuoteTemplate(name="My Tpl", is_default=True)
        assert "My Tpl" in str(tpl)
        assert "(Default)" in str(tpl)

    def test_default_layout_options(self):
        from apps.quotes.models import QuoteTemplate

        opts = QuoteTemplate.get_default_layout_options()
        assert "columns" in opts
        assert "sections" in opts

    def test_get_visible_columns(self):
        from apps.quotes.models import QuoteTemplate

        tpl = QuoteTemplate(
            name="T",
            layout_options=QuoteTemplate.get_default_layout_options(),
        )
        cols = tpl.get_visible_columns()
        assert "description" in cols
        assert "total" in cols

    def test_is_section_visible(self):
        from apps.quotes.models import QuoteTemplate

        tpl = QuoteTemplate(
            name="T",
            layout_options=QuoteTemplate.get_default_layout_options(),
        )
        assert tpl.is_section_visible("header") is True


# ═══════════════════════════════════════════════════════════════════
# QuoteHistory Model
# ═══════════════════════════════════════════════════════════════════


@pytest.mark.usefixtures("tenant_context")
class TestQuoteHistoryModel:
    def test_create_history_entry(self):
        from apps.quotes.models import QuoteHistory

        q = make_quote()
        entry = QuoteHistory.objects.create(
            quote=q,
            event_type="created",
            notes="Initial creation",
        )
        assert entry.pk is not None
        assert entry.event_type == "created"


# ═══════════════════════════════════════════════════════════════════
# QuoteSettings Model
# ═══════════════════════════════════════════════════════════════════


@pytest.mark.usefixtures("tenant_context")
class TestQuoteSettingsModel:
    def test_default_values(self):
        from apps.quotes.models import QuoteSettings

        s = QuoteSettings()
        assert s.default_validity_days == 30
        assert s.auto_expire_enabled is True
