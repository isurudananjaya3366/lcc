"""
Tier evaluation Celery tasks.

Daily task to evaluate and update customer loyalty tiers
based on qualification thresholds.
"""

import logging
from datetime import timedelta

from celery import shared_task

from apps.credit.constants import CreditStatus

logger = logging.getLogger(__name__)


@shared_task(name="credit.evaluate_customer_tiers")
def evaluate_customer_tiers():
    """
    Daily task to evaluate all active loyalty account tiers.

    Checks tier qualifications, performs upgrades/downgrades,
    and sends tier expiry warnings.

    Scheduled via Celery Beat at 3:00 AM daily.
    """
    from django.utils import timezone

    from apps.credit.models import CustomerLoyalty
    from apps.credit.services.tier_service import TierService

    now = timezone.now()
    today = now.date()

    accounts = CustomerLoyalty.objects.filter(
        status=CreditStatus.ACTIVE,
        is_deleted=False,
    ).select_related("current_tier", "program")

    stats = {
        "accounts_processed": 0,
        "upgrades": 0,
        "downgrades": 0,
        "unchanged": 0,
        "warnings_sent": 0,
        "errors": [],
    }

    for account in accounts.iterator():
        stats["accounts_processed"] += 1
        try:
            current_tier = account.current_tier
            appropriate_tier = TierService.evaluate_tier(account)

            if appropriate_tier is None:
                stats["unchanged"] += 1
                continue

            current_level = current_tier.level if current_tier else 0
            new_level = appropriate_tier.level

            if new_level > current_level:
                TierService.upgrade_tier(account, appropriate_tier)
                stats["upgrades"] += 1
            elif new_level < current_level:
                # Check tier expiry before downgrading
                if account.tier_expiry_date and account.tier_expiry_date <= today:
                    TierService.downgrade_tier(account, reason="tier_expired")
                    stats["downgrades"] += 1
                else:
                    # Send warning if expiry approaching
                    if account.tier_expiry_date:
                        days_left = (account.tier_expiry_date - today).days
                        if days_left in (30, 7, 1):
                            stats["warnings_sent"] += 1
                    stats["unchanged"] += 1
            else:
                stats["unchanged"] += 1

        except Exception:
            logger.exception(
                "Error evaluating tier for loyalty account %s", account.id
            )
            stats["errors"].append(str(account.id))

    logger.info(
        "Tier evaluation completed: %d processed, %d upgrades, %d downgrades, %d warnings",
        stats["accounts_processed"],
        stats["upgrades"],
        stats["downgrades"],
        stats["warnings_sent"],
    )
    return stats
