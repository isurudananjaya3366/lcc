"""Designation business-logic service.

Centralises create/update, status transitions, salary validation,
and search for the Designation model.
"""

import logging
from decimal import Decimal

from django.db import transaction

from apps.organization.constants import (
    DESIGNATION_STATUS_ACTIVE,
    DESIGNATION_STATUS_ARCHIVED,
    DESIGNATION_STATUS_INACTIVE,
)

logger = logging.getLogger(__name__)


class DesignationService:
    """Service layer for Designation CRUD and business rules."""

    @classmethod
    @transaction.atomic
    def create(cls, data: dict):
        """Create a new designation.

        Auto-generates a code from the title if none is provided.
        """
        from apps.organization.models import Designation
        from apps.organization.services.code_generator import DesignationCodeGenerator

        if not data.get("code"):
            data["code"] = DesignationCodeGenerator.generate_code(data["title"])
        else:
            data["code"] = data["code"].upper()

        desig = Designation(**data)
        desig.full_clean()
        desig.save()
        logger.info("Designation created: %s (%s)", desig.title, desig.code)
        return desig

    @classmethod
    @transaction.atomic
    def update(cls, designation, data: dict):
        """Update an existing designation."""
        if "code" in data and data["code"]:
            data["code"] = data["code"].upper()

        for attr, value in data.items():
            setattr(designation, attr, value)

        designation.full_clean()
        designation.save()
        logger.info(
            "Designation updated: %s (%s)", designation.title, designation.code
        )
        return designation

    @classmethod
    @transaction.atomic
    def deactivate(cls, designation):
        """Deactivate a designation."""
        if designation.status == DESIGNATION_STATUS_INACTIVE:
            return designation

        designation.status = DESIGNATION_STATUS_INACTIVE
        designation.save(update_fields=["status", "updated_on"])
        logger.info("Designation deactivated: %s", designation.code)
        return designation

    @classmethod
    @transaction.atomic
    def activate(cls, designation):
        """Re-activate a designation."""
        if designation.status == DESIGNATION_STATUS_ACTIVE:
            return designation

        designation.status = DESIGNATION_STATUS_ACTIVE
        designation.save(update_fields=["status", "updated_on"])
        logger.info("Designation activated: %s", designation.code)
        return designation

    @classmethod
    def validate_salary(cls, designation, salary: Decimal) -> dict:
        """Check whether a salary falls within the designation's range.

        Returns a dict with ``valid``, ``min_salary``, ``max_salary``,
        and an optional ``message``.
        """
        result = {
            "valid": True,
            "min_salary": str(designation.min_salary) if designation.min_salary else None,
            "max_salary": str(designation.max_salary) if designation.max_salary else None,
            "message": "",
        }

        if designation.min_salary is not None and salary < designation.min_salary:
            result["valid"] = False
            result["message"] = (
                f"Salary {salary} is below the minimum "
                f"{designation.min_salary} for {designation.title}."
            )
        elif designation.max_salary is not None and salary > designation.max_salary:
            result["valid"] = False
            result["message"] = (
                f"Salary {salary} exceeds the maximum "
                f"{designation.max_salary} for {designation.title}."
            )

        return result

    @classmethod
    def search(cls, query: str, status=None, level=None, department_id=None):
        """Search designations with optional filters.

        Args:
            query: Free-text search on title, code, description.
            status: Filter by status value.
            level: Filter by level value.
            department_id: Restrict to a specific department.
        """
        from django.db.models import Q

        from apps.organization.models import Designation

        qs = Designation.objects.filter(is_deleted=False)

        if status:
            qs = qs.filter(status=status)
        if level:
            qs = qs.filter(level=level)
        if department_id:
            qs = qs.filter(department_id=department_id)

        if query:
            qs = qs.filter(
                Q(title__icontains=query)
                | Q(code__icontains=query)
                | Q(description__icontains=query)
            )

        return qs.order_by("title")

    @classmethod
    def get_employees(cls, designation):
        """Return active employees with this designation."""
        return designation.employees.filter(is_deleted=False)

    @classmethod
    def get_by_level(cls, level):
        """Return all active designations at a given level."""
        from apps.organization.models import Designation

        return Designation.objects.filter(
            level=level, is_deleted=False, status=DESIGNATION_STATUS_ACTIVE,
        )
