"""
LankaCommerce Cloud – File Validators (SP12 Tasks 41-43).

Validators for uploaded files: size limits, image dimensions, and
allowed file-extension whitelisting.

Validators:
    FileSizeValidator        — Enforce maximum file size (default 5 MB)
    ImageDimensionValidator  — Validate image width/height ranges (Pillow)
    FileExtensionValidator   — Whitelist allowed file extensions
"""

from __future__ import annotations

import os
from typing import Any

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


def _human_size(size_bytes: int) -> str:
    """Return a human-readable file-size string (e.g. ``'5.00 MB'``)."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


# ════════════════════════════════════════════════════════════════════════
# File Size Validator
# ════════════════════════════════════════════════════════════════════════

_DEFAULT_MAX_SIZE = 5 * 1024 * 1024  # 5 MB


@deconstructible
class FileSizeValidator:
    """
    Validate that a file does not exceed *max_size* bytes.

    Parameters:
        max_size: Maximum allowed size in **bytes** (default ``5242880`` = 5 MB).

    Error messages include both the actual file size and the limit in
    human-readable form.

    Usage::

        validator = FileSizeValidator()                  # 5 MB default
        validator = FileSizeValidator(10 * 1024 * 1024)  # 10 MB

        validator(uploaded_file)
    """

    code = "file_too_large"

    def __init__(self, max_size: int = _DEFAULT_MAX_SIZE) -> None:
        self.max_size = max_size

    def __call__(self, file: Any) -> None:
        # Support Django UploadedFile (has .size) and plain values for testing.
        size: int
        if hasattr(file, "size"):
            size = file.size
        elif isinstance(file, (int, float)):
            size = int(file)
        else:
            raise ValidationError(
                _("Cannot determine file size."),
                code=self.code,
            )

        if size > self.max_size:
            raise ValidationError(
                _(
                    "File size %(actual)s exceeds the maximum allowed size of %(limit)s."
                ),
                code=self.code,
                params={
                    "actual": _human_size(size),
                    "limit": _human_size(self.max_size),
                },
            )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, FileSizeValidator) and self.max_size == other.max_size


# ════════════════════════════════════════════════════════════════════════
# Image Dimension Validator
# ════════════════════════════════════════════════════════════════════════


@deconstructible
class ImageDimensionValidator:
    """
    Validate image width and height against configurable limits.

    Parameters:
        min_width:   Minimum width in pixels (or ``None`` to skip)
        min_height:  Minimum height in pixels (or ``None`` to skip)
        max_width:   Maximum width in pixels (or ``None`` to skip)
        max_height:  Maximum height in pixels (or ``None`` to skip)

    Requires the **Pillow** library.

    Use cases:
        * Product images: ``(800, 800, 2000, 2000)``
        * Thumbnails:     ``(100, 100, 300, 300)``
        * Banners:        ``(1920, 400, None, None)``

    Usage::

        validator = ImageDimensionValidator(
            min_width=800, min_height=800,
            max_width=2000, max_height=2000,
        )
        validator(uploaded_image_file)
    """

    code = "invalid_image_dimensions"

    def __init__(
        self,
        min_width: int | None = None,
        min_height: int | None = None,
        max_width: int | None = None,
        max_height: int | None = None,
    ) -> None:
        self.min_width = min_width
        self.min_height = min_height
        self.max_width = max_width
        self.max_height = max_height

    def __call__(self, file: Any) -> None:
        # Accept pre-resolved (width, height) tuple for easy testing.
        if isinstance(file, tuple) and len(file) == 2:
            width, height = file
        else:
            try:
                from PIL import Image  # type: ignore[import-untyped]
            except ImportError:  # pragma: no cover
                raise ValidationError(
                    _("Pillow library is required for image dimension validation."),
                    code=self.code,
                )

            try:
                # Rewind if the file has already been read.
                if hasattr(file, "seek"):
                    file.seek(0)
                img = Image.open(file)
                width, height = img.size
            except Exception:
                raise ValidationError(
                    _("Unable to read image dimensions. Ensure the file is a valid image."),
                    code=self.code,
                )

        errors: list[str] = []

        if self.min_width is not None and width < self.min_width:
            errors.append(f"Image width {width}px is less than the minimum {self.min_width}px.")

        if self.max_width is not None and width > self.max_width:
            errors.append(f"Image width {width}px exceeds the maximum {self.max_width}px.")

        if self.min_height is not None and height < self.min_height:
            errors.append(f"Image height {height}px is less than the minimum {self.min_height}px.")

        if self.max_height is not None and height > self.max_height:
            errors.append(f"Image height {height}px exceeds the maximum {self.max_height}px.")

        if errors:
            raise ValidationError(
                [ValidationError(_(msg), code=self.code) for msg in errors],
            )

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, ImageDimensionValidator)
            and self.min_width == other.min_width
            and self.min_height == other.min_height
            and self.max_width == other.max_width
            and self.max_height == other.max_height
        )


# ════════════════════════════════════════════════════════════════════════
# File Extension Validator
# ════════════════════════════════════════════════════════════════════════


@deconstructible
class FileExtensionValidator:
    """
    Validate that a file's extension is in the allowed list.

    Matching is **case-insensitive**.  Extensions may be specified with or
    without a leading dot.

    Parameters:
        allowed_extensions: Iterable of allowed extensions
                            (e.g. ``['pdf', 'docx', 'jpg']``).

    Common extension sets:
        * Images:    ``['jpg', 'jpeg', 'png', 'gif', 'webp']``
        * Documents: ``['pdf', 'doc', 'docx', 'xls', 'xlsx']``
        * Archives:  ``['zip', 'rar', 'tar', 'gz']``

    Usage::

        validator = FileExtensionValidator(['pdf', 'docx', 'jpg'])
        validator(uploaded_file)
    """

    code = "invalid_extension"

    def __init__(self, allowed_extensions: list[str] | tuple[str, ...]) -> None:
        # Normalize: lowercase, without leading dot.
        self.allowed_extensions: list[str] = [
            ext.lower().lstrip(".") for ext in allowed_extensions
        ]

    def __call__(self, file: Any) -> None:
        # Determine the filename.
        if isinstance(file, str):
            name = file
        elif hasattr(file, "name"):
            name = file.name
        else:
            raise ValidationError(
                _("Cannot determine file name."),
                code=self.code,
            )

        ext = os.path.splitext(name)[1].lower().lstrip(".")

        if not ext:
            raise ValidationError(
                _("File has no extension. Allowed extensions: %(allowed)s."),
                code=self.code,
                params={"allowed": ", ".join(self.allowed_extensions)},
            )

        if ext not in self.allowed_extensions:
            raise ValidationError(
                _(
                    "File extension '%(ext)s' is not allowed. "
                    "Allowed extensions: %(allowed)s."
                ),
                code=self.code,
                params={
                    "ext": ext,
                    "allowed": ", ".join(self.allowed_extensions),
                },
            )

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, FileExtensionValidator)
            and sorted(self.allowed_extensions) == sorted(other.allowed_extensions)
        )
