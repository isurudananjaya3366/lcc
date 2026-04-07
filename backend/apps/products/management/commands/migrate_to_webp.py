"""
Management command to migrate existing images to WebP format.

Converts JPEG / PNG product images to WebP, with options to filter
by source format, verify conversions, resume interrupted runs, and
optionally delete originals.

Usage::

    python manage.py migrate_to_webp
    python manage.py migrate_to_webp --source-format jpeg --verify
    python manage.py migrate_to_webp --delete-original --dry-run
    python manage.py migrate_to_webp --resume --batch-size 50
"""

from __future__ import annotations

import io
import logging
import os

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Migrate existing product images to WebP format."

    def add_arguments(self, parser):
        parser.add_argument(
            "--source-format",
            type=str,
            choices=["jpeg", "png", "all"],
            default="all",
            help="Only migrate images of this format (default: all).",
        )
        parser.add_argument(
            "--delete-original",
            action="store_true",
            default=False,
            help="Delete original variant files after successful WebP conversion.",
        )
        parser.add_argument(
            "--verify",
            action="store_true",
            default=False,
            help="Verify WebP files are readable after conversion.",
        )
        parser.add_argument(
            "--resume",
            action="store_true",
            default=False,
            help="Skip images that already have WebP variants.",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=100,
            help="Process images in batches of this size.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Report what would be done without making changes.",
        )

    def handle(self, **options):
        from apps.products.media.services.webp_converter import WebPConverter
        from apps.products.models import ProductImage

        source_format = options["source_format"]
        delete_original = options["delete_original"]
        verify = options["verify"]
        resume = options["resume"]
        batch_size = options["batch_size"]
        dry_run = options["dry_run"]

        qs = ProductImage.objects.all()

        # Filter by source format
        if source_format == "jpeg":
            qs = qs.filter(image__iendswith=".jpg") | qs.filter(
                image__iendswith=".jpeg"
            )
        elif source_format == "png":
            qs = qs.filter(image__iendswith=".png")

        # Resume: skip images that already have all WebP variants
        if resume:
            qs = qs.filter(
                webp_thumbnail_path="",
            ) | qs.filter(
                webp_medium_path="",
            ) | qs.filter(
                webp_large_path="",
            )

        total = qs.count()
        self.stdout.write(f"Found {total} image(s) to migrate.")

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run – no changes made."))
            return

        converter = WebPConverter()
        migrated = 0
        skipped = 0
        errors = 0

        for batch_start in range(0, total, batch_size):
            batch = list(qs[batch_start : batch_start + batch_size])
            for image in batch:
                try:
                    result = self._migrate_image(
                        image, converter, verify, delete_original
                    )
                    if result:
                        migrated += 1
                    else:
                        skipped += 1
                except Exception as exc:
                    errors += 1
                    logger.error(
                        "Error migrating ProductImage %s: %s",
                        image.pk,
                        exc,
                        exc_info=True,
                    )
            self.stdout.write(
                f"  Progress: {min(batch_start + batch_size, total)}/{total}"
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Migration complete. Migrated: {migrated}, Skipped: {skipped}, Errors: {errors}"
            )
        )

    # ── Internal ────────────────────────────────────────────────────

    def _migrate_image(
        self,
        image,
        converter,
        verify: bool,
        delete_original: bool,
    ) -> bool:
        """Migrate a single image's variants to WebP. Returns True if work done."""
        updates: dict = {}
        original_variants_to_delete: list[str] = []
        any_work = False

        for size_name in ("thumbnail", "medium", "large"):
            source_attr = f"{size_name}_path"
            webp_attr = f"webp_{size_name}_path"
            source_path = getattr(image, source_attr, "") or ""

            # Skip if no source variant or already has WebP
            if not source_path:
                continue
            if getattr(image, webp_attr, ""):
                continue

            # Read source variant
            with default_storage.open(source_path, "rb") as fh:
                source_bytes = fh.read()

            is_png = source_path.lower().endswith(".png")
            if is_png:
                webp_buf = converter.convert_png_to_webp(io.BytesIO(source_bytes))
            else:
                webp_buf = converter.convert_jpeg_to_webp(io.BytesIO(source_bytes))

            # Save WebP
            base_dir = os.path.dirname(source_path)
            stem = os.path.splitext(os.path.basename(source_path))[0]
            webp_path = os.path.join(base_dir, "webp", f"{stem}.webp")
            saved = default_storage.save(webp_path, ContentFile(webp_buf.read()))

            # Verify if requested
            if verify:
                self._verify_webp(saved)

            updates[webp_attr] = saved
            any_work = True

            if delete_original:
                original_variants_to_delete.append(source_path)

        if updates:
            type(image).objects.filter(pk=image.pk).update(**updates)

        # Delete originals only after DB update succeeds
        if delete_original and original_variants_to_delete:
            for path in original_variants_to_delete:
                try:
                    default_storage.delete(path)
                except Exception:
                    logger.warning("Could not delete original variant: %s", path)

        return any_work

    @staticmethod
    def _verify_webp(path: str):
        """Verify a WebP file is readable."""
        from PIL import Image

        with default_storage.open(path, "rb") as fh:
            img = Image.open(fh)
            img.verify()
