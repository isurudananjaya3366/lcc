"""Receipt generation and management service."""

import logging

from django.db import transaction
from django.utils import timezone

from apps.payments.models.payment_receipt import PaymentReceipt

logger = logging.getLogger(__name__)


class ReceiptService:
    """Service for creating and managing payment receipts."""

    @staticmethod
    @transaction.atomic
    def generate_receipt(payment, user=None, notes="", generate_pdf=False):
        """
        Generate a receipt for a completed payment.

        Args:
            payment: Payment instance (must be COMPLETED).
            user: User generating the receipt (optional).
            notes: Optional notes for receipt.
            generate_pdf: Whether to trigger PDF generation.

        Returns:
            PaymentReceipt instance.
        """
        from apps.payments.constants import PaymentStatus

        if payment.status != PaymentStatus.COMPLETED:
            raise ValueError("Can only generate receipts for completed payments.")

        # Check if receipt already exists
        existing = PaymentReceipt.objects.filter(payment=payment).first()
        if existing:
            return existing

        receipt_number = ReceiptService._generate_receipt_number()

        receipt = PaymentReceipt.objects.create(
            receipt_number=receipt_number,
            payment=payment,
            invoice=payment.invoice,
            customer=payment.customer,
            receipt_date=payment.payment_date or timezone.now().date(),
            receipt_amount=payment.amount,
            payment_method=payment.method,
            reference_number=payment.reference_number or "",
            currency=payment.currency,
            exchange_rate=payment.exchange_rate,
            generated_by=user,
            notes=notes,
        )

        if generate_pdf:
            try:
                from apps.payments.services.receipt_pdf_service import ReceiptPDFService
                ReceiptPDFService.generate_receipt_pdf(receipt)
            except Exception:
                logger.warning("PDF generation failed for receipt %s", receipt_number)

        return receipt

    @staticmethod
    def validate_receipt_creation(payment):
        """
        Validate that a receipt can be created for the given payment.

        Returns:
            dict with 'valid' bool and optional 'errors' list.
        """
        from apps.payments.constants import PaymentStatus

        errors = []

        if payment.status != PaymentStatus.COMPLETED:
            errors.append(
                f"Cannot create receipt for payment {payment.payment_number} "
                f"(status: {payment.status}). Payment must be COMPLETED."
            )

        if payment.has_receipt():
            errors.append(
                f"Receipt already exists for payment {payment.payment_number}."
            )

        if errors:
            return {"valid": False, "errors": errors}
        return {"valid": True}

    @staticmethod
    @transaction.atomic
    def regenerate_receipt_pdf(receipt):
        """
        Regenerate the PDF for an existing receipt.

        Deletes the old PDF and generates a fresh one.

        Returns:
            PaymentReceipt with updated pdf_file.
        """
        from apps.payments.services.receipt_pdf_service import ReceiptPDFService

        if receipt.pdf_file:
            receipt.pdf_file.delete(save=False)
            receipt.pdf_generated_at = None
            receipt.save(update_fields=["pdf_generated_at", "updated_on"])

        return ReceiptPDFService.generate_receipt_pdf(receipt)

    @staticmethod
    def auto_generate_receipt_on_payment(payment):
        """
        Automatically generate a receipt when a payment is completed.

        Can be called from the payment completion workflow.

        Returns:
            PaymentReceipt or None if auto-generation is skipped/fails.
        """
        try:
            return ReceiptService.generate_receipt(payment, generate_pdf=True)
        except Exception:
            logger.exception("Auto receipt generation failed for payment %s", payment.id)
            return None

        return receipt

    @staticmethod
    def _generate_receipt_number():
        """Generate a unique receipt number in format REC-YYYY-NNNNN."""
        from apps.payments.models.payment_sequence import PaymentSequence

        year = timezone.now().year
        # Reuse PaymentSequence with a receipt-specific approach
        # Use a separate key space by querying max receipt number
        last_receipt = (
            PaymentReceipt.objects.filter(receipt_number__startswith=f"REC-{year}-")
            .order_by("-receipt_number")
            .values_list("receipt_number", flat=True)
            .first()
        )

        if last_receipt:
            last_seq = int(last_receipt.split("-")[-1])
            next_seq = last_seq + 1
        else:
            next_seq = 1

        return f"REC-{year}-{next_seq:05d}"

    @staticmethod
    def get_receipt(receipt_id):
        """Get a receipt by ID."""
        return PaymentReceipt.objects.select_related(
            "payment", "invoice", "customer"
        ).get(id=receipt_id)

    @staticmethod
    def get_receipt_by_payment(payment):
        """Get receipt for a specific payment."""
        return PaymentReceipt.objects.select_related(
            "payment", "invoice", "customer"
        ).filter(payment=payment).first()
