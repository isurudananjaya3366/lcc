"""Views for stock configuration (ProductStockConfig, GlobalStockSettings)."""

import logging

from django.db import transaction
from django.db.models import Count
from django_filters import rest_framework as django_filters
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.inventory.alerts.models import GlobalStockSettings, ProductStockConfig
from apps.inventory.alerts.serializers import (
    GlobalStockSettingsSerializer,
    ProductStockConfigSerializer,
)

logger = logging.getLogger(__name__)


# ── Filters ─────────────────────────────────────────────────────────


class ProductStockConfigFilter(django_filters.FilterSet):
    """Filter set for ProductStockConfig."""

    product_name = django_filters.CharFilter(
        field_name="product__name", lookup_expr="icontains"
    )
    product_sku = django_filters.CharFilter(
        field_name="product__sku", lookup_expr="iexact"
    )
    warehouse = django_filters.UUIDFilter(field_name="warehouse_id")
    excluded = django_filters.BooleanFilter(field_name="exclude_from_monitoring")
    has_low_stock_threshold = django_filters.BooleanFilter(
        method="filter_has_threshold"
    )

    class Meta:
        model = ProductStockConfig
        fields = ["product_name", "product_sku", "warehouse", "excluded"]

    def filter_has_threshold(self, queryset, name, value):
        if value:
            return queryset.exclude(low_stock_threshold__isnull=True)
        return queryset.filter(low_stock_threshold__isnull=True)


# ── ProductStockConfigViewSet ───────────────────────────────────────


class ProductStockConfigViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for ProductStockConfig.

    Endpoints:
        GET    /stock-config/                       - List
        POST   /stock-config/                       - Create
        GET    /stock-config/{id}/                  - Retrieve
        PUT    /stock-config/{id}/                  - Update
        PATCH  /stock-config/{id}/                  - Partial update
        DELETE /stock-config/{id}/                  - Delete
        GET    /stock-config/summary/               - Stats
        POST   /stock-config/{id}/reset_to_defaults/ - Reset
        POST   /stock-config/bulk/                  - Bulk update
        POST   /stock-config/bulk_exclude/          - Bulk exclude
    """

    queryset = ProductStockConfig.objects.all()
    serializer_class = ProductStockConfigSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        django_filters.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ProductStockConfigFilter
    search_fields = ["product__name", "product__sku", "exclusion_reason"]
    ordering_fields = [
        "product__name",
        "low_stock_threshold",
        "reorder_point",
        "created_on",
    ]
    ordering = ["product__name"]

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("product", "product__category", "warehouse", "preferred_supplier")
        )

    def perform_destroy(self, instance):
        if instance.product.stock_alerts.filter(status="active").exists():
            from rest_framework.exceptions import ValidationError

            raise ValidationError(
                "Cannot delete config with active alerts. Resolve alerts first."
            )
        instance.delete()

    # ── Custom actions ──────────────────────────────────────────

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """Statistics for stock configurations."""
        qs = self.filter_queryset(self.get_queryset())
        by_warehouse = (
            qs.values("warehouse__name")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        warehouse_map = {}
        for item in by_warehouse:
            warehouse_map[item["warehouse__name"] or "All Warehouses"] = item["count"]

        return Response(
            {
                "total_configs": qs.count(),
                "with_thresholds": qs.exclude(low_stock_threshold__isnull=True).count(),
                "with_reorder_points": qs.exclude(reorder_point__isnull=True).count(),
                "excluded_from_monitoring": qs.filter(
                    exclude_from_monitoring=True
                ).count(),
                "by_warehouse": warehouse_map,
            }
        )

    @action(detail=True, methods=["post"])
    def reset_to_defaults(self, request, pk=None):
        """Clear product-specific overrides, inherit from category / global."""
        config = self.get_object()
        config.low_stock_threshold = None
        config.reorder_point = None
        config.reorder_quantity = None
        config.auto_hide_when_oos = False
        config.allow_backorder = False
        config.save()
        return Response(self.get_serializer(config).data)

    @action(detail=False, methods=["post", "patch"])
    def bulk(self, request):
        """
        Bulk update stock configurations.

        Body:
        {
            "mode": "update_by_list",  // update_all | update_by_category | update_by_list
            "product_ids": [...],
            "category_id": ...,
            "updates": {...},
            "dry_run": false,
            "create_if_missing": true
        }
        """
        from apps.products.models import Product

        mode = request.data.get("mode", "update_by_list")
        updates = request.data.get("updates", {})
        dry_run = request.data.get("dry_run", False)

        if not updates:
            return Response(
                {"error": "updates dict is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        products = Product.objects.filter(is_active=True)
        if mode == "update_by_category":
            category_id = request.data.get("category_id")
            if not category_id:
                return Response(
                    {"error": "category_id required for update_by_category"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            products = products.filter(category_id=category_id)
        elif mode == "update_by_list":
            product_ids = request.data.get("product_ids", [])
            if not product_ids:
                return Response(
                    {"error": "product_ids required for update_by_list"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            products = products.filter(id__in=product_ids)
        elif mode != "update_all":
            return Response(
                {"error": f"Invalid mode: {mode}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not products.exists():
            return Response(
                {"error": "No products found matching criteria"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if dry_run:
            preview = []
            for p in products[:100]:
                cfg = ProductStockConfig.objects.filter(
                    product=p, warehouse__isnull=True
                ).first()
                preview.append(
                    {
                        "product_id": str(p.id),
                        "product_name": p.name,
                        "sku": p.sku,
                        "has_existing_config": cfg is not None,
                        "new_values": updates,
                    }
                )
            return Response(
                {
                    "dry_run": True,
                    "total_products": products.count(),
                    "preview_products": preview,
                    "updates_to_apply": updates,
                }
            )

        updated = created = skipped = 0
        errors_list = []
        with transaction.atomic():
            for p in products:
                try:
                    cfg, was_created = ProductStockConfig.objects.get_or_create(
                        product=p, warehouse=None, defaults=updates
                    )
                    if was_created:
                        created += 1
                    else:
                        for field, value in updates.items():
                            if hasattr(cfg, field):
                                setattr(cfg, field, value)
                        cfg.save()
                        updated += 1
                except Exception as exc:
                    skipped += 1
                    errors_list.append({"product_id": str(p.id), "error": str(exc)})

        return Response(
            {
                "success": True,
                "mode": mode,
                "total_products": products.count(),
                "updated_count": updated,
                "created_count": created,
                "skipped_count": skipped,
                "errors": errors_list[:10],
                "updates_applied": updates,
            }
        )

    @action(detail=False, methods=["post"])
    def bulk_exclude(self, request):
        """Bulk exclude / include products from monitoring."""
        product_ids = request.data.get("product_ids", [])
        exclude = request.data.get("exclude", True)
        reason = request.data.get("reason", "")

        if not product_ids:
            return Response(
                {"error": "product_ids list is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            updated = ProductStockConfig.objects.filter(
                product_id__in=product_ids
            ).update(
                exclude_from_monitoring=exclude,
                exclusion_reason=reason if exclude else "",
            )

        return Response({"success": True, "updated_count": updated, "excluded": exclude})


# ── GlobalStockSettingsViewSet ──────────────────────────────────────


class GlobalStockSettingsViewSet(viewsets.ModelViewSet):
    """
    Singleton settings endpoint per tenant.

    GET /global-settings/ returns the single settings object.
    """

    queryset = GlobalStockSettings.objects.all()
    serializer_class = GlobalStockSettingsSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        settings_obj = GlobalStockSettings.get_settings()
        return Response(self.get_serializer(settings_obj).data)
