"""Tests for organization services — DepartmentService, DesignationService, OrgChartService."""

import pytest
from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError

pytestmark = pytest.mark.django_db


# =====================================================================
# DepartmentService Tests
# =====================================================================


class TestDepartmentService:
    """Tests for the DepartmentService."""

    def test_create_department(self, tenant_context):
        from apps.organization.services.department_service import DepartmentService

        dept = DepartmentService.create({"name": "Marketing", "code": "MKT"})
        assert dept.pk is not None
        assert dept.code == "MKT"

    def test_create_department_auto_code(self, tenant_context):
        from apps.organization.services.department_service import DepartmentService

        dept = DepartmentService.create({"name": "Customer Support"})
        assert dept.code is not None
        assert len(dept.code) > 0

    def test_update_department(self, department):
        from apps.organization.services.department_service import DepartmentService

        result = DepartmentService.update(department, {"name": "Engineering v2"})
        assert result.name == "Engineering v2"

    def test_archive_department(self, department):
        from apps.organization.services.department_service import DepartmentService

        result = DepartmentService.archive(department)
        assert result.status == "archived"

    def test_archive_already_archived(self, department):
        from apps.organization.services.department_service import DepartmentService

        department.status = "archived"
        department.save()
        result = DepartmentService.archive(department)
        assert result.status == "archived"

    def test_activate_department(self, department):
        from apps.organization.services.department_service import DepartmentService

        department.status = "inactive"
        department.save()
        result = DepartmentService.activate(department)
        assert result.status == "active"

    def test_move_department(self, department, second_department):
        from apps.organization.services.department_service import DepartmentService

        result = DepartmentService.move(department, second_department)
        result.refresh_from_db()
        assert result.parent == second_department

    def test_move_to_root(self, child_department):
        from apps.organization.services.department_service import DepartmentService

        result = DepartmentService.move(child_department, None)
        result.refresh_from_db()
        assert result.parent is None

    def test_move_to_self_raises(self, department):
        from apps.organization.services.department_service import DepartmentService

        with pytest.raises(ValueError, match="own parent"):
            DepartmentService.move(department, department)

    def test_move_to_descendant_raises(self, department, child_department):
        from apps.organization.services.department_service import DepartmentService

        with pytest.raises(ValueError, match="descendants"):
            DepartmentService.move(department, child_department)

    def test_merge_departments(self, department, second_department, employee):
        from apps.organization.services.department_service import DepartmentService

        employee.department = department
        employee.save()
        result = DepartmentService.merge(department, second_department)
        employee.refresh_from_db()
        assert employee.department == second_department

    def test_merge_self_raises(self, department):
        from apps.organization.services.department_service import DepartmentService

        with pytest.raises(ValueError, match="itself"):
            DepartmentService.merge(department, department)

    def test_search_departments(self, department, second_department):
        from apps.organization.services.department_service import DepartmentService

        results = DepartmentService.search("Engineering")
        assert department in results
        assert second_department not in results

    def test_search_by_status(self, department, second_department):
        from apps.organization.services.department_service import DepartmentService

        department.status = "inactive"
        department.save()
        results = DepartmentService.search("", status="inactive")
        assert department in results


# =====================================================================
# DesignationService Tests
# =====================================================================


class TestDesignationService:
    """Tests for the DesignationService."""

    def test_create_designation(self, tenant_context):
        from apps.organization.services.designation_service import DesignationService

        desig = DesignationService.create({
            "title": "Product Manager",
            "code": "PM",
            "level": "manager",
        })
        assert desig.pk is not None
        assert desig.code == "PM"

    def test_create_designation_auto_code(self, tenant_context):
        from apps.organization.services.designation_service import DesignationService

        desig = DesignationService.create({
            "title": "Data Scientist",
            "level": "mid",
        })
        assert desig.code is not None
        assert len(desig.code) > 0

    def test_update_designation(self, designation):
        from apps.organization.services.designation_service import DesignationService

        result = DesignationService.update(designation, {"title": "Senior SE"})
        assert result.title == "Senior SE"

    def test_deactivate_designation(self, designation):
        from apps.organization.services.designation_service import DesignationService

        result = DesignationService.deactivate(designation)
        assert result.status == "inactive"

    def test_activate_designation(self, designation):
        from apps.organization.services.designation_service import DesignationService

        designation.status = "inactive"
        designation.save()
        result = DesignationService.activate(designation)
        assert result.status == "active"

    def test_validate_salary_in_range(self, designation):
        from apps.organization.services.designation_service import DesignationService

        result = DesignationService.validate_salary(designation, Decimal("75000"))
        assert result["valid"] is True

    def test_validate_salary_below_min(self, designation):
        from apps.organization.services.designation_service import DesignationService

        result = DesignationService.validate_salary(designation, Decimal("10000"))
        assert result["valid"] is False
        assert "below" in result["message"]

    def test_validate_salary_above_max(self, designation):
        from apps.organization.services.designation_service import DesignationService

        result = DesignationService.validate_salary(designation, Decimal("200000"))
        assert result["valid"] is False
        assert "exceeds" in result["message"]

    def test_search_designations(self, designation, manager_designation):
        from apps.organization.services.designation_service import DesignationService

        results = DesignationService.search("Software")
        assert designation in results
        assert manager_designation not in results

    def test_search_by_level(self, designation, manager_designation):
        from apps.organization.services.designation_service import DesignationService

        results = DesignationService.search("", level="manager")
        assert manager_designation in results
        assert designation not in results


# =====================================================================
# OrgChartService Tests
# =====================================================================


class TestOrgChartService:
    """Tests for the OrgChartService."""

    def test_get_department_tree(self, department, child_department):
        from apps.organization.services.orgchart_service import OrgChartService

        tree = OrgChartService.get_department_tree()
        assert len(tree) >= 1
        # Root department should be in top-level
        root_names = [n["name"] for n in tree]
        assert "Engineering" in root_names

    def test_get_department_tree_with_root(self, department, child_department):
        from apps.organization.services.orgchart_service import OrgChartService

        tree = OrgChartService.get_department_tree(root_id=department.pk)
        assert len(tree) == 1
        assert tree[0]["name"] == "Engineering"
        assert len(tree[0]["children"]) >= 1

    def test_get_employee_tree(self, employee, second_employee):
        from apps.organization.services.orgchart_service import OrgChartService

        second_employee.manager = employee
        second_employee.save()
        tree = OrgChartService.get_employee_tree()
        # employee has no manager, so should be root
        root_names = [n["name"] for n in tree]
        assert employee.full_name in root_names

    def test_generate_orgchart_json_department(self, department):
        from apps.organization.services.orgchart_service import OrgChartService

        data = OrgChartService.generate_orgchart_json(chart_type="department")
        assert data["type"] == "department"
        assert "generated_at" in data
        assert "tree" in data

    def test_generate_orgchart_json_employee(self, employee):
        from apps.organization.services.orgchart_service import OrgChartService

        data = OrgChartService.generate_orgchart_json(chart_type="employee")
        assert data["type"] == "employee"

    def test_get_employee_count(self, department, employee):
        from apps.organization.services.orgchart_service import OrgChartService

        employee.department = department
        employee.save()
        count = OrgChartService.get_employee_count(department.pk)
        assert count >= 1

    def test_get_total_budget(self, department, child_department):
        from apps.organization.services.orgchart_service import OrgChartService

        child_department.annual_budget = Decimal("200000.00")
        child_department.save()
        total = OrgChartService.get_total_budget(department.pk)
        assert total >= Decimal("1200000.00")

    def test_get_department_stats(self, department, employee):
        from apps.organization.services.orgchart_service import OrgChartService

        employee.department = department
        employee.save()
        stats = OrgChartService.get_department_stats(department.pk)
        assert stats["total_employees"] >= 1
        assert "total_budget" in stats
        assert "avg_tenure_years" in stats

    def test_flatten_hierarchy(self, department, child_department):
        from apps.organization.services.orgchart_service import OrgChartService

        flat = OrgChartService.flatten_hierarchy()
        codes = [d["code"] for d in flat]
        assert "DEPT-ENG" in codes
        assert "DEPT-BE" in codes

    def test_get_path_to_root(self, child_department):
        from apps.organization.services.orgchart_service import OrgChartService

        result = OrgChartService.get_path_to_root(child_department.pk)
        assert "path" in result
        assert "path_string" in result
        names = [p["name"] for p in result["path"]]
        assert "Engineering" in names
        assert "Backend" in names
        assert "Engineering" in result["path_string"]

    def test_get_subtree(self, department, child_department):
        from apps.organization.services.orgchart_service import OrgChartService

        subtree = OrgChartService.get_subtree(department.pk)
        assert len(subtree) == 1
        assert subtree[0]["name"] == "Engineering"

    def test_get_reporting_chain(self, employee, second_employee):
        from apps.organization.services.orgchart_service import OrgChartService

        second_employee.manager = employee
        second_employee.save()
        chain = OrgChartService.get_reporting_chain(second_employee.pk)
        assert len(chain) >= 2
        assert chain[0]["name"] == second_employee.full_name
        assert chain[1]["name"] == employee.full_name

    def test_get_reporting_chain_no_manager(self, employee):
        from apps.organization.services.orgchart_service import OrgChartService

        chain = OrgChartService.get_reporting_chain(employee.pk)
        assert len(chain) == 1
