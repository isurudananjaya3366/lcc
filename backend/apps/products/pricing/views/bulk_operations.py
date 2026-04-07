"""
Bulk price and schedule operations views.
"""

from datetime import timedelta
from decimal import Decimal, InvalidOperation

from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import ProductPrice, ScheduledPrice
from ..permissions import CanCreatePromotions, HasPricingPermission


class BulkPriceUpdateView(APIView):
    """
    Authenticated POST endpoint for bulk price adjustments.

    Body::

        {
            "filters": {"category_id": ..., "product_ids": [...]},
            "field": "base_price" | "sale_price",
            "update_type": "percentage" | "absolute",
            "value": 10,
            "preview": true
        }
    """

    permission_classes = [IsAuthenticated, HasPricingPermission]

    def post(self, request):
        filters = request.data.get("filters", {})
        field = request.data.get("field", "base_price")
        update_type = request.data.get("update_type")
        value = request.data.get("value")
        preview = bool(request.data.get("preview", False))

        if update_type not in ("percentage", "absolute"):
            return Response(
                {"detail": "update_type must be 'percentage' or 'absolute'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if field not in ("base_price", "sale_price"):
            return Response(
                {"detail": "field must be 'base_price' or 'sale_price'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            value = Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            return Response(
                {"detail": "Invalid value."}, status=status.HTTP_400_BAD_REQUEST
            )

        qs = ProductPrice.objects.select_related("product").all()
        product_ids = filters.get("product_ids")
        category_id = filters.get("category_id")
        if product_ids:
            qs = qs.filter(product_id__in=product_ids)
        if category_id:
            qs = qs.filter(product__category_id=category_id)

        updates = []
        with transaction.atomic():
            for pp in qs:
                old_val = getattr(pp, field) or Decimal("0")
                if update_type == "percentage":
                    new_val = old_val * (1 + value / 100)
                else:
                    new_val = old_val + value
                new_val = max(new_val, Decimal("0")).quantize(Decimal("0.01"))
                updates.append(
                    {
                        "id": str(pp.pk),
                        "product": str(pp.product_id),
                        "old_value": str(old_val),
                        "new_value": str(new_val),
                    }
                )
                if not preview:
                    setattr(pp, field, new_val)
                    pp.save(update_fields=[field, "updated_at"])

        return Response(
            {
                "preview": preview,
                "field": field,
                "update_type": update_type,
                "value": str(value),
                "count": len(updates),
                "updates": updates,
            }
        )


class BulkScheduleOperationsView(APIView):
    """
    POST /api/pricing/schedules/bulk-operations/

    Body::

        {
            "operation": "duplicate" | "activate" | "deactivate" | "update_priority",
            "schedule_ids": ["uuid1", "uuid2"],
            "params": {"days_offset": 7, "priority": 50}
        }
    """

    permission_classes = [IsAuthenticated, CanCreatePromotions]

    def post(self, request):
        operation = request.data.get("operation")
        schedule_ids = request.data.get("schedule_ids", [])
        params = request.data.get("params", {})

        if not operation or not schedule_ids:
            return Response(
                {"detail": "operation and schedule_ids are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ALLOWED = ("duplicate", "activate", "deactivate", "update_priority")
        if operation not in ALLOWED:
            return Response(
                {"detail": f"Unknown operation. Choose from {ALLOWED}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        schedules = ScheduledPrice.objects.filter(pk__in=schedule_ids)
        handler = getattr(self, f"_op_{operation}")
        result = handler(schedules, params, request)
        return Response(result)

    # ── operation handlers ─────────────────────────────────────

    @staticmethod
    def _op_duplicate(schedules, params, request):
        days_offset = int(params.get("days_offset", 7))
        created = []
        with transaction.atomic():
            for sp in schedules:
                new_sp = ScheduledPrice(
                    product=sp.product,
                    variant=sp.variant,
                    name=f"{sp.name} (Copy)",
                    description=sp.description,
                    sale_price=sp.sale_price,
                    start_datetime=sp.start_datetime + timedelta(days=days_offset),
                    end_datetime=sp.end_datetime + timedelta(days=days_offset),
                    priority=sp.priority,
                    status=ScheduledPrice.Status.PENDING,
                    created_by=request.user if request.user.is_authenticated else None,
                )
                new_sp.save()
                created.append(str(new_sp.pk))
        return {"operation": "duplicate", "count": len(created), "new_ids": created}

    @staticmethod
    def _op_activate(schedules, _params, _request):
        count = schedules.update(status=ScheduledPrice.Status.ACTIVE)
        return {"operation": "activate", "count": count}

    @staticmethod
    def _op_deactivate(schedules, _params, _request):
        count = schedules.update(status=ScheduledPrice.Status.EXPIRED)
        return {"operation": "deactivate", "count": count}

    @staticmethod
    def _op_update_priority(schedules, params, _request):
        new_priority = int(params.get("priority", 0))
        count = schedules.update(priority=new_priority)
        return {"operation": "update_priority", "count": count, "new_priority": new_priority}
