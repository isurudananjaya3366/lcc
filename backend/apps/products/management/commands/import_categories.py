"""
Management command to import categories from a JSON file.

Reads a JSON document (as produced by ``export_categories``) and
creates the corresponding Category objects while preserving the
parent-child hierarchy.

Usage::

    python manage.py import_categories --input=categories.json
    python manage.py import_categories --input=categories.json --clear
"""

import json
import sys

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from apps.products.models import Category


# Fields expected in each JSON record
REQUIRED_FIELDS = {"name", "slug"}


class Command(BaseCommand):
    """Import categories from a JSON file."""

    help = (
        "Import categories from a JSON file. The file should contain "
        "a JSON array of category objects (as exported by "
        "export_categories)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--input",
            type=str,
            required=True,
            help="Path to the JSON file to import.",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing categories before importing.",
        )

    def handle(self, *args, **options):
        input_path = options["input"]

        # ── Read & parse JSON ───────────────────────────────────────
        try:
            with open(input_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except FileNotFoundError:
            raise CommandError(f"File not found: {input_path}")
        except json.JSONDecodeError as exc:
            raise CommandError(f"Invalid JSON: {exc}")

        if not isinstance(data, list):
            raise CommandError(
                "Expected a JSON array of category objects."
            )

        # ── Validate records ────────────────────────────────────────
        for idx, record in enumerate(data):
            if not isinstance(record, dict):
                raise CommandError(
                    f"Record at index {idx} is not a JSON object."
                )
            missing = REQUIRED_FIELDS - record.keys()
            if missing:
                raise CommandError(
                    f"Record at index {idx} missing required fields: "
                    f"{', '.join(sorted(missing))}"
                )

        # ── Optionally clear ────────────────────────────────────────
        if options["clear"]:
            count = Category.objects.count()
            Category.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(
                    f"Deleted {count} existing categories."
                )
            )

        # ── Import in a transaction ─────────────────────────────────
        created_count = 0
        skipped_count = 0
        error_count = 0

        # Map old id → new Category instance for parent resolution
        id_map: dict[str, Category] = {}

        # Sort so that records without parent_id (roots) come first,
        # then by level if available, so parents are created before children.
        sorted_data = sorted(
            data,
            key=lambda r: (r.get("level", 0), r.get("display_order", 0)),
        )

        with transaction.atomic():
            for record in sorted_data:
                try:
                    parent = None
                    parent_id = record.get("parent_id")
                    if parent_id:
                        parent = id_map.get(parent_id)
                        if parent is None:
                            # Try resolving from the database (e.g. pre-existing)
                            try:
                                parent = Category.objects.get(id=parent_id)
                            except Category.DoesNotExist:
                                self.stderr.write(
                                    self.style.WARNING(
                                        f"  Parent {parent_id} not found for "
                                        f"'{record['name']}'; importing as root."
                                    )
                                )

                    slug = record.get("slug") or slugify(record["name"])

                    category, created = Category.objects.get_or_create(
                        slug=slug,
                        defaults={
                            "name": record["name"],
                            "description": record.get("description", ""),
                            "parent": parent,
                            "icon": record.get("icon", ""),
                            "is_active": record.get("is_active", True),
                            "display_order": record.get("display_order", 0),
                            "seo_title": record.get("seo_title", ""),
                            "seo_description": record.get("seo_description", ""),
                            "seo_keywords": record.get("seo_keywords", ""),
                        },
                    )

                    # Store in id_map using the record's original id
                    record_id = record.get("id")
                    if record_id:
                        id_map[record_id] = category

                    if created:
                        created_count += 1
                        self.stdout.write(f"  Created: {category.name}")
                    else:
                        skipped_count += 1
                        self.stdout.write(f"  Skipped (exists): {slug}")

                except Exception as exc:
                    error_count += 1
                    self.stderr.write(
                        self.style.ERROR(
                            f"  Error importing '{record.get('name', '?')}': {exc}"
                        )
                    )

        # ── Rebuild tree after import ───────────────────────────────
        if created_count > 0:
            Category.objects.rebuild()

        # ── Report ──────────────────────────────────────────────────
        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Import complete: {created_count} created, "
                f"{skipped_count} skipped, {error_count} errors."
            )
        )
        self.stdout.write(
            f"Total categories in database: {Category.objects.count()}"
        )

        if error_count:
            sys.exit(1)
