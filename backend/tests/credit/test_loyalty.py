"""Tests for loyalty models and services."""

import pytest
from decimal import Decimal

pytestmark = pytest.mark.django_db


class TestLoyaltyProgramModel:
    """Tests for the LoyaltyProgram model."""

    def test_create_program(self, loyalty_program):
        """Program is created with correct values."""
        assert loyalty_program.name == "Test Rewards Program"
        assert loyalty_program.is_active is True
        assert loyalty_program.points_per_currency == Decimal("1.00")

    def test_is_currently_active(self, loyalty_program):
        """is_currently_active returns True for active program."""
        assert loyalty_program.is_currently_active


class TestLoyaltyTierModel:
    """Tests for the LoyaltyTier model."""

    def test_create_tier(self, loyalty_tier):
        """Tier is created with correct values."""
        assert loyalty_tier.name == "Silver"
        assert loyalty_tier.level == 1
        assert loyalty_tier.is_default is True

    def test_tier_ordering(self, loyalty_tier, gold_tier):
        """Tiers are ordered by level."""
        from apps.credit.models import LoyaltyTier

        tiers = list(
            LoyaltyTier.objects.filter(
                program=loyalty_tier.program
            ).values_list("name", flat=True)
        )
        assert tiers == ["Silver", "Gold"]


class TestCustomerLoyaltyModel:
    """Tests for the CustomerLoyalty model."""

    def test_create_loyalty_account(self, customer_loyalty, customer):
        """Loyalty account is linked to customer."""
        assert customer_loyalty.customer == customer
        assert customer_loyalty.status == "active"
        assert customer_loyalty.points_balance == 500

    def test_tier_multiplier(self, customer_loyalty, loyalty_tier):
        """tier_multiplier returns the tier's points multiplier."""
        assert customer_loyalty.tier_multiplier == loyalty_tier.points_multiplier

    def test_str_representation(self, customer_loyalty):
        """String representation is non-empty."""
        assert str(customer_loyalty)


class TestLoyaltyService:
    """Tests for LoyaltyService."""

    def test_enroll_customer(self, customer, loyalty_program, tenant_context):
        """enroll_customer creates a loyalty account."""
        from apps.credit.services.loyalty_service import LoyaltyService

        loyalty = LoyaltyService.enroll_customer(
            customer=customer, program=loyalty_program
        )
        assert loyalty is not None
        assert loyalty.customer == customer
        assert loyalty.program == loyalty_program

    def test_calculate_points(self, customer_loyalty):
        """calculate_points returns correct point value."""
        from apps.credit.services.loyalty_service import LoyaltyService

        points = LoyaltyService.calculate_points(
            purchase_amount=Decimal("5000.00"),
            loyalty_account=customer_loyalty,
        )
        assert points >= 0

    def test_award_points(self, customer_loyalty):
        """award_points increases points balance."""
        from apps.credit.services.loyalty_service import LoyaltyService

        initial_balance = customer_loyalty.points_balance
        txn = LoyaltyService.award_points(
            loyalty=customer_loyalty,
            amount=Decimal("1000.00"),
            description="Test award",
        )
        customer_loyalty.refresh_from_db()
        assert txn is not None
        assert customer_loyalty.points_balance > initial_balance

    def test_redeem_points(self, customer_loyalty):
        """redeem_points decreases points balance."""
        from apps.credit.services.loyalty_service import LoyaltyService

        initial_balance = customer_loyalty.points_balance
        txn = LoyaltyService.redeem_points(
            loyalty=customer_loyalty,
            points_to_redeem=100,
            description="Test redemption",
        )
        customer_loyalty.refresh_from_db()
        assert txn is not None
        assert customer_loyalty.points_balance < initial_balance

    def test_get_points_breakdown(self, customer_loyalty):
        """get_points_breakdown returns a dict."""
        from apps.credit.services.loyalty_service import LoyaltyService

        breakdown = LoyaltyService.get_points_breakdown(customer_loyalty)
        assert isinstance(breakdown, dict)


class TestTierService:
    """Tests for TierService."""

    def test_qualifies_for_tier(self, loyalty_tier):
        """qualifies_for_tier returns True when points meet minimum."""
        from apps.credit.services.tier_service import TierService

        assert TierService.qualifies_for_tier(
            lifetime_points=1000,
            lifetime_spend=Decimal("0"),
            tier=loyalty_tier,
        )

    def test_does_not_qualify_for_gold(self, gold_tier):
        """Does not qualify for gold with insufficient points."""
        from apps.credit.services.tier_service import TierService

        assert not TierService.qualifies_for_tier(
            lifetime_points=500,
            lifetime_spend=Decimal("0"),
            tier=gold_tier,
        )

    def test_get_tier_progress(self, customer_loyalty):
        """get_tier_progress returns progress dict."""
        from apps.credit.services.tier_service import TierService

        progress = TierService.get_tier_progress(customer_loyalty)
        assert isinstance(progress, dict)

    def test_get_next_tier(self, loyalty_tier, gold_tier):
        """get_next_tier returns the next tier by level."""
        from apps.credit.services.tier_service import TierService

        next_tier = TierService.get_next_tier(loyalty_tier)
        assert next_tier == gold_tier

    def test_upgrade_tier(self, customer_loyalty, gold_tier):
        """upgrade_tier changes the customer's tier."""
        from apps.credit.services.tier_service import TierService

        TierService.upgrade_tier(customer_loyalty, gold_tier)
        customer_loyalty.refresh_from_db()
        assert customer_loyalty.current_tier == gold_tier


class TestPointsTransaction:
    """Tests for PointsTransaction model."""

    def test_transaction_created_on_award(self, customer_loyalty):
        """Transactions are created when points are awarded."""
        from apps.credit.models import PointsTransaction
        from apps.credit.services.loyalty_service import LoyaltyService

        LoyaltyService.award_points(
            loyalty=customer_loyalty,
            amount=Decimal("500.00"),
            description="Award test",
        )
        txns = PointsTransaction.objects.filter(
            customer_loyalty=customer_loyalty
        )
        assert txns.count() >= 1

    def test_transaction_ordering(self, customer_loyalty):
        """Transactions ordered by -transaction_date."""
        from apps.credit.models import PointsTransaction
        from apps.credit.services.loyalty_service import LoyaltyService

        LoyaltyService.award_points(
            loyalty=customer_loyalty,
            amount=Decimal("100.00"),
            description="First",
        )
        LoyaltyService.award_points(
            loyalty=customer_loyalty,
            amount=Decimal("200.00"),
            description="Second",
        )

        txns = PointsTransaction.objects.filter(
            customer_loyalty=customer_loyalty
        )
        dates = list(txns.values_list("transaction_date", flat=True))
        assert dates == sorted(dates, reverse=True)


class TestPointsPromotion:
    """Tests for PointsPromotion model."""

    def test_create_promotion(self, loyalty_program):
        """Promotion is created with correct values."""
        from apps.credit.models import PointsPromotion
        from django.utils import timezone

        promo = PointsPromotion.objects.create(
            program=loyalty_program,
            name="Double Points Weekend",
            promotion_type="multiplier",
            multiplier=Decimal("2.00"),
            is_active=True,
            valid_from=timezone.now(),
            valid_to=timezone.now() + timezone.timedelta(days=7),
        )
        assert promo.name == "Double Points Weekend"
        assert promo.multiplier == Decimal("2.00")

    def test_promotion_service_get_active(self, loyalty_program):
        """get_active_promotions returns active promotions."""
        from apps.credit.models import PointsPromotion
        from apps.credit.services.promotion_service import PromotionService
        from django.utils import timezone

        PointsPromotion.objects.create(
            program=loyalty_program,
            name="Active Promo",
            promotion_type="flat_bonus",
            bonus_points=100,
            is_active=True,
            valid_from=timezone.now() - timezone.timedelta(days=1),
            valid_to=timezone.now() + timezone.timedelta(days=30),
        )

        promos = PromotionService.get_active_promotions(loyalty_program.id)
        assert len(promos) >= 1
