"""Organization validators.

Prevents circular manager references and validates department
consistency in the employee-department hierarchy.
"""

from django.core.exceptions import ValidationError


def validate_no_circular_manager(employee):
    """Ensure assigning a manager doesn't create a circular chain.

    Walks up the ``manager`` FK chain from the proposed manager to
    detect if ``employee`` already appears as a transitive manager.
    """
    if not employee.manager_id:
        return

    visited = {employee.pk}
    current = employee.manager

    while current is not None:
        if current.pk in visited:
            raise ValidationError(
                {"manager": "Circular manager reference detected."}
            )
        visited.add(current.pk)
        current = current.manager


def validate_department_consistency(employee):
    """Warn if an employee's manager is in a different department tree.

    This is a soft validation — it raises ``ValidationError`` only if
    the manager's department is not an ancestor, descendant, or the
    same department as the employee's department.
    """
    if not employee.department_id or not employee.manager_id:
        return

    manager = employee.manager
    if not manager.department_id:
        return

    if employee.department_id == manager.department_id:
        return

    # Check if manager's department is in the same tree branch
    dept = employee.department
    manager_dept = manager.department

    ancestors = set(dept.get_ancestors(include_self=True).values_list("pk", flat=True))
    if manager_dept.pk in ancestors:
        return

    descendants = set(dept.get_descendants(include_self=True).values_list("pk", flat=True))
    if manager_dept.pk in descendants:
        return

    raise ValidationError(
        {
            "manager": (
                "Manager's department is not in the same branch of the "
                "department hierarchy."
            )
        }
    )
