"""Leave Management API URL routing.

Registers all leave ViewSets with the DRF router.
"""

from rest_framework.routers import DefaultRouter

from apps.leave.views import (
    HolidayViewSet,
    LeaveBalanceViewSet,
    LeaveRequestViewSet,
    LeaveTypeViewSet,
)

app_name = "leave"

router = DefaultRouter()
router.register(r"types", LeaveTypeViewSet, basename="leave-type")
router.register(r"requests", LeaveRequestViewSet, basename="leave-request")
router.register(r"holidays", HolidayViewSet, basename="holiday")
router.register(r"balances", LeaveBalanceViewSet, basename="balance")

urlpatterns = router.urls
