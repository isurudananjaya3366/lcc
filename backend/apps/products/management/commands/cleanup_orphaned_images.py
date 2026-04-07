"""
Management command to find and delete orphaned product image files.

Scans the media storage for product image files that have no matching
ProductImage or VariantImage database record, and optionally deletes them.

Usage::

    python manage.py cleanup_orphaned_images          # dry run
    python manage.py cleanup_orphaned_images --delete  # actually delete
"""

from __future__ import annotations

import logging
import os

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Find and remove orphaned product image files with no DB record."

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete",
            action="store_true",
            default=False,
            help="Actually delete orphaned files (default is dry-run).",
        )
        parser.add_argument(
            "--path",
            type=str,
            default="products/images",
            help="Storage sub-path to scan (default: products/images).",
        )

    def handle(self, *args, **options):
        from apps.products.models import ProductImage, VariantImage

        delete = options["delete"]
        scan_path = options["path"]
        verbosity = options["verbosity"]

        self.stdout.write(f"Scanning '{scan_path}' for orphaned image files...")
        if not delete:
            self.stdout.write(self.style.WARNING("DRY RUN — no files will be deleted."))

        # Collect all known paths from the DB
        known_paths: set[str] = set()

        for img in ProductImage.objects.values_list("image", flat=True).iterator():
            if img:
                known_paths.add(img)

        for img in VariantImage.objects.values_list("image", flat=True).iterator():
            if img:
                known_paths.add(img)

        # Also include variant paths (thumbnail, medium, large + webp)
        variant_fields = [
            "thumbnail_path",
            "medium_path",
            "large_path",
            "webp_thumbnail_path",
            "webp_medium_path",
            "webp_large_path",
        ]
        for field in variant_fields:
            for path in (
                ProductImage.objects.exclude(**{field: ""})
                .values_list(field, flat=True)
                .iterator()
            ):
                if path:
                    known_paths.add(path)
            for path in (
                VariantImage.objects.exclude(**{field: ""})
                .values_list(field, flat=True)
                .iterator()
            ):
                if path:
                    known_paths.add(path)

        # Walk storage directory
        orphaned: list[str] = []
        try:
            self._scan_directory(scan_path, known_paths, orphaned)
        except OSError as exc:
            self.stderr.write(self.style.ERROR(f"Error scanning storage: {exc}"))
            return

        if not orphaned:
            self.stdout.write(self.style.SUCCESS("No orphaned files found."))
            return

        self.stdout.write(f"Found {len(orphaned)} orphaned file(s):")
        for path in orphaned:
            if verbosity >= 2:
                self.stdout.write(f"  {path}")
            if delete:
                try:
                    default_storage.delete(path)
                    logger.info("Deleted orphaned file: %s", path)
                except OSError as exc:
                    logger.error("Failed to delete %s: %s", path, exc)

        if delete:
            self.stdout.write(
                self.style.SUCCESS(f"Deleted {len(orphaned)} orphaned file(s).")
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"Run with --delete to remove {len(orphaned)} orphaned file(s)."
                )
            )

    def _scan_directory(
        self,
        path: str,
        known_paths: set[str],
        orphaned: list[str],
    ):
        """Recursively walk a storage directory and collect orphaned files."""
        try:
            dirs, files = default_storage.listdir(path)
        except OSError:
            return

        for filename in files:
            file_path = os.path.join(path, filename).replace("\\", "/")
            if file_path not in known_paths:
                orphaned.append(file_path)

        for dirname in dirs:
            self._scan_directory(
                os.path.join(path, dirname).replace("\\", "/"),
                known_paths,
                orphaned,
            )
