"""
Management command to load default account type configurations.

Loads the five fundamental account types (Asset, Liability, Equity,
Revenue, Expense) from the account_types.json fixture into the
AccountTypeConfig table.
"""

import json
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounting.models import AccountTypeConfig
from apps.accounting.models.enums import AccountType, NormalBalance

EXPECTED_TYPES = {t.value for t in AccountType}
EXPECTED_BALANCES = {b.value for b in NormalBalance}


class Command(BaseCommand):
    help = "Load default account type configurations from fixture."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Clear existing account type configs before loading.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview changes without writing to the database.",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Show detailed output for each account type loaded.",
        )

    def _validate_fixture(self, data: list[dict]) -> list[str]:
        """Return a list of validation error messages (empty == valid)."""
        errors: list[str] = []
        seen_types: set[str] = set()
        seen_orders: set[int] = set()

        for idx, record in enumerate(data):
            fields = record.get("fields", {})
            type_name = fields.get("type_name", "")
            normal_balance = fields.get("normal_balance", "")
            code_start = fields.get("code_start")
            code_end = fields.get("code_end")
            display_order = fields.get("display_order")

            if type_name not in EXPECTED_TYPES:
                errors.append(
                    f"Record {idx}: Invalid type_name '{type_name}'."
                )
            if normal_balance not in EXPECTED_BALANCES:
                errors.append(
                    f"Record {idx}: Invalid normal_balance '{normal_balance}'."
                )
            if code_start is not None and code_end is not None and code_end <= code_start:
                errors.append(
                    f"Record {idx}: code_end ({code_end}) must be > code_start ({code_start})."
                )
            if type_name in seen_types:
                errors.append(f"Record {idx}: Duplicate type_name '{type_name}'.")
            seen_types.add(type_name)

            if display_order in seen_orders:
                errors.append(f"Record {idx}: Duplicate display_order {display_order}.")
            if display_order is not None:
                seen_orders.add(display_order)

        return errors

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        verbose = options["verbose"]

        # ── Load & validate fixture ─────────────────────────────────
        fixture_path = (
            Path(__file__).resolve().parents[2] / "fixtures" / "account_types.json"
        )
        if not fixture_path.exists():
            self.stderr.write(
                self.style.ERROR(f"Fixture not found: {fixture_path}")
            )
            return

        try:
            data = json.loads(fixture_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            self.stderr.write(self.style.ERROR(f"Invalid JSON: {exc}"))
            return

        errors = self._validate_fixture(data)
        if errors:
            for err in errors:
                self.stderr.write(self.style.ERROR(err))
            return

        if verbose:
            self.stdout.write(f"Validated {len(data)} record(s) from fixture.")

        # ── Handle existing data ────────────────────────────────────
        existing = AccountTypeConfig.objects.count()

        if options["force"]:
            if dry_run:
                self.stdout.write(f"[DRY-RUN] Would clear {existing} existing config(s).")
            else:
                AccountTypeConfig.objects.all().delete()
                self.stdout.write(f"Cleared {existing} existing account type config(s).")
        elif existing:
            self.stdout.write(
                self.style.WARNING(
                    f"{existing} account type config(s) already exist. "
                    "Use --force to reload."
                )
            )
            return

        # ── Dry-run preview ─────────────────────────────────────────
        if dry_run:
            self.stdout.write("[DRY-RUN] Would load:")
            for record in data:
                f = record.get("fields", {})
                self.stdout.write(
                    f"  {f.get('type_name')}: {f.get('code_start')}-{f.get('code_end')} "
                    f"({f.get('normal_balance')}, order={f.get('display_order')})"
                )
            self.stdout.write(self.style.SUCCESS("[DRY-RUN] No changes written."))
            return

        # ── Load fixture inside a transaction ───────────────────────
        with transaction.atomic():
            call_command("loaddata", "account_types", app_label="accounting", verbosity=0)

        loaded = AccountTypeConfig.objects.count()

        if verbose:
            for atc in AccountTypeConfig.objects.all():
                self.stdout.write(
                    f"  ✓ {atc.type_name}: {atc.code_start}-{atc.code_end} "
                    f"({atc.normal_balance}, order={atc.display_order})"
                )

        self.stdout.write(
            self.style.SUCCESS(f"Loaded {loaded} account type configuration(s).")
        )
