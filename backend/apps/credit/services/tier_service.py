"""
Tier Service.

Business logic for loyalty tier evaluation, upgrades, downgrades,
and progress tracking.
"""

import logging
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)


class TierService:
    """Service layer for tier management operations."""

    @staticmethod
    def qualifies_for_tier(lifetime_points, lifetime_spend, tier):
        """
        Check if a customer qualifies for a tier.

        Qualification uses OR logic: points >= threshold OR spend >= threshold.
        """
        if tier.min_points_required and lifetime_points >= tier.min_points_required:
            return True
        if tier.min_spend_required and lifetime_spend >= tier.min_spend_required:
            return True
        if tier.is_default:
            return True
        return False

    @classmethod
    def evaluate_tier(cls, loyalty_account):
        """
        Determine the highest tier a customer qualifies for.

        Evaluates from highest to lowest tier level. Returns the
        highest qualifying tier, or the default tier if none qualify.
        """
        from apps.credit.models import LoyaltyTier

        program = loyalty_account.program
        if program is None:
            return None

        tiers = LoyaltyTier.objects.filter(
            program=program,
            is_deleted=False,
        ).order_by("-level")

        lifetime_points = loyalty_account.lifetime_points_earned
        # Use points as a proxy; in full implementation this would
        # come from order totals aggregation.
        lifetime_spend = 0

        for tier in tiers:
            if cls.qualifies_for_tier(lifetime_points, lifetime_spend, tier):
                return tier

        # Fall back to default tier
        default = tiers.filter(is_default=True).first()
        return default

    @staticmethod
    def get_next_tier(current_tier):
        """Return the next higher tier, or None if at top."""
        from apps.credit.models import LoyaltyTier

        if current_tier is None:
            return None
        return (
            LoyaltyTier.objects.filter(
                program=current_tier.program,
                level__gt=current_tier.level,
                is_deleted=False,
            )
            .order_by("level")
            .first()
        )

    @classmethod
    def get_tier_progress(cls, loyalty_account):
        """
        Calculate progress toward the next tier.

        Returns dict with current/next tier info, progress percentage,
        and points/spend needed.
        """
        current = loyalty_account.current_tier
        next_tier = cls.get_next_tier(current) if current else None

        result = {
            "current_tier": {
                "name": current.name if current else None,
                "level": current.level if current else 0,
                "multiplier": float(current.points_multiplier) if current else 1.0,
            },
            "next_tier": None,
            "progress": {
                "points_progress": 0,
                "points_needed": 0,
                "percentage": 100,
            },
        }

        if next_tier:
            lifetime = loyalty_account.lifetime_points_earned
            needed = max(0, next_tier.min_points_required - lifetime)
            pct = 0
            if next_tier.min_points_required > 0:
                pct = min(100, int(lifetime / next_tier.min_points_required * 100))
            result["next_tier"] = {
                "name": next_tier.name,
                "level": next_tier.level,
                "min_points": next_tier.min_points_required,
            }
            result["progress"] = {
                "points_progress": lifetime,
                "points_needed": needed,
                "percentage": pct,
            }

        return result

    @classmethod
    @transaction.atomic
    def upgrade_tier(cls, loyalty_account, new_tier, set_expiry=True):
        """
        Upgrade a customer to a higher tier.

        Updates the loyalty account with the new tier, sets expiry
        (default 12 months), and records timestamps.

        Returns True if upgraded, False if validation fails.
        """
        current = loyalty_account.current_tier
        if current and new_tier.level <= current.level:
            return False

        now = timezone.now()
        loyalty_account.current_tier = new_tier
        loyalty_account.tier_upgraded_at = now
        loyalty_account.tier_evaluated_at = now

        if set_expiry:
            loyalty_account.tier_expiry_date = (now + timedelta(days=365)).date()

        loyalty_account.save(update_fields=[
            "current_tier", "tier_upgraded_at", "tier_evaluated_at",
            "tier_expiry_date", "updated_on",
        ])

        logger.info(
            "Customer %s upgraded to tier %s (from %s)",
            loyalty_account.customer_id,
            new_tier.name,
            current.name if current else "None",
        )
        return True

    @classmethod
    @transaction.atomic
    def downgrade_tier(cls, loyalty_account, reason="evaluation"):
        """
        Downgrade a customer to an appropriate lower tier.

        Re-evaluates the customer's qualifications and sets the
        appropriate tier. Sets a new 12-month expiry.

        Returns the new LoyaltyTier.
        """
        appropriate_tier = cls.evaluate_tier(loyalty_account)
        now = timezone.now()

        loyalty_account.current_tier = appropriate_tier
        loyalty_account.tier_evaluated_at = now
        loyalty_account.tier_expiry_date = (now + timedelta(days=365)).date()

        loyalty_account.save(update_fields=[
            "current_tier", "tier_evaluated_at", "tier_expiry_date", "updated_on",
        ])

        logger.info(
            "Customer %s downgraded to tier %s (reason: %s)",
            loyalty_account.customer_id,
            appropriate_tier.name if appropriate_tier else "None",
            reason,
        )
        return appropriate_tier
