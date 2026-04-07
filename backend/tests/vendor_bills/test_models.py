"""Tests for vendor_bills models."""

import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError

pytestmark = pytest.mark.django_db


class TestVendorBillModel:
    """Tests for the VendorBill model."""

    def test_create_vendor_bill(self, vendor_bill):
        assert vendor_bill.pk is not None
        assert vendor_bill.bill_number.startswith("BILL-")
        assert vendor_bill.status == "draft"

    def test_bill_number_auto_generated(self, vendor_bill):
        assert vendor_bill.bill_number
        assert len(vendor_bill.bill_number) > 0

    def test_amount_due_property(self, vendor_bill):
        vendor_bill.total = Decimal("100.00")
        vendor_bill.amount_paid = Decimal("40.00")
        vendor_bill.save(update_fields=["total", "amount_paid"])
        assert vendor_bill.amount_due == Decimal("60.00")

    def test_is_overdue_property(self, vendor_bill):
        from django.utils import timezone
        from datetime import timedelta

        vendor_bill.due_date = timezone.now().date() - timedelta(days=5)
        vendor_bill.total = Decimal("100")
        vendor_bill.amount_paid = Decimal("0")
        vendor_bill.status = "approved"
        vendor_bill.save(update_fields=["due_date", "total", "amount_paid", "status"])
        assert vendor_bill.is_overdue is True

    def test_is_not_overdue_when_paid(self, vendor_bill):
        from django.utils import timezone
        from datetime import timedelta

        vendor_bill.due_date = timezone.now().date() - timedelta(days=5)
        vendor_bill.total = Decimal("100")
        vendor_bill.amount_paid = Decimal("100")
        vendor_bill.status = "paid"
        vendor_bill.save(update_fields=["due_date", "total", "amount_paid", "status"])
        assert vendor_bill.is_overdue is False

    def test_recalculate_from_lines(self, vendor_bill_with_lines):
        bill = vendor_bill_with_lines
        # 10 * 25.00 = 250 + 20 tax = 270
        # 5 * 50.00 = 250 + 20 tax = 270
        # subtotal = 500, tax = 40, total = 540
        assert bill.subtotal == Decimal("500.00")
        assert bill.tax_amount == Decimal("40.00")
        assert bill.total == Decimal("540.00")


class TestBillLineItemModel:
    """Tests for the BillLineItem model."""

    def test_create_line_item(self, vendor_bill_with_lines):
        assert vendor_bill_with_lines.line_items.count() == 2

    def test_line_total_calculated(self, vendor_bill_with_lines):
        line = vendor_bill_with_lines.line_items.first()
        assert line.line_total is not None
        assert line.line_total > 0

    def test_tax_amount_calculated(self, vendor_bill_with_lines):
        line = vendor_bill_with_lines.line_items.first()
        assert line.tax_amount is not None


class TestBillHistoryModel:
    """Tests for the BillHistory model."""

    def test_create_history_entry(self, vendor_bill, user):
        from apps.vendor_bills.models import BillHistory

        entry = BillHistory.objects.create(
            vendor_bill=vendor_bill,
            changed_by=user,
            change_type="created",
            description="Bill created",
        )
        assert entry.pk is not None
        assert entry.change_type == "created"


class TestBillSettingsModel:
    """Tests for the BillSettings model."""

    def test_create_settings(self, tenant_context):
        from apps.vendor_bills.models import BillSettings

        settings = BillSettings.objects.create(
            bill_number_prefix="BILL",
        )
        assert settings.pk is not None
        assert settings.require_approval is True

    def test_get_next_bill_number(self, tenant_context):
        from apps.vendor_bills.models import BillSettings

        settings = BillSettings.objects.create(
            bill_number_prefix="TEST",
            bill_number_sequence=1,
        )
        number = settings.get_next_bill_number()
        assert number.startswith("TEST-")

    def test_is_approval_required(self, tenant_context):
        from apps.vendor_bills.models import BillSettings

        settings = BillSettings.objects.create(
            require_approval=True,
            approval_threshold=Decimal("1000.00"),
        )
        assert settings.is_approval_required(Decimal("5000.00")) is True
        assert settings.is_approval_required(Decimal("500.00")) is False


class TestVendorPaymentModel:
    """Tests for the VendorPayment model."""

    def test_create_payment(self, vendor, user):
        from apps.vendor_bills.models import VendorPayment

        payment = VendorPayment.objects.create(
            vendor=vendor,
            amount=Decimal("100.00"),
            payment_date="2025-06-15",
            created_by=user,
        )
        assert payment.pk is not None
        assert payment.payment_number.startswith("PAY-")

    def test_advance_payment(self, vendor, user):
        from apps.vendor_bills.models import VendorPayment

        payment = VendorPayment.objects.create(
            vendor=vendor,
            amount=Decimal("500.00"),
            payment_date="2025-06-15",
            is_advance=True,
            created_by=user,
        )
        assert payment.is_advance is True
        assert payment.vendor_bill is None


class TestPaymentScheduleModel:
    """Tests for the PaymentSchedule model."""

    def test_create_schedule(self, vendor_bill):
        from apps.vendor_bills.models import PaymentSchedule

        schedule = PaymentSchedule.objects.create(
            vendor_bill=vendor_bill,
            scheduled_date="2025-07-01",
            amount=Decimal("250.00"),
        )
        assert schedule.pk is not None
        assert schedule.status == "scheduled"
        assert schedule.reminder_sent is False


class TestMatchingResultModel:
    """Tests for the MatchingResult model."""

    def test_create_matching_result(self, vendor_bill_with_lines):
        from apps.vendor_bills.models import MatchingResult

        line = vendor_bill_with_lines.line_items.first()
        result = MatchingResult.objects.create(
            bill_line=line,
            vendor_bill=vendor_bill_with_lines,
            match_status="unmatched",
        )
        assert result.pk is not None
