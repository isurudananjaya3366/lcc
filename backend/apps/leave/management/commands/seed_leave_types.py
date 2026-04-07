"""Seed default Sri Lankan leave types for a tenant.

Usage:
    python manage.py seed_leave_types --schema <tenant_schema>
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from apps.leave.constants import GenderRestriction, LeaveTypeCategory
from apps.leave.models import LeaveType

DEFAULT_LEAVE_TYPES = [
    {
        "name": "Annual Leave",
        "code": "AL",
        "category": LeaveTypeCategory.ANNUAL,
        "description": (
            "Annual leave for rest and recreation. Requires 14 days advance notice. "
            "Entitled after 12 months of continuous service per the Shop & Office Employees Act."
        ),
        "color": "#4CAF50",
        "default_days_per_year": 14,
        "max_consecutive_days": 14,
        "is_paid": True,
        "requires_document": False,
        "allow_half_day": True,
        "applicable_gender": GenderRestriction.ALL,
        "min_service_months": 12,
        "min_notice_days": 14,
    },
    {
        "name": "Casual Leave",
        "code": "CL",
        "category": LeaveTypeCategory.CASUAL,
        "description": (
            "Short-term personal leave for immediate needs. "
            "Cannot carry forward to next year."
        ),
        "color": "#2196F3",
        "default_days_per_year": 7,
        "max_consecutive_days": 3,
        "is_paid": True,
        "requires_document": False,
        "allow_half_day": True,
        "applicable_gender": GenderRestriction.ALL,
        "min_service_months": 0,
        "min_notice_days": 1,
    },
    {
        "name": "Sick Leave",
        "code": "SL",
        "category": LeaveTypeCategory.SICK,
        "description": (
            "Medical leave for illness or injury. "
            "Medical certificate required for absences exceeding 2 days."
        ),
        "color": "#F44336",
        "default_days_per_year": 7,
        "max_consecutive_days": 7,
        "is_paid": True,
        "requires_document": True,
        "document_after_days": 2,
        "allow_half_day": True,
        "applicable_gender": GenderRestriction.ALL,
        "min_service_months": 0,
        "min_notice_days": 0,
    },
    {
        "name": "Maternity Leave",
        "code": "ML",
        "category": LeaveTypeCategory.MATERNITY,
        "description": (
            "84 working days paid leave for childbirth per the Maternity Benefits Ordinance. "
            "Cannot be denied or reduced. Job protection guaranteed."
        ),
        "color": "#E91E63",
        "default_days_per_year": 84,
        "max_consecutive_days": 84,
        "is_paid": True,
        "requires_document": True,
        "allow_half_day": False,
        "applicable_gender": GenderRestriction.FEMALE,
        "min_service_months": 0,
        "min_notice_days": 14,
    },
    {
        "name": "Paternity Leave",
        "code": "PL",
        "category": LeaveTypeCategory.PATERNITY,
        "description": (
            "3 working days paid leave for childbirth support. "
            "Must be taken within 4 weeks of birth."
        ),
        "color": "#3F51B5",
        "default_days_per_year": 3,
        "max_consecutive_days": 3,
        "is_paid": True,
        "requires_document": True,
        "allow_half_day": False,
        "applicable_gender": GenderRestriction.MALE,
        "min_service_months": 0,
        "min_notice_days": 0,
    },
    {
        "name": "No-Pay Leave",
        "code": "NPL",
        "category": LeaveTypeCategory.NO_PAY,
        "description": (
            "Unpaid leave by mutual agreement. "
            "Requires management approval. Does not affect EPF/ETF for short durations."
        ),
        "color": "#9E9E9E",
        "default_days_per_year": 30,
        "max_consecutive_days": 30,
        "is_paid": False,
        "requires_document": False,
        "allow_half_day": True,
        "applicable_gender": GenderRestriction.ALL,
        "min_service_months": 6,
        "min_notice_days": 30,
    },
]


class Command(BaseCommand):
    help = "Seed default Sri Lankan leave types for the current tenant schema."

    def add_arguments(self, parser):
        parser.add_argument(
            "--schema",
            type=str,
            default=None,
            help="Tenant schema name to seed. Defaults to current schema.",
        )

    def handle(self, *args, **options):
        schema = options.get("schema")
        if schema:
            connection.set_schema(schema)

        created_count = 0
        skipped_count = 0

        for lt_data in DEFAULT_LEAVE_TYPES:
            code = lt_data["code"]
            if LeaveType.objects.filter(code=code).exists():
                self.stdout.write(f"  Skipped: {lt_data['name']} ({code}) — already exists")
                skipped_count += 1
                continue

            LeaveType.objects.create(**lt_data)
            self.stdout.write(self.style.SUCCESS(f"  Created: {lt_data['name']} ({code})"))
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. Created {created_count}, skipped {skipped_count}."
            )
        )
