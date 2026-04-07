"""Seed statutory and common salary components for Sri Lankan payroll."""

from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.payroll.models import SalaryComponent


STATUTORY_COMPONENTS = [
    {
        "name": "Basic Salary",
        "code": "BASIC",
        "component_type": "EARNING",
        "category": "BASIC",
        "calculation_type": "FIXED",
        "is_taxable": True,
        "is_epf_applicable": True,
        "is_fixed": True,
        "display_order": 1,
        "description": "Core monthly basic salary.",
    },
    {
        "name": "EPF - Employee 8%",
        "code": "EPF_EE",
        "component_type": "DEDUCTION",
        "category": "STATUTORY",
        "calculation_type": "PERCENTAGE_OF_BASIC",
        "percentage": Decimal("8.00"),
        "is_taxable": False,
        "is_epf_applicable": False,
        "is_fixed": True,
        "display_order": 50,
        "description": "Employee Provident Fund contribution (8% of EPF base).",
    },
    {
        "name": "EPF - Employer 12%",
        "code": "EPF_ER",
        "component_type": "EMPLOYER_CONTRIBUTION",
        "category": "STATUTORY",
        "calculation_type": "PERCENTAGE_OF_BASIC",
        "percentage": Decimal("12.00"),
        "is_taxable": False,
        "is_epf_applicable": False,
        "is_fixed": True,
        "display_order": 60,
        "description": "Employer Provident Fund contribution (12% of EPF base).",
    },
    {
        "name": "ETF - Employer 3%",
        "code": "ETF_ER",
        "component_type": "EMPLOYER_CONTRIBUTION",
        "category": "STATUTORY",
        "calculation_type": "PERCENTAGE_OF_BASIC",
        "percentage": Decimal("3.00"),
        "is_taxable": False,
        "is_epf_applicable": False,
        "is_fixed": True,
        "display_order": 61,
        "description": "Employees' Trust Fund contribution (3% of EPF base).",
    },
    {
        "name": "PAYE Tax",
        "code": "PAYE",
        "component_type": "DEDUCTION",
        "category": "TAX",
        "calculation_type": "FORMULA",
        "is_taxable": False,
        "is_epf_applicable": False,
        "is_fixed": True,
        "display_order": 55,
        "description": "Pay As You Earn income tax (progressive rates).",
    },
]

COMMON_ALLOWANCES = [
    {
        "name": "Transport Allowance",
        "code": "TRANSPORT",
        "component_type": "EARNING",
        "category": "ALLOWANCE",
        "calculation_type": "FIXED",
        "is_taxable": True,
        "is_epf_applicable": True,
        "is_fixed": True,
        "display_order": 10,
        "description": "Monthly transport/travel allowance.",
    },
    {
        "name": "Medical Allowance",
        "code": "MEDICAL",
        "component_type": "EARNING",
        "category": "ALLOWANCE",
        "calculation_type": "FIXED",
        "is_taxable": False,
        "is_epf_applicable": False,
        "is_fixed": True,
        "display_order": 11,
        "description": "Monthly medical/healthcare allowance.",
    },
    {
        "name": "Housing Allowance",
        "code": "HOUSING",
        "component_type": "EARNING",
        "category": "ALLOWANCE",
        "calculation_type": "FIXED",
        "is_taxable": True,
        "is_epf_applicable": False,
        "is_fixed": True,
        "display_order": 12,
        "description": "Monthly housing/accommodation allowance.",
    },
    {
        "name": "Meal Allowance",
        "code": "MEAL",
        "component_type": "EARNING",
        "category": "ALLOWANCE",
        "calculation_type": "FIXED",
        "is_taxable": False,
        "is_epf_applicable": False,
        "is_fixed": True,
        "display_order": 13,
        "description": "Monthly meal/food allowance.",
    },
    {
        "name": "Overtime Pay",
        "code": "OVERTIME",
        "component_type": "EARNING",
        "category": "OTHER",
        "calculation_type": "FORMULA",
        "is_taxable": True,
        "is_epf_applicable": True,
        "is_fixed": False,
        "display_order": 20,
        "description": "Overtime compensation (attendance-based).",
    },
    {
        "name": "Performance Bonus",
        "code": "BONUS_PERF",
        "component_type": "EARNING",
        "category": "BONUS",
        "calculation_type": "FIXED",
        "is_taxable": True,
        "is_epf_applicable": False,
        "is_fixed": False,
        "display_order": 25,
        "description": "Performance-based bonus.",
    },
    {
        "name": "Loan Repayment",
        "code": "LOAN_REPAY",
        "component_type": "DEDUCTION",
        "category": "LOAN",
        "calculation_type": "FIXED",
        "is_taxable": False,
        "is_epf_applicable": False,
        "is_fixed": True,
        "display_order": 70,
        "description": "Monthly loan repayment deduction.",
    },
    {
        "name": "No-Pay Deduction",
        "code": "NO_PAY",
        "component_type": "DEDUCTION",
        "category": "OTHER",
        "calculation_type": "FORMULA",
        "is_taxable": False,
        "is_epf_applicable": False,
        "is_fixed": False,
        "display_order": 71,
        "description": "Deduction for unpaid leave days.",
    },
]


class Command(BaseCommand):
    help = "Seed statutory and common salary components"

    def handle(self, *args, **options):
        created_count = 0
        for data in STATUTORY_COMPONENTS + COMMON_ALLOWANCES:
            _, created = SalaryComponent.objects.get_or_create(
                code=data["code"],
                defaults=data,
            )
            if created:
                created_count += 1
                self.stdout.write(f"  Created: {data['name']} ({data['code']})")
            else:
                self.stdout.write(f"  Exists:  {data['name']} ({data['code']})")

        self.stdout.write(
            self.style.SUCCESS(f"Seed complete: {created_count} new components created")
        )
