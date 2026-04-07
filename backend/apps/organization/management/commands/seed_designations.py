"""Management command to seed default designations."""

import logging
from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.organization.constants import (
    DESIGNATION_LEVEL_ENTRY,
    DESIGNATION_LEVEL_EXECUTIVE,
    DESIGNATION_LEVEL_DIRECTOR,
    DESIGNATION_LEVEL_JUNIOR,
    DESIGNATION_LEVEL_LEAD,
    DESIGNATION_LEVEL_MANAGER,
    DESIGNATION_LEVEL_MID,
    DESIGNATION_LEVEL_SENIOR,
    DESIGNATION_STATUS_ACTIVE,
)

logger = logging.getLogger(__name__)

DEFAULT_DESIGNATIONS = [
    # EXECUTIVE
    {"code": "CEO", "title": "Chief Executive Officer", "level": DESIGNATION_LEVEL_EXECUTIVE, "is_manager": True, "min_salary": Decimal("500000"), "max_salary": Decimal("1500000"), "experience_years": 15},
    {"code": "COO", "title": "Chief Operating Officer", "level": DESIGNATION_LEVEL_EXECUTIVE, "is_manager": True, "min_salary": Decimal("400000"), "max_salary": Decimal("1200000"), "experience_years": 15},
    {"code": "CFO", "title": "Chief Financial Officer", "level": DESIGNATION_LEVEL_EXECUTIVE, "is_manager": True, "min_salary": Decimal("400000"), "max_salary": Decimal("1200000"), "experience_years": 15},
    {"code": "CTO", "title": "Chief Technology Officer", "level": DESIGNATION_LEVEL_EXECUTIVE, "is_manager": True, "min_salary": Decimal("400000"), "max_salary": Decimal("1200000"), "experience_years": 15},
    # DIRECTOR
    {"code": "DIR", "title": "Director", "level": DESIGNATION_LEVEL_DIRECTOR, "is_manager": True, "min_salary": Decimal("250000"), "max_salary": Decimal("600000"), "experience_years": 12},
    {"code": "OPD", "title": "Operations Director", "level": DESIGNATION_LEVEL_DIRECTOR, "is_manager": True, "min_salary": Decimal("250000"), "max_salary": Decimal("600000"), "experience_years": 12},
    {"code": "SD", "title": "Sales Director", "level": DESIGNATION_LEVEL_DIRECTOR, "is_manager": True, "min_salary": Decimal("250000"), "max_salary": Decimal("600000"), "experience_years": 10},
    {"code": "ITD", "title": "IT Director", "level": DESIGNATION_LEVEL_DIRECTOR, "is_manager": True, "min_salary": Decimal("250000"), "max_salary": Decimal("600000"), "experience_years": 10},
    # MANAGER
    {"code": "MGR", "title": "Manager", "level": DESIGNATION_LEVEL_MANAGER, "is_manager": True, "min_salary": Decimal("150000"), "max_salary": Decimal("350000"), "experience_years": 8},
    {"code": "HRM", "title": "HR Manager", "level": DESIGNATION_LEVEL_MANAGER, "is_manager": True, "min_salary": Decimal("150000"), "max_salary": Decimal("350000"), "experience_years": 8},
    {"code": "FM", "title": "Finance Manager", "level": DESIGNATION_LEVEL_MANAGER, "is_manager": True, "min_salary": Decimal("150000"), "max_salary": Decimal("350000"), "experience_years": 8},
    {"code": "ITM", "title": "IT Manager", "level": DESIGNATION_LEVEL_MANAGER, "is_manager": True, "min_salary": Decimal("150000"), "max_salary": Decimal("350000"), "experience_years": 8},
    {"code": "SM", "title": "Sales Manager", "level": DESIGNATION_LEVEL_MANAGER, "is_manager": True, "min_salary": Decimal("150000"), "max_salary": Decimal("350000"), "experience_years": 8},
    # LEAD
    {"code": "TL", "title": "Team Lead", "level": DESIGNATION_LEVEL_LEAD, "is_manager": True, "min_salary": Decimal("100000"), "max_salary": Decimal("200000"), "experience_years": 5},
    {"code": "PL", "title": "Project Lead", "level": DESIGNATION_LEVEL_LEAD, "is_manager": True, "min_salary": Decimal("100000"), "max_salary": Decimal("200000"), "experience_years": 5},
    {"code": "TLD", "title": "Technical Lead", "level": DESIGNATION_LEVEL_LEAD, "is_manager": True, "min_salary": Decimal("100000"), "max_salary": Decimal("200000"), "experience_years": 5},
    # SENIOR
    {"code": "SDE", "title": "Senior Developer", "level": DESIGNATION_LEVEL_SENIOR, "is_manager": False, "min_salary": Decimal("80000"), "max_salary": Decimal("150000"), "experience_years": 4},
    {"code": "SA", "title": "Senior Analyst", "level": DESIGNATION_LEVEL_SENIOR, "is_manager": False, "min_salary": Decimal("80000"), "max_salary": Decimal("150000"), "experience_years": 4},
    {"code": "SSA", "title": "Senior Associate", "level": DESIGNATION_LEVEL_SENIOR, "is_manager": False, "min_salary": Decimal("80000"), "max_salary": Decimal("150000"), "experience_years": 4},
    # MID
    {"code": "DEV", "title": "Developer", "level": DESIGNATION_LEVEL_MID, "is_manager": False, "min_salary": Decimal("60000"), "max_salary": Decimal("100000"), "experience_years": 2},
    {"code": "ANL", "title": "Analyst", "level": DESIGNATION_LEVEL_MID, "is_manager": False, "min_salary": Decimal("60000"), "max_salary": Decimal("100000"), "experience_years": 2},
    {"code": "ASSOC", "title": "Associate", "level": DESIGNATION_LEVEL_MID, "is_manager": False, "min_salary": Decimal("60000"), "max_salary": Decimal("100000"), "experience_years": 2},
    {"code": "SPEC", "title": "Specialist", "level": DESIGNATION_LEVEL_MID, "is_manager": False, "min_salary": Decimal("60000"), "max_salary": Decimal("100000"), "experience_years": 2},
    # JUNIOR
    {"code": "JDE", "title": "Junior Developer", "level": DESIGNATION_LEVEL_JUNIOR, "is_manager": False, "min_salary": Decimal("40000"), "max_salary": Decimal("70000"), "experience_years": 0},
    {"code": "JA", "title": "Junior Analyst", "level": DESIGNATION_LEVEL_JUNIOR, "is_manager": False, "min_salary": Decimal("40000"), "max_salary": Decimal("70000"), "experience_years": 0},
    {"code": "JAS", "title": "Junior Associate", "level": DESIGNATION_LEVEL_JUNIOR, "is_manager": False, "min_salary": Decimal("40000"), "max_salary": Decimal("70000"), "experience_years": 0},
    # ENTRY
    {"code": "TRN", "title": "Trainee", "level": DESIGNATION_LEVEL_ENTRY, "is_manager": False, "min_salary": Decimal("25000"), "max_salary": Decimal("45000"), "experience_years": 0},
    {"code": "INT", "title": "Intern", "level": DESIGNATION_LEVEL_ENTRY, "is_manager": False, "min_salary": Decimal("20000"), "max_salary": Decimal("35000"), "experience_years": 0},
    {"code": "GT", "title": "Graduate Trainee", "level": DESIGNATION_LEVEL_ENTRY, "is_manager": False, "min_salary": Decimal("30000"), "max_salary": Decimal("50000"), "experience_years": 0},
]


class Command(BaseCommand):
    help = "Seed default designations for the organization module."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing designations before seeding.",
        )
        parser.add_argument(
            "--update",
            action="store_true",
            help="Update existing designations with seed data.",
        )

    def handle(self, *args, **options):
        from apps.organization.models import Designation

        clear = options["clear"]
        update = options["update"]
        created_count = 0
        updated_count = 0
        skipped_count = 0

        if clear:
            count, _ = Designation.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Cleared {count} existing designations."))

        for data in DEFAULT_DESIGNATIONS:
            code = data["code"]
            existing = Designation.objects.filter(code=code).first()

            if existing:
                if update:
                    for attr, value in data.items():
                        setattr(existing, attr, value)
                    existing.status = DESIGNATION_STATUS_ACTIVE
                    existing.save()
                    updated_count += 1
                    self.stdout.write(f"  Updated: {code} - {data['title']}")
                else:
                    skipped_count += 1
                    self.stdout.write(f"  Skipped: {code} - {data['title']} (already exists)")
            else:
                Designation.objects.create(
                    status=DESIGNATION_STATUS_ACTIVE,
                    currency="LKR",
                    **data,
                )
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"  Created: {code} - {data['title']}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSeeding complete: {created_count} created, "
                f"{updated_count} updated, {skipped_count} skipped."
            )
        )
