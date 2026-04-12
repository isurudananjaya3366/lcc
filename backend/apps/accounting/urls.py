"""
Accounting URL configuration.

Uses DRF DefaultRouter for Account CRUD + custom actions,
JournalEntry CRUD + workflow actions, Reconciliation endpoints,
and Tax Reporting endpoints.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.accounting.views import (
    AccountViewSet,
    BankAccountViewSet,
    EPFReturnViewSet,
    ETFReturnViewSet,
    JournalEntryViewSet,
    MatchingRuleViewSet,
    PAYEReturnViewSet,
    ReconciliationViewSet,
    ReportViewSet,
    TaxCalendarView,
    TaxConfigurationViewSet,
    TaxPeriodViewSet,
    TaxRemindersWidgetView,
    TaxSubmissionViewSet,
    VATReturnViewSet,
)

app_name = "accounting"

router = DefaultRouter()
router.register(r"accounts", AccountViewSet, basename="account")
router.register(r"entries", JournalEntryViewSet, basename="journal-entry")
router.register(r"bank-accounts", BankAccountViewSet, basename="bank-account")
router.register(r"reconciliations", ReconciliationViewSet, basename="reconciliation")
router.register(r"matching-rules", MatchingRuleViewSet, basename="matching-rule")
router.register(r"reports", ReportViewSet, basename="report")

# Tax reporting routes
router.register(r"tax/config", TaxConfigurationViewSet, basename="tax-config")
router.register(r"tax/periods", TaxPeriodViewSet, basename="tax-period")
router.register(r"tax/vat-returns", VATReturnViewSet, basename="vat-return")
router.register(r"tax/paye-returns", PAYEReturnViewSet, basename="paye-return")
router.register(r"tax/epf-returns", EPFReturnViewSet, basename="epf-return")
router.register(r"tax/etf-returns", ETFReturnViewSet, basename="etf-return")
router.register(r"tax/submissions", TaxSubmissionViewSet, basename="tax-submission")

urlpatterns = [
    path("tax/calendar/", TaxCalendarView.as_view(), name="tax-calendar"),
    path("tax/reminders/", TaxRemindersWidgetView.as_view(), name="tax-reminders-widget"),
] + router.urls
