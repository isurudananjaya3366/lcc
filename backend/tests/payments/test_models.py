"""Payment model tests."""

import pytest
from decimal import Decimal

from apps.payments.constants import PaymentMethod, PaymentStatus, ALLOWED_TRANSITIONS, TERMINAL_STATES
from apps.payments.models import (
    Payment,
    PaymentAllocation,
    PaymentHistory,
    PaymentHistoryAction,
    PaymentMethodConfig,
    PaymentReceipt,
    PaymentSequence,
    PaymentSettings,
    Refund,
)

pytestmark = pytest.mark.django_db


class TestPaymentModel:
    """Tests for the Payment model."""

    def test_create_payment(self, payment):
        assert payment.status == PaymentStatus.PENDING
        assert payment.method == PaymentMethod.CASH
        assert payment.amount == Decimal("5000.00")
        assert payment.currency == "LKR"

    def test_payment_str(self, payment):
        result = str(payment)
        assert payment.payment_number in result

    def test_payment_number_unique(self, payment, tenant_context, customer):
        from apps.payments.services.number_generator import PaymentNumberGenerator

        p2 = Payment.objects.create(
            payment_number=PaymentNumberGenerator.generate(),
            customer=customer,
            method=PaymentMethod.CARD,
            amount=Decimal("1000.00"),
        )
        assert p2.payment_number != payment.payment_number

    def test_is_pending(self, payment):
        assert payment.is_pending is True
        assert payment.is_processed is False
        assert payment.is_cancelled is False

    def test_is_processed(self, completed_payment):
        assert completed_payment.is_processed is True
        assert completed_payment.is_pending is False

    def test_is_terminal_cancelled(self, payment):
        payment.status = PaymentStatus.CANCELLED
        payment.save()
        assert payment.is_terminal is True

    def test_is_terminal_refunded(self, payment):
        payment.status = PaymentStatus.REFUNDED
        payment.save()
        assert payment.is_terminal is True

    def test_has_invoice(self, completed_payment):
        assert completed_payment.has_invoice is True

    def test_no_invoice(self, payment):
        assert payment.has_invoice is False

    def test_has_customer(self, payment):
        assert payment.has_customer is True

    def test_default_status_pending(self, tenant_context, customer):
        from apps.payments.services.number_generator import PaymentNumberGenerator

        p = Payment.objects.create(
            payment_number=PaymentNumberGenerator.generate(),
            customer=customer,
            method=PaymentMethod.CASH,
            amount=Decimal("100.00"),
        )
        assert p.status == PaymentStatus.PENDING

    def test_soft_delete(self, payment):
        payment.is_deleted = True
        payment.save()
        assert Payment.objects.filter(is_deleted=False).count() == 0


class TestPaymentSequenceModel:
    """Tests for the PaymentSequence model."""

    def test_create_sequence(self, tenant_context):
        seq = PaymentSequence.objects.create(year=2025, last_number=0)
        assert seq.year == 2025
        assert seq.last_number == 0

    def test_increment_sequence(self, tenant_context):
        seq = PaymentSequence.objects.create(year=2025, last_number=0)
        seq.last_number += 1
        seq.save()
        seq.refresh_from_db()
        assert seq.last_number == 1


class TestPaymentMethodConfigModel:
    """Tests for PaymentMethodConfig."""

    def test_create_config(self, tenant_context):
        config = PaymentMethodConfig.objects.create(
            method=PaymentMethod.CASH,
            display_name="Cash",
            is_active=True,
            display_order=1,
        )
        assert str(config) == "Cash (active)"
        assert config.is_active is True


class TestPaymentAllocationModel:
    """Tests for PaymentAllocation."""

    def test_create_allocation(self, completed_payment, invoice):
        alloc = PaymentAllocation.objects.create(
            payment=completed_payment,
            invoice=invoice,
            amount=Decimal("5000.00"),
        )
        assert alloc.amount == Decimal("5000.00")
        assert alloc.payment == completed_payment
        assert alloc.invoice == invoice


class TestPaymentHistoryModel:
    """Tests for PaymentHistory."""

    def test_create_history(self, payment, user):
        entry = PaymentHistory.objects.create(
            payment=payment,
            action=PaymentHistoryAction.CREATED,
            new_value={"status": "PENDING"},
            changed_by=user,
            description="Payment created",
        )
        assert entry.action == PaymentHistoryAction.CREATED
        assert entry.changed_by == user


class TestPaymentSettingsModel:
    """Tests for PaymentSettings."""

    def test_create_settings(self, tenant_context):
        settings = PaymentSettings.objects.create(
            default_currency="LKR",
            approval_threshold=Decimal("50000.00"),
        )
        assert settings.default_currency == "LKR"
        assert settings.approval_threshold == Decimal("50000.00")


class TestRefundModel:
    """Tests for the Refund model."""

    def test_create_refund(self, completed_payment, user):
        refund = Refund.objects.create(
            refund_number="REF-2025-00001",
            original_payment=completed_payment,
            amount=Decimal("1000.00"),
            reason="RETURN",
            refund_method="ORIGINAL",
            status="PENDING",
            requested_by=user,
        )
        assert refund.amount == Decimal("1000.00")
        assert refund.status == "PENDING"
        assert refund.original_payment == completed_payment

    def test_refund_str(self, completed_payment, user):
        refund = Refund.objects.create(
            refund_number="REF-2025-00002",
            original_payment=completed_payment,
            amount=Decimal("500.00"),
            reason="OVERCHARGE",
            status="PENDING",
            requested_by=user,
        )
        assert "REF-2025-00002" in str(refund)


class TestPaymentReceiptModel:
    """Tests for PaymentReceipt."""

    def test_create_receipt(self, completed_payment, customer):
        from django.utils import timezone

        receipt = PaymentReceipt.objects.create(
            receipt_number="REC-2025-00001",
            payment=completed_payment,
            customer=customer,
            receipt_date=timezone.now().date(),
            receipt_amount=completed_payment.amount,
            payment_method=completed_payment.method,
        )
        assert receipt.receipt_number == "REC-2025-00001"
        assert receipt.has_pdf() is False
        assert receipt.get_pdf_url() is None
        assert receipt.is_sent is False

    def test_receipt_mark_as_sent(self, completed_payment, customer, user):
        from django.utils import timezone

        receipt = PaymentReceipt.objects.create(
            receipt_number="REC-2025-00002",
            payment=completed_payment,
            customer=customer,
            receipt_date=timezone.now().date(),
            receipt_amount=completed_payment.amount,
            payment_method=completed_payment.method,
        )
        receipt.mark_as_sent(sent_to="test@example.com", sent_by=user)
        receipt.refresh_from_db()
        assert receipt.is_sent is True
        assert receipt.sent_to == "test@example.com"
        assert receipt.sent_by == user

    def test_receipt_get_display_method(self, completed_payment, customer):
        from django.utils import timezone

        receipt = PaymentReceipt.objects.create(
            receipt_number="REC-2025-00003",
            payment=completed_payment,
            customer=customer,
            receipt_date=timezone.now().date(),
            receipt_amount=completed_payment.amount,
            payment_method=PaymentMethod.CASH,
        )
        assert receipt.get_display_method() == "Cash"


class TestConstants:
    """Tests for payment constants."""

    def test_allowed_transitions(self):
        assert PaymentStatus.COMPLETED in ALLOWED_TRANSITIONS[PaymentStatus.PENDING]
        assert PaymentStatus.FAILED in ALLOWED_TRANSITIONS[PaymentStatus.PENDING]
        assert PaymentStatus.CANCELLED in ALLOWED_TRANSITIONS[PaymentStatus.PENDING]

    def test_terminal_states(self):
        assert PaymentStatus.CANCELLED in TERMINAL_STATES
        assert PaymentStatus.REFUNDED in TERMINAL_STATES

    def test_completed_can_refund(self):
        assert PaymentStatus.REFUNDED in ALLOWED_TRANSITIONS[PaymentStatus.COMPLETED]

    def test_failed_can_retry(self):
        assert PaymentStatus.PENDING in ALLOWED_TRANSITIONS[PaymentStatus.FAILED]
