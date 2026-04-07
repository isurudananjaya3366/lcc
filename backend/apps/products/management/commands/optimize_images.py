"""
Management command to batch-optimize existing product images.

Generates missing variants (thumbnail, medium, large) and WebP versions
for images that have already been uploaded.

Usage::

    python manage.py optimize_images
    python manage.py optimize_images --product-id <uuid>
    python manage.py optimize_images --force --dry-run
    python manage.py optimize_images --batch-size 50
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
    help = "Generate missing image variants and WebP conversions for existing product images."

    def add_arguments(self, parser):
        parser.add_argument(
            "--product-id",
            type=str,
            default=None,
            help="Only optimise images for a specific product (UUID).",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            default=False,
            help="Re-generate variants even if they already exist.",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=100,
            help="Process images in batches of this size (default 100).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Report what would be done without making changes.",
        )
        parser.add_argument(
            "--tenant",
            type=str,
            default=None,
            help="Only optimise images for a specific tenant schema name.",
        )
        parser.add_argument(
            "--async",
            action="store_true",
            default=False,
            dest="use_async",
            help="Queue Celery tasks instead of processing synchronously.",
        )

    def handle(self, **options):
        from apps.products.media.constants import (
            LARGE_SIZE,
            MEDIUM_SIZE,
            PROCESSING_STATUS_COMPLETED,
            THUMBNAIL_SIZE,
        )
        from apps.products.media.services.image_processor import ProductImageProcessor
        from apps.products.media.services.webp_converter import WebPConverter
        from apps.products.models import ProductImage

        product_id = options["product_id"]
        force = options["force"]
        batch_size = options["batch_size"]
        dry_run = options["dry_run"]
        tenant_schema = options.get("tenant")
        use_async = options.get("use_async", False)

        # Tenant scoping
        if tenant_schema:
            from django.db import connection

            from django_tenants.utils import schema_context

            with schema_context(tenant_schema):
                self._run_optimization(
                    product_id, force, batch_size, dry_run, use_async,
                    THUMBNAIL_SIZE, MEDIUM_SIZE, LARGE_SIZE, PROCESSING_STATUS_COMPLETED,
                )
        else:
            self._run_optimization(
                product_id, force, batch_size, dry_run, use_async,
                THUMBNAIL_SIZE, MEDIUM_SIZE, LARGE_SIZE, PROCESSING_STATUS_COMPLETED,
            )

    def _run_optimization(
        self, product_id, force, batch_size, dry_run, use_async,
        thumbnail_size, medium_size, large_size, status_completed,
    ):
        from apps.products.media.services.webp_converter import WebPConverter
        from apps.products.models import ProductImage

        qs = ProductImage.objects.all()
        if product_id:
            qs = qs.filter(product_id=product_id)
        if not force:
            qs = qs.exclude(
                processing_status=status_completed,
                thumbnail_path__gt="",
                medium_path__gt="",
                large_path__gt="",
                webp_thumbnail_path__gt="",
                webp_medium_path__gt="",
                webp_large_path__gt="",
            )

        total = qs.count()
        self.stdout.write(f"Found {total} image(s) to optimise.")

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run – no changes made."))
            return

        if use_async:
            from apps.products.media.tasks import process_image_variants

            queued = 0
            for image in qs.only("pk").iterator():
                process_image_variants.delay(str(image.pk))
                queued += 1
            self.stdout.write(
                self.style.SUCCESS(f"Queued {queued} Celery task(s) for async processing.")
            )
            return

        converter = WebPConverter()
        processed = 0
        errors = 0

        for batch_start in range(0, total, batch_size):
            batch = list(qs[batch_start : batch_start + batch_size])
            for image in batch:
                try:
                    self._process_image(
                        image, force, converter,
                        THUMBNAIL_SIZE, MEDIUM_SIZE, LARGE_SIZE,
                        PROCESSING_STATUS_COMPLETED,
                    )
                    processed += 1
                except Exception as exc:
                    errors += 1
                    logger.error(
                        "Error optimising ProductImage %s: %s",
                        image.pk,
                        exc,
                        exc_info=True,
                    )
            self.stdout.write(f"  Processed {min(batch_start + batch_size, total)}/{total}")

        self.stdout.write(
            self.style.SUCCESS(f"Done. Processed: {processed}, Errors: {errors}")
        )

    # ── Internal ────────────────────────────────────────────────────

    def _process_image(
        self,
        image,
        force: bool,
        converter,
        thumbnail_size,
        medium_size,
        large_size,
        status_completed,
    ):
        from apps.products.media.services.image_processor import ProductImageProcessor

        original_path = image.image.name
        with default_storage.open(original_path, "rb") as fh:
            original_bytes = fh.read()

        base_dir = os.path.dirname(original_path)
        stem = os.path.splitext(os.path.basename(original_path))[0]
        ext = os.path.splitext(original_path)[1].lower() or ".jpg"

        updates: dict = {}

        # Standard variants
        for size, size_name in (
            (thumbnail_size, "thumbnail"),
            (medium_size, "medium"),
            (large_size, "large"),
        ):
            attr = f"{size_name}_path"
            if not force and getattr(image, attr, ""):
                continue

            processor = ProductImageProcessor(io.BytesIO(original_bytes))
            try:
                processor.fix_orientation()
                processor.strip_exif()
                if size_name == "thumbnail":
                    processor.create_thumbnail()
                elif size_name == "medium":
                    processor.create_medium()
                else:
                    processor.create_large()

                fmt = _ext_to_format(ext)
                buf = processor.save_to_bytes(fmt=fmt)
                variant_path = os.path.join(
                    base_dir, "variants", f"{stem}_{size_name}{ext}"
                )
                saved = default_storage.save(variant_path, ContentFile(buf.read()))
                updates[attr] = saved
            finally:
                processor.close()

        # WebP variants
        for size_name in ("thumbnail", "medium", "large"):
            webp_attr = f"webp_{size_name}_path"
            if not force and getattr(image, webp_attr, ""):
                continue

            # Source = the standard variant we just created (or existing)
            source_path = updates.get(f"{size_name}_path") or getattr(
                image, f"{size_name}_path", ""
            )
            if not source_path:
                continue

            with default_storage.open(source_path, "rb") as fh:
                variant_bytes = fh.read()

            is_png = source_path.lower().endswith(".png")
            if is_png:
                webp_buf = converter.convert_png_to_webp(io.BytesIO(variant_bytes))
            else:
                webp_buf = converter.convert_jpeg_to_webp(io.BytesIO(variant_bytes))

            webp_path = os.path.join(
                base_dir, "variants", "webp", f"{stem}_{size_name}.webp"
            )
            saved = default_storage.save(webp_path, ContentFile(webp_buf.read()))
            updates[webp_attr] = saved

        # LQIP placeholder
        if force or not image.placeholder_data_uri:
            try:
                lqip = converter.generate_placeholder(io.BytesIO(original_bytes))
                updates["placeholder_data_uri"] = lqip
            except Exception:
                logger.debug("Could not generate LQIP for %s", image.pk)

        if updates:
            updates["processing_status"] = status_completed
            type(image).objects.filter(pk=image.pk).update(**updates)


def _ext_to_format(ext: str) -> str:
    mapping = {
        ".jpg": "JPEG",
        ".jpeg": "JPEG",
        ".png": "PNG",
        ".webp": "WEBP",
        ".gif": "GIF",
    }
    return mapping.get(ext.lower(), "JPEG")
