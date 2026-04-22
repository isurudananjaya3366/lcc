"""
ProductSearchService – unified product search for POS terminals.

Provides barcode, SKU, name, and combined searches with deduplication,
stock availability, and search-history tracking.
"""

from decimal import Decimal
from typing import Any, Optional

from django.db.models import Q, QuerySet

from apps.pos.constants import (
    SEARCH_METHOD_BARCODE,
    SEARCH_METHOD_COMBINED,
    SEARCH_METHOD_NAME,
    SEARCH_METHOD_SKU,
)
from apps.pos.search.validators import detect_barcode_format, parse_weight_barcode
from apps.products.constants import PRODUCT_STATUS


class ProductSearchService:
    """Stateless service with class-method API for POS product search."""

    # ── internal helpers ────────────────────────────────────────────

    @classmethod
    def _get_tenant_products(cls, category=None) -> QuerySet:
        """Return an optimised queryset of active, POS-visible products."""
        from apps.products.models import Product

        qs = Product.objects.filter(
            is_active=True,
            is_deleted=False,
            is_pos_visible=True,
            status=PRODUCT_STATUS.ACTIVE,
        ).select_related("category", "brand", "tax_class", "unit_of_measure")

        if category is not None:
            descendants = category.get_descendants(include_self=True)
            qs = qs.filter(category__in=descendants)

        return qs

    @classmethod
    def _format_product_result(
        cls, product, *, search_method: str = "", variant=None
    ) -> dict[str, Any]:
        """Map a Product (or variant) to a dict for the POS frontend."""
        result: dict[str, Any] = {
            "id": str(product.id),
            "name": product.name,
            "sku": product.sku,
            "barcode": product.barcode,
            "selling_price": str(product.selling_price),
            "cost_price": str(product.cost_price) if product.cost_price else None,
            "category": str(product.category) if product.category_id else None,
            "brand": str(product.brand) if product.brand_id else None,
            "tax_class": str(product.tax_class) if product.tax_class_id else None,
            "product_type": product.product_type,
            "is_pos_visible": product.is_pos_visible,
        }
        if variant:
            result["variant_id"] = str(variant.id)
            result["variant_sku"] = variant.sku
            result["variant_barcode"] = variant.barcode
            result["variant_name"] = variant.name
        if search_method:
            result["search_method"] = search_method
        return result

    @classmethod
    def _deduplicate_results(
        cls, results: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Remove duplicate products, keeping the first occurrence."""
        seen: set[str] = set()
        deduped: list[dict[str, Any]] = []
        for item in results:
            pid = item["id"]
            if pid not in seen:
                seen.add(pid)
                deduped.append(item)
        return deduped

    @classmethod
    def _check_stock_availability(
        cls, product, location=None
    ) -> dict[str, Any]:
        """
        Check stock availability for a product at an optional location.

        Returns dict with quantity, available, reserved, status, etc.
        """
        result: dict[str, Any] = {
            "quantity": Decimal("0"),
            "available": Decimal("0"),
            "reserved": Decimal("0"),
            "status": "out_of_stock",
            "low_stock_threshold": None,
            "reorder_level": None,
            "below_reorder": False,
        }

        try:
            from apps.inventory.models import StockRecord

            filters = {"product": product}
            if location is not None:
                filters["location"] = location

            stock = (
                StockRecord.objects.filter(**filters)
                .order_by("-updated_on")
                .first()
            )
            if stock:
                qty = getattr(stock, "quantity", Decimal("0")) or Decimal("0")
                reserved = getattr(stock, "reserved_quantity", Decimal("0")) or Decimal("0")
                available = qty - reserved
                result["quantity"] = qty
                result["reserved"] = reserved
                result["available"] = max(available, Decimal("0"))

                low_threshold = getattr(stock, "low_stock_threshold", None)
                reorder = getattr(stock, "reorder_level", None)
                result["low_stock_threshold"] = low_threshold
                result["reorder_level"] = reorder
                result["below_reorder"] = (
                    reorder is not None and qty <= reorder
                )

                if available <= 0:
                    result["status"] = "out_of_stock"
                elif low_threshold and available <= low_threshold:
                    result["status"] = "low_stock"
                else:
                    result["status"] = "in_stock"
        except (ImportError, Exception):
            # Inventory module may not be available
            pass

        return result

    @classmethod
    def _get_effective_price(
        cls, product, customer=None, quantity: int = 1
    ) -> dict[str, Any]:
        """
        Determine the effective selling price for a product,
        considering customer group pricing and active promotions.
        """
        base_price = product.selling_price or Decimal("0")
        unit_price = base_price
        discount_amount = Decimal("0")
        discount_percent = Decimal("0")
        discount_reason = ""
        promotion = None

        # Customer group pricing
        if customer and hasattr(customer, "customer_group") and customer.customer_group:
            try:
                from apps.products.models import CustomerGroupPrice

                group_price = (
                    CustomerGroupPrice.objects.filter(
                        product=product,
                        customer_group=customer.customer_group,
                        is_active=True,
                    )
                    .first()
                )
                if group_price and group_price.price:
                    unit_price = group_price.price
                    discount_amount = base_price - unit_price
                    if base_price > 0:
                        discount_percent = (discount_amount / base_price) * 100
                    discount_reason = f"Customer group: {customer.customer_group}"
            except (ImportError, Exception):
                pass

        # Tax calculation
        tax_rate = Decimal("0")
        if hasattr(product, "tax_class") and product.tax_class:
            tax_rate = getattr(product.tax_class, "rate", Decimal("0")) or Decimal("0")
        price_with_tax = unit_price * (1 + tax_rate / 100)

        # Currency
        currency = "LKR"
        try:
            from django.conf import settings

            currency = getattr(settings, "DEFAULT_CURRENCY", "LKR")
        except Exception:
            pass

        return {
            "base_price": str(base_price),
            "unit_price": str(unit_price),
            "discount_amount": str(discount_amount),
            "discount_percent": str(discount_percent.quantize(Decimal("0.01"))),
            "discount_reason": discount_reason,
            "tax_rate": str(tax_rate),
            "price_with_tax": str(price_with_tax.quantize(Decimal("0.01"))),
            "currency": currency,
            "promotion": promotion,
        }

    # ── core search methods ─────────────────────────────────────────

    @classmethod
    def barcode_search(cls, barcode: str) -> Optional[dict[str, Any]]:
        """Exact barcode match — checks variants first, then products."""
        if not barcode or not barcode.strip():
            return None
        barcode = barcode.strip()

        # Weight-embedded barcode
        weight_data = parse_weight_barcode(barcode)
        if weight_data:
            product = (
                cls._get_tenant_products()
                .filter(barcode__endswith=weight_data["product_code"])
                .first()
            )
            if product:
                result = cls._format_product_result(
                    product, search_method=SEARCH_METHOD_BARCODE
                )
                result["weight_kg"] = str(weight_data["weight_kg"])
                return result

        # Variant barcode
        variant = cls._search_variant_by_barcode(barcode)
        if variant:
            return cls._format_product_result(
                variant.product, search_method=SEARCH_METHOD_BARCODE, variant=variant
            )

        # Product barcode
        product = cls._get_tenant_products().filter(barcode=barcode).first()
        if product:
            return cls._format_product_result(
                product, search_method=SEARCH_METHOD_BARCODE
            )

        return None

    @classmethod
    def sku_search(
        cls, sku: str, *, exact: bool = True
    ) -> list[dict[str, Any]]:
        """Search by SKU — exact or partial (icontains)."""
        if not sku or not sku.strip():
            return []
        sku = sku.strip()
        qs = cls._get_tenant_products()

        if exact:
            qs = qs.filter(sku__iexact=sku)
        else:
            qs = qs.filter(sku__icontains=sku)

        qs = qs.order_by("sku", "name")

        return [
            cls._format_product_result(p, search_method=SEARCH_METHOD_SKU)
            for p in qs
        ]

    @classmethod
    def name_search(
        cls, query: str, *, limit: int = 20
    ) -> list[dict[str, Any]]:
        """Fuzzy name search using icontains (trigram when postgres ext available)."""
        if not query or len(query.strip()) < 2:
            return []
        query = query.strip()
        qs = cls._get_tenant_products().filter(name__icontains=query).order_by("name")[
            :limit
        ]
        return [
            cls._format_product_result(p, search_method=SEARCH_METHOD_NAME)
            for p in qs
        ]

    @classmethod
    def combined_search(
        cls, query: str, *, limit: int = 20
    ) -> list[dict[str, Any]]:
        """
        Cascade search: barcode → exact SKU → name + partial SKU.

        Priority:
        1. Barcode exact match → return immediately
        2. SKU exact match → return immediately
        3. Combine name search + partial SKU search, deduplicate and limit
        """
        if not query or not query.strip():
            return []
        query = query.strip()

        # 1. barcode
        barcode_result = cls.barcode_search(query)
        if barcode_result:
            barcode_result["search_method"] = SEARCH_METHOD_COMBINED
            return [barcode_result]

        # 2. exact SKU
        sku_exact = cls.sku_search(query, exact=True)
        if sku_exact:
            for r in sku_exact:
                r["search_method"] = SEARCH_METHOD_COMBINED
            return sku_exact

        # 3. name + partial SKU
        name_results = cls.name_search(query, limit=limit)
        sku_partial = cls.sku_search(query, exact=False)
        combined = name_results + sku_partial
        for r in combined:
            r["search_method"] = SEARCH_METHOD_COMBINED
        return cls._deduplicate_results(combined)[:limit]

    # ── enhanced helpers ────────────────────────────────────────────

    @classmethod
    def _search_variant_by_barcode(cls, barcode: str):
        """Look up a ProductVariant by its barcode."""
        from apps.products.models import ProductVariant

        return (
            ProductVariant.objects.select_related("product")
            .filter(barcode=barcode, product__is_pos_visible=True)
            .first()
        )

    @classmethod
    def filter_by_category(
        cls, category, *, query: str = None, limit: int = 50, sort_by: str = "name"
    ) -> list[dict[str, Any]]:
        """Filter products by category, optionally narrowing with a text query."""
        qs = cls._get_tenant_products(category=category)
        if query:
            qs = qs.filter(Q(name__icontains=query) | Q(sku__icontains=query))

        ordering = {
            "name": "name",
            "price": "selling_price",
        }
        qs = qs.order_by(ordering.get(sort_by, "name"))[:limit]
        return [cls._format_product_result(p) for p in qs]

    # ── search history / suggestions ────────────────────────────────

    @classmethod
    def record_search(
        cls,
        query_text: str = "",
        *,
        query: str = "",
        result_count: int = 0,
        search_method: str = SEARCH_METHOD_COMBINED,
        terminal=None,
        user=None,
        selected_product=None,
    ):
        """Persist a search to SearchHistory."""
        from apps.pos.search.models import SearchHistory

        q = (query_text or query)[:200]
        SearchHistory.objects.create(
            query=q,
            result_count=result_count,
            search_method=search_method,
            terminal=terminal,
            user=user,
            selected_product=selected_product,
        )

    @classmethod
    def get_recent_searches(
        cls, *, terminal=None, user=None, limit: int = 10
    ) -> QuerySet:
        """Return distinct recent queries ordered by timestamp."""
        from apps.pos.search.models import SearchHistory

        qs = SearchHistory.objects.all()
        if terminal:
            qs = qs.filter(terminal=terminal)
        if user:
            qs = qs.filter(user=user)
        return qs.values_list("query", flat=True).distinct()[:limit]

    @classmethod
    def get_popular_products(
        cls, *, terminal=None, user=None, limit: int = 10, days: int = 30
    ) -> list[dict[str, Any]]:
        """Products most frequently selected in search history."""
        from django.db.models import Count
        from django.utils import timezone

        from apps.pos.search.models import SearchHistory

        since = timezone.now() - timezone.timedelta(days=days)
        qs = SearchHistory.objects.filter(
            timestamp__gte=since,
            selected_product__isnull=False,
        )
        if terminal:
            qs = qs.filter(terminal=terminal)
        if user:
            qs = qs.filter(user=user)

        top_ids = (
            qs.values("selected_product")
            .annotate(count=Count("id"))
            .order_by("-count")[:limit]
        )

        from apps.products.models import Product

        products = Product.objects.filter(
            id__in=[row["selected_product"] for row in top_ids]
        )
        product_map = {str(p.id): p for p in products}
        return [
            cls._format_product_result(product_map[str(row["selected_product"])])
            for row in top_ids
            if str(row["selected_product"]) in product_map
        ]

    @classmethod
    def get_search_suggestions(
        cls, partial_query: str, *, terminal=None, limit: int = 5
    ) -> list[str]:
        """Autocomplete suggestions from past search queries."""
        from django.db.models import Count

        from apps.pos.search.models import SearchHistory

        if not partial_query or len(partial_query.strip()) < 2:
            return []
        qs = SearchHistory.objects.filter(query__icontains=partial_query.strip())
        if terminal:
            qs = qs.filter(terminal=terminal)
        return list(
            qs.values_list("query", flat=True)
            .annotate(freq=Count("id"))
            .order_by("-freq")[:limit]
        )

    # ── category helpers ────────────────────────────────────────────

    @classmethod
    def get_active_categories(cls) -> list[dict[str, Any]]:
        """Return active categories that contain POS-visible products."""
        from apps.products.models import Product

        category_ids = (
            Product.objects.filter(
                is_active=True,
                is_deleted=False,
                is_pos_visible=True,
                status=PRODUCT_STATUS.ACTIVE,
                category__isnull=False,
            )
            .values_list("category_id", flat=True)
            .distinct()
        )

        from apps.products.models import Category

        categories = Category.objects.filter(
            id__in=category_ids, is_active=True
        ).order_by("name")

        return [
            {
                "id": str(cat.id),
                "name": cat.name,
                "parent_id": str(cat.parent_id) if cat.parent_id else None,
                "level": getattr(cat, "level", 0),
                "product_count": (
                    Product.objects.filter(
                        category=cat,
                        is_active=True,
                        is_deleted=False,
                        is_pos_visible=True,
                    ).count()
                ),
            }
            for cat in categories
        ]

    @classmethod
    def get_category_quick_filters(cls, limit: int = 10) -> list[dict[str, Any]]:
        """Return top-level categories with product counts for quick filter UI."""
        from django.db.models import Count

        from apps.products.models import Category

        top_categories = (
            Category.objects.filter(
                is_active=True,
                parent__isnull=True,
            )
            .annotate(
                pos_product_count=Count(
                    "product",
                    filter=Q(
                        product__is_active=True,
                        product__is_deleted=False,
                        product__is_pos_visible=True,
                    ),
                )
            )
            .filter(pos_product_count__gt=0)
            .order_by("-pos_product_count")[:limit]
        )
        return [
            {
                "id": str(cat.id),
                "name": cat.name,
                "product_count": cat.pos_product_count,
                "icon": getattr(cat, "icon", ""),
            }
            for cat in top_categories
        ]
