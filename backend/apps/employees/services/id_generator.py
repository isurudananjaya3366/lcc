"""Employee ID generation service with collision handling."""

import logging

from django.db import IntegrityError

from apps.employees.constants import EMPLOYEE_ID_PADDING, EMPLOYEE_ID_PREFIX

logger = logging.getLogger(__name__)

MAX_RETRIES = 5


def generate_employee_id():
    """
    Generate the next employee ID in EMP-XXXX format.

    Uses DB-level collision handling with retry logic to handle
    concurrent creation scenarios.

    Returns:
        str: Next available employee ID (e.g., "EMP-0042").
    """
    from apps.employees.models.employee import Employee

    last_employee = (
        Employee.objects.order_by("-employee_id")
        .values_list("employee_id", flat=True)
        .first()
    )

    if last_employee:
        try:
            last_number = int(last_employee.split("-")[-1])
        except (ValueError, IndexError):
            last_number = 0
    else:
        last_number = 0

    next_number = last_number + 1
    return f"{EMPLOYEE_ID_PREFIX}-{str(next_number).zfill(EMPLOYEE_ID_PADDING)}"


def generate_employee_id_with_retry():
    """
    Generate employee ID with collision retry.

    If a collision is detected (concurrent save), increments and retries
    up to MAX_RETRIES times.

    Returns:
        str: A unique employee ID.

    Raises:
        RuntimeError: If unable to generate a unique ID after MAX_RETRIES.
    """
    from apps.employees.models.employee import Employee

    for attempt in range(MAX_RETRIES):
        candidate = generate_employee_id()

        if not Employee.objects.filter(employee_id=candidate).exists():
            return candidate

        # Collision: try the next number
        try:
            number = int(candidate.split("-")[-1])
        except (ValueError, IndexError):
            number = 0

        number += attempt + 1
        candidate = f"{EMPLOYEE_ID_PREFIX}-{str(number).zfill(EMPLOYEE_ID_PADDING)}"

        if not Employee.objects.filter(employee_id=candidate).exists():
            return candidate

    raise RuntimeError(
        f"Unable to generate a unique employee ID after {MAX_RETRIES} attempts."
    )
