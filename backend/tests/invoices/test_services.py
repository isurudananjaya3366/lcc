"""Invoice service tests."""

import pytest
from decimal import Decimal

from apps.invoices.constants import InvoiceStatus, InvoiceType
from apps.invoices.exceptions import InvoiceError, InvalidTransitionError
from apps.invoices.models import Invoice, InvoiceLineItem

pytestmark = pytest.mark.django_db


class TestInvoiceService:
    """Tests for InvoiceService."""

    def test_create_invoice(self, tenant_context):
        from apps.invoices.services.invoice_service import InvoiceService
        invoice = InvoiceService.create_invoice(
            data={"type": InvoiceType.STANDARD, "notes": "Test invoice"},
        )
        assert invoice.status == InvoiceStatus.DRAFT
        assert invoice.type == InvoiceType.STANDARD

    def test_issue_invoice(self, invoice_data, line_item_data):
        from apps.invoices.services.invoice_service import InvoiceService
        invoice = Invoice.objects.create(**invoice_data)
        InvoiceLineItem.objects.create(invoice=invoice, **line_item_data)
        issued = InvoiceService.issue_invoice(invoice.id)
        assert issued.status == InvoiceStatus.ISSUED
        assert issued.invoice_number is not None
        assert issued.issue_date is not None

    def test_issue_non_draft_fails(self, invoice_data):
        from apps.invoices.services.invoice_service import InvoiceService
        invoice = Invoice.objects.create(**{**invoice_data, "status": InvoiceStatus.PAID})
        with pytest.raises((InvalidTransitionError, InvoiceError)):
            InvoiceService.issue_invoice(invoice.id)

    def test_cancel_draft(self, invoice_data):
        from apps.invoices.services.invoice_service import InvoiceService
        invoice = Invoice.objects.create(**invoice_data)
        cancelled = InvoiceService.cancel_invoice(invoice.id)
        assert cancelled.status == InvoiceStatus.CANCELLED

    def test_duplicate_invoice(self, invoice_data):
        from apps.invoices.services.invoice_service import InvoiceService
        invoice = Invoice.objects.create(**invoice_data)
        dup = InvoiceService.duplicate_invoice(invoice.id)
        assert dup.id != invoice.id
        assert dup.status == InvoiceStatus.DRAFT
        assert dup.customer_name == invoice.customer_name

    def test_check_and_mark_overdue(self, invoice_data):
        from datetime import date, timedelta
        from apps.invoices.services.invoice_service import InvoiceService
        invoice = Invoice.objects.create(**{
            **invoice_data,
            "status": InvoiceStatus.ISSUED,
            "invoice_number": "INV-2025-00099",
            "due_date": date.today() - timedelta(days=5),
            "balance_due": Decimal("1000.00"),
            "total": Decimal("1000.00"),
        })
        count = InvoiceService.check_and_mark_overdue()
        invoice.refresh_from_db()
        assert invoice.status == InvoiceStatus.OVERDUE
        assert count >= 1


class TestCalculationService:
    """Tests for InvoiceCalculationService."""

    def test_recalculate_invoice(self, invoice_data, line_item_data):
        from apps.invoices.services.calculation_service import InvoiceCalculationService
        invoice = Invoice.objects.create(**invoice_data)
        InvoiceLineItem.objects.create(invoice=invoice, **line_item_data)
        InvoiceCalculationService.recalculate_invoice(invoice.id)
        invoice.refresh_from_db()
        assert invoice.subtotal > Decimal("0")
        assert invoice.total > Decimal("0")
        assert invoice.balance_due > Decimal("0")


class TestCreditNoteService:
    """Tests for CreditNoteService."""

    def test_create_credit_note(self, invoice_data):
        from apps.invoices.services.credit_note_service import CreditNoteService
        invoice = Invoice.objects.create(**{
            **invoice_data,
            "status": InvoiceStatus.ISSUED,
            "invoice_number": "INV-2025-00100",
            "total": Decimal("5000.00"),
            "balance_due": Decimal("5000.00"),
        })
        cn = CreditNoteService.create_credit_note(
            original_invoice_id=invoice.id,
            reason="RETURN",
            notes="Goods returned",
        )
        assert cn.type == InvoiceType.CREDIT_NOTE
        assert cn.related_invoice == invoice

    def test_credit_note_for_draft_fails(self, invoice_data):
        from apps.invoices.services.credit_note_service import CreditNoteService
        invoice = Invoice.objects.create(**invoice_data)
        with pytest.raises(InvoiceError):
            CreditNoteService.create_credit_note(
                original_invoice_id=invoice.id,
                reason="RETURN",
            )


class TestDebitNoteService:
    """Tests for DebitNoteService."""

    def test_create_debit_note(self, invoice_data):
        from apps.invoices.services.debit_note_service import DebitNoteService
        invoice = Invoice.objects.create(**{
            **invoice_data,
            "status": InvoiceStatus.ISSUED,
            "invoice_number": "INV-2025-00101",
            "total": Decimal("5000.00"),
            "balance_due": Decimal("5000.00"),
        })
        dn = DebitNoteService.create_debit_note(
            original_invoice_id=invoice.id,
            reason="UNDERCHARGE",
            amount=Decimal("500.00"),
            notes="Additional charges",
        )
        assert dn.type == InvoiceType.DEBIT_NOTE
        assert dn.related_invoice == invoice
