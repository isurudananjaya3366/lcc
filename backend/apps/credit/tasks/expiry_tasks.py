"""
Loyalty points expiry Celery tasks.

Provides the daily task that expires old loyalty points
across all active accounts.
"""

import logging

from celery import shared_task

from apps.credit.constants import CreditStatus

logger = logging.getLogger(__name__)


@shared_task(name="credit.expire_loyalty_points")
def expire_loyalty_points():
    """
    Daily task to expire loyalty points for all active accounts.

    Iterates through active loyalty accounts with a positive balance,
    calls LoyaltyService.expire_points for each, and returns statistics.

    Scheduled via Celery Beat at 2:00 AM daily.
    """
    from apps.credit.models import CustomerLoyalty
    from apps.credit.services.loyalty_service import LoyaltyService

    accounts = CustomerLoyalty.objects.filter(
        status=CreditStatus.ACTIVE,
        points_balance__gt=0,
    )

    stats = {
        "accounts_processed": 0,
        "accounts_with_expiry": 0,
        "total_points_expired": 0,
        "errors": [],
    }

    for account in accounts.iterator():
        stats["accounts_processed"] += 1
        try:
            expire_txns = LoyaltyService.expire_points(account)
            if expire_txns:
                expired_points = sum(abs(t.points) for t in expire_txns)
                stats["accounts_with_expiry"] += 1
                stats["total_points_expired"] += expired_points
        except Exception:
            logger.exception(
                "Error expiring points for loyalty account %s", account.id
            )
            stats["errors"].append(str(account.id))

    logger.info(
        "Points expiry completed: %d accounts processed, %d with expiry, %d points expired",
        stats["accounts_processed"],
        stats["accounts_with_expiry"],
        stats["total_points_expired"],
    )
    return stats
