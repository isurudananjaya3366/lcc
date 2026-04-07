"""
Credit & Loyalty constants module.

Defines choices, status values, and other constants used across the
credit & loyalty application models.
"""

from django.db import models


class CreditStatus(models.TextChoices):
    """Status choices for customer credit accounts."""

    ACTIVE = "active", "Active"
    SUSPENDED = "suspended", "Suspended"
    CLOSED = "closed", "Closed"
    PENDING_APPROVAL = "pending_approval", "Pending Approval"

    @classmethod
    def get_active_statuses(cls):
        """Return statuses where credit can be used."""
        return [cls.ACTIVE]

    @classmethod
    def requires_approval(cls, status):
        """Check if status requires approval."""
        return status == cls.PENDING_APPROVAL


class ApprovalStatus(models.TextChoices):
    """Status choices for credit approval workflow."""

    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    CANCELLED = "cancelled", "Cancelled"


class RequestType(models.TextChoices):
    """Types of credit requests."""

    NEW_ACCOUNT = "new_account", "New Account"
    LIMIT_INCREASE = "limit_increase", "Limit Increase"
    LIMIT_DECREASE = "limit_decrease", "Limit Decrease"
    REACTIVATION = "reactivation", "Reactivation"


class RequestPriority(models.TextChoices):
    """Priority levels for credit requests."""

    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"
    URGENT = "urgent", "Urgent"


class TransactionType(models.TextChoices):
    """Types of credit transactions."""

    CREDIT_PURCHASE = "credit_purchase", "Credit Purchase"
    PAYMENT = "payment", "Payment"
    ADJUSTMENT = "adjustment", "Adjustment"
    INTEREST = "interest", "Interest"
    WRITE_OFF = "write_off", "Write Off"


class PointsTransactionType(models.TextChoices):
    """Types of points transactions."""

    EARN = "earn", "Earn"
    REDEEM = "redeem", "Redeem"
    EXPIRE = "expire", "Expire"
    BONUS = "bonus", "Bonus"
    ADJUSTMENT = "adjustment", "Adjustment"


class RewardType(models.TextChoices):
    """Types of loyalty rewards."""

    BIRTHDAY = "birthday", "Birthday"
    ANNIVERSARY = "anniversary", "Anniversary"
    BONUS_POINTS = "bonus_points", "Bonus Points"
    FREE_PRODUCT = "free_product", "Free Product"
    DISCOUNT_VOUCHER = "discount_voucher", "Discount Voucher"
    FREE_SHIPPING = "free_shipping", "Free Shipping"
    TIER_UPGRADE = "tier_upgrade", "Tier Upgrade"
    REFERRAL = "referral", "Referral"


class StoreCreditSource(models.TextChoices):
    """Source of store credit."""

    REFUND = "refund", "Refund"
    GIFT = "gift", "Gift Credit"
    PROMOTIONAL = "promotional", "Promotional Credit"
    ADJUSTMENT = "adjustment", "Manual Adjustment"
    COMPENSATION = "compensation", "Compensation"
    LOYALTY_CONVERSION = "loyalty_conversion", "Loyalty Points Conversion"


class StoreCreditTransactionType(models.TextChoices):
    """Types of store credit transactions."""

    ISSUE = "issue", "Issue Credit"
    REDEEM = "redeem", "Redeem Credit"
    EXPIRE = "expire", "Expire Credit"
    ADJUST = "adjust", "Manual Adjustment"
    REFUND = "refund", "Refund to Original Payment"


class PromotionType(models.TextChoices):
    """Types of points promotions."""

    MULTIPLIER = "multiplier", "Point Multiplier"
    FLAT_BONUS = "flat_bonus", "Flat Bonus Points"
    CATEGORY_BONUS = "category_bonus", "Category Bonus"
    SPEND_THRESHOLD = "spend_threshold", "Spend Threshold"
    FIRST_PURCHASE = "first_purchase", "First Purchase"
    BIRTHDAY_MONTH = "birthday_month", "Birthday Month"
