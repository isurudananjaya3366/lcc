"""
Loyalty, Store Credit, and Promotion serializers.

Provides serializers for LoyaltyTier, PointsTransaction,
CustomerLoyalty, StoreCredit, StoreCreditTransaction, and PointsPromotion.
"""

from rest_framework import serializers

from apps.credit.models import (
    CustomerLoyalty,
    LoyaltyTier,
    PointsPromotion,
    PointsTransaction,
    StoreCredit,
    StoreCreditTransaction,
)


class LoyaltyTierSerializer(serializers.ModelSerializer):
    """Serializer for loyalty tiers with benefit summary."""

    benefit_summary = serializers.SerializerMethodField()

    class Meta:
        model = LoyaltyTier
        fields = [
            "id",
            "name",
            "level",
            "description",
            "min_points_required",
            "min_spend_required",
            "points_multiplier",
            "discount_percentage",
            "free_shipping",
            "priority_support",
            "early_access",
            "badge_image",
            "color",
            "icon",
            "is_default",
            "benefit_summary",
        ]

    def get_benefit_summary(self, obj):
        benefits = []
        if obj.points_multiplier and obj.points_multiplier > 1:
            benefits.append(f"{obj.points_multiplier}x points")
        if obj.discount_percentage and obj.discount_percentage > 0:
            benefits.append(f"{obj.discount_percentage}% discount")
        if obj.free_shipping:
            benefits.append("Free shipping")
        if obj.priority_support:
            benefits.append("Priority support")
        if obj.early_access:
            benefits.append("Early access")
        return benefits


class PointsTransactionSerializer(serializers.ModelSerializer):
    """Serializer for points transaction history."""

    type_display = serializers.CharField(
        source="get_transaction_type_display", read_only=True
    )

    class Meta:
        model = PointsTransaction
        fields = [
            "id",
            "transaction_type",
            "type_display",
            "points",
            "balance_after",
            "description",
            "reference_type",
            "reference_id",
            "expiry_date",
            "is_expired",
            "transaction_date",
        ]
        read_only_fields = ["id", "balance_after", "transaction_date"]


class CustomerLoyaltySerializer(serializers.ModelSerializer):
    """Full serializer for customer loyalty accounts."""

    customer_name = serializers.SerializerMethodField()
    program_name = serializers.CharField(source="program.name", read_only=True)
    tier_details = LoyaltyTierSerializer(source="current_tier", read_only=True)
    recent_transactions = serializers.SerializerMethodField()

    class Meta:
        model = CustomerLoyalty
        fields = [
            "id",
            "customer",
            "customer_name",
            "program",
            "program_name",
            "enrolled_date",
            "status",
            "points_balance",
            "lifetime_points_earned",
            "total_points_redeemed",
            "current_tier",
            "tier_details",
            "tier_evaluated_at",
            "tier_expiry_date",
            "tier_upgraded_at",
            "last_activity_date",
            "recent_transactions",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "points_balance",
            "lifetime_points_earned",
            "total_points_redeemed",
            "tier_evaluated_at",
            "tier_upgraded_at",
            "enrolled_date",
            "created_on",
            "updated_on",
        ]

    def get_customer_name(self, obj):
        customer = obj.customer
        first = getattr(customer, "first_name", "")
        last = getattr(customer, "last_name", "")
        return f"{first} {last}".strip() or str(customer)

    def get_recent_transactions(self, obj):
        txns = obj.points_transactions.order_by("-transaction_date")[:5]
        return PointsTransactionSerializer(txns, many=True).data


class StoreCreditSerializer(serializers.ModelSerializer):
    """Serializer for store credit accounts."""

    customer_name = serializers.SerializerMethodField()
    source_display = serializers.CharField(
        source="get_created_from_display", read_only=True
    )
    available_balance = serializers.SerializerMethodField()

    class Meta:
        model = StoreCredit
        fields = [
            "id",
            "customer",
            "customer_name",
            "balance",
            "available_balance",
            "total_issued",
            "total_used",
            "currency",
            "created_from",
            "source_display",
            "source_reference",
            "expiry_date",
            "is_expired",
            "grace_period_days",
            "notes",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "balance",
            "total_issued",
            "total_used",
            "is_expired",
            "created_on",
            "updated_on",
        ]

    def get_customer_name(self, obj):
        customer = obj.customer
        first = getattr(customer, "first_name", "")
        last = getattr(customer, "last_name", "")
        return f"{first} {last}".strip() or str(customer)

    def get_available_balance(self, obj):
        return str(obj.get_available_balance())


class StoreCreditTransactionSerializer(serializers.ModelSerializer):
    """Serializer for store credit transactions."""

    transaction_type_display = serializers.CharField(
        source="get_transaction_type_display", read_only=True
    )

    class Meta:
        model = StoreCreditTransaction
        fields = [
            "id",
            "transaction_type",
            "transaction_type_display",
            "amount",
            "balance_before",
            "balance_after",
            "reference",
            "notes",
            "created_on",
        ]
        read_only_fields = ["id", "created_on"]


class PointsPromotionSerializer(serializers.ModelSerializer):
    """Serializer for points promotions."""

    type_display = serializers.CharField(
        source="get_promotion_type_display", read_only=True
    )
    is_currently_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = PointsPromotion
        fields = [
            "id",
            "program",
            "name",
            "description",
            "promotion_type",
            "type_display",
            "multiplier",
            "bonus_points",
            "min_purchase_amount",
            "valid_from",
            "valid_to",
            "is_active",
            "is_currently_active",
            "configuration",
            "created_on",
            "updated_on",
        ]
