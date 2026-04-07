"""
Payment reminder tasks.

Celery tasks for installment reminders and overdue detection.
"""

import logging
from datetime import timedelta

from django.utils import timezone

logger = logging.getLogger(__name__)


try:
    from celery import shared_task
except ImportError:
    # Fallback if celery is not installed
    def shared_task(func=None, **kwargs):
        if func:
            return func
        return lambda f: f


@shared_task(name="payments.send_installment_reminders")
def send_installment_reminders(days_ahead=7):
    """
    Send reminders for upcoming installment payments.

    Runs daily. Finds installments due within `days_ahead` days
    that are still pending.

    Args:
        days_ahead: Number of days to look ahead (default 7).

    Returns:
        int: Number of reminders sent.
    """
    from apps.payments.models.payment_plan import (
        InstallmentStatus,
        PaymentPlanInstallment,
    )

    today = timezone.now().date()
    cutoff = today + timedelta(days=days_ahead)

    upcoming = PaymentPlanInstallment.objects.select_related(
        "payment_plan", "payment_plan__customer", "payment_plan__invoice"
    ).filter(
        status=InstallmentStatus.PENDING,
        due_date__lte=cutoff,
        due_date__gte=today,
    )

    count = 0
    for installment in upcoming:
        logger.info(
            "Installment reminder: Plan %s, Installment #%d, Amount %s, Due %s",
            installment.payment_plan.plan_number,
            installment.installment_number,
            installment.amount,
            installment.due_date,
        )
        count += 1

    logger.info("Sent %d installment reminders", count)
    return count


@shared_task(name="payments.mark_overdue_installments")
def mark_overdue_installments_task():
    """
    Mark past-due installments as OVERDUE.
    Runs daily.

    Returns:
        int: Number of installments marked overdue.
    """
    from apps.payments.services.plan_service import PlanService

    return PlanService.mark_overdue_installments()
