"""Organization module signals.

Tracks department transfers and designation changes when an
Employee's department or designation FK is updated.
"""

import logging
from datetime import date

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(post_save, sender="employees.Employee")
def track_department_transfer(sender, instance, created, **kwargs):
    """Create / close DepartmentMember records on department change."""
    if created:
        # For brand-new employees with a department, create initial membership
        if instance.department_id:
            _create_membership(instance, instance.department)
        return

    # Compare current value with the database value
    try:
        old = sender.objects.filter(pk=instance.pk).values_list(
            "department_id", flat=True
        ).get()
    except sender.DoesNotExist:
        return

    if old == instance.department_id:
        return

    from apps.organization.models.department_member import DepartmentMember

    # Close old membership
    if old:
        DepartmentMember.objects.filter(
            employee=instance,
            department_id=old,
            left_date__isnull=True,
        ).update(left_date=date.today(), is_primary=False)

    # Open new membership
    if instance.department_id:
        _create_membership(instance, instance.department)

    logger.info(
        "Department transfer: employee=%s old_dept=%s new_dept=%s",
        instance.pk,
        old,
        instance.department_id,
    )


@receiver(post_save, sender="employees.Employee")
def track_designation_change(sender, instance, created, **kwargs):
    """Log designation changes for auditing purposes."""
    if created:
        return

    try:
        old = sender.objects.filter(pk=instance.pk).values_list(
            "designation_id", flat=True
        ).get()
    except sender.DoesNotExist:
        return

    if old == instance.designation_id:
        return

    logger.info(
        "Designation change: employee=%s old_desig=%s new_desig=%s",
        instance.pk,
        old,
        instance.designation_id,
    )


def _create_membership(employee, department):
    """Helper to create a DepartmentMember for current date."""
    from apps.organization.models.department_member import DepartmentMember

    DepartmentMember.objects.create(
        employee=employee,
        department=department,
        joined_date=date.today(),
        is_primary=True,
    )
