"""
Employee Service.

Business logic for creating, updating, and managing employees
through their lifecycle.
"""

import logging

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.employees.constants import (
    EMPLOYEE_STATUS_ACTIVE,
    EMPLOYEE_STATUS_INACTIVE,
    EMPLOYEE_STATUS_RESIGNED,
    EMPLOYEE_STATUS_TERMINATED,
    VALID_STATUS_TRANSITIONS,
)

logger = logging.getLogger(__name__)


# ── Custom Exceptions ──────────────────────────────────────────────────


class EmployeeNotFoundError(Exception):
    """Raised when an employee is not found."""
    pass


class EmployeeValidationError(Exception):
    """Raised when employee validation fails."""
    pass


class InvalidStatusTransitionError(Exception):
    """Raised when an invalid status transition is attempted."""
    pass


class EmployeeService:
    """Service class for employee lifecycle management."""

    # ── Status Transition Validation ──────────────────────────────────

    @classmethod
    def _validate_status_transition(cls, current_status, new_status):
        """
        Validate that a status transition is allowed.

        Raises:
            InvalidStatusTransitionError if the transition is not valid.
        """
        allowed = VALID_STATUS_TRANSITIONS.get(current_status, [])
        if new_status not in allowed:
            raise InvalidStatusTransitionError(
                f"Cannot transition from '{current_status}' to '{new_status}'. "
                f"Allowed transitions: {allowed}"
            )

    @classmethod
    def _validate_employee_data(cls, data):
        """Validate employee data before creation/update."""
        first_name = data.get("first_name", "").strip()
        last_name = data.get("last_name", "").strip()

        if not first_name:
            raise EmployeeValidationError("First name is required.")
        if not last_name:
            raise EmployeeValidationError("Last name is required.")

    @classmethod
    def _create_history_entry(cls, employee, change_type, **kwargs):
        """Create an employment history entry."""
        from apps.employees.models.employment_history import EmploymentHistory

        return EmploymentHistory.objects.create(
            employee=employee,
            effective_date=kwargs.pop("effective_date", timezone.now().date()),
            change_type=change_type,
            **kwargs,
        )

    # ── Employee Creation ─────────────────────────────────────────────

    @classmethod
    @transaction.atomic
    def create_employee(cls, data, user=None):
        """
        Create a new employee record.

        Args:
            data: dict with employee fields.
            user: User performing the action (optional).

        Returns:
            Employee instance.

        Raises:
            EmployeeValidationError: If data validation fails.
        """
        from apps.employees.models import Employee

        # Validate unique constraints
        nic_number = data.get("nic_number")
        if nic_number and Employee.objects.filter(nic_number=nic_number).exists():
            raise EmployeeValidationError(f"Employee with NIC {nic_number} already exists.")

        email = data.get("email")
        if email and Employee.objects.filter(email=email).exists():
            raise EmployeeValidationError(f"Employee with email {email} already exists.")

        employee = Employee(**data)
        employee.full_clean()
        employee.save()

        logger.info("Employee %s created by %s", employee.employee_id, user)
        return employee

    # ── Employee Update ───────────────────────────────────────────────

    @classmethod
    @transaction.atomic
    def update_employee(cls, employee_id, data, user=None):
        """
        Update an existing employee record.

        Args:
            employee_id: UUID or employee_id string.
            data: dict with fields to update.
            user: User performing the action.

        Returns:
            Updated Employee instance.
        """
        from apps.employees.models import Employee

        try:
            employee = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            raise EmployeeNotFoundError(f"Employee {employee_id} not found.")

        for field, value in data.items():
            if hasattr(employee, field):
                setattr(employee, field, value)

        employee.full_clean()
        employee.save()

        logger.info("Employee %s updated by %s", employee.employee_id, user)
        return employee

    # ── Status Changes ────────────────────────────────────────────────

    @classmethod
    @transaction.atomic
    def activate(cls, employee_id, user=None):
        """Activate an employee."""
        from apps.employees.models import Employee

        try:
            employee = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            raise EmployeeNotFoundError(f"Employee {employee_id} not found.")

        cls._validate_status_transition(employee.status, EMPLOYEE_STATUS_ACTIVE)
        employee.status = EMPLOYEE_STATUS_ACTIVE
        employee.is_active = True
        employee.save(update_fields=["status", "is_active", "updated_on"])

        logger.info("Employee %s activated by %s", employee.employee_id, user)
        return employee

    @classmethod
    @transaction.atomic
    def deactivate(cls, employee_id, reason="", user=None):
        """Deactivate an employee."""
        from apps.employees.models import Employee

        try:
            employee = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            raise EmployeeNotFoundError(f"Employee {employee_id} not found.")

        cls._validate_status_transition(employee.status, EMPLOYEE_STATUS_INACTIVE)
        employee.status = EMPLOYEE_STATUS_INACTIVE
        employee.is_active = False
        employee.save(update_fields=["status", "is_active", "updated_on"])

        logger.info("Employee %s deactivated by %s: %s", employee.employee_id, user, reason)
        return employee

    @classmethod
    @transaction.atomic
    def terminate(cls, employee_id, termination_date=None, reason="", user=None):
        """Terminate an employee."""
        from apps.employees.models import Employee

        try:
            employee = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            raise EmployeeNotFoundError(f"Employee {employee_id} not found.")

        cls._validate_status_transition(employee.status, EMPLOYEE_STATUS_TERMINATED)
        employee.status = EMPLOYEE_STATUS_TERMINATED
        employee.is_active = False
        employee.termination_date = termination_date or timezone.now().date()
        employee.termination_reason = reason
        employee.save(update_fields=[
            "status", "is_active", "termination_date", "termination_reason", "updated_on",
        ])

        logger.info("Employee %s terminated by %s", employee.employee_id, user)
        return employee

    @classmethod
    @transaction.atomic
    def resign(cls, employee_id, resignation_date=None, reason="", notice_period=None, user=None):
        """Process an employee resignation."""
        from apps.employees.models import Employee

        try:
            employee = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            raise EmployeeNotFoundError(f"Employee {employee_id} not found.")

        cls._validate_status_transition(employee.status, EMPLOYEE_STATUS_RESIGNED)
        employee.status = EMPLOYEE_STATUS_RESIGNED
        employee.is_active = False
        employee.resignation_date = resignation_date or timezone.now().date()
        employee.resignation_reason = reason
        if notice_period is not None:
            employee.notice_period = notice_period
        employee.save(update_fields=[
            "status", "is_active", "resignation_date", "resignation_reason",
            "notice_period", "updated_on",
        ])

        logger.info("Employee %s resigned, processed by %s", employee.employee_id, user)
        return employee

    # ── User Account Link ─────────────────────────────────────────────

    @classmethod
    @transaction.atomic
    def link_user_account(cls, employee_id, user_account, performed_by=None):
        """
        Link a user account to an employee record.

        Args:
            employee_id: UUID or employee_id string.
            user_account: PlatformUser instance to link.
            performed_by: User performing the action.

        Returns:
            Updated Employee instance.
        """
        from apps.employees.models import Employee

        try:
            employee = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            raise EmployeeNotFoundError(f"Employee {employee_id} not found.")

        # Check if user is already linked to another employee
        if Employee.objects.filter(user=user_account).exclude(pk=employee.pk).exists():
            raise EmployeeValidationError("This user account is already linked to another employee.")

        employee.user = user_account
        employee.save(update_fields=["user", "updated_on"])

        logger.info(
            "User %s linked to employee %s by %s",
            user_account, employee.employee_id, performed_by,
        )
        return employee

    @classmethod
    @transaction.atomic
    def unlink_user_account(cls, employee_id, performed_by=None):
        """Unlink a user account from an employee record."""
        from apps.employees.models import Employee

        try:
            employee = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            raise EmployeeNotFoundError(f"Employee {employee_id} not found.")

        employee.user = None
        employee.save(update_fields=["user", "updated_on"])

        logger.info("User unlinked from employee %s by %s", employee.employee_id, performed_by)
        return employee
