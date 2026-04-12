"""Accounting views package."""

from apps.accounting.views.account import AccountViewSet
from apps.accounting.views.journal_entry import JournalEntryViewSet
from apps.accounting.views.reconciliation import (
    BankAccountViewSet,
    MatchingRuleViewSet,
    ReconciliationViewSet,
)
from apps.accounting.views.reports import ReportViewSet
from apps.accounting.views.tax import (
    EPFReturnViewSet,
    ETFReturnViewSet,
    PAYEReturnViewSet,
    TaxCalendarView,
    TaxConfigurationViewSet,
    TaxPeriodViewSet,
    TaxRemindersWidgetView,
    TaxSubmissionViewSet,
    VATReturnViewSet,
)

__all__ = [
    "AccountViewSet",
    "BankAccountViewSet",
    "EPFReturnViewSet",
    "ETFReturnViewSet",
    "JournalEntryViewSet",
    "MatchingRuleViewSet",
    "PAYEReturnViewSet",
    "ReconciliationViewSet",
    "ReportViewSet",
    "TaxCalendarView",
    "TaxConfigurationViewSet",
    "TaxPeriodViewSet",
    "TaxRemindersWidgetView",
    "TaxSubmissionViewSet",
    "VATReturnViewSet",
]
