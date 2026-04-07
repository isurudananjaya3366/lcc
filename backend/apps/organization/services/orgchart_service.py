"""Organization Chart Service.

Provides tree traversal, hierarchy queries, and org-chart
JSON generation for department and employee hierarchies.
"""

import logging
from decimal import Decimal

from django.db.models import Count, Q, Sum

logger = logging.getLogger(__name__)


class OrgChartService:
    """Service for org-chart tree queries and statistics."""

    # ── Department Tree ─────────────────────────────────────────────

    @classmethod
    def get_department_tree(cls, root_id=None):
        """Return the full department tree, optionally rooted at *root_id*.

        Uses MPTT ``get_descendants`` for efficient subtree retrieval.
        Returns a nested list of dictionaries.
        """
        from apps.organization.models import Department

        if root_id:
            try:
                root = Department.objects.get(pk=root_id, is_deleted=False)
            except Department.DoesNotExist:
                return []
            nodes = root.get_descendants(include_self=True).filter(is_deleted=False)
        else:
            nodes = Department.objects.filter(is_deleted=False)

        nodes = nodes.select_related("parent", "manager")

        node_map = {}
        roots = []

        for dept in nodes:
            node_map[dept.pk] = {
                "id": str(dept.pk),
                "name": dept.name,
                "code": dept.code,
                "status": dept.status,
                "manager": (
                    {
                        "id": str(dept.manager.pk),
                        "name": dept.manager.full_name,
                    }
                    if dept.manager
                    else None
                ),
                "level": dept.level,
                "employee_count": dept.employees.filter(is_deleted=False).count(),
                "children": [],
            }

        for dept in nodes:
            node = node_map[dept.pk]
            if dept.parent_id and dept.parent_id in node_map:
                node_map[dept.parent_id]["children"].append(node)
            else:
                roots.append(node)

        return roots

    # ── Employee Tree ───────────────────────────────────────────────

    @classmethod
    def get_employee_tree(cls, root_employee_id=None):
        """Build a reporting-chain tree rooted at *root_employee_id*.

        If no root is given, returns trees for all employees that
        have no manager (i.e. top-level).
        """
        from apps.employees.models import Employee

        qs = Employee.objects.filter(is_deleted=False).select_related(
            "department", "designation", "manager",
        )

        node_map = {}
        for emp in qs:
            node_map[emp.pk] = {
                "id": str(emp.pk),
                "name": emp.full_name,
                "employee_id": emp.employee_id,
                "department": emp.department.name if emp.department else None,
                "designation": emp.designation.title if emp.designation else None,
                "children": [],
            }

        roots = []
        for emp in qs:
            node = node_map[emp.pk]
            if emp.manager_id and emp.manager_id in node_map:
                node_map[emp.manager_id]["children"].append(node)
            else:
                roots.append(node)

        if root_employee_id:
            # Return only the subtree rooted at the requested employee
            target = node_map.get(root_employee_id)
            return [target] if target else []

        return roots

    # ── JSON Generation ─────────────────────────────────────────────

    @classmethod
    def generate_orgchart_json(cls, chart_type="department"):
        """High-level entry point for org-chart data.

        Args:
            chart_type: ``"department"`` or ``"employee"``.

        Returns:
            Dict with ``type``, ``generated_at``, and ``tree`` keys.
        """
        from django.utils import timezone

        if chart_type == "employee":
            tree = cls.get_employee_tree()
        else:
            tree = cls.get_department_tree()

        from apps.employees.models import Employee
        from apps.organization.models import Department

        return {
            "type": chart_type,
            "generated_at": timezone.now().isoformat(),
            "total_departments": Department.objects.filter(is_deleted=False).count(),
            "total_employees": Employee.objects.filter(is_deleted=False).count(),
            "tree": tree,
        }

    # ── Statistics ──────────────────────────────────────────────────

    @classmethod
    def get_employee_count(cls, department_id):
        """Count active (non-deleted) employees in a department and all descendants."""
        from apps.employees.models import Employee
        from apps.organization.models import Department

        dept = Department.objects.get(pk=department_id, is_deleted=False)
        descendant_ids = (
            dept.get_descendants(include_self=True)
            .filter(is_deleted=False)
            .values_list("pk", flat=True)
        )
        return Employee.objects.filter(
            department_id__in=descendant_ids, is_deleted=False,
        ).count()

    @classmethod
    def get_total_budget(cls, department_id):
        """Sum the budgets of a department and all its descendants."""
        from apps.organization.models import Department

        dept = Department.objects.get(pk=department_id, is_deleted=False)
        descendants = dept.get_descendants(include_self=True).filter(is_deleted=False)
        total = descendants.aggregate(total=Sum("annual_budget"))["total"]
        return total or Decimal("0.00")

    @classmethod
    def get_department_stats(cls, department_id):
        """Return a statistics dictionary for a department.

        Keys: total_employees, active_employees, sub_departments,
        total_descendants, total_budget, budget_per_employee,
        avg_tenure.
        """
        from datetime import date

        from django.db.models import Avg, F

        from apps.organization.models import Department

        dept = Department.objects.get(pk=department_id, is_deleted=False)
        employees = dept.employees.filter(is_deleted=False)
        total_employees = employees.count()
        active_employees = employees.filter(status="active").count()
        sub_departments = dept.get_children().filter(is_deleted=False).count()
        total_descendants = dept.get_descendant_count()
        total_budget = cls.get_total_budget(department_id)

        budget_per_employee = (
            total_budget / active_employees
            if active_employees
            else Decimal("0.00")
        )

        # Average tenure in days for active employees with hire_date
        today = date.today()
        tenured = employees.filter(hire_date__isnull=False, status="active")
        if tenured.exists():
            avg_days = tenured.aggregate(
                avg_tenure=Avg(
                    today - F("hire_date"),
                ),
            )["avg_tenure"]
            avg_tenure_years = round(avg_days.days / 365.25, 1) if avg_days else 0
        else:
            avg_tenure_years = 0

        return {
            "total_employees": total_employees,
            "active_employees": active_employees,
            "sub_departments": sub_departments,
            "total_descendants": total_descendants,
            "total_budget": str(total_budget),
            "budget_per_employee": str(budget_per_employee),
            "avg_tenure_years": avg_tenure_years,
        }

    # ── Hierarchy Utilities ─────────────────────────────────────────

    @classmethod
    def flatten_hierarchy(cls, department_id=None):
        """Return a flat list of departments with their depth level.

        Useful for dropdown or indented list rendering.
        """
        from apps.organization.models import Department

        if department_id:
            dept = Department.objects.get(pk=department_id, is_deleted=False)
            qs = dept.get_descendants(include_self=True).filter(is_deleted=False)
        else:
            qs = Department.objects.filter(is_deleted=False)

        return [
            {
                "id": str(d.pk),
                "name": d.name,
                "code": d.code,
                "level": d.level,
                "parent_id": str(d.parent_id) if d.parent_id else None,
                "indent": "  " * d.level,
                "has_children": not d.is_leaf_node(),
                "employee_count": d.employees.filter(is_deleted=False).count(),
                "manager_name": d.manager.full_name if d.manager else None,
            }
            for d in qs.select_related("manager").order_by("tree_id", "lft")
        ]

    @classmethod
    def get_path_to_root(cls, department_id):
        """Return the department path from a given node up to the root."""
        from apps.organization.models import Department

        dept = Department.objects.get(pk=department_id, is_deleted=False)
        ancestors = dept.get_ancestors(include_self=True).filter(is_deleted=False)
        path = [
            {
                "id": str(a.pk),
                "name": a.name,
                "code": a.code,
                "level": a.level,
            }
            for a in ancestors
        ]
        path_string = " > ".join(item["name"] for item in path)
        return {"path": path, "path_string": path_string}

    @classmethod
    def get_subtree(cls, department_id):
        """Return the department subtree as nested dicts (same format as ``get_department_tree``)."""
        return cls.get_department_tree(root_id=department_id)

    @classmethod
    def get_reporting_chain(cls, employee_id):
        """Walk up the manager chain from an employee to the top.

        Returns a list of dicts from the given employee up to the
        topmost manager (no manager).
        """
        from apps.employees.models import Employee

        try:
            emp = Employee.objects.select_related(
                "department", "designation",
            ).get(pk=employee_id, is_deleted=False)
        except Employee.DoesNotExist:
            return []

        chain = []
        visited = set()
        current = emp

        while current and current.pk not in visited:
            visited.add(current.pk)
            chain.append(
                {
                    "id": str(current.pk),
                    "name": current.full_name,
                    "employee_id": current.employee_id,
                    "department": (
                        current.department.name if current.department else None
                    ),
                    "designation": (
                        current.designation.title if current.designation else None
                    ),
                    "level_in_chain": len(chain),
                }
            )
            if current.manager_id:
                try:
                    current = Employee.objects.select_related(
                        "department", "designation",
                    ).get(pk=current.manager_id, is_deleted=False)
                except Employee.DoesNotExist:
                    break
            else:
                break

        return chain
