"""Employee Management API URL routing.

Registers all employee ViewSets with DRF DefaultRouter.
"""

from rest_framework.routers import DefaultRouter

from apps.employees.views.document_viewset import DocumentViewSet
from apps.employees.views.employee_viewset import EmployeeViewSet

app_name = "employees"

router = DefaultRouter()
router.register(r"employees", EmployeeViewSet, basename="employee")
router.register(r"employee-documents", DocumentViewSet, basename="employee-document")

urlpatterns = router.urls
