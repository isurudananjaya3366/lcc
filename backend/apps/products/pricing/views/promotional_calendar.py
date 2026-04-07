"""
Promotional calendar API endpoint.

Returns all promotions grouped by date for calendar display.
"""

from collections import defaultdict
from datetime import timedelta

from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import FlashSale, PromotionalPrice, ScheduledPrice
from ..permissions import CanCreatePromotions


class PromotionalCalendarView(APIView):
    """
    GET /api/pricing/promotional-calendar/

    Query params:
        start_date  – ISO datetime (default: now)
        end_date    – ISO datetime (default: start_date + 30 days)
        product_id  – filter by product UUID
        category_id – filter by category UUID
        status      – PENDING | ACTIVE | EXPIRED
    """

    permission_classes = [IsAuthenticated, CanCreatePromotions]

    def get(self, request):
        start_date = self._parse_dt(request.query_params.get("start_date")) or timezone.now()
        end_date = self._parse_dt(request.query_params.get("end_date")) or (start_date + timedelta(days=30))
        product_id = request.query_params.get("product_id")
        category_id = request.query_params.get("category_id")
        status_filter = request.query_params.get("status")

        calendar = self._build_calendar(start_date, end_date, product_id, category_id, status_filter)
        return Response(calendar)

    # ── internals ──────────────────────────────────────────────

    @staticmethod
    def _parse_dt(value):
        if not value:
            return None
        return parse_datetime(value)

    def _build_calendar(self, start_date, end_date, product_id, category_id, status_filter):
        calendar = defaultdict(lambda: {
            "date": None,
            "flash_sales": [],
            "scheduled_prices": [],
            "promotional_prices": [],
            "conflicts": [],
        })

        # --- Scheduled prices (excluding flash sales) ---
        sp_qs = ScheduledPrice.objects.filter(
            end_datetime__gte=start_date,
            start_datetime__lte=end_date,
        ).select_related("product", "variant")
        if product_id:
            sp_qs = sp_qs.filter(Q(product_id=product_id) | Q(variant__product_id=product_id))
        if status_filter:
            sp_qs = sp_qs.filter(status=status_filter.upper())

        flash_sp_ids = set(
            FlashSale.objects.filter(
                scheduled_price__in=sp_qs,
            ).values_list("scheduled_price_id", flat=True)
        )

        for sp in sp_qs:
            date_key = sp.start_datetime.date().isoformat()
            calendar[date_key]["date"] = date_key
            entry = {
                "id": str(sp.pk),
                "name": sp.name,
                "start": sp.start_datetime.isoformat(),
                "end": sp.end_datetime.isoformat(),
                "price": str(sp.sale_price),
                "priority": sp.priority,
                "status": sp.status,
            }
            if sp.pk in flash_sp_ids:
                try:
                    fs = sp.flash_sale_detail
                    entry.update({
                        "max_quantity": fs.max_quantity,
                        "quantity_remaining": fs.quantity_remaining,
                        "urgency": fs.urgency_level,
                    })
                    calendar[date_key]["flash_sales"].append(entry)
                except FlashSale.DoesNotExist:
                    calendar[date_key]["scheduled_prices"].append(entry)
            else:
                calendar[date_key]["scheduled_prices"].append(entry)

        # --- Promotional prices ---
        promo_qs = PromotionalPrice.objects.filter(
            is_active=True,
            end_datetime__gte=start_date,
            start_datetime__lte=end_date,
        )
        if category_id:
            promo_qs = promo_qs.filter(categories__id=category_id)

        for promo in promo_qs:
            date_key = promo.start_datetime.date().isoformat()
            calendar[date_key]["date"] = date_key
            calendar[date_key]["promotional_prices"].append({
                "id": str(promo.pk),
                "name": promo.name,
                "description": promo.description,
                "start": promo.start_datetime.isoformat(),
                "end": promo.end_datetime.isoformat(),
                "discount_type": promo.discount_type,
                "discount_value": str(promo.discount_value),
                "priority": promo.priority,
                "conditions": promo.get_conditions_display(),
            })

        # --- Conflict detection ---
        for date_key, day in calendar.items():
            day["conflicts"] = self._check_conflicts(day)

        calendar_list = sorted(calendar.values(), key=lambda d: d["date"])
        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "calendar": calendar_list,
        }

    @staticmethod
    def _check_conflicts(day_data):
        conflicts = []
        schedules = day_data["scheduled_prices"]
        for i, s1 in enumerate(schedules):
            for s2 in schedules[i + 1:]:
                if s1["priority"] == s2["priority"]:
                    conflicts.append({
                        "type": "priority_conflict",
                        "message": f"Same priority: {s1['name']} and {s2['name']}",
                    })
        return conflicts
