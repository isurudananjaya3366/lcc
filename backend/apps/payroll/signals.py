"""Signals for the Payroll app.

Creates salary history records when employee salary changes.
Manages is_current flag for employee salary records.
"""

import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.payroll.models.employee_salary import EmployeeSalary

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=EmployeeSalary)
def create_salary_history_on_change(sender, instance, **kwargs):
    """Create a SalaryHistory record when an employee's salary is revised."""
    if not instance.pk:
        return

    try:
        old_instance = EmployeeSalary.objects.get(pk=instance.pk)
    except EmployeeSalary.DoesNotExist:
        return

    if old_instance.basic_salary != instance.basic_salary:
        from apps.payroll.models.salary_history import SalaryHistory

        SalaryHistory.objects.create(
            employee=instance.employee,
            salary=instance,
            previous_basic=old_instance.basic_salary,
            new_basic=instance.basic_salary,
            previous_gross=old_instance.gross_salary,
            new_gross=instance.gross_salary,
            effective_date=instance.effective_from,
        )
        logger.info(
            "Salary history created for employee %s: %s → %s",
            instance.employee_id,
            old_instance.basic_salary,
            instance.basic_salary,
        )


@receiver(post_save, sender=EmployeeSalary)
def manage_is_current_flag(sender, instance, created, **kwargs):
    """Ensure only one salary per employee is marked as current.

    When a new salary is created or updated with is_current=True,
    set all other salaries for the same employee to is_current=False.
    """
    if instance.is_current:
        EmployeeSalary.objects.filter(
            employee=instance.employee,
            is_current=True,
        ).exclude(pk=instance.pk).update(is_current=False)
