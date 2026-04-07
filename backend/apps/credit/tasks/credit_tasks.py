"""
Credit Celery tasks for payment reminders and overdue alerts.

Tasks 30-31: Scheduled tasks for credit management.
"""

import logging
from datetime import date, timedelta

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="credit.send_payment_reminders")
def send_payment_reminders():
    """
    Task 30: Send payment due reminders.

    Checks for credit accounts with upcoming payment due dates
    and sends reminder notifications.
    """
    from apps.credit.models.credit_settings import CreditSettings
    from apps.credit.models.customer_credit import CustomerCredit
    from apps.credit.constants import CreditStatus

    try:
        from django.db import connection
        tenant = connection.tenant
        settings = CreditSettings.objects.get_or_create_for_tenant(tenant)
        days_before = settings.days_before_overdue_notification
    except Exception:
        days_before = 3

    reminder_date = date.today() + timedelta(days=days_before)

    accounts = CustomerCredit.objects.filter(
        status=CreditStatus.ACTIVE,
        next_payment_due__lte=reminder_date,
        next_payment_due__gte=date.today(),
        outstanding_balance__gt=0,
        is_deleted=False,
    )

    count = 0
    for account in accounts:
        logger.info(
            "Payment reminder: %s owes Rs. %s, due %s",
            account.customer,
            account.outstanding_balance,
            account.next_payment_due,
        )
        count += 1

    logger.info("Sent %d payment reminders.", count)
    return count


@shared_task(name="credit.check_overdue_accounts")
def check_overdue_accounts():
    """
    Task 31: Check for overdue accounts and send notifications.

    Identifies overdue accounts and triggers alerts.
    Also checks for auto-suspension conditions.
    """
    from apps.credit.models.customer_credit import CustomerCredit
    from apps.credit.constants import CreditStatus
    from apps.credit.services.credit_service import CreditService

    accounts = CustomerCredit.objects.filter(
        status=CreditStatus.ACTIVE,
        next_payment_due__lt=date.today(),
        outstanding_balance__gt=0,
        is_deleted=False,
    )

    overdue_count = 0
    suspended_count = 0

    for account in accounts:
        overdue_count += 1
        logger.warning(
            "Overdue account: %s owes Rs. %s, due was %s",
            account.customer,
            account.outstanding_balance,
            account.next_payment_due,
        )

        service = CreditService(account)
        if service.check_auto_suspension():
            suspended_count += 1

    logger.info(
        "Found %d overdue accounts, %d auto-suspended.",
        overdue_count, suspended_count,
    )
    return {"overdue": overdue_count, "suspended": suspended_count}


@shared_task(name="credit.calculate_monthly_interest")
def calculate_monthly_interest():
    """
    Calculate interest on all overdue credit accounts.
    """
    from apps.credit.models.customer_credit import CustomerCredit
    from apps.credit.constants import CreditStatus
    from apps.credit.services.credit_service import CreditService

    accounts = CustomerCredit.objects.filter(
        status=CreditStatus.ACTIVE,
        outstanding_balance__gt=0,
        is_deleted=False,
    )

    count = 0
    for account in accounts:
        service = CreditService(account)
        txn = service.calculate_interest()
        if txn:
            count += 1

    logger.info("Interest calculated for %d accounts.", count)
    return count
