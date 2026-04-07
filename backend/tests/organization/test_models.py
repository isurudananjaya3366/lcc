"""Tests for organization models — Department, Designation, DepartmentMember, DepartmentHead."""

import pytest
from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError

pytestmark = pytest.mark.django_db


# =====================================================================
# Department Model Tests
# =====================================================================


class TestDepartmentModel:
    """Tests for the Department model."""

    def test_create_department(self, department):
        assert department.pk is not None
        assert department.name == "Engineering"
        assert department.code == "DEPT-ENG"
        assert department.status == "active"

    def test_department_str(self, department):
        assert str(department) == "Engineering"

    def test_department_code_uppercase(self, tenant_context):
        from apps.organization.models import Department

        dept = Department(name="Sales", code="dept-sal")
        dept.full_clean()
        assert dept.code == "DEPT-SAL"

    def test_department_parent_child(self, department, child_department):
        assert child_department.parent == department
        assert child_department in department.get_children()

    def test_department_is_root(self, department, child_department):
        assert department.is_root is True
        assert child_department.is_root is False

    def test_department_full_path(self, department, child_department):
        path = child_department.full_path
        assert "Engineering" in path
        assert "Backend" in path

    def test_department_ordering(self, department, second_department):
        from apps.organization.models import Department

        depts = list(
            Department.objects.filter(is_deleted=False).values_list("name", flat=True)
        )
        assert depts == sorted(depts)

    def test_department_budget_min_value(self, tenant_context):
        from apps.organization.models import Department

        dept = Department(
            name="Test", code="TST", annual_budget=Decimal("-1"),
        )
        with pytest.raises(ValidationError):
            dept.full_clean()

    def test_department_unique_code(self, department, tenant_context):
        from django.db import IntegrityError, transaction
        from apps.organization.models import Department

        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Department.objects.create(
                    name="Duplicate", code="DEPT-ENG",
                )

    def test_department_soft_delete_fields(self, department):
        assert department.is_deleted is False
        assert department.deleted_on is None


# =====================================================================
# Designation Model Tests
# =====================================================================


class TestDesignationModel:
    """Tests for the Designation model."""

    def test_create_designation(self, designation):
        assert designation.pk is not None
        assert designation.title == "Software Engineer"
        assert designation.code == "SE"
        assert designation.level == "mid"

    def test_designation_str(self, designation):
        assert str(designation) == "Software Engineer"

    def test_designation_code_uppercase(self, tenant_context):
        from apps.organization.models import Designation

        d = Designation(title="Tester", code="qa")
        d.full_clean()
        assert d.code == "QA"

    def test_designation_salary_range_valid(self, designation):
        assert designation.min_salary <= designation.max_salary

    def test_designation_salary_range_invalid(self, tenant_context):
        from apps.organization.models import Designation

        d = Designation(
            title="Test",
            code="T1",
            min_salary=Decimal("200000"),
            max_salary=Decimal("100000"),
        )
        with pytest.raises(ValidationError):
            d.full_clean()

    def test_designation_level_rank(self, designation, manager_designation):
        assert designation.level_rank < manager_designation.level_rank

    def test_designation_active_queryset(self, designation, tenant_context):
        from apps.organization.models import Designation

        Designation.objects.create(
            title="Inactive Role",
            code="IR",
            status="inactive",
        )
        active = Designation.objects.active()
        assert designation in active
        assert active.filter(status="inactive").count() == 0

    def test_designation_is_manager_flag(self, designation, manager_designation):
        assert designation.is_manager is False
        assert manager_designation.is_manager is True

    def test_designation_unique_code(self, designation, tenant_context):
        from django.db import IntegrityError, transaction
        from apps.organization.models import Designation

        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Designation.objects.create(title="Dup", code="SE")

    def test_designation_reports_to(self, designation, manager_designation):
        designation.reports_to = manager_designation
        designation.save()
        assert designation.reports_to == manager_designation
        assert designation in manager_designation.direct_reports.all()

    def test_designation_department_link(self, designation, department):
        designation.department = department
        designation.save()
        assert designation in department.designations.all()


# =====================================================================
# DepartmentMember Model Tests
# =====================================================================


class TestDepartmentMemberModel:
    """Tests for the DepartmentMember model."""

    def test_create_membership(self, employee, department):
        from apps.organization.models import DepartmentMember

        member = DepartmentMember.objects.create(
            employee=employee,
            department=department,
            joined_date=date.today(),
            is_primary=True,
        )
        assert member.pk is not None
        assert member.is_active is True

    def test_membership_ended(self, employee, department):
        from apps.organization.models import DepartmentMember

        member = DepartmentMember.objects.create(
            employee=employee,
            department=department,
            joined_date=date(2024, 1, 1),
            left_date=date(2024, 6, 1),
        )
        assert member.is_active is False

    def test_membership_str(self, employee, department):
        from apps.organization.models import DepartmentMember

        member = DepartmentMember.objects.create(
            employee=employee,
            department=department,
            joined_date=date.today(),
        )
        assert "active" in str(member)

    def test_membership_role_default(self, employee, department):
        from apps.organization.models import DepartmentMember

        member = DepartmentMember.objects.create(
            employee=employee,
            department=department,
            joined_date=date.today(),
        )
        assert member.role == "member"


# =====================================================================
# DepartmentHead Model Tests
# =====================================================================


class TestDepartmentHeadModel:
    """Tests for the DepartmentHead model."""

    def test_create_head(self, employee, department, user):
        from apps.organization.models import DepartmentHead

        head = DepartmentHead.objects.create(
            department=department,
            employee=employee,
            start_date=date.today(),
            appointed_by=user,
        )
        assert head.pk is not None
        assert head.is_current is True

    def test_head_ended(self, employee, department):
        from apps.organization.models import DepartmentHead

        head = DepartmentHead.objects.create(
            department=department,
            employee=employee,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 1),
        )
        assert head.is_current is False

    def test_acting_head(self, employee, department):
        from apps.organization.models import DepartmentHead

        head = DepartmentHead.objects.create(
            department=department,
            employee=employee,
            start_date=date.today(),
            is_acting=True,
        )
        assert head.is_acting is True
        assert "(Acting)" in str(head)

    def test_head_str(self, employee, department):
        from apps.organization.models import DepartmentHead

        head = DepartmentHead.objects.create(
            department=department,
            employee=employee,
            start_date=date.today(),
        )
        result = str(head)
        assert "present" in result
