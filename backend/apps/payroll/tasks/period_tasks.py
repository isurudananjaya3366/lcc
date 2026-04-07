"""Celery tasks for automatic payroll period management."""

import calendar
import logging
from datetime import date

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    name="payroll.auto_create_payroll_periods",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def auto_create_payroll_periods(self):
    """Auto-create payroll periods for tenants with auto_create_period enabled.

    Runs daily (scheduled via Celery Beat). For each PayrollSettings
    with auto_create_period=True and auto_create_day matching today,
    creates periods for the current month + create_months_ahead.
    """
    from apps.payroll.constants import PayrollStatus
    from apps.payroll.models.payroll_period import PayrollPeriod
    from apps.payroll.models.payroll_settings import PayrollSettings

    today = date.today()
    settings_qs = PayrollSettings.objects.filter(
        auto_create_period=True,
        auto_create_day=today.day,
    )

    tenants_checked = 0
    periods_created = 0
    errors = []

    for ps in settings_qs:
        tenants_checked += 1
        try:
            months_ahead = ps.create_months_ahead or 1

            for offset in range(months_ahead + 1):
                month = today.month + offset
                year = today.year
                while month > 12:
                    month -= 12
                    year += 1

                # Skip if period already exists
                if PayrollPeriod.objects.filter(
                    period_month=month, period_year=year
                ).exists():
                    continue

                # Calculate dates
                start_date, end_date = ps.calculate_cutoff_dates(month, year)
                pay_date = ps.calculate_pay_date(month, year)

                # Calculate working days
                last_day = calendar.monthrange(year, month)[1]

                PayrollPeriod.objects.create(
                    period_month=month,
                    period_year=year,
                    start_date=start_date,
                    end_date=end_date,
                    pay_date=pay_date,
                    status=PayrollStatus.DRAFT,
                )
                periods_created += 1
                logger.info(
                    "Created payroll period %s/%s (pay date: %s)",
                    month, year, pay_date,
                )

        except Exception:
            msg = f"Error creating periods for PayrollSettings {ps.pk}"
            logger.exception(msg)
            errors.append(msg)

    result = {
        "tenants_checked": tenants_checked,
        "periods_created": periods_created,
        "errors": errors,
    }
    logger.info("auto_create_payroll_periods completed: %s", result)
    return result
