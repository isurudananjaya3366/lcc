"""
Category URL routing for the products API.

Uses DRF DefaultRouter to auto-generate RESTful endpoints.

Endpoints:
    GET    /                  → category-list
    POST   /                  → category-list
    GET    /{id}/             → category-detail
    PUT    /{id}/             → category-detail
    PATCH  /{id}/             → category-detail
    DELETE /{id}/             → category-detail
    GET    /tree/             → category-tree
    POST   /{id}/move/        → category-move
"""

from rest_framework.routers import DefaultRouter

from apps.products.api.views import (
    BillOfMaterialsViewSet,
    BOMItemViewSet,
    BrandViewSet,
    BundleItemViewSet,
    CategoryViewSet,
    ProductBundleViewSet,
    ProductOptionConfigViewSet,
    ProductVariantViewSet,
    ProductViewSet,
    TaxClassViewSet,
    VariantOptionTypeViewSet,
    VariantOptionValueViewSet,
)
from apps.products.media.views import ProductImageViewSet, VariantImageViewSet

app_name = "products"

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"brands", BrandViewSet, basename="brand")
router.register(r"tax-classes", TaxClassViewSet, basename="taxclass")
router.register(r"products", ProductViewSet, basename="product")
router.register(
    r"variant-option-types",
    VariantOptionTypeViewSet,
    basename="variant-option-type",
)
router.register(
    r"variant-option-values",
    VariantOptionValueViewSet,
    basename="variant-option-value",
)
router.register(
    r"product-variants",
    ProductVariantViewSet,
    basename="product-variant",
)
router.register(
    r"product-option-configs",
    ProductOptionConfigViewSet,
    basename="product-option-config",
)
router.register(r"bundles", ProductBundleViewSet, basename="bundle")
router.register(r"bundle-items", BundleItemViewSet, basename="bundle-item")
router.register(r"bom", BillOfMaterialsViewSet, basename="bom")
router.register(r"bom-items", BOMItemViewSet, basename="bom-item")
router.register(r"product-images", ProductImageViewSet, basename="product-image")
router.register(r"variant-images", VariantImageViewSet, basename="variant-image")

urlpatterns = router.urls
