"""
Management command to populate the database with sample/demo data.

This is a placeholder skeleton. Actual seeding logic will be
implemented in Phase 4-6 when models are available.

Usage:
    python manage.py seed_data
    python manage.py seed_data --tenant=demo
    python manage.py seed_data --minimal
    python manage.py seed_data --clear --force
"""

import os

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Populate the database with sample data for development and demos."""

    help = (
        "Seed the database with sample data for development. "
        "Use --minimal for a small data set, --clear to wipe first."
    )

    def add_arguments(self, parser):
        """Define command arguments."""
        parser.add_argument(
            "--tenant",
            type=str,
            default=None,
            help="Target tenant schema name to seed data into.",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            default=False,
            help="Clear existing data before seeding.",
        )
        parser.add_argument(
            "--minimal",
            action="store_true",
            default=False,
            help="Create a minimal data set instead of full demo data.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            default=False,
            help="Allow seeding in production (required with DJANGO_ENV=production).",
        )

    def handle(self, *args, **options):
        """Execute the seed data command."""
        tenant = options["tenant"]
        clear = options["clear"]
        minimal = options["minimal"]
        force = options["force"]

        # ── Safety checks ──────────────────────────────────────────
        environment = os.environ.get("DJANGO_ENV", "local")

        if environment == "production" and not force:
            self.stderr.write(
                self.style.ERROR(
                    "Seeding in production requires the --force flag. Aborting."
                )
            )
            raise SystemExit(1)

        # ── Start seeding ──────────────────────────────────────────
        target = tenant or "default"
        self.stdout.write(f"Seeding database for tenant: {target}")

        if clear:
            self._clear_data(tenant)

        # Run seed functions
        counts = {
            "users": self._seed_users(tenant, minimal),
            "products": self._seed_products(tenant, minimal),
            "customers": self._seed_customers(tenant, minimal),
            "transactions": self._seed_transactions(tenant, minimal),
        }

        # ── Summary ────────────────────────────────────────────────
        for category, count in counts.items():
            self.stdout.write(f"  Created {count} {category}")

        self.stdout.write(self.style.SUCCESS("Seed data complete!"))

    # ── Placeholder seed functions ─────────────────────────────────
    # These will be implemented in Phase 4-6 when models are created.

    def _clear_data(self, tenant=None):
        """Clear existing seeded data.

        TODO: Implement when models are available (Phase 4-6).
        """
        self.stdout.write(self.style.WARNING("Cleared existing data"))

    def _seed_users(self, tenant=None, minimal=False):
        """Seed demo users and staff accounts.

        TODO: Implement when User model is finalized (Phase 3).
        """
        return 0

    def _seed_products(self, tenant=None, minimal=False):
        """Seed sample products with categories and variants.

        TODO: Implement when Product models are created (Phase 4).
        """
        return 0

    def _seed_customers(self, tenant=None, minimal=False):
        """Seed demo customer records.

        TODO: Implement when Customer model is created (Phase 5).
        """
        return 0

    def _seed_transactions(self, tenant=None, minimal=False):
        """Seed sample orders and transactions.

        TODO: Implement when Order/Transaction models are created (Phase 5).
        """
        return 0
