"""Management command to seed Sri Lankan holidays.

Seeds public holidays, Poya days, and optional holidays for a given year.
"""

from datetime import date

from django.core.management.base import BaseCommand
from django_tenants.utils import tenant_context

from apps.leave.constants import HolidayType
from apps.leave.models.holiday import Holiday
from apps.tenants.models import Tenant


class Command(BaseCommand):
    help = "Seed Sri Lankan holidays for a given year."

    def add_arguments(self, parser):
        parser.add_argument(
            "--year",
            type=int,
            default=2026,
            help="Year to seed holidays for (default: 2026).",
        )
        parser.add_argument(
            "--schema",
            type=str,
            default=None,
            help="Specific tenant schema name.",
        )
        parser.add_argument(
            "--all-tenants",
            action="store_true",
            help="Seed holidays for all active tenants.",
        )

    def handle(self, *args, **options):
        year = options["year"]
        schema = options.get("schema")
        all_tenants = options.get("all_tenants", False)

        if all_tenants:
            tenants = Tenant.objects.exclude(schema_name="public")
        elif schema:
            tenants = Tenant.objects.filter(schema_name=schema)
        else:
            tenants = Tenant.objects.exclude(schema_name="public")

        for tenant in tenants:
            with tenant_context(tenant):
                fixed = self.create_fixed_holidays(year)
                poya = self.create_poya_holidays(year)
                optional = self.create_optional_holidays(year)

                self.stdout.write(
                    self.style.SUCCESS(
                        f"[{tenant.schema_name}] Seeded {fixed + poya + optional} "
                        f"holidays for {year} "
                        f"(fixed={fixed}, poya={poya}, optional={optional})"
                    )
                )

    def create_fixed_holidays(self, year):
        """Create fixed-date Sri Lankan public holidays."""
        holidays = [
            (date(year, 1, 14), "Thai Pongal"),
            (date(year, 2, 4), "Independence Day"),
            (date(year, 4, 13), "Sinhala and Tamil New Year Day 1"),
            (date(year, 4, 14), "Sinhala and Tamil New Year Day 2"),
            (date(year, 5, 1), "May Day"),
            (date(year, 12, 25), "Christmas Day"),
        ]
        created = 0
        for h_date, name in holidays:
            _, was_created = Holiday.objects.get_or_create(
                name=name,
                date=h_date,
                defaults={
                    "holiday_type": HolidayType.PUBLIC,
                    "is_active": True,
                    "year": year,
                },
            )
            if was_created:
                created += 1
        return created

    def create_poya_holidays(self, year):
        """Create Poya day holidays (lunar calendar for 2026)."""
        poya_days = [
            (date(year, 1, 4), "Duruthu Full Moon Poya Day"),
            (date(year, 2, 3), "Navam Full Moon Poya Day"),
            (date(year, 3, 4), "Madin Full Moon Poya Day"),
            (date(year, 4, 3), "Bak Full Moon Poya Day"),
            (date(year, 5, 3), "Vesak Full Moon Poya Day"),
            (date(year, 6, 1), "Poson Full Moon Poya Day"),
            (date(year, 7, 1), "Esala Full Moon Poya Day"),
            (date(year, 7, 31), "Nikini Full Moon Poya Day"),
            (date(year, 8, 29), "Binara Full Moon Poya Day"),
            (date(year, 9, 28), "Vap Full Moon Poya Day"),
            (date(year, 10, 27), "Il Full Moon Poya Day"),
            (date(year, 11, 26), "Unduvap Full Moon Poya Day"),
        ]
        created = 0
        for h_date, name in poya_days:
            _, was_created = Holiday.objects.get_or_create(
                name=name,
                date=h_date,
                defaults={
                    "holiday_type": HolidayType.PUBLIC,
                    "is_active": True,
                    "year": year,
                },
            )
            if was_created:
                created += 1
        return created

    def create_optional_holidays(self, year):
        """Create optional/restricted holidays."""
        optional_holidays = [
            (date(year, 3, 14), "Maha Sivarathri Day"),
            (date(year, 4, 18), "Good Friday"),
            (date(year, 10, 22), "Deepavali"),
        ]
        created = 0
        for h_date, name in optional_holidays:
            _, was_created = Holiday.objects.get_or_create(
                name=name,
                date=h_date,
                defaults={
                    "holiday_type": HolidayType.OPTIONAL,
                    "is_active": True,
                    "year": year,
                },
            )
            if was_created:
                created += 1
        return created
