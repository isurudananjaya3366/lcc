"""Seed current Sri Lanka PAYE tax slabs."""

from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.payroll.models import PAYETaxSlab


PAYE_SLABS_2024 = [
    {"order": 0, "from_amount": Decimal("0.00"), "to_amount": Decimal("1200000.00"), "rate": Decimal("0.00")},
    {"order": 1, "from_amount": Decimal("1200001.00"), "to_amount": Decimal("1700000.00"), "rate": Decimal("6.00")},
    {"order": 2, "from_amount": Decimal("1700001.00"), "to_amount": Decimal("2200000.00"), "rate": Decimal("12.00")},
    {"order": 3, "from_amount": Decimal("2200001.00"), "to_amount": Decimal("2700000.00"), "rate": Decimal("18.00")},
    {"order": 4, "from_amount": Decimal("2700001.00"), "to_amount": Decimal("3200000.00"), "rate": Decimal("24.00")},
    {"order": 5, "from_amount": Decimal("3200001.00"), "to_amount": Decimal("3700000.00"), "rate": Decimal("30.00")},
    {"order": 6, "from_amount": Decimal("3700001.00"), "to_amount": None, "rate": Decimal("36.00")},
]


class Command(BaseCommand):
    help = "Seed current Sri Lanka PAYE tax slabs for 2024"

    def handle(self, *args, **options):
        tax_year = 2024
        created_slabs = 0
        for slab_data in PAYE_SLABS_2024:
            _, created = PAYETaxSlab.objects.get_or_create(
                tax_year=tax_year,
                order=slab_data["order"],
                defaults={
                    "from_amount": slab_data["from_amount"],
                    "to_amount": slab_data["to_amount"],
                    "rate": slab_data["rate"],
                },
            )
            if created:
                created_slabs += 1

        self.stdout.write(f"  Tax slabs: {created_slabs} new slabs for {tax_year}")
        self.stdout.write(self.style.SUCCESS("PAYE tax slabs seed complete"))
