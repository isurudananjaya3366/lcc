"""Payment service tests."""

import pytest
from decimal import Decimal

from apps.payments.constants import PaymentMethod, PaymentStatus
from apps.payments.exceptions import (
    DuplicatePaymentError,
    InvalidPaymentStatusTransition,
    PaymentValidationError,
    RefundError,
)
from apps.payments.models import Payment, PaymentHistory, Refund
from apps.payments.services.number_generator import PaymentNumberGenerator
from apps.payments.services.payment_service import PaymentService
from apps.payments.services.receipt_service import ReceiptService
from apps.payments.services.refund_service import RefundService

pytestmark = pytest.mark.django_db


class TestPaymentNumberGenerator:
    """Tests for PaymentNumberGenerator."""

    def test_generate_number(self, tenant_context):
        number = PaymentNumberGenerator.generate()
        assert number.startswith("PAY-")
        parts = number.split("-")
        assert len(parts) == 3
        assert len(parts[2]) == 5

    def test_sequential_numbers(self, tenant_context):
        n1 = PaymentNumberGenerator.generate()
        n2 = PaymentNumberGenerator.generate()
        seq1 = int(n1.split("-")[-1])
        seq2 = int(n2.split("-")[-1])
        assert seq2 == seq1 + 1

    def test_generate_with_year(self, tenant_context):
        number = PaymentNumberGenerator.generate(year=2024)
        assert "2024" in number


class TestPaymentService:
    """Tests for PaymentService."""

    def test_create_payment(self, tenant_context, customer):
        payment = PaymentService.create_payment(
            method=PaymentMethod.CASH,
            amount=Decimal("5000.00"),
            customer=customer,
        )
        assert payment.payment_number.startswith("PAY-")
        assert payment.status == PaymentStatus.PENDING
        assert payment.amount == Decimal("5000.00")
        assert payment.customer == customer

    def test_create_payment_with_invoice(self, tenant_context, customer, invoice):
        payment = PaymentService.create_payment(
            method=PaymentMethod.CASH,
            amount=Decimal("5000.00"),
            customer=customer,
            invoice=invoice,
        )
        assert payment.invoice == invoice

    def test_create_payment_history_logged(self, tenant_context, customer):
        payment = PaymentService.create_payment(
            method=PaymentMethod.CASH,
            amount=Decimal("1000.00"),
            customer=customer,
        )
        assert PaymentHistory.objects.filter(payment=payment).count() >= 1

    def test_complete_payment(self, payment, user):
        PaymentService.complete_payment(payment, user=user)
        payment.refresh_from_db()
        assert payment.status == PaymentStatus.COMPLETED
        assert payment.processed_at is not None

    def test_fail_payment(self, payment, user):
        PaymentService.fail_payment(payment, reason="Declined", user=user)
        payment.refresh_from_db()
        assert payment.status == PaymentStatus.FAILED

    def test_cancel_payment(self, payment, user):
        PaymentService.cancel_payment(payment, reason="Changed mind", user=user)
        payment.refresh_from_db()
        assert payment.status == PaymentStatus.CANCELLED
        assert payment.cancelled_at is not None

    def test_cannot_complete_cancelled(self, payment, user):
        PaymentService.cancel_payment(payment, user=user)
        with pytest.raises(InvalidPaymentStatusTransition):
            PaymentService.complete_payment(payment, user=user)

    def test_record_cash_payment(self, tenant_context, customer, invoice, user):
        result = PaymentService.record_cash_payment(
            amount=Decimal("5000.00"),
            user=user,
            customer=customer,
            invoice=invoice,
        )
        payment = result["payment"]
        assert payment.method == PaymentMethod.CASH
        assert payment.status == PaymentStatus.COMPLETED

    def test_record_card_payment(self, tenant_context, customer, user):
        payment = PaymentService.record_card_payment(
            amount=Decimal("3000.00"),
            card_details={"card_type": "Visa", "last_four": "1234"},
            user=user,
            customer=customer,
        )
        assert payment.method == PaymentMethod.CARD

    def test_record_bank_transfer(self, tenant_context, customer, user):
        payment = PaymentService.record_bank_transfer(
            amount=Decimal("10000.00"),
            bank_details={"bank_name": "BOC", "reference_number": "TRF-12345"},
            user=user,
            customer=customer,
        )
        assert payment.method == PaymentMethod.BANK_TRANSFER
        assert payment.reference_number == "TRF-12345"

    def test_allocate_to_invoice(self, completed_payment, invoice):
        alloc = PaymentService.allocate_to_invoice(completed_payment, invoice, Decimal("5000.00"))
        assert alloc.amount == Decimal("5000.00")
        invoice.refresh_from_db()
        assert invoice.amount_paid == Decimal("5000.00")

    def test_validate_payment_data(self, tenant_context):
        # Valid data should not raise
        PaymentService.validate_payment_data(
            method=PaymentMethod.CASH,
            amount=Decimal("100.00"),
        )

    def test_validate_payment_data_negative_amount(self, tenant_context):
        with pytest.raises(PaymentValidationError):
            PaymentService.validate_payment_data(
                method=PaymentMethod.CASH,
                amount=Decimal("-100.00"),
            )

    def test_approve_payment(self, payment, user):
        PaymentService.approve_payment(payment, user=user)
        payment.refresh_from_db()
        assert payment.approved_by == user


class TestRefundService:
    """Tests for RefundService."""

    def test_request_refund(self, completed_payment, user):
        refund = RefundService.request_refund(
            original_payment=completed_payment,
            amount=Decimal("1000.00"),
            reason="RETURN",
            user=user,
        )
        assert refund.status == "PENDING"
        assert refund.amount == Decimal("1000.00")

    def test_refund_exceeds_payment(self, completed_payment, user):
        with pytest.raises(RefundError):
            RefundService.request_refund(
                original_payment=completed_payment,
                amount=Decimal("999999.00"),
                reason="RETURN",
                user=user,
            )

    def test_approve_refund(self, completed_payment, user):
        refund = RefundService.request_refund(
            original_payment=completed_payment,
            amount=Decimal("500.00"),
            reason="OVERCHARGE",
            user=user,
        )
        RefundService.approve_refund(refund, user=user)
        refund.refresh_from_db()
        assert refund.status == "APPROVED"

    def test_reject_refund(self, completed_payment, user):
        refund = RefundService.request_refund(
            original_payment=completed_payment,
            amount=Decimal("500.00"),
            reason="OVERCHARGE",
            user=user,
        )
        RefundService.reject_refund(refund, notes="Not eligible", user=user)
        refund.refresh_from_db()
        assert refund.status == "REJECTED"

    def test_process_refund(self, completed_payment, user):
        refund = RefundService.request_refund(
            original_payment=completed_payment,
            amount=Decimal("500.00"),
            reason="RETURN",
            user=user,
        )
        RefundService.approve_refund(refund, user=user)
        RefundService.process_refund(refund, user=user)
        refund.refresh_from_db()
        assert refund.status == "PROCESSED"


class TestReceiptService:
    """Tests for ReceiptService."""

    def test_generate_receipt(self, completed_payment):
        receipt = ReceiptService.generate_receipt(completed_payment)
        assert receipt.receipt_number.startswith("REC-")
        assert receipt.receipt_amount == completed_payment.amount

    def test_generate_receipt_idempotent(self, completed_payment):
        r1 = ReceiptService.generate_receipt(completed_payment)
        r2 = ReceiptService.generate_receipt(completed_payment)
        assert r1.id == r2.id

    def test_generate_receipt_pending_fails(self, payment):
        with pytest.raises(ValueError, match="completed"):
            ReceiptService.generate_receipt(payment)

    def test_get_receipt_by_payment(self, completed_payment):
        ReceiptService.generate_receipt(completed_payment)
        receipt = ReceiptService.get_receipt_by_payment(completed_payment)
        assert receipt is not None
        assert receipt.payment == completed_payment
