"""
Store API URL configuration.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import StoreCategoryViewSet, StoreOrderCreateView, StoreProductViewSet

app_name = "store"

router = DefaultRouter()
router.register(r"products", StoreProductViewSet, basename="store-product")
router.register(r"categories", StoreCategoryViewSet, basename="store-category")

urlpatterns = router.urls + [
    path("orders/", StoreOrderCreateView.as_view(), name="store-order-create"),
]
