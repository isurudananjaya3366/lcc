"""
Category views for the products API.

Provides a full CRUD ViewSet with custom tree endpoint.
"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.products.models import (
    BillOfMaterials,
    BOMItem,
    Brand,
    BundleItem,
    Category,
    Product,
    ProductBundle,
    ProductOptionConfig,
    ProductVariant,
    TaxClass,
    UnitOfMeasure,
    VariantOptionType,
    VariantOptionValue,
)

from .filters import ProductFilter
from .serializers import (
    BillOfMaterialsSerializer,
    BOMDetailSerializer,
    BOMItemSerializer,
    BrandSerializer,
    BulkVariantCreateSerializer,
    BundleDetailSerializer,
    BundleItemSerializer,
    CategoryCreateUpdateSerializer,
    CategoryDetailSerializer,
    CategoryListSerializer,
    CategoryTreeSerializer,
    ProductBundleSerializer,
    ProductCreateSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
    ProductOptionConfigSerializer,
    ProductVariantCreateSerializer,
    ProductVariantDetailSerializer,
    ProductVariantListSerializer,
    TaxClassSerializer,
    UnitOfMeasureSerializer,
    VariantOptionTypeSerializer,
    VariantOptionValueSerializer,
)


class CategoryViewSet(ModelViewSet):
    """
    ViewSet for product categories.

    Endpoints
    ---------
    GET    /api/v1/categories/          — list
    POST   /api/v1/categories/          — create
    GET    /api/v1/categories/{id}/     — retrieve
    PUT    /api/v1/categories/{id}/     — update
    PATCH  /api/v1/categories/{id}/     — partial_update
    DELETE /api/v1/categories/{id}/     — destroy
    GET    /api/v1/categories/tree/     — tree (custom)
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["parent", "is_active"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "display_order", "created_on"]
    ordering = ["display_order", "name"]

    # ── QuerySet ────────────────────────────────────────────────────

    def get_queryset(self):
        """
        Return categories for the current tenant.

        For list actions the queryset is optimised with
        ``select_related``.  The ``DjangoFilterBackend`` handles
        ``parent`` and ``is_active`` query-parameter filtering.
        """
        return Category.objects.all().select_related("parent")

    # ── Serializer selection ────────────────────────────────────────

    def get_serializer_class(self):
        """Return the appropriate serializer for the current action."""
        if self.action == "list":
            return CategoryListSerializer
        if self.action == "retrieve":
            return CategoryDetailSerializer
        if self.action in ("create", "update", "partial_update"):
            return CategoryCreateUpdateSerializer
        if self.action == "tree":
            return CategoryTreeSerializer
        return CategoryListSerializer

    # ── Custom actions ──────────────────────────────────────────────

    @action(detail=False, methods=["get"], url_path="tree")
    def tree(self, request):
        """
        Return the complete category tree (or a subtree).

        Query params:
            active_only (bool): ``true`` (default) to include only
                active categories.
            root_id (uuid, optional): Return only the subtree rooted
                at this category.
        """
        active_only = (
            request.query_params.get("active_only", "true").lower()
            in ("true", "1", "yes")
        )
        root_id = request.query_params.get("root_id")
        if root_id:
            try:
                root_node = Category.objects.get(pk=root_id)
            except Category.DoesNotExist:
                return Response(
                    {"detail": "Root category not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            serializer = CategoryTreeSerializer(root_node)
            return Response(serializer.data)
        root_qs = Category.objects.get_tree(active_only=active_only)
        serializer = CategoryTreeSerializer(root_qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="move")
    def move(self, request, pk=None):
        """
        Move category to a new parent or position.

        Body:
            target (uuid|null): Target parent ID (null → make root).
            position (str): ``'first-child'``, ``'last-child'``,
                ``'left'``, ``'right'``. Default ``'last-child'``.
        """
        category = self.get_object()
        target_id = request.data.get("target")
        position = request.data.get("position", "last-child")

        if position not in ("first-child", "last-child", "left", "right"):
            return Response(
                {"detail": "Invalid position."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        target = None
        if target_id is not None:
            try:
                target = Category.objects.get(pk=target_id)
            except Category.DoesNotExist:
                return Response(
                    {"detail": "Target category not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        try:
            Category.objects.move_node(category, target, position=position)
        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = CategoryDetailSerializer(category)
        return Response(serializer.data)


class BrandViewSet(ModelViewSet):
    """
    ViewSet for product brands.

    Endpoints
    ---------
    GET    /api/v1/brands/          — list
    POST   /api/v1/brands/          — create
    GET    /api/v1/brands/{id}/     — retrieve
    PUT    /api/v1/brands/{id}/     — update
    PATCH  /api/v1/brands/{id}/     — partial_update
    DELETE /api/v1/brands/{id}/     — destroy
    """

    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["is_active"]
    search_fields = ["name"]


class TaxClassViewSet(ModelViewSet):
    """
    ViewSet for tax classes.

    Endpoints
    ---------
    GET    /api/v1/tax-classes/          — list
    POST   /api/v1/tax-classes/          — create
    GET    /api/v1/tax-classes/{id}/     — retrieve
    PUT    /api/v1/tax-classes/{id}/     — update
    PATCH  /api/v1/tax-classes/{id}/     — partial_update
    DELETE /api/v1/tax-classes/{id}/     — destroy
    """

    queryset = TaxClass.objects.all()
    serializer_class = TaxClassSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_default"]


class ProductViewSet(ModelViewSet):
    """
    ViewSet for products.

    Endpoints
    ---------
    GET    /api/v1/products/              — list
    POST   /api/v1/products/              — create
    GET    /api/v1/products/{id}/         — retrieve
    PUT    /api/v1/products/{id}/         — update
    PATCH  /api/v1/products/{id}/         — partial_update
    DELETE /api/v1/products/{id}/         — destroy
    GET    /api/v1/products/published/    — published (custom)
    GET    /api/v1/products/featured/     — featured (custom)
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["name", "sku", "barcode", "description"]
    ordering_fields = ["name", "created_on", "updated_on", "selling_price"]
    ordering = ["-created_on"]

    def get_queryset(self):
        """Return products with related objects pre-fetched."""
        return Product.objects.select_related(
            "category", "brand", "tax_class", "unit_of_measure"
        )

    def get_serializer_class(self):
        """Return the appropriate serializer for the current action."""
        if self.action == "list":
            return ProductListSerializer
        if self.action == "retrieve":
            return ProductDetailSerializer
        return ProductCreateSerializer

    @action(detail=False, methods=["get"], url_path="published")
    def published(self, request):
        """Return published products (active + webstore visible)."""
        queryset = self.get_queryset().published()
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ProductListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="featured")
    def featured(self, request):
        """Return featured active products."""
        queryset = self.get_queryset().active().featured()
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ProductListSerializer(queryset, many=True)
        return Response(serializer.data)


# ════════════════════════════════════════════════════════════════════════
# Variant Option Type ViewSet
# ════════════════════════════════════════════════════════════════════════


class VariantOptionTypeViewSet(ModelViewSet):
    """
    Full CRUD ViewSet for VariantOptionType.

    Supports filtering by ``is_active``, ``is_color_swatch``,
    ``is_image_swatch``, and full-text search on ``name``.
    """

    serializer_class = VariantOptionTypeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["is_active", "is_color_swatch", "is_image_swatch"]
    search_fields = ["name"]
    ordering_fields = ["name", "display_order", "created_on"]
    ordering = ["display_order", "name"]

    def get_queryset(self):
        return (
            VariantOptionType.objects.all()
            .prefetch_related("values")
            .order_by("display_order", "name")
        )


# ════════════════════════════════════════════════════════════════════════
# Variant Option Value ViewSet
# ════════════════════════════════════════════════════════════════════════


class VariantOptionValueViewSet(ModelViewSet):
    """
    Full CRUD ViewSet for VariantOptionValue.

    Supports filtering by ``option_type`` and ``is_active``.
    Custom action ``by_type`` returns values for a given
    option type slug.
    """

    serializer_class = VariantOptionValueSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["option_type", "is_active"]
    search_fields = ["value", "label"]
    ordering_fields = ["value", "display_order", "created_on"]
    ordering = ["display_order", "value"]

    def get_queryset(self):
        return (
            VariantOptionValue.objects.all()
            .select_related("option_type")
            .order_by("display_order", "value")
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="by-type/(?P<slug>[\\w-]+)",
    )
    def by_type(self, request, slug=None):
        """Return option values filtered by option type slug."""
        queryset = self.get_queryset().filter(
            option_type__slug=slug,
            is_active=True,
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# ════════════════════════════════════════════════════════════════════════
# Product Variant ViewSet
# ════════════════════════════════════════════════════════════════════════


class ProductVariantViewSet(ModelViewSet):
    """
    Full CRUD ViewSet for ProductVariant.

    Uses separate serializers for list, detail, and create.

    Custom actions:
        ``by_options``: Lookup a variant by exact option values.
        ``generate_variants``: Bulk-generate all combinations.
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["product", "is_active"]
    search_fields = ["sku", "name", "barcode"]
    ordering_fields = ["sku", "name", "sort_order", "created_on"]
    ordering = ["sort_order", "name"]

    def get_queryset(self):
        return (
            ProductVariant.objects.all()
            .select_related("product")
            .prefetch_related(
                "variant_options__option_value__option_type",
            )
            .order_by("sort_order", "name")
        )

    def get_serializer_class(self):
        if self.action == "list":
            return ProductVariantListSerializer
        if self.action == "retrieve":
            return ProductVariantDetailSerializer
        if self.action in ("create", "update", "partial_update"):
            return ProductVariantCreateSerializer
        if self.action == "generate_variants":
            return BulkVariantCreateSerializer
        return ProductVariantDetailSerializer

    @action(detail=False, methods=["get"], url_path="by-options")
    def by_options(self, request):
        """
        Look up a variant by exact option value combination.

        Query params:
            product_id: UUID of the product.
            option_values: Comma-separated VariantOptionValue UUIDs.

        Returns 200 with variant or 404 if no match.
        """
        product_id = request.query_params.get("product_id")
        option_value_ids = request.query_params.get("option_values", "")

        if not product_id or not option_value_ids:
            return Response(
                {"detail": "product_id and option_values are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        option_values = VariantOptionValue.objects.filter(
            pk__in=option_value_ids.split(","),
        )
        variant = ProductVariant.objects.get_by_options(
            product_id, list(option_values)
        )

        if not variant:
            return Response(
                {"detail": "No variant matches the given options."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProductVariantDetailSerializer(variant)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="generate")
    def generate_variants(self, request):
        """
        Bulk-generate variants for a VARIABLE product.

        Reads the product's configured option types and their
        values, then generates all missing combinations via
        ``VariantGenerator``.
        """
        serializer = BulkVariantCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from apps.products.models import Product
        from apps.products.services import VariantGenerator

        product = Product.objects.get(
            pk=serializer.validated_data["product_id"]
        )
        generator = VariantGenerator(product)
        variants = generator.generate_variants()

        result = ProductVariantListSerializer(variants, many=True)
        return Response(result.data, status=status.HTTP_201_CREATED)


# ════════════════════════════════════════════════════════════════════════
# Product Option Config ViewSet
# ════════════════════════════════════════════════════════════════════════


class ProductOptionConfigViewSet(ModelViewSet):
    """
    Full CRUD ViewSet for ProductOptionConfig.

    Manages which option types are associated with a product.
    """

    serializer_class = ProductOptionConfigSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["product", "option_type", "is_active"]
    ordering_fields = ["display_order", "created_on"]
    ordering = ["display_order"]

    def get_queryset(self):
        return (
            ProductOptionConfig.objects.all()
            .select_related("product", "option_type")
            .order_by("display_order")
        )


# ════════════════════════════════════════════════════════════════════════
# Bundle ViewSets (SP05)
# ════════════════════════════════════════════════════════════════════════


class ProductBundleViewSet(ModelViewSet):
    """
    Full CRUD ViewSet for ProductBundle.

    Supports listing, creating, retrieving, updating, and deleting
    product bundles. Retrieve action returns detailed info with items.
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["product", "bundle_type", "discount_type", "is_active"]
    search_fields = ["product__name"]
    ordering_fields = ["created_on", "bundle_type"]
    ordering = ["-created_on"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BundleDetailSerializer
        return ProductBundleSerializer

    def get_queryset(self):
        qs = ProductBundle.objects.select_related("product").order_by("-created_on")
        if self.action == "retrieve":
            qs = qs.prefetch_related("items", "items__product", "items__variant")
        return qs

    @action(detail=True, methods=["get"])
    def availability(self, request, pk=None):
        """Check bundle stock availability."""
        from apps.products.services import BundleStockService

        bundle = self.get_object()
        service = BundleStockService(bundle)
        return Response({
            "available_stock": service.get_available_stock(),
            "is_available": service.check_availability(),
            "limiting_item": str(service.get_limiting_item()) if service.get_limiting_item() else None,
        })

    @action(detail=True, methods=["get"])
    def pricing(self, request, pk=None):
        """Get bundle pricing breakdown."""
        from apps.products.services import BundlePricingService

        bundle = self.get_object()
        service = BundlePricingService(bundle)
        return Response({
            "bundle_price": str(service.get_bundle_price()),
            "individual_total": str(service.get_individual_total()),
            "savings": str(service.get_savings()),
        })


class BundleItemViewSet(ModelViewSet):
    """Full CRUD ViewSet for BundleItem."""

    serializer_class = BundleItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["bundle", "product", "is_optional", "is_active"]
    ordering_fields = ["sort_order", "created_on"]
    ordering = ["sort_order"]

    def get_queryset(self):
        return (
            BundleItem.objects.all()
            .select_related("bundle", "product", "variant")
            .order_by("sort_order")
        )


# ════════════════════════════════════════════════════════════════════════
# BOM ViewSets (SP05)
# ════════════════════════════════════════════════════════════════════════


class BillOfMaterialsViewSet(ModelViewSet):
    """
    Full CRUD ViewSet for BillOfMaterials.

    Supports listing, creating, retrieving, updating and deleting BOMs.
    Retrieve action returns detailed info with items.
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["product", "is_active", "version"]
    search_fields = ["product__name", "version", "notes"]
    ordering_fields = ["created_on", "version"]
    ordering = ["-created_on"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BOMDetailSerializer
        return BillOfMaterialsSerializer

    def get_queryset(self):
        qs = BillOfMaterials.objects.select_related("product").order_by("-created_on")
        if self.action == "retrieve":
            qs = qs.prefetch_related(
                "items", "items__raw_material", "items__substitute", "items__unit"
            )
        return qs

    @action(detail=True, methods=["get"])
    def cost_breakdown(self, request, pk=None):
        """Get manufacturing cost breakdown."""
        from apps.products.services import CostCalculationService

        bom = self.get_object()
        service = CostCalculationService(bom)
        return Response({
            "material_cost": str(service.calculate_material_cost()),
            "material_cost_with_wastage": str(service.calculate_with_wastage()),
            "labor_cost": str(service.calculate_labor_cost()),
            "overhead_cost": str(service.calculate_overhead()),
            "total_cost": str(service.calculate_total_cost()),
            "unit_cost": str(service.calculate_unit_cost()),
            "suggested_price": service.suggest_selling_price(),
        })

    @action(detail=True, methods=["get"])
    def stock_check(self, request, pk=None):
        """Check raw material availability for production."""
        from apps.products.services import ManufacturingStockService

        bom = self.get_object()
        service = ManufacturingStockService(bom)
        materials = service.check_raw_materials()
        producible = service.get_producible_quantity()
        return Response({
            "producible_quantity": producible,
            "materials": [
                {
                    "raw_material": str(m["item"].raw_material),
                    "required": str(m["required"]),
                    "available": str(m["available"]),
                    "sufficient": m["sufficient"],
                    "substitute_available": m["substitute_available"],
                }
                for m in materials
            ],
        })


class BOMItemViewSet(ModelViewSet):
    """Full CRUD ViewSet for BOMItem."""

    serializer_class = BOMItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["bom", "raw_material", "is_critical", "is_active"]
    ordering_fields = ["sort_order", "created_on"]
    ordering = ["sort_order"]

    def get_queryset(self):
        return (
            BOMItem.objects.all()
            .select_related("bom", "raw_material", "substitute", "unit")
            .order_by("sort_order")
        )
