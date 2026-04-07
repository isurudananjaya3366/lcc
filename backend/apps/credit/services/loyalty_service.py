"""
Loyalty Service.

Business logic for loyalty program operations including enrollment,
points earning, redemption, expiry, and balance calculations.
"""

import logging
import math
from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps.credit.constants import CreditStatus, PointsTransactionType

logger = logging.getLogger(__name__)


class InsufficientPointsError(Exception):
    """Raised when a customer has insufficient points for an operation."""


class LoyaltyAccountError(Exception):
    """Raised for loyalty account validation failures."""


class LoyaltyService:
    """Service layer for all loyalty program operations."""

    # ------------------------------------------------------------------
    # Enrollment
    # ------------------------------------------------------------------

    @staticmethod
    def enroll_customer(customer, program=None):
        """
        Enroll a customer in a loyalty program.

        Creates a new CustomerLoyalty account. If no program is specified,
        looks for the tenant's active program.

        Returns:
            CustomerLoyalty instance.
        Raises:
            LoyaltyAccountError if customer already enrolled.
        """
        from apps.credit.models import CustomerLoyalty, LoyaltyProgram

        if CustomerLoyalty.objects.filter(customer=customer).exists():
            raise LoyaltyAccountError("Customer is already enrolled in loyalty program.")

        if program is None:
            program = LoyaltyProgram.objects.filter(
                is_active=True,
            ).first()

        loyalty = CustomerLoyalty.objects.create(
            customer=customer,
            program=program,
        )
        logger.info("Customer %s enrolled in loyalty program %s", customer.id, program)
        return loyalty

    @staticmethod
    def get_or_create_loyalty(customer):
        """
        Get existing loyalty account or create one.

        Returns:
            Tuple of (CustomerLoyalty, created: bool).
        """
        from apps.credit.models import CustomerLoyalty, LoyaltyProgram

        loyalty = CustomerLoyalty.objects.filter(customer=customer).first()
        if loyalty:
            return loyalty, False

        program = LoyaltyProgram.objects.filter(is_active=True).first()
        loyalty = CustomerLoyalty.objects.create(
            customer=customer,
            program=program,
        )
        return loyalty, True

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_account_active(loyalty):
        """Raise if loyalty account is not active."""
        if loyalty.status != CreditStatus.ACTIVE:
            raise LoyaltyAccountError(
                f"Loyalty account is {loyalty.status}, not active."
            )

    @staticmethod
    def _validate_program_active(program):
        """Raise if loyalty program is not currently active."""
        if program is None:
            raise LoyaltyAccountError("No loyalty program assigned.")
        if not program.is_currently_active:
            raise LoyaltyAccountError("Loyalty program is not currently active.")

    @staticmethod
    def _validate_sufficient_points(loyalty, required):
        """Raise if customer has insufficient points."""
        if loyalty.points_balance < required:
            raise InsufficientPointsError(
                f"Insufficient points: {loyalty.points_balance} available, "
                f"{required} required."
            )

    @staticmethod
    def _validate_minimum_purchase(amount, program):
        """Raise if purchase amount is below minimum for points earning."""
        if amount < program.min_purchase_for_points:
            raise LoyaltyAccountError(
                f"Purchase amount Rs. {amount} is below minimum "
                f"Rs. {program.min_purchase_for_points} for earning points."
            )

    # ------------------------------------------------------------------
    # Points calculation
    # ------------------------------------------------------------------

    @staticmethod
    def calculate_points(purchase_amount, loyalty_account):
        """
        Calculate points to award for a purchase amount.

        Formula: floor(amount / 100) × points_per_currency × tier_multiplier

        Returns:
            Integer number of points to award.
        """
        program = loyalty_account.program
        if program is None:
            return 0

        base_units = int(purchase_amount / Decimal("100"))
        base_points = float(base_units) * float(program.points_per_currency)
        tier_multiplier = loyalty_account.tier_multiplier
        total_points = math.floor(base_points * float(tier_multiplier))
        return max(0, total_points)

    # ------------------------------------------------------------------
    # Points earning (Task 46)
    # ------------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def award_points(
        cls, loyalty, amount, reference_id=None, reference_type=None, description=None
    ):
        """
        Award points for a purchase.

        Validates account/program, calculates points, creates a transaction,
        and updates the loyalty account balance.

        Returns:
            PointsTransaction instance.
        """
        from apps.credit.models import PointsTransaction

        cls._validate_account_active(loyalty)
        program = loyalty.program
        cls._validate_program_active(program)
        cls._validate_minimum_purchase(amount, program)

        points = cls.calculate_points(amount, loyalty)
        if points <= 0:
            raise LoyaltyAccountError("No points to award for this amount.")

        # Calculate expiry date
        expiry_date = None
        if program.points_expiry_months:
            expiry_date = (
                timezone.now().date() + timedelta(days=program.points_expiry_months * 30)
            )

        loyalty.points_balance += points
        loyalty.lifetime_points_earned += points
        loyalty.save(update_fields=[
            "points_balance", "lifetime_points_earned", "updated_on",
        ])

        txn = PointsTransaction.objects.create(
            customer_loyalty=loyalty,
            transaction_type=PointsTransactionType.EARN,
            points=points,
            balance_after=loyalty.points_balance,
            reference_id=reference_id,
            reference_type=reference_type or "purchase",
            description=description or f"Points earned on purchase of Rs. {amount}",
            expiry_date=expiry_date,
        )

        logger.info(
            "Awarded %d points to customer %s (balance: %d)",
            points, loyalty.customer_id, loyalty.points_balance,
        )
        return txn

    # ------------------------------------------------------------------
    # Points redemption (Task 47)
    # ------------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def redeem_points(
        cls, loyalty, points_to_redeem, reference_id=None, reference_type=None,
        description=None,
    ):
        """
        Redeem points for a discount.

        Validates account/program, checks balance and minimums,
        creates a negative-points transaction, and updates the balance.

        Returns:
            Tuple of (PointsTransaction, discount_amount: Decimal).
        """
        from apps.credit.models import PointsTransaction

        cls._validate_account_active(loyalty)
        program = loyalty.program
        cls._validate_program_active(program)

        if points_to_redeem < program.min_points_for_redemption:
            raise LoyaltyAccountError(
                f"Minimum {program.min_points_for_redemption} points required "
                f"for redemption."
            )

        cls._validate_sufficient_points(loyalty, points_to_redeem)

        discount_amount = Decimal(str(points_to_redeem)) * program.redemption_value_per_point

        loyalty.points_balance -= points_to_redeem
        loyalty.total_points_redeemed += points_to_redeem
        loyalty.save(update_fields=[
            "points_balance", "total_points_redeemed", "updated_on",
        ])

        txn = PointsTransaction.objects.create(
            customer_loyalty=loyalty,
            transaction_type=PointsTransactionType.REDEEM,
            points=-points_to_redeem,
            balance_after=loyalty.points_balance,
            reference_id=reference_id,
            reference_type=reference_type or "redemption",
            description=description or f"Redeemed {points_to_redeem} points for Rs. {discount_amount} discount",
        )

        logger.info(
            "Redeemed %d points for customer %s (discount: Rs. %s, balance: %d)",
            points_to_redeem, loyalty.customer_id, discount_amount, loyalty.points_balance,
        )
        return txn, discount_amount

    # ------------------------------------------------------------------
    # Points expiry (Task 48)
    # ------------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def expire_points(cls, loyalty_account, cutoff_date=None):
        """
        Expire EARN transactions past their expiry date (FIFO).

        Finds all un-expired EARN transactions with expiry_date <= cutoff,
        creates EXPIRE transactions, and updates the balance.

        Returns:
            List of EXPIRE PointsTransaction instances created.
        """
        from apps.credit.models import PointsTransaction

        if cutoff_date is None:
            cutoff_date = timezone.now().date()

        expired_earns = PointsTransaction.objects.filter(
            customer_loyalty=loyalty_account,
            transaction_type=PointsTransactionType.EARN,
            is_expired=False,
            expiry_date__lte=cutoff_date,
        ).order_by("expiry_date", "created_on")  # FIFO

        expire_transactions = []
        total_expired = 0

        for earn_txn in expired_earns:
            points_to_expire = earn_txn.points
            if points_to_expire <= 0:
                continue

            # Prevent negative balance
            available = loyalty_account.points_balance - total_expired
            if available <= 0:
                break
            points_to_expire = min(points_to_expire, available)
            total_expired += points_to_expire

            earn_txn.is_expired = True
            earn_txn.save(update_fields=["is_expired", "updated_on"])

            expire_txn = PointsTransaction(
                customer_loyalty=loyalty_account,
                transaction_type=PointsTransactionType.EXPIRE,
                points=-points_to_expire,
                balance_after=loyalty_account.points_balance - total_expired,
                description=f"Points expired (earned on {earn_txn.created_on.date()})",
                reference_id=earn_txn.id,
                reference_type="expiry",
            )
            expire_transactions.append(expire_txn)

        if expire_transactions:
            PointsTransaction.objects.bulk_create(expire_transactions)
            loyalty_account.points_balance = max(
                0, loyalty_account.points_balance - total_expired
            )
            loyalty_account.save(update_fields=["points_balance", "updated_on"])
            logger.info(
                "Expired %d points for customer %s (new balance: %d)",
                total_expired, loyalty_account.customer_id, loyalty_account.points_balance,
            )

        return expire_transactions

    # ------------------------------------------------------------------
    # Points balance calculator (Task 50)
    # ------------------------------------------------------------------

    @classmethod
    def get_points_breakdown(cls, loyalty_account):
        """
        Comprehensive points balance breakdown.

        Returns dict with: current balance, expiring-soon windows,
        lifetime statistics, redemption value, tier info, and
        upcoming expiries.
        """
        from apps.credit.models import PointsTransaction

        now = timezone.now()
        today = now.date()
        program = loyalty_account.program

        # Expiring soon windows
        expiring_soon = {}
        for days_window in [7, 30, 60, 90]:
            window_date = today + timedelta(days=days_window)
            expiring = PointsTransaction.objects.filter(
                customer_loyalty=loyalty_account,
                transaction_type=PointsTransactionType.EARN,
                is_expired=False,
                expiry_date__lte=window_date,
                expiry_date__gt=today,
            ).aggregate(total=Sum("points"))["total"] or 0
            expiring_soon[f"next_{days_window}_days"] = expiring

        # Lifetime stats
        lifetime_expired = loyalty_account.lifetime_points_expired

        # Redemption value
        redemption_value = Decimal("0")
        if program:
            redemption_value = (
                Decimal(str(loyalty_account.points_balance))
                * program.redemption_value_per_point
            )

        # Upcoming expiries (next 10)
        upcoming_expiries = list(
            PointsTransaction.objects.filter(
                customer_loyalty=loyalty_account,
                transaction_type=PointsTransactionType.EARN,
                is_expired=False,
                expiry_date__gt=today,
            )
            .order_by("expiry_date")
            .values("expiry_date", "points")[:10]
        )

        # Tier info
        tier_info = None
        if loyalty_account.current_tier:
            tier = loyalty_account.current_tier
            tier_info = {
                "name": tier.name,
                "multiplier": float(tier.points_multiplier),
                "expiry_date": str(loyalty_account.tier_expiry_date) if loyalty_account.tier_expiry_date else None,
            }

        return {
            "available_points": loyalty_account.points_balance,
            "expiring_soon": expiring_soon,
            "lifetime": {
                "earned": loyalty_account.lifetime_points_earned,
                "redeemed": loyalty_account.total_points_redeemed,
                "expired": lifetime_expired,
                "net": loyalty_account.points_balance,
            },
            "redemption_value": float(redemption_value),
            "tier": tier_info,
            "upcoming_expiries": upcoming_expiries,
        }

    # ------------------------------------------------------------------
    # Birthday & Anniversary Rewards (Tasks 64-65)
    # ------------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def apply_birthday_reward(cls, loyalty_account, reward):
        """
        Award birthday bonus points to a loyalty account.

        Args:
            loyalty_account: CustomerLoyalty instance.
            reward: LoyaltyReward instance (BIRTHDAY type).

        Returns:
            PointsTransaction instance or None.
        """
        from apps.credit.models import PointsTransaction
        from datetime import date

        today = date.today()

        # Already awarded this year?
        if (
            loyalty_account.last_birthday_reward_date
            and loyalty_account.last_birthday_reward_date.year == today.year
        ):
            return None

        points = reward.get_points()
        if points <= 0:
            return None

        loyalty_account.points_balance += points
        loyalty_account.lifetime_points_earned += points
        loyalty_account.last_birthday_reward_date = today
        loyalty_account.save(update_fields=[
            "points_balance", "lifetime_points_earned",
            "last_birthday_reward_date", "updated_on",
        ])

        txn = PointsTransaction.objects.create(
            customer_loyalty=loyalty_account,
            transaction_type=PointsTransactionType.BONUS,
            points=points,
            balance_after=loyalty_account.points_balance,
            reference_id=reward.id,
            reference_type="birthday_reward",
            description=f"Birthday bonus: {points} points",
        )

        logger.info(
            "Birthday reward: %d points awarded to customer %s",
            points, loyalty_account.customer_id,
        )
        return txn

    @classmethod
    @transaction.atomic
    def apply_anniversary_reward(cls, loyalty_account, reward):
        """
        Award anniversary bonus points based on milestone configuration.

        Args:
            loyalty_account: CustomerLoyalty instance.
            reward: LoyaltyReward instance (ANNIVERSARY type).

        Returns:
            PointsTransaction instance or None.
        """
        from apps.credit.models import PointsTransaction
        from datetime import date

        today = date.today()

        # Already awarded this year?
        if loyalty_account.last_anniversary_reward_year == today.year:
            return None

        # Calculate completed years (accounting for month/day)
        years = today.year - loyalty_account.enrolled_date.year
        if (today.month, today.day) < (
            loyalty_account.enrolled_date.month,
            loyalty_account.enrolled_date.day,
        ):
            years -= 1
        if years <= 0:
            return None

        config = reward.configuration or {}
        milestones = config.get("milestones", {})
        default_points = config.get("default_points_per_year", 500)
        milestone = milestones.get(str(years), {})
        points = milestone.get("points", default_points)

        if points <= 0:
            return None

        loyalty_account.points_balance += points
        loyalty_account.lifetime_points_earned += points
        loyalty_account.last_anniversary_reward_year = today.year
        loyalty_account.anniversary_rewards_count += 1
        loyalty_account.save(update_fields=[
            "points_balance", "lifetime_points_earned",
            "last_anniversary_reward_year", "anniversary_rewards_count",
            "updated_on",
        ])

        txn = PointsTransaction.objects.create(
            customer_loyalty=loyalty_account,
            transaction_type=PointsTransactionType.BONUS,
            points=points,
            balance_after=loyalty_account.points_balance,
            reference_id=reward.id,
            reference_type="anniversary_reward",
            description=f"Anniversary bonus: {years} year(s) - {points} points",
        )

        logger.info(
            "Anniversary reward: %d points for %d year(s), customer %s",
            points, years, loyalty_account.customer_id,
        )
        return txn
