"""Tests for vendor_bills services."""

import pytest
from decimal import Decimal

pytestmark = pytest.mark.django_db


class TestBillService:
    """Tests for BillService."""

    def test_create_manual_bill(self, vendor, user):
        from datetime import date
        from apps.vendor_bills.services.bill_service import BillService

        bill = BillService.create_manual(
            vendor=vendor,
            user=user,
            bill_data={
                "bill_date": date(2025, 6, 1),
                "due_date": date(2025, 7, 1),
            },
            line_items_data=[
                {
                    "item_description": "Test item",
                    "quantity": Decimal("5"),
                    "billed_price": Decimal("20.00"),
                    "tax_rate": Decimal("0"),
                },
            ],
        )
        assert bill.pk is not None
        assert bill.vendor == vendor
        assert bill.line_items.count() == 1
        assert bill.total == Decimal("100.00")

    def test_submit_bill(self, vendor_bill_with_lines, user):
        from apps.vendor_bills.services.bill_service import BillService

        bill = BillService.submit_bill(vendor_bill_with_lines.pk, user)
        assert bill.status == "pending"

    def test_approve_bill(self, vendor_bill_with_lines, user):
        from apps.vendor_bills.services.bill_service import BillService

        bill = BillService.submit_bill(vendor_bill_with_lines.pk, user)
        bill = BillService.approve_bill(bill.pk, user)
        assert bill.status == "approved"

    def test_cancel_bill(self, vendor_bill_with_lines, user):
        from apps.vendor_bills.services.bill_service import BillService

        bill = BillService.cancel_bill(vendor_bill_with_lines.pk, user, "Test cancel")
        assert bill.status == "cancelled"

    def test_dispute_bill(self, vendor_bill_with_lines, user):
        from apps.vendor_bills.services.bill_service import BillService

        bill = BillService.submit_bill(vendor_bill_with_lines.pk, user)
        bill = BillService.dispute_bill(bill.pk, user, "Price mismatch")
        assert bill.status == "disputed"

    def test_duplicate_bill(self, vendor_bill_with_lines, user):
        from apps.vendor_bills.services.bill_service import BillService

        new_bill = BillService.duplicate_bill(vendor_bill_with_lines.pk, user)
        assert new_bill.pk != vendor_bill_with_lines.pk
        assert new_bill.status == "draft"
        assert new_bill.line_items.count() == 2

    def test_add_line_item(self, vendor_bill, user):
        from apps.vendor_bills.services.bill_service import BillService

        BillService.add_line_item(
            vendor_bill.pk,
            {
                "item_description": "New item",
                "quantity": Decimal("3"),
                "billed_price": Decimal("10.00"),
                "tax_rate": Decimal("0"),
            },
            user,
        )
        assert vendor_bill.line_items.count() == 1

    def test_invalid_transition_raises(self, vendor_bill_with_lines, user):
        from apps.vendor_bills.services.bill_service import (
            BillService,
            InvalidBillTransitionError,
        )

        # Try to approve a draft bill (must go through pending first)
        with pytest.raises(InvalidBillTransitionError):
            BillService.approve_bill(vendor_bill_with_lines.pk, user)


class TestBillCalculationService:
    """Tests for BillCalculationService."""

    def test_calculate_line_total(self):
        from apps.vendor_bills.services.calculation_service import (
            BillCalculationService,
        )

        total, tax, subtotal = BillCalculationService.calculate_line_total(
            Decimal("10"), Decimal("25.00"), Decimal("8.00")
        )
        # 10 * 25 = 250, tax = 250 * 0.08 = 20, total = 270
        assert total == Decimal("270.00")
        assert tax == Decimal("20.00")
        assert subtotal == Decimal("250.00")

    def test_recalculate_bill(self, vendor_bill_with_lines):
        from apps.vendor_bills.services.calculation_service import (
            BillCalculationService,
        )

        BillCalculationService.recalculate_bill(vendor_bill_with_lines)
        vendor_bill_with_lines.refresh_from_db()
        assert vendor_bill_with_lines.subtotal == Decimal("500.00")


class TestPaymentService:
    """Tests for PaymentService."""

    def test_record_full_payment(self, approved_bill, user):
        from apps.vendor_bills.services.payment_service import PaymentService

        payment = PaymentService.record_full_payment(approved_bill.pk, user)
        approved_bill.refresh_from_db()
        assert approved_bill.status == "paid"
        assert approved_bill.amount_paid == approved_bill.total
        assert payment.amount == Decimal("540.00")

    def test_record_partial_payment(self, approved_bill, user):
        from apps.vendor_bills.services.payment_service import PaymentService

        payment = PaymentService.record_partial_payment(
            approved_bill.pk, Decimal("200.00"), user
        )
        approved_bill.refresh_from_db()
        assert approved_bill.status == "partial_paid"
        assert approved_bill.amount_paid == Decimal("200.00")
        assert payment.amount == Decimal("200.00")

    def test_record_advance_payment(self, vendor, user):
        from apps.vendor_bills.services.payment_service import PaymentService

        payment = PaymentService.record_advance_payment(
            vendor, Decimal("1000.00"), user
        )
        assert payment.is_advance is True
        assert payment.vendor_bill is None
        assert payment.amount == Decimal("1000.00")

    def test_void_payment(self, approved_bill, user):
        from apps.vendor_bills.services.payment_service import PaymentService

        payment = PaymentService.record_full_payment(approved_bill.pk, user)
        voided = PaymentService.void_payment(payment.pk, user, "Error")
        assert voided.status == "reversed"
        approved_bill.refresh_from_db()
        assert approved_bill.amount_paid == Decimal("0")
        assert approved_bill.status == "approved"

    def test_cannot_pay_draft_bill(self, vendor_bill_with_lines, user):
        from apps.vendor_bills.services.payment_service import (
            InvalidPaymentError,
            PaymentService,
        )

        with pytest.raises(InvalidPaymentError):
            PaymentService.record_full_payment(vendor_bill_with_lines.pk, user)

    def test_overpayment_raises(self, approved_bill, user):
        from apps.vendor_bills.services.payment_service import (
            InsufficientBalanceError,
            PaymentService,
        )

        with pytest.raises(InsufficientBalanceError):
            PaymentService.record_partial_payment(
                approved_bill.pk, Decimal("999999.00"), user
            )


class TestAgingService:
    """Tests for BillAgingService."""

    def test_classify_into_bucket(self):
        from apps.vendor_bills.services.aging_service import BillAgingService

        assert BillAgingService.classify_into_bucket(0) == "current"
        assert BillAgingService.classify_into_bucket(15) == "1-30"
        assert BillAgingService.classify_into_bucket(45) == "31-60"
        assert BillAgingService.classify_into_bucket(75) == "61-90"
        assert BillAgingService.classify_into_bucket(100) == "over_90"

    def test_calculate_aging(self, approved_bill):
        from apps.vendor_bills.services.aging_service import BillAgingService

        result = BillAgingService.calculate_aging()
        assert "buckets" in result
        assert "total_outstanding" in result

    def test_get_aging_summary(self, approved_bill):
        from apps.vendor_bills.services.aging_service import BillAgingService

        summary = BillAgingService.get_aging_summary()
        assert "buckets" in summary


class TestStatementService:
    """Tests for VendorStatementService."""

    def test_generate_statement(self, approved_bill, vendor):
        from apps.vendor_bills.services.statement_service import (
            VendorStatementService,
        )

        statement = VendorStatementService.generate_statement(vendor)
        assert "opening_balance" in statement
        assert "total_billed" in statement
        assert "closing_balance" in statement
        assert "bills" in statement


class TestReportService:
    """Tests for PaymentHistoryService and ReportService."""

    def test_payment_summary(self, tenant_context):
        from apps.vendor_bills.services.report_service import (
            PaymentHistoryService,
        )

        summary = PaymentHistoryService.get_payment_summary()
        assert "total_paid" in summary
        assert "payment_count" in summary

    def test_accounts_payable_summary(self, tenant_context):
        from apps.vendor_bills.services.report_service import ReportService

        result = ReportService.accounts_payable_summary()
        assert "total_outstanding" in result

    def test_dashboard_widgets(self, tenant_context):
        from apps.vendor_bills.services.report_service import ReportService

        result = ReportService.dashboard_widgets()
        assert "bills_due_soon" in result
        assert "overdue_count" in result
