"""
Promotion service layer.

Calculates bonus points from active PointsPromotion campaigns,
including multiplier, flat-bonus, category-bonus, and spend-threshold logic.
"""

from decimal import Decimal

from django.utils import timezone

from apps.credit.constants import PromotionType
from apps.credit.models.points_promotion import PointsPromotion


class PromotionService:
    """Business logic for points promotions."""

    @staticmethod
    def get_active_promotions(program_id):
        """
        Return all currently-active promotions for a loyalty program.
        """
        now = timezone.now()
        return PointsPromotion.objects.filter(
            program_id=program_id,
            is_active=True,
            valid_from__lte=now,
            valid_to__gte=now,
        )

    @staticmethod
    def calculate_promotion_bonus(
        program_id,
        base_points,
        purchase_amount,
        category_ids=None,
        product_ids=None,
        customer_tier=None,
    ):
        """
        Calculate total bonus points from active promotions.

        Applies the best multiplier (highest) and sums all flat /
        category / threshold bonuses.

        Args:
            program_id: UUID of the LoyaltyProgram.
            base_points: int – base points earned before promotions.
            purchase_amount: Decimal – total purchase amount.
            category_ids: optional set/list of product category UUIDs.
            product_ids: optional set/list of product UUIDs.
            customer_tier: optional LoyaltyTier instance for tier-gating.

        Returns:
            dict with base_points, multiplier, bonus_points, final_points,
            applied_promotions.
        """
        now = timezone.now()
        promotions = PointsPromotion.objects.filter(
            program_id=program_id,
            is_active=True,
            valid_from__lte=now,
            valid_to__gte=now,
        ).prefetch_related("applicable_categories", "applicable_products")

        best_multiplier = Decimal("1.0")
        total_bonus = 0
        applied = []

        for promo in promotions:
            # Tier gate check
            if promo.tier_required_id and (
                not customer_tier or customer_tier.pk != promo.tier_required_id
            ):
                continue

            if promo.promotion_type == PromotionType.MULTIPLIER:
                if purchase_amount >= promo.min_purchase_amount:
                    if promo.multiplier > best_multiplier:
                        best_multiplier = promo.multiplier
                        applied.append(promo.name)

            elif promo.promotion_type == PromotionType.FLAT_BONUS:
                if purchase_amount >= promo.min_purchase_amount:
                    total_bonus += promo.bonus_points
                    applied.append(promo.name)

            elif promo.promotion_type == PromotionType.CATEGORY_BONUS:
                if category_ids:
                    promo_cats = set(
                        promo.applicable_categories.values_list("id", flat=True)
                    )
                    if set(category_ids) & promo_cats:
                        total_bonus += promo.bonus_points
                        applied.append(promo.name)

            elif promo.promotion_type == PromotionType.SPEND_THRESHOLD:
                if purchase_amount >= promo.min_purchase_amount:
                    total_bonus += promo.bonus_points
                    applied.append(promo.name)

        points_after_multiplier = int(base_points * best_multiplier)
        final_points = points_after_multiplier + total_bonus

        return {
            "base_points": base_points,
            "multiplier": best_multiplier,
            "bonus_points": total_bonus,
            "final_points": final_points,
            "applied_promotions": applied,
        }

    @staticmethod
    def get_category_bonuses(program_id, category_ids):
        """
        Return category-specific bonus promotions matching given categories.
        """
        now = timezone.now()
        bonuses = PointsPromotion.objects.filter(
            program_id=program_id,
            promotion_type=PromotionType.CATEGORY_BONUS,
            is_active=True,
            valid_from__lte=now,
            valid_to__gte=now,
            applicable_categories__id__in=category_ids,
        ).distinct()

        total = sum(p.bonus_points for p in bonuses)
        return {
            "applicable_promotions": [p.name for p in bonuses],
            "total_bonus_points": total,
        }
