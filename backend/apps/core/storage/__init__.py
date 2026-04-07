"""
File Storage Module
===================

Tenant-isolated file storage backends, image processing, and path utilities.

Usage::

    # Image processing
    from apps.core.storage import ImageProcessor

    processor = ImageProcessor(uploaded_file)
    processor.optimize_for_web()
    output = processor.save()

    # Upload handling
    from apps.core.storage import handle_image_upload

    processed_image = handle_image_upload(uploaded_file)

    # Thumbnail constants
    from apps.core.storage import THUMB_SMALL, THUMB_MEDIUM, THUMB_LARGE

    thumb = processor.generate_thumbnail(THUMB_MEDIUM)

    # In models.py
    from apps.core.storage import TenantMediaStorage, product_path

    class Product(models.Model):
        image = models.ImageField(
            upload_to=product_path,
            storage=TenantMediaStorage(),
        )

Exports:
    Storage Backends:
        - TenantFileStorage: Base tenant-aware storage
        - TenantMediaStorage: Preconfigured tenant media storage
        - TenantS3Storage: S3 tenant-aware storage (production)
        - PrivateTenantS3Storage: Private S3 storage (signed URLs)
        - PublicTenantS3Storage: Public S3 storage (CDN-friendly)
        - PublicStorage: Shared public file storage
        - get_storage_class: Factory for storage backend instances

    Path Utilities:
        - product_path: Date-organized product images
        - invoice_path: Invoice number-based paths
        - document_path: Type-organized documents
        - avatar_path: User ID-based avatars
        - tenant_upload_path: Generic tenant-scoped uploads

    S3 Utilities:
        - generate_signed_url: Generate a pre-signed S3 URL
        - generate_bulk_signed_urls: Generate signed URLs in bulk

    Constants:
        - get_signed_url_expiry: Resolve expiry by file type/path
        - SIGNED_URL_DEFAULT_EXPIRY, SIGNED_URL_SHORT_EXPIRY, …
        - THUMB_SMALL, THUMB_MEDIUM, THUMB_LARGE, THUMBNAIL_SIZES
        - get_thumbnail_size, validate_thumbnail_size

    Image Processing:
        - ImageProcessor: Image resizing, compression, web optimisation
        - handle_image_upload: Smart sync/async upload handler
        - process_image_sync: Synchronous image processing
        - generate_thumbnails: Generate all standard thumbnails

    Validators:
        - FileValidator: Upload validation
        - get_image_validator: Pre-configured image validator
        - get_document_validator: Pre-configured document validator
        - get_avatar_validator: Pre-configured avatar validator
        - get_invoice_validator: Pre-configured invoice validator

    Extension / Size Helpers:
        - IMAGE_EXTENSIONS, DOCUMENT_EXTENSIONS, ARCHIVE_EXTENSIONS
        - ALL_ALLOWED_EXTENSIONS
        - is_image_extension, is_document_extension, is_archive_extension
        - get_allowed_extensions_by_type
        - KB, MB, GB
        - validate_image_size, validate_document_size
        - get_max_size_for_extension

    Cleanup Utilities:
        - FileCleanup: Orphaned-file cleanup class
        - cleanup_old_files: Convenience function
"""

from apps.core.storage.backends import (
    PrivateTenantS3Storage,
    PublicTenantS3Storage,
    TenantFileStorage,
    TenantMediaStorage,
    TenantS3Storage,
    PublicStorage,
    get_storage_class,
)
from apps.core.storage.constants import (
    SIGNED_URL_DEFAULT_EXPIRY,
    SIGNED_URL_EXTENDED_EXPIRY,
    SIGNED_URL_EXPIRY_BY_TYPE,
    SIGNED_URL_LONG_EXPIRY,
    SIGNED_URL_MEDIUM_EXPIRY,
    SIGNED_URL_SHORT_EXPIRY,
    get_signed_url_expiry,
    # Thumbnail sizes (SP10 Tasks 54-57)
    THUMB_SMALL,
    THUMB_MEDIUM,
    THUMB_LARGE,
    THUMBNAIL_SIZES,
    THUMBNAIL_USE_CASES,
    get_thumbnail_size,
    validate_thumbnail_size,
    # Extension configuration (SP10 Tasks 67-69)
    IMAGE_EXTENSIONS,
    DOCUMENT_EXTENSIONS,
    ARCHIVE_EXTENSIONS,
    ALL_ALLOWED_EXTENSIONS,
    is_image_extension,
    is_document_extension,
    is_archive_extension,
    get_allowed_extensions_by_type,
    # Size helpers (SP10 Tasks 70-72)
    KB,
    MB,
    GB,
    validate_image_size,
    validate_document_size,
    get_max_size_for_extension,
)
from apps.core.storage.paths import (
    product_path,
    invoice_path,
    document_path,
    avatar_path,
    tenant_upload_path,
)
from apps.core.storage.s3 import generate_signed_url, generate_bulk_signed_urls
from apps.core.storage.images import ImageProcessor
from apps.core.storage.handlers import (
    handle_image_upload,
    process_image_sync,
    generate_thumbnails,
)
from apps.core.storage.validators import (
    FileValidator,
    get_image_validator,
    get_document_validator,
    get_avatar_validator,
    get_invoice_validator,
)
from apps.core.storage.cleanup import FileCleanup, cleanup_old_files

__all__ = [
    # Backends
    "TenantFileStorage",
    "TenantMediaStorage",
    "TenantS3Storage",
    "PrivateTenantS3Storage",
    "PublicTenantS3Storage",
    "PublicStorage",
    "get_storage_class",
    # Path utilities
    "product_path",
    "invoice_path",
    "document_path",
    "avatar_path",
    "tenant_upload_path",
    # S3 utilities
    "generate_signed_url",
    "generate_bulk_signed_urls",
    # Signed URL constants
    "SIGNED_URL_DEFAULT_EXPIRY",
    "SIGNED_URL_SHORT_EXPIRY",
    "SIGNED_URL_MEDIUM_EXPIRY",
    "SIGNED_URL_LONG_EXPIRY",
    "SIGNED_URL_EXTENDED_EXPIRY",
    "SIGNED_URL_EXPIRY_BY_TYPE",
    "get_signed_url_expiry",
    # Thumbnail constants (SP10 Tasks 54-57)
    "THUMB_SMALL",
    "THUMB_MEDIUM",
    "THUMB_LARGE",
    "THUMBNAIL_SIZES",
    "THUMBNAIL_USE_CASES",
    "get_thumbnail_size",
    "validate_thumbnail_size",
    # Image processing
    "ImageProcessor",
    # Upload handlers
    "handle_image_upload",
    "process_image_sync",
    "generate_thumbnails",
    # Validators
    "FileValidator",
    "get_image_validator",
    "get_document_validator",
    "get_avatar_validator",
    "get_invoice_validator",
    # Extension configuration (SP10 Tasks 67-69)
    "IMAGE_EXTENSIONS",
    "DOCUMENT_EXTENSIONS",
    "ARCHIVE_EXTENSIONS",
    "ALL_ALLOWED_EXTENSIONS",
    "is_image_extension",
    "is_document_extension",
    "is_archive_extension",
    "get_allowed_extensions_by_type",
    # Size helpers (SP10 Tasks 70-72)
    "KB",
    "MB",
    "GB",
    "validate_image_size",
    "validate_document_size",
    "get_max_size_for_extension",
    # Cleanup utilities (SP10 Tasks 73-74)
    "FileCleanup",
    "cleanup_old_files",
]
