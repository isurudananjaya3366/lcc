"""Invoice model tests."""

import pytest
from decimal import Decimal

from apps.invoices.constants import InvoiceStatus, InvoiceType, ALLOWED_TRANSITIONS
from apps.invoices.models import Invoice

pytestmark = pytest.mark.django_db


class TestInvoiceModel:
    """Tests for the Invoice model."""

    def test_create_draft_invoice(self, invoice_data):
        invoice = Invoice.objects.create(**invoice_data)
        assert invoice.status == InvoiceStatus.DRAFT
        assert invoice.type == InvoiceType.STANDARD
        assert invoice.is_draft is True
        assert invoice.is_editable is True

    def test_invoice_str_draft(self, invoice_data):
        invoice = Invoice.objects.create(**invoice_data)
        assert "Draft" in str(invoice)

    def test_invoice_str_with_number(self, invoice_data):
        invoice = Invoice.objects.create(**{**invoice_data, "invoice_number": "INV-2025-00001"})
        assert str(invoice) == "INV-2025-00001"

    def test_default_financial_fields(self, invoice_data):
        invoice = Invoice.objects.create(**invoice_data)
        assert invoice.subtotal == Decimal("0.00")
        assert invoice.total == Decimal("0.00")
        assert invoice.amount_paid == Decimal("0.00")
        assert invoice.balance_due == Decimal("0.00")

    def test_is_cancellable_draft(self, invoice_data):
        invoice = Invoice.objects.create(**invoice_data)
        assert invoice.is_cancellable is True

    def test_is_not_cancellable_issued(self, invoice_data):
        invoice = Invoice.objects.create(**{**invoice_data, "status": InvoiceStatus.ISSUED})
        assert invoice.is_cancellable is False

    def test_available_transitions(self, invoice_data):
        invoice = Invoice.objects.create(**invoice_data)
        transitions = invoice.get_available_transitions()
        assert InvoiceStatus.ISSUED in transitions

    def test_can_transition_to(self, invoice_data):
        invoice = Invoice.objects.create(**invoice_data)
        assert invoice.can_transition_to(InvoiceStatus.ISSUED) is True
        assert invoice.can_transition_to(InvoiceStatus.PAID) is False

    def test_manager_drafts(self, invoice_data):
        Invoice.objects.create(**invoice_data)
        assert Invoice.objects.drafts().count() == 1

    def test_manager_active(self, invoice_data):
        Invoice.objects.create(**invoice_data)
        Invoice.objects.create(**{**invoice_data, "status": InvoiceStatus.CANCELLED, "invoice_number": "CN-001"})
        assert Invoice.objects.active().count() == 1

    def test_soft_delete(self, invoice_data):
        invoice = Invoice.objects.create(**invoice_data)
        invoice.is_deleted = True
        invoice.save()
        assert Invoice.objects.filter(is_deleted=False).count() == 0


class TestInvoiceLineItemModel:
    """Tests for InvoiceLineItem."""

    def test_create_line_item(self, invoice_data, line_item_data):
        from apps.invoices.models import InvoiceLineItem
        invoice = Invoice.objects.create(**invoice_data)
        item = InvoiceLineItem.objects.create(invoice=invoice, **line_item_data)
        assert item.invoice == invoice
        assert item.quantity == Decimal("2")
        assert item.unit_price == Decimal("1000.00")

    def test_line_item_recalculate(self, invoice_data, line_item_data):
        from apps.invoices.models import InvoiceLineItem
        invoice = Invoice.objects.create(**invoice_data)
        item = InvoiceLineItem.objects.create(invoice=invoice, **line_item_data)
        item.recalculate()
        assert item.line_total > Decimal("0")


class TestInvoiceHistoryModel:
    """Tests for InvoiceHistory."""

    def test_create_history_entry(self, invoice_data):
        from apps.invoices.models import InvoiceHistory
        invoice = Invoice.objects.create(**invoice_data)
        history = InvoiceHistory.objects.create(
            invoice=invoice,
            action="CREATED",
            new_status=InvoiceStatus.DRAFT,
            notes="Test history",
        )
        assert history.invoice == invoice
        assert history.action == "CREATED"
