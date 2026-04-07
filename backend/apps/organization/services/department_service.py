"""Department business-logic service.

All write operations go through this service so that validation,
code generation, and history tracking are applied consistently.
"""

import logging

from django.db import transaction

from apps.organization.constants import (
    DEPARTMENT_STATUS_ACTIVE,
    DEPARTMENT_STATUS_ARCHIVED,
    DEPARTMENT_STATUS_INACTIVE,
)

logger = logging.getLogger(__name__)


class DepartmentService:
    """Service layer for Department CRUD and hierarchy operations."""

    @classmethod
    @transaction.atomic
    def create(cls, data: dict):
        """Create a new department.

        Auto-generates a code if one is not supplied.
        """
        from apps.organization.models import Department
        from apps.organization.services.code_generator import DepartmentCodeGenerator

        if not data.get("code"):
            data["code"] = DepartmentCodeGenerator.generate_code(data["name"])
        else:
            data["code"] = data["code"].upper()

        dept = Department(**data)
        dept.full_clean()
        dept.save()
        logger.info("Department created: %s (%s)", dept.name, dept.code)
        return dept

    @classmethod
    @transaction.atomic
    def update(cls, department, data: dict):
        """Update an existing department's fields."""
        from apps.organization.services.code_generator import DepartmentCodeGenerator

        if "code" in data and data["code"]:
            data["code"] = data["code"].upper()
        elif "name" in data and not data.get("code"):
            # Regenerate code if name changed and no explicit code given
            pass  # keep existing code

        for attr, value in data.items():
            setattr(department, attr, value)

        department.full_clean()
        department.save()
        logger.info("Department updated: %s (%s)", department.name, department.code)
        return department

    @classmethod
    @transaction.atomic
    def archive(cls, department):
        """Archive a department (soft-disable, preserves data)."""
        if department.status == DEPARTMENT_STATUS_ARCHIVED:
            return department

        department.status = DEPARTMENT_STATUS_ARCHIVED
        department.save(update_fields=["status", "updated_on"])
        logger.info("Department archived: %s", department.code)
        return department

    @classmethod
    @transaction.atomic
    def activate(cls, department):
        """Re-activate a department."""
        if department.status == DEPARTMENT_STATUS_ACTIVE:
            return department

        department.status = DEPARTMENT_STATUS_ACTIVE
        department.save(update_fields=["status", "updated_on"])
        logger.info("Department activated: %s", department.code)
        return department

    @classmethod
    @transaction.atomic
    def move(cls, department, new_parent):
        """Move a department to a new parent in the MPTT tree.

        Args:
            department: The department to relocate.
            new_parent: The new parent department (or ``None`` for root).
        """
        from apps.organization.models import Department

        if new_parent and new_parent.pk == department.pk:
            raise ValueError("A department cannot be its own parent.")

        # Prevent moving a parent under one of its own descendants
        if new_parent:
            descendants = department.get_descendants()
            if new_parent in descendants:
                raise ValueError(
                    "Cannot move a department under one of its descendants."
                )

        department.parent = new_parent
        department.save()
        # MPTT tree rebuild to ensure integrity
        Department.objects.rebuild()
        logger.info(
            "Department moved: %s → parent=%s",
            department.code,
            new_parent.code if new_parent else "ROOT",
        )
        return department

    @classmethod
    @transaction.atomic
    def merge(cls, source, target):
        """Merge *source* department into *target*.

        Moves all employees and child departments from the source
        into the target, then archives the source.
        """
        from apps.organization.models import Department

        if source.pk == target.pk:
            raise ValueError("Cannot merge a department into itself.")

        # Move employees
        source.employees.filter(is_deleted=False).update(department=target)

        # Move direct children
        for child in source.get_children():
            child.parent = target
            child.save()

        Department.objects.rebuild()

        # Archive the source
        cls.archive(source)

        logger.info(
            "Department merged: %s → %s",
            source.code,
            target.code,
        )
        return target

    @classmethod
    def search(cls, query: str, status=None):
        """Search departments by name, code, or description.

        Args:
            query: Free-text search string.
            status: Optional status filter.
        """
        from django.db.models import Q

        from apps.organization.models import Department

        qs = Department.objects.filter(is_deleted=False)

        if status:
            qs = qs.filter(status=status)

        if query:
            qs = qs.filter(
                Q(name__icontains=query)
                | Q(code__icontains=query)
                | Q(description__icontains=query)
            )

        return qs.order_by("name")

    @classmethod
    def get_children(cls, department):
        """Return direct children of a department."""
        return department.get_children().filter(is_deleted=False)

    @classmethod
    def get_employees(cls, department):
        """Return active employees in a department."""
        return department.employees.filter(is_deleted=False)
