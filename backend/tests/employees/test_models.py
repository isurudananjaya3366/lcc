"""Tests for employees models."""

import pytest
from datetime import date
from django.core.exceptions import ValidationError

pytestmark = pytest.mark.django_db


class TestEmployeeModel:
    """Tests for the Employee model."""

    def test_create_employee(self, employee):
        assert employee.pk is not None
        assert employee.employee_id.startswith("EMP-")
        assert employee.status == "active"

    def test_employee_id_auto_generated(self, employee):
        assert employee.employee_id
        assert employee.employee_id.startswith("EMP-")

    def test_full_name_property(self, employee):
        assert employee.full_name == "John Silva"

    def test_full_name_with_middle_name(self, employee):
        employee.middle_name = "Kumar"
        employee.save(update_fields=["middle_name"])
        assert employee.full_name == "John Kumar Silva"

    def test_age_property(self, employee):
        assert employee.age is not None
        assert employee.age >= 30  # Born in 1991

    def test_is_minor_property(self, employee):
        assert employee.is_minor is False

    def test_get_display_name(self, employee):
        assert employee.get_display_name() == "John Silva"

    def test_get_display_name_with_preferred(self, employee):
        employee.preferred_name = "Johnny"
        employee.save(update_fields=["preferred_name"])
        assert employee.get_display_name() == "Johnny"

    def test_str_representation(self, employee):
        assert str(employee) == f"{employee.employee_id}: John Silva"

    def test_unique_employee_id(self, employee, second_employee):
        assert employee.employee_id != second_employee.employee_id

    def test_nic_number_validation_old_format(self, tenant_context):
        from apps.employees.models import Employee
        emp = Employee(
            first_name="Test",
            last_name="User",
            nic_number="912345678V",
        )
        emp.full_clean()  # Should not raise

    def test_nic_number_validation_new_format(self, tenant_context):
        from apps.employees.models import Employee
        emp = Employee(
            first_name="Test",
            last_name="User",
            nic_number="199123456789",
        )
        emp.full_clean()  # Should not raise

    def test_invalid_nic_number(self, tenant_context):
        from apps.employees.models import Employee
        from apps.employees.validators.nic_validator import validate_nic
        with pytest.raises(ValidationError):
            validate_nic("123")

    def test_is_active_employee_property(self, employee):
        assert employee.is_active_employee is True

    def test_is_terminated_property(self, employee):
        assert employee.is_terminated is False

    def test_is_resigned_property(self, employee):
        assert employee.is_resigned is False

    def test_dob_future_validation(self, tenant_context):
        from apps.employees.models import Employee
        from datetime import timedelta
        emp = Employee(
            first_name="Future",
            last_name="Employee",
            nic_number="200023456789",
            date_of_birth=date.today() + timedelta(days=1),
        )
        with pytest.raises(ValidationError):
            emp.full_clean()


class TestEmployeeAddressModel:
    """Tests for the EmployeeAddress model."""

    def test_create_address(self, employee_address):
        assert employee_address.pk is not None
        assert employee_address.address_type == "permanent"
        assert employee_address.is_primary is True

    def test_str_representation(self, employee_address):
        assert "Colombo" in str(employee_address)


class TestEmergencyContactModel:
    """Tests for the EmergencyContact model."""

    def test_create_contact(self, emergency_contact):
        assert emergency_contact.pk is not None
        assert emergency_contact.name == "Mary Silva"

    def test_str_representation(self, emergency_contact):
        assert emergency_contact.name in str(emergency_contact)


class TestEmployeeFamilyModel:
    """Tests for the EmployeeFamily model."""

    def test_create_family_member(self, employee):
        from apps.employees.models import EmployeeFamily
        family = EmployeeFamily.objects.create(
            employee=employee,
            name="Sam Silva",
            relationship="child",
            is_dependent=True,
        )
        assert family.pk is not None
        assert family.is_dependent is True


class TestEmployeeBankAccountModel:
    """Tests for the EmployeeBankAccount model."""

    def test_create_bank_account(self, employee_bank_account):
        assert employee_bank_account.pk is not None
        assert employee_bank_account.bank_name == "Bank of Ceylon"
        assert employee_bank_account.is_primary is True

    def test_str_representation(self, employee_bank_account):
        assert "Bank of Ceylon" in str(employee_bank_account)
        assert "Primary" in str(employee_bank_account)

    def test_primary_flag_uniqueness(self, employee):
        from apps.employees.models import EmployeeBankAccount
        first = EmployeeBankAccount.objects.create(
            employee=employee,
            bank_name="Bank A",
            account_number="111",
            is_primary=True,
        )
        second = EmployeeBankAccount.objects.create(
            employee=employee,
            bank_name="Bank B",
            account_number="222",
            is_primary=True,
        )
        first.refresh_from_db()
        assert first.is_primary is False
        assert second.is_primary is True


class TestEmployeeDocumentModel:
    """Tests for the EmployeeDocument model."""

    def test_create_document(self, employee):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from apps.employees.models import EmployeeDocument
        doc = EmployeeDocument.objects.create(
            employee=employee,
            document_type="contract",
            title="Employment Contract 2024",
            file=SimpleUploadedFile("contract.pdf", b"file content", content_type="application/pdf"),
        )
        assert doc.pk is not None
        assert doc.title == "Employment Contract 2024"

    def test_is_expired_property(self, employee):
        from datetime import timedelta
        from apps.employees.models import EmployeeDocument
        from django.core.files.uploadedfile import SimpleUploadedFile
        doc = EmployeeDocument(
            employee=employee,
            document_type="certificate",
            title="Expired Cert",
            file=SimpleUploadedFile("cert.pdf", b"content"),
            expiry_date=date.today() - timedelta(days=1),
        )
        assert doc.is_expired is True

    def test_not_expired(self, employee):
        from datetime import timedelta
        from apps.employees.models import EmployeeDocument
        from django.core.files.uploadedfile import SimpleUploadedFile
        doc = EmployeeDocument(
            employee=employee,
            document_type="certificate",
            title="Valid Cert",
            file=SimpleUploadedFile("cert.pdf", b"content"),
            expiry_date=date.today() + timedelta(days=30),
        )
        assert doc.is_expired is False


class TestEmploymentHistoryModel:
    """Tests for the EmploymentHistory model."""

    def test_create_history(self, employee):
        from apps.employees.models import EmploymentHistory
        history = EmploymentHistory.objects.create(
            employee=employee,
            effective_date=date.today(),
            change_type="promotion",
            from_department="Sales",
            to_department="Marketing",
            notes="Promoted to Marketing Manager",
        )
        assert history.pk is not None
        assert history.change_type == "promotion"
