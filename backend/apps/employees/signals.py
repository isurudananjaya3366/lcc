"""Employees signals module."""

from datetime import date

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.employees.models.employee import Employee


@receiver(pre_save, sender=Employee)
def track_employment_changes(sender, instance, **kwargs):
    """Auto-create employment history when key fields change."""
    if not instance.pk:
        return  # New employees handled by post_save

    try:
        old_instance = Employee.objects.get(pk=instance.pk)
    except Employee.DoesNotExist:
        return

    from apps.employees.constants import (
        CHANGE_TYPE_MANAGER_CHANGE,
        CHANGE_TYPE_PROMOTION,
        CHANGE_TYPE_ROLE_CHANGE,
        CHANGE_TYPE_SALARY_CHANGE,
        CHANGE_TYPE_TRANSFER,
    )
    from apps.employees.models.employment_history import EmploymentHistory

    today = date.today()

    # Track department change
    if old_instance.department != instance.department and (
        old_instance.department or instance.department
    ):
        EmploymentHistory.objects.create(
            employee=instance,
            effective_date=today,
            change_type=CHANGE_TYPE_TRANSFER,
            from_department=str(old_instance.department) if old_instance.department else "",
            to_department=str(instance.department) if instance.department else "",
        )

    # Track designation change (with promotion/demotion detection)
    if old_instance.designation != instance.designation and (
        old_instance.designation or instance.designation
    ):
        EmploymentHistory.objects.create(
            employee=instance,
            effective_date=today,
            change_type=CHANGE_TYPE_ROLE_CHANGE,
            from_designation=str(old_instance.designation) if old_instance.designation else "",
            to_designation=str(instance.designation) if instance.designation else "",
        )

    # Track manager change
    if old_instance.manager_id != instance.manager_id:
        EmploymentHistory.objects.create(
            employee=instance,
            effective_date=today,
            change_type=CHANGE_TYPE_MANAGER_CHANGE,
            from_manager=old_instance.manager,
            to_manager=instance.manager,
        )

    # Track confirmation date change (probation confirmation)
    if (
        old_instance.confirmation_date != instance.confirmation_date
        and instance.confirmation_date
        and not old_instance.confirmation_date
    ):
        from apps.employees.constants import CHANGE_TYPE_PROBATION_CONFIRMATION

        EmploymentHistory.objects.create(
            employee=instance,
            effective_date=instance.confirmation_date,
            change_type=CHANGE_TYPE_PROBATION_CONFIRMATION,
            notes="Employee confirmed after probation period.",
        )


@receiver(post_save, sender=Employee)
def create_hire_history(sender, instance, created, **kwargs):
    """Create a HIRE history entry when a new employee is created."""
    if not created:
        return

    from apps.employees.constants import CHANGE_TYPE_HIRE
    from apps.employees.models.employment_history import EmploymentHistory

    EmploymentHistory.objects.create(
        employee=instance,
        effective_date=instance.hire_date or date.today(),
        change_type=CHANGE_TYPE_HIRE,
        to_department=str(instance.department) if instance.department else "",
        to_designation=str(instance.designation) if instance.designation else "",
        to_manager=instance.manager,
        notes="Initial hire.",
    )
