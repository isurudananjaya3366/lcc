"""
Scheduled price & flash sale ViewSets.
"""

from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from ..models import ScheduledPrice, FlashSale
from ..permissions import CanCreatePromotions
from ..serializers import ScheduledPriceSerializer, FlashSaleSerializer


class ScheduledPriceViewSet(ModelViewSet):
    """CRUD + lifecycle actions for scheduled prices."""

    permission_classes = [IsAuthenticated, CanCreatePromotions]
    serializer_class = ScheduledPriceSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "product", "variant", "priority"]
    search_fields = ["name", "product__name"]
    ordering_fields = ["start_date", "end_date", "priority", "created_on"]
    ordering = ["-start_date"]

    def get_queryset(self):
        return ScheduledPrice.objects.select_related("product", "variant").all()

    @action(detail=True, methods=["post"], url_path="activate")
    def activate(self, request, pk=None):
        """Manually activate a scheduled price."""
        obj = self.get_object()
        obj.status = ScheduledPrice.Status.ACTIVE
        obj.save(update_fields=["status", "updated_at"])
        return Response(ScheduledPriceSerializer(obj).data)

    @action(detail=True, methods=["post"], url_path="deactivate")
    def deactivate(self, request, pk=None):
        """Manually deactivate (expire) a scheduled price."""
        obj = self.get_object()
        obj.status = ScheduledPrice.Status.EXPIRED
        obj.save(update_fields=["status", "updated_at"])
        return Response(ScheduledPriceSerializer(obj).data)

    @action(detail=False, methods=["get"], url_path="upcoming")
    def upcoming(self, request):
        """List scheduled prices that haven't started yet."""
        qs = self.filter_queryset(self.get_queryset()).filter(
            status=ScheduledPrice.Status.PENDING,
            start_date__gt=timezone.now(),
        )
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(
                ScheduledPriceSerializer(page, many=True).data
            )
        return Response(ScheduledPriceSerializer(qs, many=True).data)

    @action(detail=False, methods=["get"], url_path="active")
    def active(self, request):
        """List currently active scheduled prices."""
        qs = self.filter_queryset(self.get_queryset()).filter(
            status=ScheduledPrice.Status.ACTIVE,
        )
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(
                ScheduledPriceSerializer(page, many=True).data
            )
        return Response(ScheduledPriceSerializer(qs, many=True).data)

    @action(detail=True, methods=["get"], url_path="conflicts")
    def conflicts(self, request, pk=None):
        """Find overlapping scheduled prices for the same product/variant."""
        obj = self.get_object()
        overlaps = obj.get_overlapping_schedules()
        return Response(ScheduledPriceSerializer(overlaps, many=True).data)


class FlashSaleViewSet(ModelViewSet):
    """CRUD + availability actions for flash sales."""

    permission_classes = [IsAuthenticated, CanCreatePromotions]
    serializer_class = FlashSaleSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["scheduled_price__status", "scheduled_price__product"]
    search_fields = ["scheduled_price__name"]
    ordering_fields = ["scheduled_price__start_date"]
    ordering = ["-scheduled_price__start_date"]

    def get_queryset(self):
        return FlashSale.objects.select_related(
            "scheduled_price", "scheduled_price__product", "scheduled_price__variant"
        ).all()

    @action(detail=True, methods=["get"], url_path="availability")
    def availability(self, request, pk=None):
        """Return current availability and urgency info."""
        fs = self.get_object()
        return Response(
            {
                "is_sold_out": fs.is_sold_out,
                "quantity_remaining": fs.quantity_remaining,
                "percent_sold": str(fs.percent_sold),
                "time_remaining": str(fs.time_remaining) if fs.time_remaining else None,
                "urgency_level": fs.urgency_level,
                "urgency_message": fs.get_urgency_message(),
            }
        )

    @action(detail=False, methods=["get"], url_path="active-now")
    def active_now(self, request):
        """List flash sales that are currently active and not sold out."""
        qs = self.filter_queryset(self.get_queryset()).filter(
            scheduled_price__status=ScheduledPrice.Status.ACTIVE,
        )
        # Exclude sold-out in Python since is_sold_out is a property
        active = [fs for fs in qs if not fs.is_sold_out]
        return Response(FlashSaleSerializer(active, many=True).data)
