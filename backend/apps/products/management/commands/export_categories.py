"""
Management command to export categories to JSON.

Exports the category tree (or a subset) as a JSON document
suitable for backup, transfer, or re-import.

Usage::

    python manage.py export_categories
    python manage.py export_categories --output=categories.json
    python manage.py export_categories --active-only --indent=4
"""

import json
import sys

from django.core.management.base import BaseCommand

from apps.products.models import Category


class Command(BaseCommand):
    """Export categories to JSON format."""

    help = (
        "Export categories to JSON. Outputs to stdout by default; "
        "use --output to write to a file."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            type=str,
            default=None,
            help="File path to write JSON output (default: stdout).",
        )
        parser.add_argument(
            "--indent",
            type=int,
            default=2,
            help="JSON indentation level (default: 2).",
        )
        parser.add_argument(
            "--active-only",
            action="store_true",
            help="Export only active categories.",
        )

    def handle(self, *args, **options):
        queryset = Category.objects.all().order_by("tree_id", "lft")

        if options["active_only"]:
            queryset = queryset.filter(is_active=True)

        categories = []
        for cat in queryset:
            categories.append(
                {
                    "id": str(cat.id),
                    "name": cat.name,
                    "slug": cat.slug,
                    "parent_id": str(cat.parent_id) if cat.parent_id else None,
                    "description": cat.description,
                    "icon": cat.icon,
                    "is_active": cat.is_active,
                    "display_order": cat.display_order,
                    "level": cat.level,
                    "seo_title": cat.seo_title,
                    "seo_description": cat.seo_description,
                    "seo_keywords": cat.seo_keywords,
                }
            )

        json_output = json.dumps(categories, indent=options["indent"], ensure_ascii=False)

        output_path = options["output"]
        if output_path:
            try:
                with open(output_path, "w", encoding="utf-8") as fh:
                    fh.write(json_output)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Exported {len(categories)} categories to {output_path}"
                    )
                )
            except OSError as exc:
                self.stderr.write(
                    self.style.ERROR(f"Failed to write file: {exc}")
                )
                sys.exit(1)
        else:
            self.stdout.write(json_output)
