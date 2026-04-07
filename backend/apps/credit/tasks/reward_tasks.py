"""
Birthday and anniversary reward Celery tasks.

Daily tasks to process birthday and anniversary rewards
for loyalty program members.
"""

import logging
from datetime import date

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="credit.process_birthday_rewards")
def process_birthday_rewards():
    """
    Daily task to award birthday rewards.

    Finds customers with today's birthday who have loyalty accounts,
    and awards configured birthday bonus points.

    Scheduled via Celery Beat at 6:00 AM daily.
    """
    from apps.credit.services.loyalty_service import LoyaltyService

    today = date.today()
    stats = {"total": 0, "success": 0, "skipped": 0, "errors": []}

    # Import here to avoid circular imports
    from apps.credit.models import CustomerLoyalty, LoyaltyReward
    from apps.credit.constants import CreditStatus, RewardType

    # Find birthday reward configuration
    reward = LoyaltyReward.objects.filter(
        reward_type=RewardType.BIRTHDAY,
        is_active=True,
        is_deleted=False,
    ).first()

    if not reward:
        logger.info("No active birthday reward configured.")
        return stats

    # Find loyalty accounts whose customer has a birthday today
    accounts = CustomerLoyalty.objects.filter(
        status=CreditStatus.ACTIVE,
        is_deleted=False,
        customer__date_of_birth__month=today.month,
        customer__date_of_birth__day=today.day,
    ).select_related("customer", "program")

    for account in accounts:
        stats["total"] += 1
        try:
            txn = LoyaltyService.apply_birthday_reward(account, reward)
            if txn is None:
                stats["skipped"] += 1
            else:
                stats["success"] += 1
        except Exception:
            logger.exception(
                "Error processing birthday reward for account %s", account.id
            )
            stats["errors"].append(str(account.id))

    logger.info(
        "Birthday rewards: %d total, %d success, %d skipped, %d errors",
        stats["total"], stats["success"], stats["skipped"], len(stats["errors"]),
    )
    return stats


@shared_task(name="credit.process_anniversary_rewards")
def process_anniversary_rewards():
    """
    Daily task to award anniversary rewards.

    Finds customers whose loyalty enrollment anniversary is today
    and awards milestone-based bonus points.

    Scheduled via Celery Beat at 6:30 AM daily.
    """
    from apps.credit.models import CustomerLoyalty, LoyaltyReward
    from apps.credit.constants import CreditStatus, RewardType
    from apps.credit.services.loyalty_service import LoyaltyService

    today = date.today()
    stats = {"total": 0, "success": 0, "skipped": 0, "errors": []}

    reward = LoyaltyReward.objects.filter(
        reward_type=RewardType.ANNIVERSARY,
        is_active=True,
        is_deleted=False,
    ).first()

    if not reward:
        logger.info("No active anniversary reward configured.")
        return stats

    # Find accounts enrolled on this month/day
    accounts = CustomerLoyalty.objects.filter(
        status=CreditStatus.ACTIVE,
        is_deleted=False,
        enrolled_date__month=today.month,
        enrolled_date__day=today.day,
    ).select_related("customer", "program")

    for account in accounts:
        stats["total"] += 1
        try:
            txn = LoyaltyService.apply_anniversary_reward(account, reward)
            if txn is None:
                stats["skipped"] += 1
            else:
                stats["success"] += 1
        except Exception:
            logger.exception(
                "Error processing anniversary reward for account %s", account.id
            )
            stats["errors"].append(str(account.id))

    logger.info(
        "Anniversary rewards: %d total, %d success, %d skipped, %d errors",
        stats["total"], stats["success"], stats["skipped"], len(stats["errors"]),
    )
    return stats
