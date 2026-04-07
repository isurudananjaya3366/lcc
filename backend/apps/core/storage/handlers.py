"""
LankaCommerce Cloud – Image Upload Handlers (SP10 Task 58).

Intercepts image uploads and applies appropriate processing based on
file size and type.  Small images are processed synchronously; large
images are queued for asynchronous Celery processing.

Usage::

    from apps.core.storage.handlers import handle_image_upload

    processed = handle_image_upload(uploaded_file, 'image', instance)
"""

from __future__ import annotations

import logging
from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile

from apps.core.storage.images import ImageProcessor
from apps.core.storage.constants import THUMBNAIL_SIZES

logger = logging.getLogger(__name__)

# Size threshold for async processing (1 MB in bytes)
ASYNC_PROCESSING_THRESHOLD: int = 1024 * 1024


# ════════════════════════════════════════════════════════════════════════
# Public API
# ════════════════════════════════════════════════════════════════════════


def handle_image_upload(uploaded_file, field_name: str = "image", instance=None):
    """
    Handle an image upload with automatic processing.

    Determines whether to process the image synchronously or
    asynchronously based on file size.

    Args:
        uploaded_file: Django ``UploadedFile`` object.
        field_name:    Name of the model image field.
        instance:      Model instance (used to update after async processing).

    Returns:
        Processed file (sync) or the original file (async – replaced later).

    Processing strategy:
        - Files < 1 MB → process immediately (synchronous).
        - Files ≥ 1 MB → queue for background processing (asynchronous).
    """
    try:
        file_size = uploaded_file.size

        logger.info(
            "Processing image upload: %s, size: %d bytes",
            uploaded_file.name,
            file_size,
        )

        # Small files: process synchronously
        if file_size < ASYNC_PROCESSING_THRESHOLD:
            return process_image_sync(uploaded_file)

        # Large files: queue for async processing
        from apps.core.storage.backends import get_storage_class

        storage = get_storage_class()
        file_path = storage.save(uploaded_file.name, uploaded_file)

        # Import here to avoid circular dependency
        from apps.core.tasks.images import process_image_async

        if instance and instance.pk:
            process_image_async.delay(
                file_path=file_path,
                model_name=instance.__class__.__name__,
                instance_id=instance.pk,
                field_name=field_name,
            )
        else:
            process_image_async.delay(file_path=file_path)

        logger.info("Queued async processing for %s", uploaded_file.name)
        return uploaded_file

    except Exception as e:
        logger.error("Error handling image upload: %s", e)
        return uploaded_file


def process_image_sync(uploaded_file):
    """
    Process an image synchronously.

    Applies web optimisation and returns a new ``InMemoryUploadedFile``
    containing the processed image data.

    Args:
        uploaded_file: Django ``UploadedFile`` object.

    Returns:
        Processed ``InMemoryUploadedFile``, or the original on error.
    """
    try:
        processor = ImageProcessor(uploaded_file)
        processor.optimize_for_web(quality=85)

        output_io = processor.save()

        # Derive a content type from the processor format
        fmt = (processor.format or "WEBP").lower()
        content_type = f"image/{fmt}"

        # Determine output size
        output_io.seek(0, 2)  # seek to end
        output_size = output_io.tell()
        output_io.seek(0)

        processed_file = InMemoryUploadedFile(
            file=output_io,
            field_name=getattr(uploaded_file, "field_name", None),
            name=uploaded_file.name,
            content_type=content_type,
            size=output_size,
            charset=None,
        )

        logger.info("Synchronously processed: %s", uploaded_file.name)
        return processed_file

    except Exception as e:
        logger.error("Error in sync processing: %s", e)
        return uploaded_file


def generate_thumbnails(image_path: str, save_to_storage: bool = True) -> dict[str, str]:
    """
    Generate all standard thumbnail sizes for an image already in storage.

    Args:
        image_path:       Path to the image file in storage.
        save_to_storage:  Whether to persist the thumbnails (default: ``True``).

    Returns:
        Dictionary ``{size_name: thumbnail_path}`` for saved thumbnails.
    """
    try:
        from apps.core.storage.backends import get_storage_class

        storage = get_storage_class()

        with storage.open(image_path) as image_file:
            processor = ImageProcessor(image_file)

        thumbnails = processor.generate_thumbnails(THUMBNAIL_SIZES)
        thumbnail_paths: dict[str, str] = {}

        if save_to_storage:
            for size_name, thumb_processor in thumbnails.items():
                base_name = image_path.rsplit(".", 1)[0]
                thumb_path = f"{base_name}_{size_name}.webp"

                thumb_io = thumb_processor.save(format="WEBP")
                storage.save(thumb_path, thumb_io)
                thumbnail_paths[size_name] = thumb_path

                logger.info("Saved thumbnail: %s", thumb_path)

        return thumbnail_paths

    except Exception as e:
        logger.error("Error generating thumbnails: %s", e)
        return {}
