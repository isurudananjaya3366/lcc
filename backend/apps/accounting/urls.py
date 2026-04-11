"""
Accounting URL configuration.

Uses DRF DefaultRouter for Account CRUD + custom actions
and JournalEntry CRUD + workflow actions.
"""

from rest_framework.routers import DefaultRouter

from apps.accounting.views import AccountViewSet, JournalEntryViewSet

app_name = "accounting"

router = DefaultRouter()
router.register(r"accounts", AccountViewSet, basename="account")
router.register(r"entries", JournalEntryViewSet, basename="journal-entry")

urlpatterns = router.urls
