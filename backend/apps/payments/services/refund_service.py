"""
Refund service.

Handles the refund workflow: request, approval, rejection,
processing, balance updates, and method-specific refund handling.
"""

import logging
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps.payments.constants import PaymentStatus
from apps.payments.exceptions import PaymentValidationError, RefundError
from apps.payments.models.refund import REFUND_TRANSITIONS, RefundMethod, RefundStatus
from apps.payments.services.number_generator import PaymentNumberGenerator

logger = logging.getLogger(__name__)


class RefundService:
    """
    Service for managing refund workflow.
    """

    @staticmethod
    @transaction.atomic
    def request_refund(
        original_payment,
        amount,
        reason,
        reason_notes="",
        refund_method=None,
        user=None,
        customer_notes="",
        notes="",
    ):
        """
        Create a refund request for an original payment.

        Args:
            original_payment: The Payment being refunded.
            amount: Refund amount.
            reason: RefundReason choice.
            reason_notes: Additional reason details.
            refund_method: How to refund (defaults to ORIGINAL).
            user: User requesting the refund.
            customer_notes: Notes visible to customer.
            notes: Internal notes.

        Returns:
            Refund instance.
        """
        from apps.payments.models.refund import Refund, RefundMethod as RM

        amount = Decimal(str(amount))

        # Validate payment status
        if original_payment.status != PaymentStatus.COMPLETED:
            raise RefundError("Can only refund completed payments.")

        # Validate amount doesn't exceed available refundable
        if not original_payment.can_be_refunded(amount):
            remaining = original_payment.get_remaining_refundable()
            raise RefundError(
                f"Refund amount ({amount}) exceeds available "
                f"refundable amount ({remaining})."
            )

        number = PaymentNumberGenerator.generate()
        refund_number = f"REF-{number[4:]}"

        # Infer invoice/customer from original payment
        invoice = getattr(original_payment, "invoice", None)
        customer = getattr(original_payment, "customer", None)

        refund = Refund.objects.create(
            refund_number=refund_number,
            original_payment=original_payment,
            invoice=invoice,
            customer=customer,
            amount=amount,
            reason=reason,
            reason_notes=reason_notes,
            refund_method=refund_method or RM.ORIGINAL,
            status=RefundStatus.PENDING,
            requested_by=user,
            customer_notes=customer_notes,
            notes=notes,
        )

        logger.info(
            "Refund requested: %s for %s from payment %s",
            refund_number,
            amount,
            original_payment.payment_number,
        )

        return refund

    @staticmethod
    @transaction.atomic
    def approve_refund(refund, user, notes=""):
        """
        Approve a pending refund request.

        Args:
            refund: Refund instance.
            user: User approving.
            notes: Optional approval notes.

        Returns:
            Updated Refund.
        """
        RefundService._transition_status(refund, RefundStatus.APPROVED)
        refund.approved_by = user
        refund.approved_at = timezone.now()
        if notes:
            refund.notes = f"{refund.notes}\n[Approved] {notes}".strip()
        refund.save(update_fields=["status", "approved_by", "approved_at", "notes", "updated_on"])

        logger.info("Refund %s approved by %s", refund.refund_number, user)
        return refund

    @staticmethod
    @transaction.atomic
    def reject_refund(refund, user, notes=""):
        """
        Reject a pending refund request.

        Args:
            refund: Refund instance.
            user: User rejecting.
            notes: Rejection reason/notes.

        Returns:
            Updated Refund.
        """
        RefundService._transition_status(refund, RefundStatus.REJECTED)
        refund.rejection_reason = notes
        if notes:
            refund.notes = f"{refund.notes}\n[Rejected] {notes}".strip()
        refund.save(update_fields=["status", "rejection_reason", "notes", "updated_on"])

        logger.info("Refund %s rejected", refund.refund_number)
        return refund

    @staticmethod
    @transaction.atomic
    def process_refund(refund, user, transaction_id="", reference_number=""):
        """
        Process an approved refund: update payment status,
        invoice balance, and customer credit as needed.

        Args:
            refund: Approved Refund instance.
            user: User processing.
            transaction_id: External transaction ID.
            reference_number: External reference number.

        Returns:
            Updated Refund.
        """
        RefundService._transition_status(refund, RefundStatus.PROCESSED)
        refund.processed_by = user
        refund.processed_at = timezone.now()
        refund.completed_at = timezone.now()
        if transaction_id:
            refund.transaction_id = transaction_id
        if reference_number:
            refund.reference_number = reference_number
        refund.save(update_fields=[
            "status", "processed_by", "processed_at", "completed_at",
            "transaction_id", "reference_number", "updated_on",
        ])

        original = refund.original_payment

        # Update payment refund tracking
        original.update_refund_status()

        # If fully refunded, mark original payment as REFUNDED
        if original.refund_status == "FULLY_REFUNDED":
            from apps.payments.services.payment_service import PaymentService

            try:
                PaymentService._transition_status(original, PaymentStatus.REFUNDED, user)
                original.save(update_fields=["status", "updated_on"])
            except Exception:
                pass  # Partial refund — don't change original status

        # Update invoice balance if applicable
        RefundService._update_invoice_balance(refund)

        # Issue store credit if refund method is STORE_CREDIT
        if refund.refund_method == RefundMethod.STORE_CREDIT and refund.customer:
            RefundService._apply_store_credit(refund)

        logger.info("Refund %s processed: %s", refund.refund_number, refund.amount)
        return refund

    @staticmethod
    def _update_invoice_balance(refund):
        """Update invoice balance after refund processing."""
        original = refund.original_payment
        if original.invoice and hasattr(original.invoice, "amount_paid"):
            invoice = original.invoice
            invoice.amount_paid -= refund.amount
            if invoice.amount_paid < 0:
                invoice.amount_paid = Decimal("0.00")
            invoice.balance_due = invoice.total - invoice.amount_paid
            update_fields = ["amount_paid", "balance_due"]

            try:
                from apps.invoices.constants import InvoiceStatus
                if invoice.balance_due > 0 and invoice.status == InvoiceStatus.PAID:
                    invoice.status = InvoiceStatus.PARTIAL
                    update_fields.append("status")
            except ImportError:
                pass

            invoice.save(update_fields=update_fields)

    @staticmethod
    def _apply_store_credit(refund):
        """Apply refund amount as store credit to customer."""
        customer = refund.customer
        if hasattr(customer, "current_balance"):
            customer.current_balance += refund.amount
            customer.save(update_fields=["current_balance"])

    @staticmethod
    @transaction.atomic
    def mark_failed(refund, reason=""):
        """
        Mark a processing refund as failed.

        Args:
            refund: Refund instance in PROCESSING state.
            reason: Failure reason.

        Returns:
            Updated Refund.
        """
        RefundService._transition_status(refund, RefundStatus.FAILED)
        if reason:
            refund.notes = f"{refund.notes}\n[Failed] {reason}".strip()
        refund.save(update_fields=["status", "notes", "updated_on"])

        logger.info("Refund %s failed: %s", refund.refund_number, reason)
        return refund

    @staticmethod
    @transaction.atomic
    def cancel_refund(refund, user, reason=""):
        """
        Cancel a refund request.

        Args:
            refund: Refund instance.
            user: User cancelling.
            reason: Cancellation reason.

        Returns:
            Updated Refund.
        """
        if not refund.can_be_cancelled():
            raise RefundError(
                f"Cannot cancel refund in {refund.status} status."
            )

        RefundService._transition_status(refund, RefundStatus.CANCELLED)
        if reason:
            refund.notes = f"{refund.notes}\n[Cancelled] {reason}".strip()
        refund.save(update_fields=["status", "notes", "updated_on"])

        logger.info("Refund %s cancelled: %s", refund.refund_number, reason)
        return refund

    @staticmethod
    def get_refunds_for_payment(payment):
        """Return all refunds for a payment."""
        from apps.payments.models.refund import Refund

        return Refund.objects.filter(
            original_payment=payment,
        ).order_by("-created_on")

    @staticmethod
    def get_refunds_for_customer(customer):
        """Return all refunds for a customer."""
        from apps.payments.models.refund import Refund

        return Refund.objects.filter(
            customer=customer,
        ).order_by("-created_on")

    @staticmethod
    def _transition_status(refund, new_status):
        """Validate and perform a refund status transition."""
        allowed = REFUND_TRANSITIONS.get(refund.status, [])
        if new_status not in allowed:
            raise RefundError(
                f"Cannot transition refund from '{refund.status}' to '{new_status}'."
            )
        refund.status = new_status
