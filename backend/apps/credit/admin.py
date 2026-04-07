"""Credit & Loyalty admin configuration."""

from django.contrib import admin

from apps.credit.models import (
    CreditApprovalWorkflow,
    CreditSettings,
    CreditTransaction,
    CustomerCredit,
    CustomerLoyalty,
    LoyaltyProgram,
    LoyaltyReward,
    LoyaltyTier,
    PointsPromotion,
    PointsTransaction,
    StoreCredit,
    StoreCreditTransaction,
)


@admin.register(CustomerCredit)
class CustomerCreditAdmin(admin.ModelAdmin):
    """Admin for CustomerCredit."""

    list_display = [
        "customer",
        "status",
        "credit_limit",
        "available_credit",
        "outstanding_balance",
        "risk_score",
    ]
    list_filter = ["status", "risk_score"]
    search_fields = ["customer__first_name", "customer__last_name", "customer__email"]
    readonly_fields = ["account_opened_date", "created_on", "updated_on"]


@admin.register(CreditSettings)
class CreditSettingsAdmin(admin.ModelAdmin):
    """Admin for CreditSettings."""

    list_display = [
        "tenant",
        "default_credit_limit",
        "default_payment_terms_days",
        "auto_approval_threshold",
    ]


@admin.register(CreditApprovalWorkflow)
class CreditApprovalWorkflowAdmin(admin.ModelAdmin):
    """Admin for CreditApprovalWorkflow."""

    list_display = [
        "customer",
        "request_type",
        "requested_credit_limit",
        "status",
        "priority",
        "requested_at",
    ]
    list_filter = ["status", "request_type", "priority"]
    readonly_fields = ["requested_at", "reviewed_at", "created_on", "updated_on"]


@admin.register(CreditTransaction)
class CreditTransactionAdmin(admin.ModelAdmin):
    """Admin for CreditTransaction."""

    list_display = [
        "transaction_number",
        "credit_account",
        "transaction_type",
        "amount",
        "balance_after",
        "status",
        "transaction_date",
    ]
    list_filter = ["transaction_type", "status", "is_reversed"]
    search_fields = ["transaction_number", "reference_id", "notes"]
    readonly_fields = ["transaction_number", "created_on", "updated_on"]


@admin.register(LoyaltyProgram)
class LoyaltyProgramAdmin(admin.ModelAdmin):
    """Admin for LoyaltyProgram."""

    list_display = [
        "name",
        "tenant",
        "points_per_currency",
        "is_active",
        "start_date",
        "end_date",
    ]
    list_filter = ["is_active"]
    readonly_fields = ["created_on", "updated_on"]


@admin.register(CustomerLoyalty)
class CustomerLoyaltyAdmin(admin.ModelAdmin):
    """Admin for CustomerLoyalty."""

    list_display = [
        "customer",
        "program",
        "status",
        "points_balance",
        "lifetime_points_earned",
        "current_tier",
    ]
    list_filter = ["status"]
    search_fields = ["customer__first_name", "customer__last_name", "customer__email"]
    readonly_fields = ["enrolled_date", "created_on", "updated_on"]


@admin.register(PointsTransaction)
class PointsTransactionAdmin(admin.ModelAdmin):
    """Admin for PointsTransaction."""

    list_display = [
        "customer_loyalty",
        "transaction_type",
        "points",
        "balance_after",
        "transaction_date",
        "is_expired",
    ]
    list_filter = ["transaction_type", "is_expired"]
    search_fields = ["description", "reference_id"]
    readonly_fields = ["transaction_date", "created_on", "updated_on"]


@admin.register(LoyaltyTier)
class LoyaltyTierAdmin(admin.ModelAdmin):
    """Admin for LoyaltyTier."""

    list_display = ["name", "program", "level", "points_multiplier", "min_points_required", "is_default"]
    list_filter = ["is_default"]
    readonly_fields = ["created_on", "updated_on"]


@admin.register(LoyaltyReward)
class LoyaltyRewardAdmin(admin.ModelAdmin):
    """Admin for LoyaltyReward."""

    list_display = ["name", "program", "reward_type", "is_active", "valid_from", "valid_until"]
    list_filter = ["reward_type", "is_active"]
    readonly_fields = ["created_on", "updated_on"]


@admin.register(StoreCredit)
class StoreCreditAdmin(admin.ModelAdmin):
    """Admin for StoreCredit."""

    list_display = [
        "customer",
        "balance",
        "total_issued",
        "total_used",
        "created_from",
        "expiry_date",
    ]
    list_filter = ["created_from"]
    search_fields = ["customer__first_name", "customer__last_name", "customer__email"]
    readonly_fields = ["last_transaction_at", "created_on", "updated_on"]


@admin.register(StoreCreditTransaction)
class StoreCreditTransactionAdmin(admin.ModelAdmin):
    """Admin for StoreCreditTransaction."""

    list_display = [
        "store_credit",
        "transaction_type",
        "amount",
        "balance_before",
        "balance_after",
        "reference",
    ]
    list_filter = ["transaction_type"]
    search_fields = ["reference", "notes"]
    readonly_fields = ["created_on", "updated_on"]


@admin.register(PointsPromotion)
class PointsPromotionAdmin(admin.ModelAdmin):
    """Admin for PointsPromotion."""

    list_display = [
        "name",
        "program",
        "promotion_type",
        "multiplier",
        "bonus_points",
        "is_active",
        "valid_from",
        "valid_to",
    ]
    list_filter = ["promotion_type", "is_active"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_on", "updated_on"]
    filter_horizontal = ["applicable_categories", "applicable_products"]
