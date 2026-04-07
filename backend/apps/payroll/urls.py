"""Payroll API URL routing.

Registers all payroll ViewSets with the DRF router and
standalone report endpoints.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.payroll.views.component_viewset import SalaryComponentViewSet
from apps.payroll.views.employee_salary_viewset import EmployeeSalaryViewSet
from apps.payroll.views.period_viewset import PayrollPeriodViewSet
from apps.payroll.views.run_viewset import PayrollRunViewSet
from apps.payroll.views.template_viewset import SalaryTemplateViewSet
from apps.payroll.views.report_views import (
    BankFileView,
    EPFReportView,
    ETFReportView,
    PAYEReportView,
    PayrollSummaryView,
    ReportListView,
)

app_name = "payroll"

router = DefaultRouter()
router.register(r"components", SalaryComponentViewSet, basename="salary-component")
router.register(r"templates", SalaryTemplateViewSet, basename="salary-template")
router.register(r"salaries", EmployeeSalaryViewSet, basename="employee-salary")
router.register(r"periods", PayrollPeriodViewSet, basename="payroll-period")
router.register(r"runs", PayrollRunViewSet, basename="payroll-run")

urlpatterns = router.urls + [
    path("reports/epf/", EPFReportView.as_view(), name="payroll-report-epf"),
    path("reports/etf/", ETFReportView.as_view(), name="payroll-report-etf"),
    path("reports/paye/", PAYEReportView.as_view(), name="payroll-report-paye"),
    path("reports/summary/", PayrollSummaryView.as_view(), name="payroll-report-summary"),
    path("reports/bank-file/", BankFileView.as_view(), name="payroll-bank-file"),
    path("reports/list/", ReportListView.as_view(), name="payroll-report-list"),
]
