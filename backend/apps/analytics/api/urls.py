"""Analytics URL configuration."""

from rest_framework.routers import DefaultRouter

from apps.analytics.api.views import ReportViewSet

app_name = "analytics"

router = DefaultRouter()
router.register(r"", ReportViewSet, basename="analytics")

urlpatterns = router.urls
