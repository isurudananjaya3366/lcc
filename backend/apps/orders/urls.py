"""
Orders URL routing (Task 90).

Registers all order-related API endpoints:
- /orders/           — Order CRUD + status actions
- /fulfillments/     — Fulfillment workflow
- /returns/          — Return requests & processing
"""

from rest_framework.routers import DefaultRouter

from apps.orders.views import (
    FulfillmentViewSet,
    OrderViewSet,
    ReturnViewSet,
)

app_name = "orders"

router = DefaultRouter()
router.register(r"orders", OrderViewSet, basename="order")
router.register(r"fulfillments", FulfillmentViewSet, basename="fulfillment")
router.register(r"returns", ReturnViewSet, basename="return")

urlpatterns = router.urls
