"""
Accounting URL configuration.

Uses DRF DefaultRouter for Account CRUD + custom actions.
"""

from rest_framework.routers import DefaultRouter

from apps.accounting.views import AccountViewSet

app_name = "accounting"

router = DefaultRouter()
router.register(r"accounts", AccountViewSet, basename="account")

urlpatterns = router.urls
