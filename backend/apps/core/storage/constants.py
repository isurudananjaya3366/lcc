"""
LankaCommerce Cloud – Storage Constants (SP10 Tasks 45, 54-57, 67-72).

Signed-URL expiry values, thumbnail size presets, file-extension
configuration, size-limit helpers, and related utilities.

Usage::

    from apps.core.storage.constants import get_signed_url_expiry

    expiry = get_signed_url_expiry(file_type="invoice")
    expiry = get_signed_url_expiry(file_path="invoices/2026/01/INV-001.pdf")

    from apps.core.storage.constants import THUMB_SMALL, THUMBNAIL_SIZES

    size = get_thumbnail_size('product_list')  # (100, 100)

    from apps.core.storage.constants import (
        is_image_extension,
        is_document_extension,
        get_max_size_for_extension,
    )

    is_image_extension('.jpg')       # True
    get_max_size_for_extension('pdf') # 26_214_400
"""

from __future__ import annotations

# ════════════════════════════════════════════════════════════════════════
# Signed URL Expiry Times (seconds)
# ════════════════════════════════════════════════════════════════════════

SIGNED_URL_SHORT_EXPIRY: int = 1_800        # 30 minutes – quick previews
SIGNED_URL_DEFAULT_EXPIRY: int = 3_600      # 1 hour – general access
SIGNED_URL_MEDIUM_EXPIRY: int = 14_400      # 4 hours – reports, analysis
SIGNED_URL_LONG_EXPIRY: int = 86_400        # 24 hours – shared documents
SIGNED_URL_EXTENDED_EXPIRY: int = 604_800   # 7 days – archival access


# ════════════════════════════════════════════════════════════════════════
# File-Type → Expiry Mapping
# ════════════════════════════════════════════════════════════════════════
# More-sensitive file types get shorter expiry windows.

SIGNED_URL_EXPIRY_BY_TYPE: dict[str, int] = {
    "invoice": SIGNED_URL_DEFAULT_EXPIRY,
    "receipt": SIGNED_URL_DEFAULT_EXPIRY,
    "contract": SIGNED_URL_LONG_EXPIRY,
    "report": SIGNED_URL_MEDIUM_EXPIRY,
    "statement": SIGNED_URL_DEFAULT_EXPIRY,
    "document": SIGNED_URL_MEDIUM_EXPIRY,
    "image": SIGNED_URL_SHORT_EXPIRY,
}


# ════════════════════════════════════════════════════════════════════════
# Helper
# ════════════════════════════════════════════════════════════════════════


def get_signed_url_expiry(
    *,
    file_path: str | None = None,
    file_type: str | None = None,
) -> int:
    """
    Return the appropriate expiry (seconds) for a signed URL.

    Resolution order:
      1. Explicit *file_type* (e.g. ``"invoice"``).
      2. Inferred from *file_path* by substring match
         (e.g. ``"invoices/2026/01/INV-001.pdf"`` → ``"invoice"``).
      3. Fallback to ``SIGNED_URL_DEFAULT_EXPIRY``.

    Args:
        file_path: S3 key / relative path (optional).
        file_type: Logical file type string (optional).

    Returns:
        Expiry time in seconds.
    """
    if file_type:
        return SIGNED_URL_EXPIRY_BY_TYPE.get(
            file_type.lower(),
            SIGNED_URL_DEFAULT_EXPIRY,
        )

    if file_path:
        path_lower = file_path.lower()
        for ft, expiry in SIGNED_URL_EXPIRY_BY_TYPE.items():
            if ft in path_lower:
                return expiry

    return SIGNED_URL_DEFAULT_EXPIRY


# ════════════════════════════════════════════════════════════════════════
# Thumbnail Size Configuration (SP10 Tasks 54-57)
# ════════════════════════════════════════════════════════════════════════

"""
Standard thumbnail sizes for LankaCommerce Cloud.

These sizes are used consistently across:
- Product images
- User avatars
- Category images
- Document previews

All thumbnails are square for consistent layout.
"""

# Thumbnail Size Constants (width, height)
THUMB_SMALL: tuple[int, int] = (100, 100)    # List views, avatars, small grids
THUMB_MEDIUM: tuple[int, int] = (300, 300)   # Card layouts, medium grids
THUMB_LARGE: tuple[int, int] = (600, 600)    # Detail views, lightbox, hero images

# Thumbnail sizes dictionary for easy iteration
THUMBNAIL_SIZES: dict[str, tuple[int, int]] = {
    "small": THUMB_SMALL,
    "medium": THUMB_MEDIUM,
    "large": THUMB_LARGE,
}

# Thumbnail size by use case
THUMBNAIL_USE_CASES: dict[str, str] = {
    "product_list": "small",
    "product_grid": "medium",
    "product_detail": "large",
    "category_icon": "small",
    "user_avatar": "small",
    "cart_item": "small",
    "search_result": "medium",
    "featured_product": "large",
}


def get_thumbnail_size(name_or_use_case: str) -> tuple[int, int]:
    """
    Get thumbnail dimensions by name or use case.

    Args:
        name_or_use_case: Size name (``'small'``, ``'medium'``, ``'large'``)
                          or use case (``'product_list'``, etc.).

    Returns:
        ``(width, height)`` tuple.

    Examples::

        get_thumbnail_size('medium')        # (300, 300)
        get_thumbnail_size('product_list')  # (100, 100)
    """
    if name_or_use_case in THUMBNAIL_SIZES:
        return THUMBNAIL_SIZES[name_or_use_case]

    if name_or_use_case in THUMBNAIL_USE_CASES:
        size_name = THUMBNAIL_USE_CASES[name_or_use_case]
        return THUMBNAIL_SIZES[size_name]

    return THUMB_MEDIUM


def validate_thumbnail_size(size: tuple[int, int]) -> bool:
    """
    Validate whether *size* is a standard thumbnail size.

    Args:
        size: ``(width, height)`` tuple.

    Returns:
        ``True`` if *size* matches one of the standard presets.
    """
    return size in THUMBNAIL_SIZES.values()


# ════════════════════════════════════════════════════════════════════════
# FILE EXTENSION CONFIGURATION (SP10 Tasks 67-69)
# ════════════════════════════════════════════════════════════════════════

"""
Allowed file extensions for uploads.

These lists define which file types can be uploaded to the system.
Only add extensions that are absolutely necessary and safe.

Security Note:
- Never allow executable extensions (.exe, .bat, .sh, .com)
- Be careful with script extensions (.js, .php, .py)
- Review and validate all new extensions before adding

The **canonical** values live in ``config.settings.storage`` and are
re-exported here so that storage-module code can import from a single
place.  The helper functions below always read from Django settings at
call time so that runtime overrides (e.g. in tests) are honoured.
"""

# Image File Extensions
# Common image formats safe for upload.
# Riskier formats (SVG — can embed scripts) are included but
# should be sanitised before serving inline.
IMAGE_EXTENSIONS: set[str] = {
    ".jpg",    # JPEG — most common, good compression
    ".jpeg",   # JPEG alternative extension
    ".png",    # PNG — lossless, supports transparency
    ".gif",    # GIF — animations, limited colours
    ".webp",   # WebP — modern format, best compression
    ".bmp",    # Bitmap — uncompressed, large files
    ".svg",    # SVG — vector (sanitise before serving!)
    ".ico",    # Icon format
}

# Document File Extensions
# Business document formats for invoices, reports, contracts.
# Office files can contain macros — always scan for malware.
DOCUMENT_EXTENSIONS: set[str] = {
    ".pdf",    # PDF — preferred format
    ".doc",    # Microsoft Word (legacy)
    ".docx",   # Microsoft Word (modern)
    ".xls",    # Microsoft Excel (legacy)
    ".xlsx",   # Microsoft Excel (modern)
    ".csv",    # CSV — data import/export
    ".txt",    # Plain text
    ".rtf",    # Rich Text Format
}

# Archive File Extensions
ARCHIVE_EXTENSIONS: set[str] = {".zip", ".tar", ".gz", ".rar"}

# Union of all allowed extensions
ALL_ALLOWED_EXTENSIONS: set[str] = (
    IMAGE_EXTENSIONS | DOCUMENT_EXTENSIONS | ARCHIVE_EXTENSIONS
)


def is_image_extension(extension: str) -> bool:
    """
    Check whether *extension* is a valid image format.

    Accepts both ``'jpg'`` (without dot) and ``'.jpg'`` (with dot).
    """
    from django.conf import settings as _s

    exts: set[str] = getattr(_s, "IMAGE_EXTENSIONS", IMAGE_EXTENSIONS)
    ext = extension.lower() if extension.startswith(".") else f".{extension.lower()}"
    return ext in exts


def is_document_extension(extension: str) -> bool:
    """
    Check whether *extension* is a valid document format.

    Accepts both ``'pdf'`` (without dot) and ``'.pdf'`` (with dot).
    """
    from django.conf import settings as _s

    exts: set[str] = getattr(_s, "DOCUMENT_EXTENSIONS", DOCUMENT_EXTENSIONS)
    ext = extension.lower() if extension.startswith(".") else f".{extension.lower()}"
    return ext in exts


def is_archive_extension(extension: str) -> bool:
    """Check whether *extension* is a valid archive format."""
    from django.conf import settings as _s

    exts: set[str] = getattr(_s, "ARCHIVE_EXTENSIONS", ARCHIVE_EXTENSIONS)
    ext = extension.lower() if extension.startswith(".") else f".{extension.lower()}"
    return ext in exts


def get_allowed_extensions_by_type(file_type: str = "all") -> list[str]:
    """
    Return allowed extensions for a given file-type category.

    Args:
        file_type: ``'image'``, ``'document'``, ``'archive'``, or ``'all'``.

    Returns:
        Sorted list of extensions (with leading dot).
    """
    from django.conf import settings as _s

    if file_type == "image":
        return sorted(getattr(_s, "IMAGE_EXTENSIONS", IMAGE_EXTENSIONS))
    if file_type == "document":
        return sorted(getattr(_s, "DOCUMENT_EXTENSIONS", DOCUMENT_EXTENSIONS))
    if file_type == "archive":
        return sorted(getattr(_s, "ARCHIVE_EXTENSIONS", ARCHIVE_EXTENSIONS))
    if file_type == "all":
        return sorted(getattr(_s, "ALL_ALLOWED_EXTENSIONS", ALL_ALLOWED_EXTENSIONS))
    return []


# ════════════════════════════════════════════════════════════════════════
# FILE SIZE LIMITS (SP10 Tasks 70-72)
# ════════════════════════════════════════════════════════════════════════

"""
Maximum file sizes for uploads.

These limits protect against:
- Resource exhaustion (disk space, memory)
- Denial of Service (DoS) attacks
- Slow uploads on poor connections
- Processing timeouts

The actual numeric values are defined in ``config.settings.storage``.
Helper functions below resolve at call time via ``django.conf.settings``.
"""

# Size calculation helpers (for clarity in code that builds limits)
KB: int = 1024
MB: int = 1024 * KB
GB: int = 1024 * MB


def validate_image_size(
    file_size: int,
    image_type: str = "default",
) -> tuple[bool, int, str | None]:
    """
    Validate that *file_size* is within the limit for *image_type*.

    Args:
        file_size: Size in bytes.
        image_type: ``'default'``, ``'avatar'``, ``'product'``, or ``'banner'``.

    Returns:
        ``(is_valid, max_allowed, error_message | None)``.
    """
    from django.conf import settings as _s

    limits: dict[str, int] = {
        "default": getattr(_s, "MAX_IMAGE_SIZE", 5 * MB),
        "avatar": getattr(_s, "MAX_AVATAR_SIZE", 2 * MB),
        "product": getattr(_s, "MAX_IMAGE_SIZE", 5 * MB),
        "banner": getattr(_s, "MAX_BANNER_SIZE", 10 * MB),
    }
    max_size = limits.get(image_type, limits["default"])

    if file_size > max_size:
        return (
            False,
            max_size,
            f"Image size ({file_size / MB:.2f} MB) exceeds "
            f"maximum ({max_size / MB:.2f} MB)",
        )
    return (True, max_size, None)


def validate_document_size(
    file_size: int,
    document_type: str = "default",
) -> tuple[bool, int, str | None]:
    """
    Validate that *file_size* is within the limit for *document_type*.

    Args:
        file_size: Size in bytes.
        document_type: ``'default'``, ``'invoice'``, ``'report'``,
                       ``'contract'``, or ``'import'``.

    Returns:
        ``(is_valid, max_allowed, error_message | None)``.
    """
    from django.conf import settings as _s

    limits: dict[str, int] = {
        "default": getattr(_s, "MAX_DOCUMENT_SIZE", 25 * MB),
        "invoice": getattr(_s, "MAX_INVOICE_SIZE", 10 * MB),
        "report": getattr(_s, "MAX_REPORT_SIZE", 25 * MB),
        "contract": getattr(_s, "MAX_CONTRACT_SIZE", 50 * MB),
        "import": 50 * MB,
    }
    max_size = limits.get(document_type, limits["default"])

    if file_size > max_size:
        return (
            False,
            max_size,
            f"Document size ({file_size / MB:.2f} MB) exceeds "
            f"maximum ({max_size / MB:.2f} MB)",
        )
    return (True, max_size, None)


def get_max_size_for_extension(extension: str) -> int:
    """
    Return the maximum upload size (bytes) for a given extension.

    Falls back to 5 MB for unrecognised extensions.
    """
    from django.conf import settings as _s

    if is_image_extension(extension):
        return getattr(_s, "MAX_IMAGE_SIZE", 5 * MB)
    if is_document_extension(extension):
        return getattr(_s, "MAX_DOCUMENT_SIZE", 25 * MB)
    if is_archive_extension(extension):
        return getattr(_s, "MAX_DOCUMENT_SIZE", 25 * MB)
    return 5 * MB
