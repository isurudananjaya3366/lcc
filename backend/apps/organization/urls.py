"""Organization API URL routing.

Registers Department / Designation ViewSets and the org-chart view.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.organization.views import (
    DepartmentViewSet,
    DesignationViewSet,
    OrgChartView,
)

app_name = "organization"

router = DefaultRouter()
router.register(r"departments", DepartmentViewSet, basename="department")
router.register(r"designations", DesignationViewSet, basename="designation")

urlpatterns = [
    path("org-chart/", OrgChartView.as_view(), name="org-chart"),
] + router.urls
