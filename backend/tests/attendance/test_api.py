"""API endpoint tests for the Attendance module."""

import uuid
from datetime import date, time, timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from rest_framework import status

pytestmark = pytest.mark.django_db

TENANT_DOMAIN = "attendance.testserver"


# ═══════════════════════════════════════════════════════════════════════
# Shift API Tests
# ═══════════════════════════════════════════════════════════════════════


class TestShiftAPI:
    """Tests for Shift CRUD endpoints."""

    def test_list_shifts(self, api_client, shift):
        response = api_client.get("/api/v1/attendance/shifts/")
        assert response.status_code == status.HTTP_200_OK

    def test_create_shift(self, api_client):
        data = {
            "name": "API Test Shift",
            "code": f"SHF-API-{uuid.uuid4().hex[:4].upper()}",
            "shift_type": "regular",
            "start_time": "08:00:00",
            "end_time": "16:00:00",
        }
        response = api_client.post("/api/v1/attendance/shifts/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "API Test Shift"

    def test_retrieve_shift(self, api_client, shift):
        response = api_client.get(f"/api/v1/attendance/shifts/{shift.pk}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(shift.pk)

    def test_update_shift(self, api_client, shift):
        data = {"name": "Updated Shift Name"}
        response = api_client.patch(
            f"/api/v1/attendance/shifts/{shift.pk}/", data, format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Updated Shift Name"

    def test_delete_shift(self, api_client, shift):
        response = api_client.delete(f"/api/v1/attendance/shifts/{shift.pk}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_active_shifts(self, api_client, shift):
        response = api_client.get("/api/v1/attendance/shifts/active/")
        assert response.status_code == status.HTTP_200_OK

    def test_activate_shift(self, api_client, shift):
        response = api_client.post(
            f"/api/v1/attendance/shifts/{shift.pk}/activate/",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "active"

    def test_deactivate_shift(self, api_client, shift):
        response = api_client.post(
            f"/api/v1/attendance/shifts/{shift.pk}/deactivate/",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "inactive"

    def test_filter_by_shift_type(self, api_client, shift):
        response = api_client.get("/api/v1/attendance/shifts/?shift_type=regular")
        assert response.status_code == status.HTTP_200_OK

    def test_search_shifts(self, api_client, shift):
        response = api_client.get("/api/v1/attendance/shifts/?search=Regular")
        assert response.status_code == status.HTTP_200_OK


# ═══════════════════════════════════════════════════════════════════════
# Attendance Record API Tests
# ═══════════════════════════════════════════════════════════════════════


class TestAttendanceRecordAPI:
    """Tests for Attendance Record endpoints."""

    def test_list_records(self, api_client, attendance_record):
        response = api_client.get("/api/v1/attendance/records/")
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_record(self, api_client, attendance_record):
        response = api_client.get(
            f"/api/v1/attendance/records/{attendance_record.pk}/",
        )
        assert response.status_code == status.HTTP_200_OK

    def test_my_attendance(self, api_client, attendance_record):
        response = api_client.get("/api/v1/attendance/records/my-attendance/")
        assert response.status_code == status.HTTP_200_OK

    def test_today_summary(self, api_client, attendance_record):
        response = api_client.get("/api/v1/attendance/records/today/")
        assert response.status_code == status.HTTP_200_OK

    def test_filter_by_status(self, api_client, attendance_record):
        response = api_client.get("/api/v1/attendance/records/?status=present")
        assert response.status_code == status.HTTP_200_OK

    def test_filter_by_date_range(self, api_client, attendance_record):
        today = date.today().isoformat()
        response = api_client.get(
            f"/api/v1/attendance/records/?date_from={today}&date_to={today}",
        )
        assert response.status_code == status.HTTP_200_OK

    def test_filter_is_late(self, api_client, attendance_record):
        response = api_client.get("/api/v1/attendance/records/?is_late=false")
        assert response.status_code == status.HTTP_200_OK


# ═══════════════════════════════════════════════════════════════════════
# Check-In/Out API Tests
# ═══════════════════════════════════════════════════════════════════════


class TestCheckInOutAPI:
    """Tests for clock-in/clock-out endpoints."""

    def test_check_status_not_clocked_in(self, api_client, employee):
        response = api_client.get("/api/v1/attendance/check-status/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "not_clocked_in"

    def test_check_in(self, api_client, employee, shift):
        data = {"clock_in_method": "web"}
        response = api_client.post("/api/v1/attendance/check-in/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["status"] == "success"

    def test_check_in_already_clocked(self, api_client, attendance_record):
        data = {"clock_in_method": "web"}
        response = api_client.post("/api/v1/attendance/check-in/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["code"] == "ALREADY_CLOCKED_IN"

    def test_check_out(self, api_client, attendance_record):
        data = {"clock_out_method": "web"}
        response = api_client.post(
            "/api/v1/attendance/check-out/", data, format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "success"

    def test_check_out_no_clock_in(self, api_client, employee):
        data = {"clock_out_method": "web"}
        response = api_client.post(
            "/api/v1/attendance/check-out/", data, format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["code"] == "NO_CLOCK_IN_FOUND"

    def test_check_status_clocked_in(self, api_client, attendance_record):
        response = api_client.get("/api/v1/attendance/check-status/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "clocked_in"


# ═══════════════════════════════════════════════════════════════════════
# Regularization API Tests
# ═══════════════════════════════════════════════════════════════════════


class TestRegularizationAPI:
    """Tests for Regularization endpoints."""

    def test_list_regularizations(self, api_client):
        response = api_client.get("/api/v1/attendance/regularizations/")
        assert response.status_code == status.HTTP_200_OK

    def test_create_regularization(self, api_client, attendance_record, employee):
        corrected_in = (timezone.now() - timedelta(hours=1)).isoformat()
        data = {
            "attendance_record": str(attendance_record.pk),
            "employee": str(employee.pk),
            "corrected_clock_in": corrected_in,
            "reason": "I forgot to clock in on time this morning.",
        }
        response = api_client.post(
            "/api/v1/attendance/regularizations/", data, format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_pending_regularizations(self, api_client):
        response = api_client.get("/api/v1/attendance/regularizations/pending/")
        assert response.status_code == status.HTTP_200_OK

    def test_approve_regularization(self, api_client, attendance_record, employee, user):
        from apps.attendance.models import AttendanceRegularization

        reg = AttendanceRegularization.objects.create(
            attendance_record=attendance_record,
            employee=employee,
            corrected_clock_in=timezone.now() - timedelta(hours=1),
            reason="Need correction.",
        )
        response = api_client.post(
            f"/api/v1/attendance/regularizations/{reg.pk}/approve/",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "approved"

    def test_reject_regularization(self, api_client, attendance_record, employee):
        from apps.attendance.models import AttendanceRegularization

        reg = AttendanceRegularization.objects.create(
            attendance_record=attendance_record,
            employee=employee,
            corrected_clock_in=timezone.now(),
            reason="Correction.",
        )
        data = {"rejection_reason": "Not valid."}
        response = api_client.post(
            f"/api/v1/attendance/regularizations/{reg.pk}/reject/",
            data,
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "rejected"


# ═══════════════════════════════════════════════════════════════════════
# Overtime Request API Tests
# ═══════════════════════════════════════════════════════════════════════


class TestOvertimeRequestAPI:
    """Tests for OvertimeRequest endpoints."""

    def test_list_overtime_requests(self, api_client):
        response = api_client.get("/api/v1/attendance/overtime-requests/")
        assert response.status_code == status.HTTP_200_OK

    def test_create_overtime_request(self, api_client, employee):
        data = {
            "employee": str(employee.pk),
            "date": date.today().isoformat(),
            "planned_hours": "2.00",
            "reason": "Project deadline approaching, need overtime.",
        }
        response = api_client.post(
            "/api/v1/attendance/overtime-requests/", data, format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_pending_overtime_requests(self, api_client):
        response = api_client.get("/api/v1/attendance/overtime-requests/pending/")
        assert response.status_code == status.HTTP_200_OK

    def test_approve_overtime(self, api_client, employee, user):
        from apps.attendance.models import OvertimeRequest

        ot = OvertimeRequest.objects.create(
            employee=employee,
            date=date.today(),
            planned_hours=Decimal("2.00"),
            reason="Need approval.",
        )
        response = api_client.post(
            f"/api/v1/attendance/overtime-requests/{ot.pk}/approve/",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "approved"

    def test_reject_overtime(self, api_client, employee):
        from apps.attendance.models import OvertimeRequest

        ot = OvertimeRequest.objects.create(
            employee=employee,
            date=date.today(),
            planned_hours=Decimal("1.00"),
            reason="Test.",
        )
        data = {"rejection_reason": "Not needed."}
        response = api_client.post(
            f"/api/v1/attendance/overtime-requests/{ot.pk}/reject/",
            data,
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "rejected"


# ═══════════════════════════════════════════════════════════════════════
# Biometric Webhook API Tests
# ═══════════════════════════════════════════════════════════════════════


class TestBiometricWebhookAPI:
    """Tests for the Biometric Webhook endpoint."""

    def test_missing_fields(self, api_client):
        data = {"device_id": "DEV-001"}
        response = api_client.post(
            "/api/v1/attendance/webhook/biometric/", data, format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Missing required fields" in response.data["message"]

    def test_invalid_event_type(self, api_client):
        data = {
            "device_id": "DEV-001",
            "event_type": "INVALID",
            "employee_biometric_id": "BIO123",
            "timestamp": timezone.now().isoformat(),
        }
        response = api_client.post(
            "/api/v1/attendance/webhook/biometric/", data, format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid event_type" in response.data["message"]
