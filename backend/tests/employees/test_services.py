"""Tests for employees services."""

import pytest
from datetime import date

pytestmark = pytest.mark.django_db


class TestEmployeeService:
    """Tests for the EmployeeService class."""

    def test_create_employee(self, tenant_context):
        from apps.employees.services.employee_service import EmployeeService
        employee = EmployeeService.create_employee({
            "first_name": "New",
            "last_name": "Employee",
            "nic_number": "200012345678",
            "email": "new.employee@example.com",
        })
        assert employee.pk is not None
        assert employee.employee_id.startswith("EMP-")

    def test_create_employee_duplicate_nic(self, employee):
        from apps.employees.services.employee_service import (
            EmployeeService,
            EmployeeValidationError,
        )
        with pytest.raises(EmployeeValidationError, match="NIC"):
            EmployeeService.create_employee({
                "first_name": "Duplicate",
                "last_name": "NIC",
                "nic_number": employee.nic_number,
            })

    def test_create_employee_duplicate_email(self, employee):
        from apps.employees.services.employee_service import (
            EmployeeService,
            EmployeeValidationError,
        )
        with pytest.raises(EmployeeValidationError, match="email"):
            EmployeeService.create_employee({
                "first_name": "Duplicate",
                "last_name": "Email",
                "nic_number": "200098765432",
                "email": employee.email,
            })

    def test_update_employee(self, employee):
        from apps.employees.services.employee_service import EmployeeService
        updated = EmployeeService.update_employee(
            employee.employee_id,
            {"first_name": "Updated"},
        )
        assert updated.first_name == "Updated"

    def test_update_employee_not_found(self, tenant_context):
        from apps.employees.services.employee_service import (
            EmployeeService,
            EmployeeNotFoundError,
        )
        with pytest.raises(EmployeeNotFoundError):
            EmployeeService.update_employee("EMP-9999", {"first_name": "Test"})

    def test_activate_employee(self, employee):
        from apps.employees.services.employee_service import EmployeeService
        employee.status = "inactive"
        employee.save(update_fields=["status"])
        activated = EmployeeService.activate(employee.employee_id)
        assert activated.status == "active"

    def test_deactivate_employee(self, employee):
        from apps.employees.services.employee_service import EmployeeService
        deactivated = EmployeeService.deactivate(
            employee.employee_id, reason="Leave of absence"
        )
        assert deactivated.status == "inactive"

    def test_terminate_employee(self, employee):
        from apps.employees.services.employee_service import EmployeeService
        terminated = EmployeeService.terminate(
            employee.employee_id,
            termination_date=date(2025, 6, 30),
            reason="End of contract",
        )
        assert terminated.status == "terminated"
        assert terminated.termination_date == date(2025, 6, 30)
        assert terminated.termination_reason == "End of contract"

    def test_resign_employee(self, employee):
        from apps.employees.services.employee_service import EmployeeService
        resigned = EmployeeService.resign(
            employee.employee_id,
            resignation_date=date(2025, 7, 15),
            reason="Personal reasons",
            notice_period=30,
        )
        assert resigned.status == "resigned"
        assert resigned.resignation_date == date(2025, 7, 15)
        assert resigned.notice_period == 30

    def test_link_user_account(self, employee, user):
        from apps.employees.services.employee_service import EmployeeService
        linked = EmployeeService.link_user_account(
            employee.employee_id, user
        )
        assert linked.user == user

    def test_unlink_user_account(self, employee, user):
        from apps.employees.services.employee_service import EmployeeService
        employee.user = user
        employee.save(update_fields=["user"])
        unlinked = EmployeeService.unlink_user_account(employee.employee_id)
        assert unlinked.user is None

    def test_link_already_linked_user(self, employee, second_employee, user):
        from apps.employees.services.employee_service import (
            EmployeeService,
            EmployeeValidationError,
        )
        employee.user = user
        employee.save(update_fields=["user"])
        with pytest.raises(EmployeeValidationError, match="already linked"):
            EmployeeService.link_user_account(
                second_employee.employee_id, user
            )


class TestEmployeeSearchService:
    """Tests for the EmployeeSearchService class."""

    def test_search_by_name(self, employee):
        from apps.employees.models import Employee
        from apps.employees.services.search_service import EmployeeSearchService
        qs = Employee.objects.all()
        results = EmployeeSearchService.search(qs, "John")
        assert results.count() >= 1

    def test_search_by_employee_id(self, employee):
        from apps.employees.models import Employee
        from apps.employees.services.search_service import EmployeeSearchService
        qs = Employee.objects.all()
        results = EmployeeSearchService.search(qs, employee.employee_id)
        assert results.count() == 1

    def test_filter_by_status(self, employee):
        from apps.employees.models import Employee
        from apps.employees.services.search_service import EmployeeSearchService
        qs = Employee.objects.all()
        results = EmployeeSearchService.filter_by_status(qs, "active")
        assert results.count() >= 1

    def test_filter_active(self, employee):
        from apps.employees.models import Employee
        from apps.employees.services.search_service import EmployeeSearchService
        results = EmployeeSearchService.filter_active(Employee.objects.all())
        assert results.count() >= 1

    def test_search_empty_query(self, employee):
        from apps.employees.models import Employee
        from apps.employees.services.search_service import EmployeeSearchService
        qs = Employee.objects.all()
        results = EmployeeSearchService.search(qs, "")
        assert results.count() == qs.count()


class TestEmployeeExportService:
    """Tests for the EmployeeExportService class."""

    def test_export_to_csv(self, employee):
        from apps.employees.services.export_service import EmployeeExportService
        output = EmployeeExportService.export_to_csv()
        content = output.read()
        assert "employee_id" in content
        assert employee.first_name in content

    def test_get_employee_summary(self, employee):
        from apps.employees.services.export_service import EmployeeExportService
        summary = EmployeeExportService.get_employee_summary()
        assert summary["total"] >= 1
        assert "by_status" in summary
        assert "by_employment_type" in summary


class TestNICValidator:
    """Tests for NIC validation."""

    def test_valid_old_nic_with_v(self):
        from apps.employees.validators.nic_validator import validate_nic
        validate_nic("912345678V")  # Should not raise

    def test_valid_old_nic_with_x(self):
        from apps.employees.validators.nic_validator import validate_nic
        validate_nic("852341234X")  # Should not raise

    def test_valid_new_nic(self):
        from apps.employees.validators.nic_validator import validate_nic
        validate_nic("199123456789")  # Should not raise

    def test_invalid_nic_too_short(self):
        from apps.employees.validators.nic_validator import validate_nic
        with pytest.raises(Exception):
            validate_nic("12345")

    def test_invalid_nic_wrong_format(self):
        from apps.employees.validators.nic_validator import validate_nic
        with pytest.raises(Exception):
            validate_nic("ABC123")

    def test_extract_birth_year_old_nic(self):
        from apps.employees.validators.nic_validator import extract_birth_year_from_nic
        assert extract_birth_year_from_nic("912345678V") == 1991

    def test_extract_birth_year_new_nic(self):
        from apps.employees.validators.nic_validator import extract_birth_year_from_nic
        assert extract_birth_year_from_nic("199123456789") == 1991

    def test_extract_gender_from_old_nic_male(self):
        from apps.employees.validators.nic_validator import extract_gender_from_nic
        # Day value < 500 = male
        assert extract_gender_from_nic("911234567V") == "male"

    def test_extract_gender_from_old_nic_female(self):
        from apps.employees.validators.nic_validator import extract_gender_from_nic
        # Day value >= 500 = female
        assert extract_gender_from_nic("915004567V") == "female"
