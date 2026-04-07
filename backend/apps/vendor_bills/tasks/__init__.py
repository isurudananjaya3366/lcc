"""Vendor Bills celery tasks."""

import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(name="vendor_bills.payment_reminder")
def payment_reminder(days_before=7):
    """Send reminders for bills due within *days_before* days."""
    from apps.vendor_bills.constants import (
        BILL_STATUS_APPROVED,
        BILL_STATUS_PARTIAL_PAID,
    )
    from apps.vendor_bills.models.vendor_bill import VendorBill

    cutoff = timezone.now().date() + timezone.timedelta(days=days_before)
    bills = VendorBill.objects.filter(
        status__in=[BILL_STATUS_APPROVED, BILL_STATUS_PARTIAL_PAID],
        due_date__lte=cutoff,
        due_date__gte=timezone.now().date(),
    )
    count = 0
    for bill in bills:
        # Mark schedule entries so we don't re-alert
        schedules = bill.payment_schedules.filter(
            reminder_sent=False,
            scheduled_date__lte=cutoff,
        )
        schedules.update(reminder_sent=True)
        count += 1
    logger.info("payment_reminder: flagged %d bills due within %d days.", count, days_before)
    return count


@shared_task(name="vendor_bills.overdue_bill_alert")
def overdue_bill_alert():
    """Flag overdue payment schedules and log alerts."""
    from apps.vendor_bills.constants import (
        BILL_STATUS_APPROVED,
        BILL_STATUS_PARTIAL_PAID,
        SCHEDULE_STATUS_OVERDUE,
        SCHEDULE_STATUS_SCHEDULED,
    )
    from apps.vendor_bills.models.payment_schedule import PaymentSchedule
    from apps.vendor_bills.models.vendor_bill import VendorBill

    today = timezone.now().date()

    # Mark overdue schedule entries
    overdue_schedules = PaymentSchedule.objects.filter(
        status=SCHEDULE_STATUS_SCHEDULED,
        scheduled_date__lt=today,
    )
    updated = overdue_schedules.update(status=SCHEDULE_STATUS_OVERDUE)

    # Count overdue bills
    overdue_bills = VendorBill.objects.filter(
        status__in=[BILL_STATUS_APPROVED, BILL_STATUS_PARTIAL_PAID],
        due_date__lt=today,
    ).count()

    logger.info(
        "overdue_bill_alert: %d schedule entries marked overdue, %d overdue bills.",
        updated,
        overdue_bills,
    )
    return {"overdue_schedules": updated, "overdue_bills": overdue_bills}
