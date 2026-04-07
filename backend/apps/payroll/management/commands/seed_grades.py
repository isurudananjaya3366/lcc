"""Seed sample salary grades."""

from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.payroll.models import SalaryGrade


DEFAULT_GRADES = [
    {
        "name": "Grade 1 - Entry Level",
        "code": "G1",
        "level": 1,
        "min_salary": Decimal("35000.00"),
        "max_salary": Decimal("50000.00"),
    },
    {
        "name": "Grade 2 - Junior",
        "code": "G2",
        "level": 2,
        "min_salary": Decimal("50000.00"),
        "max_salary": Decimal("80000.00"),
    },
    {
        "name": "Grade 3 - Mid-Level",
        "code": "G3",
        "level": 3,
        "min_salary": Decimal("80000.00"),
        "max_salary": Decimal("120000.00"),
    },
    {
        "name": "Grade 4 - Senior",
        "code": "G4",
        "level": 4,
        "min_salary": Decimal("120000.00"),
        "max_salary": Decimal("200000.00"),
    },
    {
        "name": "Grade 5 - Management",
        "code": "G5",
        "level": 5,
        "min_salary": Decimal("200000.00"),
        "max_salary": Decimal("400000.00"),
    },
    {
        "name": "Grade 6 - Executive",
        "code": "G6",
        "level": 6,
        "min_salary": Decimal("400000.00"),
        "max_salary": Decimal("800000.00"),
    },
]


class Command(BaseCommand):
    help = "Seed default salary grades"

    def handle(self, *args, **options):
        created_count = 0
        for data in DEFAULT_GRADES:
            _, created = SalaryGrade.objects.get_or_create(
                code=data["code"],
                defaults=data,
            )
            if created:
                created_count += 1
                self.stdout.write(f"  Created: {data['name']}")
            else:
                self.stdout.write(f"  Exists:  {data['name']}")

        self.stdout.write(
            self.style.SUCCESS(f"Seed complete: {created_count} new grades created")
        )
