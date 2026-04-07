"""Seed default Sri Lanka tax exemptions."""

from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.payroll.models import TaxExemption


DEFAULT_EXEMPTIONS = [
    {
        "name": "Personal Relief",
        "code": "PERSONAL",
        "exemption_type": "PERSONAL",
        "annual_amount": Decimal("1200000.00"),
        "monthly_amount": Decimal("100000.00"),
        "max_claims": 1,
        "description": "Annual personal relief deduction under Inland Revenue Act.",
    },
    {
        "name": "Spouse Relief",
        "code": "SPOUSE",
        "exemption_type": "SPOUSE",
        "annual_amount": Decimal("500000.00"),
        "monthly_amount": Decimal("41666.67"),
        "max_claims": 1,
        "description": "Relief for married employees with non-working spouse.",
    },
    {
        "name": "Child Relief",
        "code": "CHILD",
        "exemption_type": "CHILD",
        "annual_amount": Decimal("300000.00"),
        "monthly_amount": Decimal("25000.00"),
        "max_claims": 4,
        "description": "Relief per qualifying child (maximum 4 children).",
    },
    {
        "name": "Disabled Child Relief",
        "code": "DISABLED_CHILD",
        "exemption_type": "DISABLED_CHILD",
        "annual_amount": Decimal("500000.00"),
        "monthly_amount": Decimal("41666.67"),
        "max_claims": 2,
        "description": "Enhanced relief for disabled children.",
    },
]


class Command(BaseCommand):
    help = "Seed default Sri Lanka tax exemptions for 2024"

    def handle(self, *args, **options):
        tax_year = 2024
        created_count = 0
        for exemption_data in DEFAULT_EXEMPTIONS:
            _, created = TaxExemption.objects.get_or_create(
                code=exemption_data["code"],
                tax_year=tax_year,
                defaults=exemption_data,
            )
            if created:
                created_count += 1

        self.stdout.write(f"  Exemptions: {created_count} new exemptions for {tax_year}")
        self.stdout.write(self.style.SUCCESS("Tax exemptions seed complete"))
