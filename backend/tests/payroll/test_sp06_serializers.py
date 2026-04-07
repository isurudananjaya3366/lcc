"""Tests for SP06 serializers."""

import pytest
from decimal import Decimal

from apps.payroll.serializers.period_serializer import (
    PayrollPeriodListSerializer,
    PayrollPeriodSerializer,
)
from apps.payroll.serializers.run_serializer import (
    PayrollRunListSerializer,
    PayrollRunSerializer,
)
from apps.payroll.serializers.employee_payroll_serializer import (
    EmployeePayrollListSerializer,
    EmployeePayrollSerializer,
    PayrollLineItemSerializer,
)
from apps.payroll.serializers.history_serializer import PayrollHistorySerializer

pytestmark = pytest.mark.django_db


class TestPayrollPeriodSerializer:
    """Tests for PayrollPeriod serializers."""

    def test_list_serializer_fields(self, payroll_period):
        serializer = PayrollPeriodListSerializer(payroll_period)
        data = serializer.data
        assert data["name"] == "January 2024"
        assert data["period_month"] == 1
        assert data["period_year"] == 2024
        assert "status_display" in data

    def test_detail_serializer_fields(self, payroll_period):
        serializer = PayrollPeriodSerializer(payroll_period)
        data = serializer.data
        assert "notes" in data
        assert "created_on" in data
        assert "updated_on" in data


class TestPayrollRunSerializer:
    """Tests for PayrollRun serializers."""

    def test_list_serializer_fields(self, payroll_run):
        serializer = PayrollRunListSerializer(payroll_run)
        data = serializer.data
        assert data["run_number"] == 1
        assert "status_display" in data
        assert "total_employees" in data

    def test_detail_serializer_fields(self, processed_run):
        serializer = PayrollRunSerializer(processed_run)
        data = serializer.data
        assert data["total_gross"] == "108000.00"
        assert data["total_net"] == "95000.00"
        assert "errors" in data
        assert "notes" in data


class TestEmployeePayrollSerializer:
    """Tests for EmployeePayroll serializers."""

    def test_list_serializer_fields(self, employee_payroll_record):
        serializer = EmployeePayrollListSerializer(employee_payroll_record)
        data = serializer.data
        assert "gross_salary" in data
        assert "net_salary" in data
        assert "payment_status_display" in data

    def test_detail_serializer_with_line_items(self, employee_payroll_record, payroll_line_item):
        serializer = EmployeePayrollSerializer(employee_payroll_record)
        data = serializer.data
        assert len(data["line_items"]) == 1
        assert data["line_items"][0]["final_amount"] == "100000.00"

    def test_line_item_serializer(self, payroll_line_item):
        serializer = PayrollLineItemSerializer(payroll_line_item)
        data = serializer.data
        assert "component_name" in data
        assert "line_type_display" in data
        assert data["final_amount"] == "100000.00"


class TestPayrollHistorySerializer:
    """Tests for PayrollHistory serializers."""

    def test_history_serializer_fields(self, payroll_run, user, tenant_context):
        from apps.payroll.models import PayrollHistory
        from apps.payroll.constants import HistoryAction, PayrollStatus

        history = PayrollHistory.objects.create(
            payroll_run=payroll_run,
            action=HistoryAction.CREATED,
            new_status=PayrollStatus.DRAFT,
            performed_by=user,
        )
        serializer = PayrollHistorySerializer(history)
        data = serializer.data
        assert "action_display" in data
        assert "performed_by_email" in data
        assert "performed_at" in data
