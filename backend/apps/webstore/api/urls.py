"""
Store API URL configuration.
"""

from rest_framework.routers import DefaultRouter

from .views import StoreCategoryViewSet, StoreProductViewSet

app_name = "store"

router = DefaultRouter()
router.register(r"products", StoreProductViewSet, basename="store-product")
router.register(r"categories", StoreCategoryViewSet, basename="store-category")

urlpatterns = router.urls
