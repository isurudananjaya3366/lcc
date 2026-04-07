"""Payment service for vendor bill payments."""

from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.vendor_bills.constants import (
    BILL_STATUS_APPROVED,
    BILL_STATUS_PAID,
    BILL_STATUS_PARTIAL_PAID,
    CHANGE_TYPE_PAYMENT_RECORDED,
    CHANGE_TYPE_STATUS_CHANGED,
    VENDOR_PAYMENT_STATUS_COMPLETED,
    VENDOR_PAYMENT_STATUS_REVERSED,
)
from apps.vendor_bills.models.bill_history import BillHistory
from apps.vendor_bills.models.vendor_bill import VendorBill
from apps.vendor_bills.models.vendor_payment import VendorPayment


class PaymentError(Exception):
    """Base error for payment operations."""


class InsufficientBalanceError(PaymentError):
    """Payment amount exceeds outstanding balance."""


class InvalidPaymentError(PaymentError):
    """Payment cannot be processed in current state."""


class PaymentService:
    """Service for recording and managing vendor payments."""

    @classmethod
    @transaction.atomic
    def record_full_payment(cls, bill_id, user, payment_data=None):
        """Record full payment for a bill's outstanding balance."""
        bill = VendorBill.objects.select_for_update().get(pk=bill_id)
        payment_data = payment_data or {}

        if bill.status not in (
            BILL_STATUS_APPROVED,
            BILL_STATUS_PARTIAL_PAID,
        ):
            raise InvalidPaymentError(
                f"Cannot record payment for bill in '{bill.status}' status."
            )

        amount_due = bill.amount_due
        if amount_due <= 0:
            raise InvalidPaymentError("Bill has no outstanding balance.")

        payment = VendorPayment.objects.create(
            vendor=bill.vendor,
            vendor_bill=bill,
            amount=amount_due,
            payment_date=payment_data.get("payment_date", timezone.now().date()),
            payment_method=payment_data.get("payment_method", "bank_transfer"),
            status=VENDOR_PAYMENT_STATUS_COMPLETED,
            reference=payment_data.get("reference", ""),
            check_number=payment_data.get("check_number"),
            bank_name=payment_data.get("bank_name", ""),
            bank_account_number=payment_data.get("bank_account_number", ""),
            transaction_id=payment_data.get("transaction_id", ""),
            notes=payment_data.get("notes", ""),
            created_by=user,
            approved_by=user,
            approved_at=timezone.now(),
        )

        bill.amount_paid = bill.total
        old_status = bill.status
        bill.status = BILL_STATUS_PAID
        bill.save(update_fields=["amount_paid", "status", "updated_on"])

        cls._log_payment_history(
            bill,
            user,
            CHANGE_TYPE_PAYMENT_RECORDED,
            f"Full payment of {amount_due} recorded.",
            old_status=old_status,
            new_status=BILL_STATUS_PAID,
        )
        return payment

    @classmethod
    @transaction.atomic
    def record_partial_payment(cls, bill_id, amount, user, payment_data=None):
        """Record a partial payment against a bill."""
        bill = VendorBill.objects.select_for_update().get(pk=bill_id)
        payment_data = payment_data or {}
        amount = Decimal(str(amount))

        if bill.status not in (
            BILL_STATUS_APPROVED,
            BILL_STATUS_PARTIAL_PAID,
        ):
            raise InvalidPaymentError(
                f"Cannot record payment for bill in '{bill.status}' status."
            )

        amount_due = bill.amount_due
        if amount <= 0:
            raise InvalidPaymentError("Payment amount must be positive.")
        if amount > amount_due:
            raise InsufficientBalanceError(
                f"Payment amount {amount} exceeds outstanding balance {amount_due}."
            )

        payment = VendorPayment.objects.create(
            vendor=bill.vendor,
            vendor_bill=bill,
            amount=amount,
            payment_date=payment_data.get("payment_date", timezone.now().date()),
            payment_method=payment_data.get("payment_method", "bank_transfer"),
            status=VENDOR_PAYMENT_STATUS_COMPLETED,
            reference=payment_data.get("reference", ""),
            check_number=payment_data.get("check_number"),
            bank_name=payment_data.get("bank_name", ""),
            bank_account_number=payment_data.get("bank_account_number", ""),
            transaction_id=payment_data.get("transaction_id", ""),
            notes=payment_data.get("notes", ""),
            created_by=user,
            approved_by=user,
            approved_at=timezone.now(),
        )

        old_status = bill.status
        bill.amount_paid = (bill.amount_paid or Decimal("0")) + amount
        new_status = (
            BILL_STATUS_PAID
            if bill.amount_paid >= bill.total
            else BILL_STATUS_PARTIAL_PAID
        )
        bill.status = new_status
        bill.save(update_fields=["amount_paid", "status", "updated_on"])

        cls._log_payment_history(
            bill,
            user,
            CHANGE_TYPE_PAYMENT_RECORDED,
            f"Partial payment of {amount} recorded.",
            old_status=old_status,
            new_status=new_status,
        )
        return payment

    @classmethod
    @transaction.atomic
    def pay_multiple_bills(cls, vendor, bills_data, user, payment_data=None):
        """Pay multiple bills for the same vendor in a batch."""
        payment_data = payment_data or {}
        payments = []
        for item in bills_data:
            bill_id = item["bill_id"]
            amount = Decimal(str(item["amount"]))
            payment = cls.record_partial_payment(
                bill_id, amount, user, payment_data
            )
            payments.append(payment)
        return payments

    @classmethod
    @transaction.atomic
    def record_advance_payment(cls, vendor, amount, user, payment_data=None):
        """Record an advance payment to a vendor without a specific bill."""
        payment_data = payment_data or {}
        amount = Decimal(str(amount))

        if amount <= 0:
            raise InvalidPaymentError("Payment amount must be positive.")

        payment = VendorPayment.objects.create(
            vendor=vendor,
            vendor_bill=None,
            amount=amount,
            payment_date=payment_data.get("payment_date", timezone.now().date()),
            payment_method=payment_data.get("payment_method", "bank_transfer"),
            status=VENDOR_PAYMENT_STATUS_COMPLETED,
            reference=payment_data.get("reference", ""),
            check_number=payment_data.get("check_number"),
            bank_name=payment_data.get("bank_name", ""),
            bank_account_number=payment_data.get("bank_account_number", ""),
            transaction_id=payment_data.get("transaction_id", ""),
            notes=payment_data.get("notes", ""),
            created_by=user,
            approved_by=user,
            approved_at=timezone.now(),
            is_advance=True,
        )
        return payment

    @classmethod
    @transaction.atomic
    def void_payment(cls, payment_id, user, reason=""):
        """Reverse / void a completed payment."""
        payment = VendorPayment.objects.select_for_update().get(pk=payment_id)

        if payment.status != VENDOR_PAYMENT_STATUS_COMPLETED:
            raise InvalidPaymentError(
                f"Cannot void payment in '{payment.status}' status."
            )

        payment.status = VENDOR_PAYMENT_STATUS_REVERSED
        payment.notes = (
            f"{payment.notes}\nVoided by {user}: {reason}".strip()
        )
        payment.save(update_fields=["status", "notes", "updated_on"])

        # Reverse the bill balance if payment was linked to a bill
        bill = payment.vendor_bill
        if bill is not None:
            old_status = bill.status
            bill.amount_paid = max(
                Decimal("0"),
                (bill.amount_paid or Decimal("0")) - payment.amount,
            )
            if bill.amount_paid <= 0:
                bill.status = BILL_STATUS_APPROVED
            elif bill.amount_paid < bill.total:
                bill.status = BILL_STATUS_PARTIAL_PAID
            bill.save(update_fields=["amount_paid", "status", "updated_on"])

            cls._log_payment_history(
                bill,
                user,
                CHANGE_TYPE_STATUS_CHANGED,
                f"Payment {payment.payment_number} voided. Reason: {reason}",
                old_status=old_status,
                new_status=bill.status,
            )
        return payment

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    @classmethod
    def _log_payment_history(
        cls,
        bill,
        user,
        change_type,
        description,
        old_status="",
        new_status="",
    ):
        """Create a BillHistory entry for a payment event."""
        BillHistory.objects.create(
            vendor_bill=bill,
            changed_by=user,
            change_type=change_type,
            old_status=old_status,
            new_status=new_status,
            description=description,
            changes={},
            data_snapshot={},
        )
