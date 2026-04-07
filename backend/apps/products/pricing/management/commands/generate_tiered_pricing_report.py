"""
Management command: generate_tiered_pricing_report

Produces a summary of tiered pricing setup across all products,
including tier counts, unused tiers, and potential savings analysis.
"""

import csv
import sys
from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.products.pricing.models.tiered_pricing import TieredPricing
from apps.products.pricing.utils import format_lkr


class Command(BaseCommand):
    help = "Generate a tiered pricing report for all products with tier rules."

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv",
            action="store_true",
            help="Output in CSV format instead of table.",
        )

    def handle(self, *args, **options):
        tiers = (
            TieredPricing.objects.filter(is_active=True, is_deleted=False)
            .select_related("product")
            .order_by("product__name", "min_quantity")
        )

        if not tiers.exists():
            self.stdout.write(self.style.WARNING("No active tiered pricing rules found."))
            return

        if options["csv"]:
            self._output_csv(tiers)
        else:
            self._output_table(tiers)

        # Summary statistics
        products_with_tiers = tiers.values("product").distinct().count()
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Products with tiers: {products_with_tiers}"))
        self.stdout.write(self.style.SUCCESS(f"Total tier rules: {tiers.count()}"))

    def _output_table(self, tiers):
        self.stdout.write(
            f"{'Product':<30} {'Range':<20} {'Price':>12} {'Type':<12} {'Discount':>10}"
        )
        self.stdout.write("-" * 86)
        for t in tiers:
            name = str(t.product.name)[:28] if t.product else "?"
            self.stdout.write(
                f"{name:<30} {t.get_tier_range():<20} {format_lkr(t.tier_price):>12} "
                f"{t.tier_type:<12} {t.discount_percentage or '-':>10}"
            )

    def _output_csv(self, tiers):
        writer = csv.writer(sys.stdout)
        writer.writerow(["Product", "Range", "Min Qty", "Max Qty", "Tier Price", "Type", "Discount %"])
        for t in tiers:
            writer.writerow([
                str(t.product.name) if t.product else "?",
                t.get_tier_range(),
                t.min_quantity,
                t.max_quantity or "",
                str(t.tier_price),
                t.tier_type,
                str(t.discount_percentage) if t.discount_percentage else "",
            ])
