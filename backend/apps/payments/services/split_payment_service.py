"""
Split payment service.

Handles creation, validation, and query operations for split payment
transactions where a single total is paid via multiple payment methods.
"""

import logging
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.payments.constants import PaymentStatus
from apps.payments.exceptions import PaymentValidationError
from apps.payments.services.number_generator import PaymentNumberGenerator
from apps.payments.services.payment_service import PaymentService

logger = logging.getLogger(__name__)


class SplitPaymentService:
    """
    Service for recording split payments across multiple methods.
    """

    @staticmethod
    def _generate_split_payment_reference():
        """Generate a unique SPLIT-YYYY-NNNNN reference number."""
        number = PaymentNumberGenerator.generate()
        return f"SP-{number[4:]}"

    @staticmethod
    @transaction.atomic
    def record_split_payment(
        total_amount,
        components,
        user,
        invoice=None,
        order=None,
        customer=None,
        notes="",
    ):
        """
        Record a split payment across multiple methods.

        Args:
            total_amount: Total payment amount.
            components: List of dicts, each with:
                - method: PaymentMethod value
                - amount: Decimal amount for this component
                - method_details: Optional dict of method-specific details
            user: User recording the payment.
            invoice: Optional linked invoice.
            order: Optional linked order.
            customer: Optional customer.
            notes: Notes for the split payment.

        Returns:
            SplitPayment instance with components.
        """
        from apps.payments.models import SplitPayment, SplitPaymentComponent
        from apps.payments.models.split_payment import SplitPaymentStatus

        # Validate components total equals total_amount
        components_total = sum(Decimal(str(c["amount"])) for c in components)
        if components_total != Decimal(str(total_amount)):
            raise PaymentValidationError(
                f"Component total ({components_total}) does not match "
                f"split payment total ({total_amount})."
            )

        if len(components) < 2:
            raise PaymentValidationError("Split payment requires at least 2 components.")

        # Validate each component has required fields
        for idx, comp in enumerate(components):
            if not comp.get("method"):
                raise PaymentValidationError(
                    f"Component {idx + 1} is missing 'method'."
                )
            comp_amount = Decimal(str(comp["amount"]))
            if comp_amount <= 0:
                raise PaymentValidationError(
                    f"Component {idx + 1} amount must be positive."
                )

        split_number = SplitPaymentService._generate_split_payment_reference()

        split_payment = SplitPayment.objects.create(
            split_payment_number=split_number,
            invoice=invoice,
            order=order,
            customer=customer,
            total_amount=total_amount,
            split_count=len(components),
            status=SplitPaymentStatus.PENDING,
            notes=notes,
        )

        for idx, comp in enumerate(components):
            comp_amount = Decimal(str(comp["amount"]))
            payment = PaymentService.create_payment(
                amount=comp_amount,
                method=comp["method"],
                invoice=invoice,
                order=order,
                customer=customer,
                user=user,
                method_details=comp.get("method_details"),
                notes=f"Split payment component {idx + 1} of {split_number}",
            )

            SplitPaymentComponent.objects.create(
                split_payment=split_payment,
                payment=payment,
                method=comp["method"],
                amount=comp_amount,
                sequence=idx,
                order_index=idx,
                method_details=comp.get("method_details") or {},
            )

        # Update status based on component payment statuses
        SplitPaymentService._update_split_status(split_payment)

        logger.info(
            "Split payment %s recorded: %s across %d components",
            split_number,
            total_amount,
            len(components),
        )

        return split_payment

    @staticmethod
    def _update_split_status(split_payment):
        """Update split payment status based on component payment statuses."""
        from apps.payments.models.split_payment import SplitPaymentStatus

        components = split_payment.components.select_related("payment").all()
        if not components.exists():
            return

        completed_count = components.filter(
            payment__status=PaymentStatus.COMPLETED,
        ).count()
        failed_count = components.filter(
            payment__status=PaymentStatus.FAILED,
        ).count()
        total_count = components.count()

        if completed_count == total_count:
            split_payment.status = SplitPaymentStatus.COMPLETED
            split_payment.processed_at = timezone.now()
        elif failed_count > 0:
            split_payment.status = SplitPaymentStatus.FAILED
        elif completed_count > 0:
            split_payment.status = SplitPaymentStatus.PARTIAL_COMPLETED
        else:
            split_payment.status = SplitPaymentStatus.PENDING

        split_payment.save(update_fields=["status", "processed_at", "updated_on"])

    @staticmethod
    def complete_split_payment(split_payment):
        """
        Mark all pending component payments as completed and update status.
        """
        from apps.payments.models.split_payment import SplitPaymentStatus

        components = split_payment.components.select_related("payment").all()
        for comp in components:
            if comp.payment.status == PaymentStatus.PENDING:
                PaymentService.complete_payment(comp.payment)

        split_payment.status = SplitPaymentStatus.COMPLETED
        split_payment.processed_at = timezone.now()
        split_payment.save(update_fields=["status", "processed_at", "updated_on"])

        logger.info("Split payment %s completed", split_payment.split_payment_number)
        return split_payment

    @staticmethod
    def get_split_payment(split_payment_number):
        """
        Retrieve a split payment by its number with components.
        """
        from apps.payments.models import SplitPayment

        return SplitPayment.objects.select_related(
            "invoice", "order", "customer",
        ).prefetch_related(
            "components__payment",
        ).get(split_payment_number=split_payment_number)

    @staticmethod
    def get_split_payments_for_invoice(invoice):
        """Return all split payments linked to an invoice."""
        from apps.payments.models import SplitPayment

        return SplitPayment.objects.filter(
            invoice=invoice,
        ).prefetch_related("components__payment").order_by("-created_on")

    @staticmethod
    def get_split_payments_for_customer(customer):
        """Return all split payments for a customer."""
        from apps.payments.models import SplitPayment

        return SplitPayment.objects.filter(
            customer=customer,
        ).prefetch_related("components__payment").order_by("-created_on")
