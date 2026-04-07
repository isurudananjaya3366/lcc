"""
Management command to rebuild the MPTT tree structure.

Recalculates lft, rght, tree_id, and level fields for all Category
nodes. Use this after direct SQL changes, bulk imports, or when the
tree structure appears corrupted.

Usage::

    python manage.py rebuild_tree
"""

from django.core.management.base import BaseCommand
from django.db import DatabaseError

from apps.products.models import Category


class Command(BaseCommand):
    """Rebuild the MPTT tree structure for categories."""

    help = (
        "Rebuild the MPTT tree structure (lft, rght, tree_id, level) "
        "for all categories. Use when the tree is corrupted or after "
        "bulk database operations."
    )

    def handle(self, *args, **options):
        self.stdout.write("Gathering pre-rebuild statistics...")

        total = Category.objects.count()
        if total == 0:
            self.stdout.write(
                self.style.WARNING("No categories found. Nothing to rebuild.")
            )
            return

        root_count = Category.objects.filter(parent__isnull=True).count()
        max_depth = (
            Category.objects.order_by("-level")
            .values_list("level", flat=True)
            .first()
        )

        self.stdout.write(f"  Total categories : {total}")
        self.stdout.write(f"  Root categories  : {root_count}")
        self.stdout.write(f"  Max tree depth   : {max_depth}")
        self.stdout.write("")
        self.stdout.write("Rebuilding MPTT tree...")

        try:
            Category.objects.rebuild()
        except DatabaseError as exc:
            self.stderr.write(
                self.style.ERROR(f"Tree rebuild failed: {exc}")
            )
            raise

        # Post-rebuild stats
        new_root_count = Category.objects.filter(parent__isnull=True).count()
        new_max_depth = (
            Category.objects.order_by("-level")
            .values_list("level", flat=True)
            .first()
        )

        self.stdout.write(
            self.style.SUCCESS("Tree rebuild completed successfully.")
        )
        self.stdout.write("")
        self.stdout.write("Post-rebuild statistics:")
        self.stdout.write(f"  Total categories : {total}")
        self.stdout.write(f"  Root categories  : {new_root_count}")
        self.stdout.write(f"  Max tree depth   : {new_max_depth}")
