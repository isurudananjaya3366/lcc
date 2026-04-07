"""
Credit & Loyalty dashboard aggregation views.

Provides admin dashboard data including credit overview, loyalty overview,
promotion analytics, transaction trends, and top-customer rankings.
"""

from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.credit.models.customer_loyalty import CustomerLoyalty
from apps.credit.models.points_promotion import PointsPromotion
from apps.credit.models.points_transaction import PointsTransaction
from apps.credit.models.store_credit import StoreCredit, StoreCreditTransaction


# ── Helper aggregators ──────────────────────────────────────────────


def get_credit_dashboard_data():
    """Aggregate store credit metrics."""
    credits = StoreCredit.objects.all()
    today = date.today()

    return {
        "total_customers_with_credit": credits.count(),
        "total_credit_balance": credits.aggregate(total=Sum("balance"))["total"]
        or Decimal("0.00"),
        "total_credit_issued_lifetime": credits.aggregate(total=Sum("total_issued"))[
            "total"
        ]
        or Decimal("0.00"),
        "total_credit_used_lifetime": credits.aggregate(total=Sum("total_used"))[
            "total"
        ]
        or Decimal("0.00"),
        "average_credit_balance": credits.aggregate(avg=Avg("balance"))["avg"]
        or Decimal("0.00"),
        "credits_expiring_soon": credits.filter(
            expiry_date__lte=today + timedelta(days=30),
            expiry_date__gte=today,
        ).count(),
        "expired_credits_count": credits.filter(
            expiry_date__lt=today,
            balance__gt=Decimal("0.00"),
        ).count(),
        "expired_credits_value": credits.filter(
            expiry_date__lt=today,
        ).aggregate(total=Sum("balance"))["total"]
        or Decimal("0.00"),
    }


def get_loyalty_dashboard_data():
    """Aggregate loyalty program metrics."""
    loyalty = CustomerLoyalty.objects.all()

    return {
        "total_loyalty_members": loyalty.count(),
        "total_points_balance": loyalty.aggregate(total=Sum("points_balance"))["total"]
        or 0,
        "total_points_earned_lifetime": loyalty.aggregate(
            total=Sum("lifetime_points_earned")
        )["total"]
        or 0,
        "total_points_redeemed_lifetime": loyalty.aggregate(
            total=Sum("total_points_redeemed")
        )["total"]
        or 0,
        "average_points_per_customer": loyalty.aggregate(avg=Avg("points_balance"))[
            "avg"
        ]
        or 0,
        "tier_breakdown": list(
            loyalty.values("current_tier__name").annotate(
                count=Count("id"),
            )
        ),
        "points_expiring_soon": PointsTransaction.objects.filter(
            transaction_type="earn",
            is_expired=False,
            expiry_date__lte=date.today() + timedelta(days=30),
            expiry_date__gt=date.today(),
        ).aggregate(total=Sum("points"))["total"]
        or 0,
    }


def get_promotion_analytics(days=30):
    """Track active promotion effectiveness over the last N days."""
    now = timezone.now()
    start_date = now - timedelta(days=days)

    active_promos = PointsPromotion.objects.filter(
        is_active=True,
        valid_from__lte=now,
        valid_to__gte=now,
    )

    promo_stats = []
    for promo in active_promos:
        bonus_txns = PointsTransaction.objects.filter(
            transaction_type="bonus",
            description__icontains=promo.name,
            created_on__gte=start_date,
        )
        participants = bonus_txns.values("customer_loyalty").distinct().count()
        total_bonus = bonus_txns.aggregate(total=Sum("points"))["total"] or 0
        promo_stats.append(
            {
                "promotion_name": promo.name,
                "type": promo.get_promotion_type_display(),
                "customers_participated": participants,
                "total_bonus_awarded": total_bonus,
                "average_bonus_per_customer": (
                    round(total_bonus / participants) if participants > 0 else 0
                ),
            }
        )

    return promo_stats


def get_transaction_trends(days=90):
    """Daily store-credit and points transaction trends."""
    start_dt = timezone.now() - timedelta(days=days)

    credit_trends = list(
        StoreCreditTransaction.objects.filter(created_on__gte=start_dt)
        .values("created_on__date")
        .annotate(
            issue_count=Count("id", filter=Q(transaction_type="issue")),
            redeem_count=Count("id", filter=Q(transaction_type="redeem")),
            issue_amount=Sum("amount", filter=Q(transaction_type="issue")),
            redeem_amount=Sum("amount", filter=Q(transaction_type="redeem")),
        )
        .order_by("created_on__date")
    )

    points_trends = list(
        PointsTransaction.objects.filter(created_on__gte=start_dt)
        .values("created_on__date")
        .annotate(
            earn_count=Count("id", filter=Q(transaction_type="earn")),
            redeem_count=Count("id", filter=Q(transaction_type="redeem")),
            earn_points=Sum("points", filter=Q(transaction_type="earn")),
            redeem_points=Sum("points", filter=Q(transaction_type="redeem")),
        )
        .order_by("created_on__date")
    )

    return {
        "credit_trends": credit_trends,
        "points_trends": points_trends,
    }


def get_top_loyalty_customers(limit=10):
    """Top customers by lifetime points earned."""
    return list(
        CustomerLoyalty.objects.select_related("customer")
        .order_by("-lifetime_points_earned")[:limit]
        .values(
            "customer__id",
            "customer__first_name",
            "customer__last_name",
            "lifetime_points_earned",
            "points_balance",
        )
    )


def get_top_credit_users(limit=10):
    """Top customers by total store credit used."""
    return list(
        StoreCredit.objects.select_related("customer")
        .order_by("-total_used")[:limit]
        .values(
            "customer__id",
            "customer__first_name",
            "customer__last_name",
            "total_used",
            "balance",
        )
    )


# ── DRF View ────────────────────────────────────────────────────────


class CreditLoyaltyDashboardView(APIView):
    """Combined credit & loyalty dashboard for admin users."""

    permission_classes = [IsAdminUser]

    def get(self, request):
        data = {
            "credit_metrics": get_credit_dashboard_data(),
            "loyalty_metrics": get_loyalty_dashboard_data(),
            "promotion_analytics": get_promotion_analytics(days=30),
            "trends": get_transaction_trends(days=90),
            "top_loyalty_customers": get_top_loyalty_customers(limit=10),
            "top_credit_users": get_top_credit_users(limit=10),
        }
        return Response(data)
