"""Dashboard URL configuration."""

from rest_framework.routers import DefaultRouter

from apps.dashboard.views import DashboardViewSet

app_name = "dashboard"

router = DefaultRouter()
router.register(r"", DashboardViewSet, basename="dashboard")

urlpatterns = router.urls
