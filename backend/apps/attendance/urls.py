"""Attendance API URL routing.

Registers all attendance ViewSets and standalone views.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.attendance.views import (
    AttendanceViewSet,
    BiometricWebhookView,
    CheckInView,
    CheckOutView,
    CheckStatusView,
    OvertimeRequestViewSet,
    RegularizationViewSet,
    ShiftViewSet,
)

app_name = "attendance"

router = DefaultRouter()
router.register(r"shifts", ShiftViewSet, basename="shift")
router.register(r"records", AttendanceViewSet, basename="record")
router.register(r"regularizations", RegularizationViewSet, basename="regularization")
router.register(r"overtime-requests", OvertimeRequestViewSet, basename="overtime-request")

urlpatterns = [
    path("check-in/", CheckInView.as_view(), name="check-in"),
    path("check-out/", CheckOutView.as_view(), name="check-out"),
    path("check-status/", CheckStatusView.as_view(), name="check-status"),
    path("webhook/biometric/", BiometricWebhookView.as_view(), name="biometric-webhook"),
] + router.urls
