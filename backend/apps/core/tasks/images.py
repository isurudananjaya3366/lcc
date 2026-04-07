"""
LankaCommerce Cloud – Celery Image Processing Tasks (SP10 Task 59).

Provides asynchronous image processing using Celery.  Large images
are optimised and thumbnailed in the background without blocking the
request/response cycle.

Usage::

    from apps.core.tasks.images import process_image_async

    process_image_async.delay(
        file_path='tenant-shop123/products/product.jpg',
        model_name='Product',
        instance_id=42,
        field_name='image',
    )
"""

from __future__ import annotations

import logging

from celery import shared_task
from django.apps import apps
from django.core.files.base import ContentFile

from apps.core.storage.images import ImageProcessor
from apps.core.storage.backends import get_storage_class
from apps.core.storage.constants import THUMBNAIL_SIZES

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, name="core.process_image_async")
def process_image_async(
    self,
    file_path: str,
    model_name: str | None = None,
    instance_id: int | None = None,
    field_name: str = "image",
    generate_thumbs: bool = True,
):
    """
    Process an image asynchronously.

    Applies web optimisation and generates thumbnails in the background.

    Args:
        file_path:       Path to image in storage.
        model_name:      Model class name (e.g. ``'Product'``).
        instance_id:     Model instance primary key.
        field_name:      Name of the image field on the model.
        generate_thumbs: Whether to generate thumbnails (default: ``True``).

    Returns:
        Dictionary with processing results.

    Retry policy:
        - Max retries: 3
        - Backoff: exponential – ``2 ** retry_count`` seconds.
        - Retries on: ``IOError``, ``OSError``.
    """
    try:
        # ── Stage 1: Load image ─────────────────────────────────────
        self.update_state(
            state="PROGRESS",
            meta={"status": "Loading image", "progress": 10},
        )

        storage = get_storage_class()

        with storage.open(file_path) as image_file:
            processor = ImageProcessor(image_file)

        logger.info("Processing image: %s", file_path)

        # ── Stage 2: Optimise ───────────────────────────────────────
        self.update_state(
            state="PROGRESS",
            meta={"status": "Optimizing image", "progress": 30},
        )

        processor.optimize_for_web(quality=85)

        optimized_io = processor.save(format="WEBP")
        optimized_path = file_path.rsplit(".", 1)[0] + "_optimized.webp"
        storage.save(optimized_path, ContentFile(optimized_io.read()))

        logger.info("Saved optimized image: %s", optimized_path)

        # ── Stage 3: Thumbnails ─────────────────────────────────────
        thumbnail_paths: dict[str, str] = {}

        if generate_thumbs:
            self.update_state(
                state="PROGRESS",
                meta={"status": "Generating thumbnails", "progress": 60},
            )

            thumbnails = processor.generate_thumbnails(THUMBNAIL_SIZES)

            for size_name, thumb_processor in thumbnails.items():
                base_name = file_path.rsplit(".", 1)[0]
                thumb_path = f"{base_name}_{size_name}.webp"

                thumb_io = thumb_processor.save(format="WEBP")
                storage.save(thumb_path, ContentFile(thumb_io.read()))
                thumbnail_paths[size_name] = thumb_path

                logger.info("Saved thumbnail: %s", thumb_path)

        # ── Stage 4: Update model ──────────────────────────────────
        if model_name and instance_id:
            self.update_state(
                state="PROGRESS",
                meta={"status": "Updating model", "progress": 90},
            )
            _update_model_instance(
                model_name, instance_id, field_name,
                optimized_path, thumbnail_paths,
            )

        return {
            "status": "success",
            "original_path": file_path,
            "optimized_path": optimized_path,
            "thumbnail_paths": thumbnail_paths,
            "progress": 100,
        }

    except (IOError, OSError) as exc:
        logger.warning("I/O error processing image, retrying: %s", exc)
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)

    except Exception as exc:
        logger.error("Error processing image: %s", exc, exc_info=True)
        return {
            "status": "error",
            "error": str(exc),
            "file_path": file_path,
        }


@shared_task(name="core.process_bulk_images")
def process_bulk_images(file_paths: list[str], **kwargs) -> list[str]:
    """
    Queue asynchronous processing for multiple images.

    Args:
        file_paths: List of storage file paths.
        **kwargs:   Additional arguments forwarded to ``process_image_async``.

    Returns:
        List of Celery task IDs.
    """
    task_ids: list[str] = []

    for file_path in file_paths:
        task = process_image_async.delay(file_path, **kwargs)
        task_ids.append(task.id)

    logger.info("Queued %d image processing tasks", len(task_ids))
    return task_ids


@shared_task(name="core.cleanup_temp_images")
def cleanup_temp_images():
    """
    Clean up temporary and orphaned image files.

    Intended for periodic execution via Celery Beat to remove:
    - Failed upload attempts
    - Orphaned temporary files
    - Old unprocessed images
    """
    logger.info("Running temporary image cleanup")
    # Implementation deferred to Group F / operational tasks.
    pass


# ════════════════════════════════════════════════════════════════════════
# Internal helpers
# ════════════════════════════════════════════════════════════════════════


def _update_model_instance(
    model_name: str,
    instance_id: int,
    field_name: str,
    optimized_path: str,
    thumbnail_paths: dict[str, str],
) -> None:
    """Update a model instance with optimised image paths."""
    try:
        model_class = apps.get_model("core", model_name)
        instance = model_class.objects.get(pk=instance_id)

        update_fields = [field_name]
        setattr(instance, field_name, optimized_path)

        for suffix in ("small", "medium", "large"):
            thumb_field = f"{field_name}_{suffix}"
            if hasattr(instance, thumb_field) and suffix in thumbnail_paths:
                setattr(instance, thumb_field, thumbnail_paths[suffix])
                update_fields.append(thumb_field)

        instance.save(update_fields=update_fields)
        logger.info("Updated %s instance %s", model_name, instance_id)

    except Exception as exc:
        logger.error("Error updating model instance: %s", exc)
