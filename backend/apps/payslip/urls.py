"""Payslip API URL routing."""

from rest_framework.routers import DefaultRouter

from apps.payslip.views.admin import AdminPayslipViewSet, PayslipBatchViewSet
from apps.payslip.views.employee import EmployeePayslipViewSet

app_name = "payslip"

router = DefaultRouter()
router.register("my", EmployeePayslipViewSet, basename="my-payslips")
router.register("admin/payslips", AdminPayslipViewSet, basename="admin-payslips")
router.register("admin/batches", PayslipBatchViewSet, basename="admin-batches")

urlpatterns = router.urls
