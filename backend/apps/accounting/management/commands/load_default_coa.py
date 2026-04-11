"""
Management command to load the default chart of accounts.

Creates all accounts defined in ``apps.accounting.data.default_accounts``
within the current tenant schema, preserving parent-child hierarchy.
"""

from django.core.management.base import BaseCommand

from apps.accounting.data.default_accounts import DEFAULT_ACCOUNTS
from apps.accounting.models import Account


class Command(BaseCommand):
    help = "Load the default chart of accounts for the current tenant."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Delete existing accounts and reload from scratch.",
        )

    def handle(self, *args, **options):
        if options["force"]:
            # Delete leaf-first to respect PROTECT on parent FK.
            deleted = 0
            while Account.objects.exists():
                leaves = Account.objects.filter(children__isnull=True)
                count, _ = leaves.delete()
                deleted += count
            self.stdout.write(f"Deleted {deleted} existing account(s).")

        if Account.objects.exists() and not options["force"]:
            self.stdout.write(
                self.style.WARNING(
                    "Accounts already exist. Use --force to replace them."
                )
            )
            return

        # Build a code → Account lookup for parent resolution.
        code_map: dict[str, Account] = {}
        created = 0

        for entry in DEFAULT_ACCOUNTS:
            parent_code = entry.get("parent_code")
            parent = code_map.get(parent_code) if parent_code else None

            account, was_created = Account.objects.get_or_create(
                code=entry["code"],
                defaults={
                    "name": entry["name"],
                    "account_type": entry["account_type"],
                    "is_header": entry.get("is_header", False),
                    "is_system": entry.get("is_system", False),
                    "description": entry.get("description", ""),
                    "parent": parent,
                },
            )
            code_map[entry["code"]] = account
            if was_created:
                created += 1

        # Rebuild the MPTT tree to ensure consistent lft/rght values.
        Account.objects.rebuild()

        self.stdout.write(
            self.style.SUCCESS(
                f"Loaded {created} account(s) into the default chart of accounts."
            )
        )
