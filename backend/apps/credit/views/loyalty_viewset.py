"""
Loyalty ViewSet.

Provides CRUD + custom actions for CustomerLoyalty accounts:
award_points, redeem_points, upgrade_tier, tier_eligibility,
points_forecast, points_history, tier_progress, dashboard.
"""

import logging
from decimal import Decimal, InvalidOperation

from django.db.models import Avg, Count, Sum
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.credit.filters import LoyaltyFilterSet
from apps.credit.models import CustomerLoyalty, LoyaltyTier
from apps.credit.serializers import (
    CustomerLoyaltySerializer,
    LoyaltyTierSerializer,
    PointsTransactionSerializer,
)
from apps.credit.services.loyalty_service import LoyaltyService
from apps.credit.services.tier_service import TierService

logger = logging.getLogger(__name__)


class LoyaltyViewSet(ModelViewSet):
    """ViewSet for customer loyalty accounts."""

    permission_classes = [IsAuthenticated]
    serializer_class = CustomerLoyaltySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = LoyaltyFilterSet
    search_fields = [
        "customer__first_name",
        "customer__last_name",
        "customer__email",
    ]
    ordering_fields = [
        "points_balance",
        "lifetime_points_earned",
        "enrolled_date",
        "created_on",
    ]
    ordering = ["-created_on"]

    def get_queryset(self):
        return CustomerLoyalty.objects.select_related(
            "customer", "program", "current_tier"
        ).filter(is_deleted=False)

    # ── Read-only detail actions ────────────────────────────────────

    @action(detail=True, methods=["get"], url_path="points-history")
    def points_history(self, request, pk=None):
        """List points transactions for this loyalty account."""
        loyalty = self.get_object()
        txns = loyalty.points_transactions.order_by("-transaction_date")
        page = self.paginate_queryset(txns)
        if page is not None:
            serializer = PointsTransactionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = PointsTransactionSerializer(txns, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="tier-progress")
    def tier_progress(self, request, pk=None):
        """Show progress toward next tier."""
        loyalty = self.get_object()
        progress = TierService.get_tier_progress(loyalty)
        return Response(progress)

    @action(detail=False, methods=["get"], url_path="dashboard")
    def dashboard(self, request):
        """Aggregate loyalty statistics."""
        qs = self.get_queryset()
        data = {
            "total_members": qs.count(),
            "active_members": qs.filter(status="active").count(),
            "total_points_in_circulation": str(
                qs.aggregate(total=Sum("points_balance"))["total"]
                or Decimal("0.00")
            ),
            "total_lifetime_points": str(
                qs.aggregate(total=Sum("lifetime_points_earned"))["total"]
                or Decimal("0.00")
            ),
            "average_points_balance": str(
                qs.aggregate(avg=Avg("points_balance"))["avg"]
                or Decimal("0.00")
            ),
            "tier_distribution": list(
                qs.values("current_tier__name")
                .annotate(count=Count("id"))
                .order_by("-count")
            ),
        }
        return Response(data)

    # ── Point operations ────────────────────────────────────────────

    @action(detail=True, methods=["post"], url_path="award-points")
    def award_points(self, request, pk=None):
        """Award points to a loyalty account."""
        loyalty = self.get_object()
        amount = request.data.get("amount")
        description = request.data.get("description", "")
        reference_id = request.data.get("reference_id")
        reference_type = request.data.get("reference_type")

        if amount is None:
            return Response(
                {"detail": "amount is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            amount = Decimal(str(amount))
        except (InvalidOperation, TypeError, ValueError):
            return Response(
                {"detail": "Invalid amount value."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            txn = LoyaltyService.award_points(
                loyalty=loyalty,
                amount=amount,
                reference_id=reference_id,
                reference_type=reference_type,
                description=description,
            )
        except Exception as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            PointsTransactionSerializer(txn).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="redeem-points")
    def redeem_points(self, request, pk=None):
        """Redeem points from a loyalty account."""
        loyalty = self.get_object()
        points = request.data.get("points")
        description = request.data.get("description", "")
        reference_id = request.data.get("reference_id")
        reference_type = request.data.get("reference_type")

        if points is None:
            return Response(
                {"detail": "points is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            points = int(points)
        except (TypeError, ValueError):
            return Response(
                {"detail": "Invalid points value."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            txn = LoyaltyService.redeem_points(
                loyalty=loyalty,
                points_to_redeem=points,
                reference_id=reference_id,
                reference_type=reference_type,
                description=description,
            )
        except Exception as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            PointsTransactionSerializer(txn).data,
            status=status.HTTP_201_CREATED,
        )

    # ── Admin tier actions ──────────────────────────────────────────

    @action(
        detail=True,
        methods=["post"],
        url_path="upgrade-tier",
        permission_classes=[IsAdminUser],
    )
    def upgrade_tier(self, request, pk=None):
        """Manually upgrade a customer's tier (admin only)."""
        loyalty = self.get_object()
        tier_id = request.data.get("tier_id")
        if not tier_id:
            return Response(
                {"detail": "tier_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            new_tier = LoyaltyTier.objects.get(pk=tier_id)
        except LoyaltyTier.DoesNotExist:
            return Response(
                {"detail": "Tier not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        TierService.upgrade_tier(loyalty, new_tier)
        loyalty.refresh_from_db()
        return Response(CustomerLoyaltySerializer(loyalty).data)

    @action(detail=True, methods=["get"], url_path="tier-eligibility")
    def tier_eligibility(self, request, pk=None):
        """Check which tiers this customer qualifies for."""
        loyalty = self.get_object()
        program = loyalty.program
        tiers = LoyaltyTier.objects.filter(program=program).order_by("level")
        eligible = []
        for tier in tiers:
            qualifies = TierService.qualifies_for_tier(
                loyalty.lifetime_points_earned, Decimal("0"), tier
            )
            eligible.append(
                {
                    "tier": LoyaltyTierSerializer(tier).data,
                    "qualifies": qualifies,
                }
            )
        return Response(eligible)

    @action(detail=True, methods=["get"], url_path="points-forecast")
    def points_forecast(self, request, pk=None):
        """Forecast points and tier status based on current trajectory."""
        loyalty = self.get_object()
        progress = TierService.get_tier_progress(loyalty)
        breakdown = LoyaltyService.get_points_breakdown(loyalty)
        return Response(
            {
                "current_points": loyalty.points_balance,
                "lifetime_earned": loyalty.lifetime_points_earned,
                "tier_progress": progress,
                "points_breakdown": breakdown,
            }
        )
