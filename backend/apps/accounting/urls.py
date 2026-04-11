"""
Accounting URL configuration.

Uses DRF DefaultRouter for Account CRUD + custom actions,
JournalEntry CRUD + workflow actions, and Reconciliation endpoints.
"""

from rest_framework.routers import DefaultRouter

from apps.accounting.views import (
    AccountViewSet,
    BankAccountViewSet,
    JournalEntryViewSet,
    MatchingRuleViewSet,
    ReconciliationViewSet,
)

app_name = "accounting"

router = DefaultRouter()
router.register(r"accounts", AccountViewSet, basename="account")
router.register(r"entries", JournalEntryViewSet, basename="journal-entry")
router.register(r"bank-accounts", BankAccountViewSet, basename="bank-account")
router.register(r"reconciliations", ReconciliationViewSet, basename="reconciliation")
router.register(r"matching-rules", MatchingRuleViewSet, basename="matching-rule")

urlpatterns = router.urls
