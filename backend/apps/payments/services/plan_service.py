"""
Payment plan service.

Handles creation, tracking, installment payment recording,
overdue handling, and reminder sending for payment plans.
"""

import logging
from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.payments.exceptions import PaymentValidationError
from apps.payments.models.payment_plan import (
    InstallmentStatus,
    PaymentPlan,
    PaymentPlanInstallment,
    PlanFrequency,
    PlanStatus,
)
from apps.payments.services.number_generator import PaymentNumberGenerator

logger = logging.getLogger(__name__)

FREQUENCY_DAYS = {
    PlanFrequency.WEEKLY: 7,
    PlanFrequency.BIWEEKLY: 14,
    PlanFrequency.MONTHLY: 30,
    PlanFrequency.QUARTERLY: 90,
}


class PlanService:
    """
    Service for managing payment plans and installments.
    """

    @staticmethod
    def _generate_plan_number():
        """Generate a unique PP-YYYY-NNNNN plan number."""
        number = PaymentNumberGenerator.generate()
        return f"PP-{number[4:]}"

    @staticmethod
    @transaction.atomic
    def create_plan(
        invoice,
        customer,
        total_amount,
        number_of_installments,
        start_date,
        frequency=PlanFrequency.MONTHLY,
        distribution="EQUAL",
        custom_amounts=None,
        plan_name="",
        allow_early_payment=True,
        late_fee_applicable=False,
        grace_period_days=3,
        max_missed_installments=2,
        created_by=None,
        notes="",
    ):
        """
        Create a payment plan with scheduled installments.

        Args:
            invoice: Invoice to create the plan for.
            customer: Customer making the payments.
            total_amount: Total amount to be paid.
            number_of_installments: Number of installments (2-24).
            start_date: Date of first installment.
            frequency: Installment frequency.
            distribution: EQUAL, WEIGHTED, or CUSTOM.
            custom_amounts: List of amounts for CUSTOM distribution.
            plan_name: Optional descriptive name.
            allow_early_payment: Whether early payments are allowed.
            late_fee_applicable: Whether late fees apply.
            grace_period_days: Days after due date before late fees.
            max_missed_installments: Max overdue before default.
            created_by: User creating the plan.
            notes: Optional plan notes.

        Returns:
            PaymentPlan with installments.
        """
        if number_of_installments < 2:
            raise PaymentValidationError("Payment plan requires at least 2 installments.")

        if number_of_installments > 24:
            raise PaymentValidationError("Payment plan cannot exceed 24 installments.")

        if total_amount <= 0:
            raise PaymentValidationError("Total amount must be positive.")

        plan_number = PlanService._generate_plan_number()

        # Calculate installment amounts based on distribution strategy
        amounts = PlanService._calculate_installment_amounts(
            total_amount, number_of_installments, distribution, custom_amounts,
        )

        # Calculate end date
        days_between = FREQUENCY_DAYS.get(frequency, 30)
        end_date = start_date + timedelta(days=days_between * (number_of_installments - 1))

        plan = PaymentPlan.objects.create(
            plan_number=plan_number,
            plan_name=plan_name,
            invoice=invoice,
            customer=customer,
            total_amount=total_amount,
            number_of_installments=number_of_installments,
            frequency=frequency,
            start_date=start_date,
            end_date=end_date,
            status=PlanStatus.ACTIVE,
            allow_early_payment=allow_early_payment,
            late_fee_applicable=late_fee_applicable,
            grace_period_days=grace_period_days,
            max_missed_installments=max_missed_installments,
            created_by=created_by,
            notes=notes,
        )

        installments = []
        for i in range(number_of_installments):
            due_date = start_date + timedelta(days=days_between * i)
            installments.append(
                PaymentPlanInstallment(
                    payment_plan=plan,
                    installment_number=i + 1,
                    due_date=due_date,
                    amount=amounts[i],
                    amount_paid=Decimal("0"),
                    status=InstallmentStatus.PENDING,
                )
            )

        PaymentPlanInstallment.objects.bulk_create(installments)

        logger.info(
            "Payment plan %s created: %s in %d installments for invoice %s",
            plan_number,
            total_amount,
            number_of_installments,
            getattr(invoice, "invoice_number", invoice.pk),
        )

        return plan

    @staticmethod
    def _calculate_installment_amounts(total_amount, count, distribution, custom_amounts=None):
        """
        Calculate installment amounts based on distribution strategy.

        Args:
            total_amount: Total plan amount.
            count: Number of installments.
            distribution: EQUAL, WEIGHTED, or CUSTOM.
            custom_amounts: Required for CUSTOM distribution.

        Returns:
            list[Decimal]: List of installment amounts.
        """
        if distribution == "CUSTOM":
            if not custom_amounts or len(custom_amounts) != count:
                raise PaymentValidationError(
                    f"CUSTOM distribution requires exactly {count} amounts."
                )
            amounts = [Decimal(str(a)) for a in custom_amounts]
            if sum(amounts) != Decimal(str(total_amount)):
                raise PaymentValidationError(
                    "Custom amounts must sum to the total amount."
                )
            return amounts

        if distribution == "WEIGHTED":
            # 40% first installment, rest equal
            first_amount = (total_amount * Decimal("0.4")).quantize(Decimal("0.01"))
            remaining = total_amount - first_amount
            if count > 1:
                rest_amount = (remaining / (count - 1)).quantize(Decimal("0.01"))
                amounts = [first_amount]
                for i in range(1, count):
                    if i == count - 1:
                        # Adjust last to absorb rounding
                        amounts.append(remaining - rest_amount * (count - 2))
                    else:
                        amounts.append(rest_amount)
                return amounts
            return [total_amount]

        # EQUAL distribution (default)
        base_amount = (total_amount / count).quantize(Decimal("0.01"))
        remainder = total_amount - (base_amount * count)
        amounts = [base_amount] * count
        # Add remainder to last installment
        amounts[-1] += remainder
        return amounts

    @staticmethod
    @transaction.atomic
    def record_installment_payment(installment, payment):
        """
        Record a payment against a specific installment.

        Args:
            installment: PaymentPlanInstallment instance.
            payment: Payment instance.

        Returns:
            Updated installment.
        """
        if installment.status == InstallmentStatus.PAID:
            raise PaymentValidationError("Installment is already paid.")

        if installment.status == InstallmentStatus.CANCELLED:
            raise PaymentValidationError("Cannot pay a cancelled installment.")

        installment.payment = payment
        installment.paid_date = timezone.now().date()
        installment.amount_paid = payment.amount

        if installment.amount_paid >= installment.amount:
            installment.status = InstallmentStatus.PAID
        else:
            installment.status = InstallmentStatus.PARTIAL

        installment.save(update_fields=[
            "payment", "paid_date", "amount_paid", "status", "updated_on",
        ])

        # Update plan last_payment_date
        plan = installment.payment_plan
        plan.last_payment_date = timezone.now().date()
        plan.save(update_fields=["last_payment_date", "updated_on"])

        # Check if the entire plan is complete
        PlanService._check_plan_completion(plan)

        return installment

    @staticmethod
    @transaction.atomic
    def apply_payment_to_installment(installment, amount):
        """
        Apply a partial or full amount to an installment.

        Updates amount_paid and transitions status accordingly.

        Args:
            installment: PaymentPlanInstallment instance.
            amount: Decimal amount to apply.

        Returns:
            Updated installment.
        """
        if installment.status in (InstallmentStatus.PAID, InstallmentStatus.CANCELLED):
            raise PaymentValidationError(
                f"Cannot apply payment to {installment.status} installment."
            )

        installment.amount_paid += Decimal(str(amount))

        if installment.amount_paid >= installment.amount:
            installment.status = InstallmentStatus.PAID
            installment.paid_date = timezone.now().date()
        elif installment.amount_paid > 0:
            installment.status = InstallmentStatus.PARTIAL

        installment.save(update_fields=[
            "amount_paid", "status", "paid_date", "updated_on",
        ])

        plan = installment.payment_plan
        plan.last_payment_date = timezone.now().date()
        plan.save(update_fields=["last_payment_date", "updated_on"])

        PlanService._check_plan_completion(plan)

        return installment

    @staticmethod
    def _check_plan_completion(plan):
        """Check if plan is fully paid and update status if so."""
        pending_count = plan.installments.exclude(
            status__in=[InstallmentStatus.PAID, InstallmentStatus.CANCELLED],
        ).count()

        if pending_count == 0:
            plan.status = PlanStatus.COMPLETED
            plan.completed_at = timezone.now()
            plan.save(update_fields=["status", "completed_at", "updated_on"])
            logger.info("Payment plan %s completed", plan.plan_number)

    @staticmethod
    def mark_overdue_installments():
        """
        Mark past-due installments as OVERDUE.
        Called by a scheduled task.

        Returns:
            int: Number of installments marked overdue.
        """
        today = timezone.now().date()
        overdue = PaymentPlanInstallment.objects.filter(
            status__in=[InstallmentStatus.PENDING, InstallmentStatus.PARTIAL],
            due_date__lt=today,
        )
        count = overdue.update(status=InstallmentStatus.OVERDUE)

        if count > 0:
            logger.info("Marked %d installments as overdue", count)

        return count

    @staticmethod
    @transaction.atomic
    def mark_installment_overdue(installment, apply_late_fee=False):
        """
        Mark a single installment as overdue, optionally applying a late fee.

        Args:
            installment: PaymentPlanInstallment to mark.
            apply_late_fee: Whether to apply late fee from FeeCalculatorService.

        Returns:
            Updated installment.
        """
        if installment.status in (InstallmentStatus.PAID, InstallmentStatus.CANCELLED):
            return installment

        installment.status = InstallmentStatus.OVERDUE

        if apply_late_fee and installment.late_fee_applied == 0:
            plan = installment.payment_plan
            if plan.late_fee_applicable:
                try:
                    from apps.payments.services.fee_calculator_service import FeeCalculatorService
                    fee = FeeCalculatorService.calculate_late_fee(
                        plan.invoice, as_of_date=timezone.now().date(),
                    )
                    installment.late_fee_applied = fee
                except Exception:
                    logger.warning(
                        "Failed to calculate late fee for installment %s",
                        installment.pk,
                    )

        installment.save(update_fields=["status", "late_fee_applied", "updated_on"])
        return installment

    @staticmethod
    @transaction.atomic
    def default_payment_plan(plan, reason=""):
        """
        Mark a plan as DEFAULTED when overdue count exceeds max.

        Args:
            plan: PaymentPlan instance.
            reason: Reason for defaulting.

        Returns:
            Updated plan.
        """
        if plan.status in (PlanStatus.COMPLETED, PlanStatus.CANCELLED):
            raise PaymentValidationError(f"Cannot default a {plan.status} plan.")

        plan.status = PlanStatus.DEFAULTED
        if reason:
            plan.notes = f"{plan.notes}\nDefaulted: {reason}".strip()
        plan.save(update_fields=["status", "notes", "updated_on"])

        logger.info("Payment plan %s defaulted: %s", plan.plan_number, reason)
        return plan

    @staticmethod
    def check_and_default_plans():
        """
        Check active plans for excess overdue installments and default them.

        Returns:
            int: Number of plans defaulted.
        """
        active_plans = PaymentPlan.objects.filter(status=PlanStatus.ACTIVE)
        defaulted_count = 0

        for plan in active_plans:
            if plan.is_defaulted():
                PlanService.default_payment_plan(
                    plan, reason="Exceeded maximum missed installments.",
                )
                defaulted_count += 1

        return defaulted_count

    @staticmethod
    @transaction.atomic
    def cancel_plan(plan, reason=""):
        """
        Cancel a payment plan and its pending installments.

        Args:
            plan: PaymentPlan instance.
            reason: Reason for cancellation.

        Returns:
            Updated plan.
        """
        if plan.status in (PlanStatus.COMPLETED, PlanStatus.CANCELLED):
            raise PaymentValidationError(f"Cannot cancel a {plan.status} plan.")

        plan.status = PlanStatus.CANCELLED
        plan.notes = f"{plan.notes}\nCancelled: {reason}".strip() if reason else plan.notes
        plan.save(update_fields=["status", "notes", "updated_on"])

        # Cancel pending installments
        plan.installments.filter(
            status__in=[InstallmentStatus.PENDING, InstallmentStatus.OVERDUE, InstallmentStatus.PARTIAL]
        ).update(status=InstallmentStatus.CANCELLED)

        logger.info("Payment plan %s cancelled: %s", plan.plan_number, reason)
        return plan

    @staticmethod
    def send_installment_reminder(installment, reminder_type="UPCOMING"):
        """
        Send a payment reminder for an installment.

        Args:
            installment: PaymentPlanInstallment instance.
            reminder_type: UPCOMING or OVERDUE.

        Returns:
            bool: Whether reminder was sent.
        """
        today = timezone.now().date()

        # 3-day cooldown to prevent duplicate reminders
        if installment.reminder_sent_date and (today - installment.reminder_sent_date).days < 3:
            logger.debug(
                "Skipping reminder for installment %s (cooldown)",
                installment.pk,
            )
            return False

        # Would integrate with PaymentEmailService here
        logger.info(
            "Sending %s reminder for installment %s of plan %s",
            reminder_type,
            installment.installment_number,
            installment.payment_plan.plan_number,
        )

        installment.reminder_sent_date = today
        installment.save(update_fields=["reminder_sent_date", "updated_on"])
        return True

    @staticmethod
    def check_upcoming_installments(days_ahead=3):
        """
        Find installments due within days_ahead and send reminders.

        Args:
            days_ahead: Number of days to look ahead.

        Returns:
            int: Number of reminders sent.
        """
        today = timezone.now().date()
        upcoming_date = today + timedelta(days=days_ahead)

        upcoming = PaymentPlanInstallment.objects.filter(
            status=InstallmentStatus.PENDING,
            due_date__lte=upcoming_date,
            due_date__gte=today,
            payment_plan__status=PlanStatus.ACTIVE,
        ).select_related("payment_plan")

        sent_count = 0
        for installment in upcoming:
            if PlanService.send_installment_reminder(installment, "UPCOMING"):
                sent_count += 1

        return sent_count
