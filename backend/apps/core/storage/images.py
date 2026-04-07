"""
LankaCommerce Cloud – Image Processing Utilities (SP10 Tasks 47-53).

Provides the ``ImageProcessor`` class for image manipulation operations
including resizing, compression, format conversion, thumbnail generation,
and web optimisation using the Pillow library.

Usage::

    from apps.core.storage.images import ImageProcessor

    processor = ImageProcessor(uploaded_file)
    processor.optimize_for_web()
    output = processor.save()

Supported Formats:
    - JPEG (read/write) – photos, complex images
    - PNG  (read/write) – images with transparency
    - WebP (read/write) – web optimisation
    - GIF  (read/write) – simple animations
    - HEIC (read only)  – Apple device imports
"""

from __future__ import annotations

import io
import logging
import os
from io import BytesIO

from PIL import Image, ImageOps, ImageFilter

from django.conf import settings

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════
# ImageProcessor Class
# ════════════════════════════════════════════════════════════════════════


class ImageProcessor:
    """
    Image processing utility for LankaCommerce Cloud.

    Handles image manipulation operations including resizing, compression,
    format conversion, and thumbnail generation.

    Usage::

        processor = ImageProcessor(image_file)
        processor.resize(max_width=800, max_height=600)
        output = processor.save(format='JPEG', quality=85)

    Attributes:
        image: PIL Image object
        format: Original image format
        original_width: Original image width
        original_height: Original image height
    """

    def __init__(self, image_file):
        """
        Initialise ImageProcessor with an image file.

        Args:
            image_file: Django UploadedFile, file-like object, or file path string.
        """
        try:
            if hasattr(image_file, "read"):
                # File-like object – reset to start before opening
                image_file.seek(0)
                self.image = Image.open(image_file)
            else:
                # File path
                self.image = Image.open(image_file)

            # Force load so we can close the underlying file handle
            self.image.load()

            # Store original properties
            self.format = self.image.format or "JPEG"
            self.original_width, self.original_height = self.image.size

            # Convert RGBA to RGB for JPEG compatibility
            if self.image.mode == "RGBA" and self.format == "JPEG":
                self.image = self.image.convert("RGB")

            # Internal compression settings (set by compress())
            self._compression_quality: int = getattr(settings, "IMAGE_QUALITY", 85)
            self._compression_optimize: bool = True

        except Exception as e:
            logger.error("Failed to load image: %s", e)
            raise

    # ── Properties ──────────────────────────────────────────────────

    @property
    def width(self) -> int:
        """Get current image width."""
        return self.image.size[0]

    @property
    def height(self) -> int:
        """Get current image height."""
        return self.image.size[1]

    @property
    def aspect_ratio(self) -> float:
        """Calculate image aspect ratio (width / height)."""
        return self.width / self.height if self.height > 0 else 1.0

    # ── Task 49: resize ─────────────────────────────────────────────

    def resize(
        self,
        max_width: int | None = None,
        max_height: int | None = None,
        mode: str = "fit",
    ) -> "ImageProcessor":
        """
        Resize image to fit within specified dimensions.

        Args:
            max_width:  Maximum width in pixels (``None`` = no limit).
            max_height: Maximum height in pixels (``None`` = no limit).
            mode:       Resize mode – ``'fit'``, ``'fill'``, or ``'exact'``.

        Returns:
            ``self`` (for method chaining).

        Modes:
            - **fit**:   Scale to fit within dimensions, maintain aspect ratio.
            - **fill**:  Scale and crop to fill dimensions exactly.
            - **exact**: Resize to exact dimensions, may distort.
        """
        if not max_width and not max_height:
            logger.warning("No dimensions specified for resize")
            return self

        current_width, current_height = self.image.size

        # Don't upscale images
        if (
            max_width
            and max_width >= current_width
            and max_height
            and max_height >= current_height
        ):
            logger.info("Image already smaller than target dimensions")
            return self

        if mode == "fit":
            self.image.thumbnail(
                (max_width or current_width, max_height or current_height),
                Image.Resampling.LANCZOS,
            )
        elif mode == "fill":
            if not max_width or not max_height:
                raise ValueError("fill mode requires both max_width and max_height")
            self.image = ImageOps.fit(
                self.image,
                (max_width, max_height),
                Image.Resampling.LANCZOS,
            )
        elif mode == "exact":
            if not max_width or not max_height:
                raise ValueError("exact mode requires both max_width and max_height")
            self.image = self.image.resize(
                (max_width, max_height),
                Image.Resampling.LANCZOS,
            )
        else:
            raise ValueError(f"Unknown resize mode: {mode}")

        logger.info(
            "Resized from %dx%d to %dx%d (mode=%s)",
            current_width,
            current_height,
            self.image.size[0],
            self.image.size[1],
            mode,
        )
        return self

    # ── Task 50: compress & save ────────────────────────────────────

    def compress(self, quality: int = 85, optimize: bool = True) -> "ImageProcessor":
        """
        Configure compression settings for the next ``save()`` call.

        Args:
            quality:  Compression quality 1-100 (default: 85).
            optimize: Enable format-specific optimisation (default: ``True``).

        Returns:
            ``self`` (for method chaining).

        Quality guide:
            - 60: Low quality, small file size (thumbnails)
            - 75: Medium quality, balanced (web images)
            - 85: High quality, good balance (recommended)
            - 95: Maximum quality, large file size (hero images)
        """
        self._compression_quality = max(1, min(100, quality))
        self._compression_optimize = optimize
        logger.info(
            "Compression configured: quality=%d, optimize=%s",
            self._compression_quality,
            optimize,
        )
        return self

    def save(self, output=None, format: str | None = None, **kwargs) -> BytesIO | None:
        """
        Save processed image to a file path or ``BytesIO``.

        Args:
            output: Output file path or ``BytesIO`` (``None`` → return new ``BytesIO``).
            format: Output format (``JPEG``, ``PNG``, ``WEBP``, etc.).
            **kwargs: Extra keyword arguments forwarded to ``PIL.Image.save``.

        Returns:
            ``BytesIO`` object when *output* is ``None``, otherwise ``None``.
        """
        if not format:
            format = self.format or "JPEG"
        format = format.upper()

        return_bytes = output is None
        output_io: BytesIO | object = BytesIO() if return_bytes else output

        save_kwargs: dict = {
            "format": format,
            "optimize": self._compression_optimize,
        }

        # Format-specific settings
        if format in ("JPEG", "JPG"):
            save_kwargs["quality"] = self._compression_quality
            save_kwargs["progressive"] = True
            if self.image.mode not in ("RGB", "L"):
                self.image = self.image.convert("RGB")

        elif format == "PNG":
            # PNG is lossless – optimize only
            pass

        elif format == "WEBP":
            save_kwargs["quality"] = self._compression_quality
            save_kwargs["method"] = 6  # Maximum compression effort

        save_kwargs.update(kwargs)
        self.image.save(output_io, **save_kwargs)

        if return_bytes:
            output_io.seek(0)
            return output_io

        logger.info("Image saved: format=%s", format)
        return None

    # ── Task 51: convert_format ─────────────────────────────────────

    def convert_format(
        self,
        target_format: str,
        background_color: tuple[int, int, int] = (255, 255, 255),
    ) -> "ImageProcessor":
        """
        Convert image to a different format.

        Args:
            target_format:    Target format (``JPEG``, ``PNG``, ``WEBP``).
            background_color: RGB tuple used when removing transparency
                              (default: white).

        Returns:
            ``self`` (for method chaining).
        """
        target_format = target_format.upper()
        supported_formats = {"JPEG", "JPG", "PNG", "WEBP"}

        if target_format not in supported_formats:
            raise ValueError(
                f"Unsupported format: {target_format}. "
                f"Supported: {', '.join(sorted(supported_formats))}"
            )

        if target_format in ("JPEG", "JPG"):
            if self.image.mode in ("RGBA", "LA", "P"):
                rgb_image = Image.new("RGB", self.image.size, background_color)
                if self.image.mode == "P":
                    self.image = self.image.convert("RGBA")
                rgb_image.paste(self.image, mask=self.image.split()[-1])
                self.image = rgb_image
            elif self.image.mode != "RGB":
                self.image = self.image.convert("RGB")
            self.format = "JPEG"

        elif target_format == "PNG":
            if self.image.mode not in ("RGB", "RGBA"):
                self.image = self.image.convert("RGBA")
            self.format = "PNG"

        elif target_format == "WEBP":
            if self.image.mode not in ("RGB", "RGBA"):
                self.image = self.image.convert("RGBA")
            self.format = "WEBP"

        logger.info("Converted image to %s", self.format)
        return self

    # ── Task 52: generate_thumbnail / generate_thumbnails ───────────

    def generate_thumbnail(
        self,
        size: tuple[int, int] | int,
        crop: str = "center",
    ) -> "ImageProcessor":
        """
        Generate a thumbnail at the specified size.

        Args:
            size: ``(width, height)`` tuple or single ``int`` for square.
            crop: Crop position – ``'center'``, ``'top'``, ``'bottom'``.

        Returns:
            New ``ImageProcessor`` instance containing the thumbnail.
        """
        if isinstance(size, int):
            size = (size, size)

        thumb_image = self.image.copy()

        centering = {
            "center": (0.5, 0.5),
            "top": (0.5, 0.0),
            "bottom": (0.5, 1.0),
        }.get(crop, (0.5, 0.5))

        thumb_image = ImageOps.fit(
            thumb_image,
            size,
            Image.Resampling.LANCZOS,
            centering=centering,
        )

        thumb_processor = ImageProcessor.__new__(ImageProcessor)
        thumb_processor.image = thumb_image
        thumb_processor.format = self.format
        thumb_processor.original_width = self.original_width
        thumb_processor.original_height = self.original_height
        thumb_processor._compression_quality = self._compression_quality
        thumb_processor._compression_optimize = self._compression_optimize

        logger.info("Generated thumbnail: %dx%d", size[0], size[1])
        return thumb_processor

    def generate_thumbnails(
        self,
        sizes: dict[str, tuple[int, int]] | list[tuple[int, int]],
    ) -> dict[str, "ImageProcessor"]:
        """
        Generate multiple thumbnails at different sizes.

        Args:
            sizes: A ``dict`` mapping name → ``(w, h)`` or a list of
                   ``(w, h)`` tuples.

        Returns:
            Dictionary ``{name_or_key: ImageProcessor}`` with thumbnail instances.
        """
        thumbnails: dict[str, ImageProcessor] = {}

        if isinstance(sizes, dict):
            for name, size in sizes.items():
                thumbnails[name] = self.generate_thumbnail(size)
        else:
            for size in sizes:
                key = f"{size[0]}x{size[1]}"
                thumbnails[key] = self.generate_thumbnail(size)

        logger.info("Generated %d thumbnails", len(thumbnails))
        return thumbnails

    # ── Task 53: optimize_for_web ───────────────────────────────────

    def optimize_for_web(
        self,
        max_width: int = 1920,
        max_height: int = 1920,
        target_format: str = "WEBP",
        quality: int = 85,
        strip_metadata: bool = True,
    ) -> "ImageProcessor":
        """
        Optimise image for web delivery.

        Pipeline:
            1. Apply EXIF orientation.
            2. Resize to max dimensions.
            3. Convert to web-friendly format (WebP preferred).
            4. Configure compression.
            5. Strip unnecessary metadata (EXIF, GPS, camera info).

        Args:
            max_width:      Maximum width in pixels (default: 1920).
            max_height:     Maximum height in pixels (default: 1920).
            target_format:  Preferred format – ``WEBP``, ``JPEG``, ``PNG``.
            quality:        Compression quality 1-100 (default: 85).
            strip_metadata: Remove EXIF and other metadata (default: ``True``).

        Returns:
            ``self`` (for method chaining).
        """
        # Step 1: Handle image orientation from EXIF
        try:
            self.image = ImageOps.exif_transpose(self.image)
        except Exception:
            pass  # No EXIF orientation data

        # Step 2: Resize if larger than max dimensions
        current_width, current_height = self.image.size
        if current_width > max_width or current_height > max_height:
            self.resize(max_width=max_width, max_height=max_height, mode="fit")
            logger.info(
                "Resized for web: %dx%d → %dx%d",
                current_width,
                current_height,
                self.width,
                self.height,
            )

        # Step 3: Convert to target format
        self.convert_format(target_format)

        # Step 4: Apply compression
        self.compress(quality=quality, optimize=True)

        # Step 5: Strip metadata if requested
        if strip_metadata:
            data = list(self.image.getdata())
            image_without_exif = Image.new(self.image.mode, self.image.size)
            image_without_exif.putdata(data)
            self.image = image_without_exif
            logger.info("Stripped image metadata")

        logger.info(
            "Web optimisation complete: format=%s, size=%dx%d, quality=%d",
            self.format,
            self.width,
            self.height,
            quality,
        )
        return self

    def optimize_for_responsive(
        self,
        sizes: list[int] | None = None,
    ) -> dict[int, BytesIO]:
        """
        Generate responsive image set with multiple widths.

        Creates optimised versions at different sizes suitable for
        the HTML ``srcset`` attribute.

        Args:
            sizes: List of max widths (default: ``[320, 640, 1024, 1920]``).

        Returns:
            Dictionary ``{width: BytesIO}`` with optimised image data.
        """
        if sizes is None:
            sizes = [320, 640, 1024, 1920]

        responsive_images: dict[int, BytesIO] = {}

        for max_width in sizes:
            if self.width <= max_width:
                continue

            copy_processor = ImageProcessor.__new__(ImageProcessor)
            copy_processor.image = self.image.copy()
            copy_processor.format = self.format
            copy_processor.original_width = self.original_width
            copy_processor.original_height = self.original_height
            copy_processor._compression_quality = self._compression_quality
            copy_processor._compression_optimize = self._compression_optimize

            copy_processor.optimize_for_web(max_width=max_width)
            output = copy_processor.save()
            responsive_images[max_width] = output

            logger.info("Generated responsive variant: %dw", max_width)

        return responsive_images

    # ── Legacy static helper (backward compatibility) ───────────────

    @staticmethod
    def create_thumbnail(
        image_file,
        size: tuple[int, int] | None = None,
        quality: int | None = None,
        output_format: str | None = None,
    ) -> BytesIO:
        """Return a ``BytesIO`` thumbnail of *image_file* (legacy helper)."""
        size = size or getattr(settings, "THUMB_MEDIUM", (300, 300))
        quality = quality or getattr(settings, "IMAGE_QUALITY", 85)
        output_format = output_format or getattr(settings, "IMAGE_FORMAT", "WEBP")

        img = Image.open(image_file)
        img.thumbnail(size, Image.Resampling.LANCZOS)

        if img.mode in ("RGBA", "P") and output_format.upper() == "JPEG":
            img = img.convert("RGB")

        buffer = BytesIO()
        img.save(buffer, format=output_format, quality=quality)
        buffer.seek(0)
        return buffer


# ════════════════════════════════════════════════════════════════════════
# Utility Functions
# ════════════════════════════════════════════════════════════════════════


def get_image_dimensions(image_file) -> tuple[int, int]:
    """
    Return ``(width, height)`` of an image file without full processing.
    """
    img = Image.open(image_file)
    return img.size


def calculate_aspect_ratio(width: int, height: int) -> float:
    """Return the aspect ratio ``width / height``."""
    return width / height if height > 0 else 1.0


def is_valid_image(image_file) -> bool:
    """
    Verify that *image_file* is a readable image.

    Returns ``True`` if Pillow can open and verify the file.
    """
    try:
        if hasattr(image_file, "seek"):
            image_file.seek(0)
        img = Image.open(image_file)
        img.verify()
        return True
    except Exception:
        return False
