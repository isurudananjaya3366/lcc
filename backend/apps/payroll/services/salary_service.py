"""Salary service for assignment, revision, and calculation operations."""

import logging
from decimal import Decimal

from django.db import models, transaction
from django.utils import timezone

from apps.payroll.constants import ComponentType
from apps.payroll.models.employee_salary import EmployeeSalary
from apps.payroll.models.employee_salary_component import EmployeeSalaryComponent
from apps.payroll.models.salary_history import SalaryHistory
from apps.payroll.models.template_component import TemplateComponent

logger = logging.getLogger(__name__)


class SalaryService:
    """Main service for salary operations."""

    @staticmethod
    @transaction.atomic
    def assign_template(employee, template, basic_salary, effective_from=None):
        """Assign a salary template to an employee.

        Creates an EmployeeSalary record with components from the template.
        Deactivates any existing current salary.
        """
        if effective_from is None:
            effective_from = timezone.now().date()

        # Deactivate current salary
        EmployeeSalary.objects.filter(
            employee=employee, is_current=True
        ).update(is_current=False, effective_to=effective_from)

        # Create new salary record
        employee_salary = EmployeeSalary.objects.create(
            employee=employee,
            template=template,
            basic_salary=basic_salary,
            effective_from=effective_from,
            is_current=True,
        )

        # Copy template components
        template_components = TemplateComponent.objects.filter(
            template=template
        ).select_related("component")

        gross = Decimal("0")
        for tc in template_components:
            component = tc.component
            if component.component_type == ComponentType.EARNING:
                if component.category == "BASIC":
                    amount = basic_salary
                else:
                    amount = tc.default_value
                gross += amount
            else:
                amount = tc.default_value

            EmployeeSalaryComponent.objects.create(
                employee_salary=employee_salary,
                component=component,
                amount=amount,
            )

        employee_salary.gross_salary = gross
        employee_salary.save(update_fields=["gross_salary"])

        return employee_salary

    @staticmethod
    @transaction.atomic
    def override_component(employee_salary, component, amount):
        """Override a specific component value for an employee's salary."""
        esc, created = EmployeeSalaryComponent.objects.update_or_create(
            employee_salary=employee_salary,
            component=component,
            defaults={"amount": amount},
        )

        # Recalculate gross
        SalaryService.recalculate_gross(employee_salary)
        return esc

    @staticmethod
    def recalculate_gross(employee_salary):
        """Recalculate gross salary from earning components."""
        gross = EmployeeSalaryComponent.objects.filter(
            employee_salary=employee_salary,
            component__component_type=ComponentType.EARNING,
        ).aggregate(total=models.Sum("amount"))["total"] or Decimal("0")

        employee_salary.gross_salary = gross
        employee_salary.save(update_fields=["gross_salary"])
        return gross

    @staticmethod
    @transaction.atomic
    def revise_salary(employee, new_basic, effective_from, change_reason="OTHER", remarks=""):
        """Create a salary revision with history tracking."""
        current = EmployeeSalary.objects.filter(
            employee=employee, is_current=True
        ).first()

        old_basic = current.basic_salary if current else Decimal("0")
        old_gross = current.gross_salary if current else Decimal("0")

        # Deactivate current
        if current:
            current.is_current = False
            current.effective_to = effective_from
            current.save(update_fields=["is_current", "effective_to"])

        # Create new salary
        new_salary = EmployeeSalary.objects.create(
            employee=employee,
            template=current.template if current else None,
            basic_salary=new_basic,
            effective_from=effective_from,
            is_current=True,
        )

        # Copy components from old salary, adjusting basic
        if current:
            for esc in current.salary_components.select_related("component").all():
                new_amount = new_basic if esc.component.category == "BASIC" else esc.amount
                EmployeeSalaryComponent.objects.create(
                    employee_salary=new_salary,
                    component=esc.component,
                    amount=new_amount,
                )

        SalaryService.recalculate_gross(new_salary)

        # Create history record
        SalaryHistory.objects.create(
            employee=employee,
            previous_basic=old_basic,
            new_basic=new_basic,
            previous_gross=old_gross,
            new_gross=new_salary.gross_salary,
            effective_date=effective_from,
            change_reason=change_reason,
            remarks=remarks,
        )

        return new_salary

    @staticmethod
    def calculate_gross(employee_salary):
        """Calculate gross salary from all earning components."""
        components = EmployeeSalaryComponent.objects.filter(
            employee_salary=employee_salary,
            component__component_type=ComponentType.EARNING,
        ).select_related("component")

        gross = sum(c.amount for c in components)
        return gross

    @staticmethod
    def compare_salaries(old_salary, new_salary):
        """Compare two salary records and return differences."""
        old_components = {
            esc.component_id: esc
            for esc in old_salary.salary_components.select_related("component").all()
        }
        new_components = {
            esc.component_id: esc
            for esc in new_salary.salary_components.select_related("component").all()
        }

        all_ids = set(old_components.keys()) | set(new_components.keys())
        differences = []
        for comp_id in all_ids:
            old_esc = old_components.get(comp_id)
            new_esc = new_components.get(comp_id)
            old_amt = old_esc.amount if old_esc else Decimal("0")
            new_amt = new_esc.amount if new_esc else Decimal("0")
            if old_amt != new_amt:
                change_pct = (
                    ((new_amt - old_amt) / old_amt * 100).quantize(Decimal("0.01"))
                    if old_amt
                    else Decimal("0")
                )
                differences.append({
                    "component_id": comp_id,
                    "old_amount": old_amt,
                    "new_amount": new_amt,
                    "difference": new_amt - old_amt,
                    "change_percent": change_pct,
                })

        basic_change = new_salary.basic_salary - old_salary.basic_salary
        gross_change = new_salary.gross_salary - old_salary.gross_salary

        return {
            "basic_change": basic_change,
            "gross_change": gross_change,
            "basic_change_percent": (
                (basic_change / old_salary.basic_salary * 100).quantize(Decimal("0.01"))
                if old_salary.basic_salary
                else Decimal("0")
            ),
            "gross_change_percent": (
                (gross_change / old_salary.gross_salary * 100).quantize(Decimal("0.01"))
                if old_salary.gross_salary
                else Decimal("0")
            ),
            "component_differences": differences,
        }

    @staticmethod
    def get_current_salary(employee):
        """Get the employee's currently active salary record."""
        return EmployeeSalary.objects.filter(
            employee=employee, is_current=True
        ).select_related("template").first()

    @staticmethod
    def get_salary_for_date(employee, target_date):
        """Get the salary record effective on a specific date."""
        return (
            EmployeeSalary.objects.filter(
                employee=employee,
                effective_from__lte=target_date,
            )
            .filter(
                models.Q(effective_to__gte=target_date) | models.Q(effective_to__isnull=True)
            )
            .select_related("template")
            .first()
        )
