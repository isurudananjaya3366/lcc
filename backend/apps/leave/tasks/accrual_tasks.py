"""Celery tasks for leave accrual and expiry processing."""

import logging

from django.utils import timezone

logger = logging.getLogger(__name__)

try:
    from celery import shared_task
except ImportError:  # pragma: no cover
    # Fallback when Celery is not installed
    def shared_task(func=None, **kwargs):
        if func:
            return func
        return lambda f: f


@shared_task
def year_end_accrual(from_year=None, to_year=None):
    """Process year-end carry-forward and new allocations.

    Scheduled for December 31 at 23:59.
    """
    from apps.leave.services.accrual_service import LeaveAccrualService

    now = timezone.now()
    if from_year is None:
        from_year = now.year
    if to_year is None:
        to_year = from_year + 1

    logger.info("Starting year-end accrual rollover: %d → %d", from_year, to_year)
    result = LeaveAccrualService.execute_year_end_rollover(from_year, to_year)
    logger.info("Year-end accrual complete: %s", result)
    return result


@shared_task
def daily_leave_expiry_check():
    """Check and expire carried-forward leave past expiry date.

    Scheduled daily at 00:30.
    """
    from apps.leave.services.accrual_service import LeaveAccrualService

    logger.info("Running daily leave expiry check")
    result = LeaveAccrualService.check_and_expire_leaves()
    logger.info("Expiry check complete: expired %d balances", result.get("expired_count", 0))
    return result
