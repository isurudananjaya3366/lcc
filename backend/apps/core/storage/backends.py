"""
LankaCommerce Cloud – Tenant-Isolated Storage Backends (SP10 Tasks 15-24, 40-46, 58).
"""

import logging
import os
from urllib.parse import urljoin  # noqa: F401

from django.conf import settings
from django.core.files.storage import FileSystemStorage, default_storage
from django.db import connection

logger = logging.getLogger(__name__)


class TenantFileStorage(FileSystemStorage):
    """
    Custom file storage backend with tenant isolation.

    Automatically prepends tenant identifier to all file paths,
    ensuring complete data separation between tenants.

    Path Format: tenant-{schema}/{file_path}
    Example: tenant-shop123/products/2026/01/22/product.jpg

    Methods overridden:
        _save   – prepend tenant prefix before writing
        url     – generate tenant-aware URLs
        path    – return tenant-scoped absolute path
        delete  – remove files within tenant directory only
        exists  – check existence within tenant directory

    Usage::

        storage = TenantFileStorage()
        storage.save('products/item.jpg', content)
        # Saved to: MEDIA_ROOT/tenant-shop123/products/item.jpg
    """

    def _get_tenant_schema(self) -> str:
        try:
            tenant = connection.tenant
            if tenant and hasattr(tenant, "schema_name"):
                return tenant.schema_name
        except Exception:
            pass
        return "public"

    def get_tenant_path(self, name: str) -> str:
        """
        Return tenant-prefixed path for file.

        Centralizes tenant prefix logic for reuse across all storage methods.
        Checks for existing prefix to avoid double-prefixing.

        Args:
            name: Original file name/path

        Returns:
            Path with tenant prefix (tenant-{schema}/{name})

        Example:
            'products/item.jpg' → 'tenant-shop123/products/item.jpg'
        """
        if name.startswith("tenant-"):
            return name
        schema = self._get_tenant_schema()
        return os.path.join(f"tenant-{schema}", name)

    # --- overrides ---

    def _save(self, name: str, content) -> str:
        tenant_name = self.get_tenant_path(name)
        return super()._save(tenant_name, content)

    def url(self, name: str) -> str:
        tenant_name = self.get_tenant_path(name)
        return super().url(tenant_name)

    def path(self, name: str) -> str:
        tenant_name = self.get_tenant_path(name)
        return super().path(tenant_name)

    def delete(self, name: str) -> None:
        tenant_name = self.get_tenant_path(name)
        try:
            super().delete(tenant_name)
        except Exception:
            logger.warning("Failed to delete file: %s", tenant_name, exc_info=True)

    def exists(self, name: str) -> bool:
        tenant_name = self.get_tenant_path(name)
        return super().exists(tenant_name)


class TenantMediaStorage(TenantFileStorage):
    """Media-specific tenant storage with MEDIA_ROOT / MEDIA_URL defaults."""

    def __init__(self, **kwargs):
        kwargs.setdefault("location", settings.MEDIA_ROOT)
        kwargs.setdefault("base_url", settings.MEDIA_URL)
        super().__init__(**kwargs)


class PublicStorage(FileSystemStorage):
    """Shared/public asset storage (no tenant prefix)."""

    def __init__(self, **kwargs):
        kwargs.setdefault("location", os.path.join(settings.MEDIA_ROOT, "public"))
        kwargs.setdefault("base_url", f"{settings.MEDIA_URL}public/")
        super().__init__(**kwargs)


# ════════════════════════════════════════════════════════════════════════
# S3 Storage (Production) — Tasks 40-43
# ════════════════════════════════════════════════════════════════════════

try:
    from storages.backends.s3boto3 import S3Boto3Storage

    _HAS_S3 = True
except ImportError:
    _HAS_S3 = False


class _TenantS3Mixin:
    """
    Mixin that prepends ``tenant-{schema}/`` to S3 object keys.

    Uses the ``_normalize_name`` hook so that *every* S3 operation
    (_save, url, delete, exists, …) automatically receives the
    tenant-scoped key without overriding each method individually.

    Path Format: tenant-{schema}/{file_path}
    Example: tenant-shop123/products/2026/01/22/item.jpg
    """

    def _get_tenant_schema(self) -> str:
        try:
            tenant = connection.tenant
            if tenant and hasattr(tenant, "schema_name"):
                return tenant.schema_name
        except Exception:
            pass
        return "public"

    def get_tenant_path(self, name: str) -> str:
        """
        Return tenant-prefixed path for a file.

        Checks for an existing prefix to avoid double-prefixing.

        Args:
            name: Original file name/path

        Returns:
            Path with tenant prefix (``tenant-{schema}/{name}``)
        """
        if name.startswith("tenant-"):
            return name
        schema = self._get_tenant_schema()
        return f"tenant-{schema}/{name}"

    # ── Core method overrides ────────────────────────────────────────

    def _normalize_name(self, name: str) -> str:
        """Inject tenant prefix before S3Boto3Storage normalises the key."""
        tenant_name = self.get_tenant_path(name)
        return super()._normalize_name(tenant_name)

    def _save(self, name: str, content) -> str:
        """Save file to S3 with tenant prefix."""
        tenant_path = self.get_tenant_path(name)
        return super()._save(tenant_path, content)

    def url(self, name: str) -> str:
        """Get URL for file with tenant prefix (S3 or CloudFront)."""
        tenant_path = self.get_tenant_path(name)
        return super().url(tenant_path)

    def delete(self, name: str) -> None:
        """Delete file from S3 within tenant directory."""
        tenant_path = self.get_tenant_path(name)
        try:
            super().delete(tenant_path)
        except Exception:
            logger.warning("Failed to delete S3 file: %s", tenant_path, exc_info=True)

    def exists(self, name: str) -> bool:
        """Check if file exists in tenant's S3 storage."""
        tenant_path = self.get_tenant_path(name)
        return super().exists(tenant_path)

    # ── Signed URL helper ────────────────────────────────────────────

    def generate_presigned_url(self, name: str, expiry: int | None = None) -> str:
        """
        Generate a pre-signed URL for private file access.

        Args:
            name: File path (without tenant prefix).
            expiry: Seconds until URL expires (default from settings).

        Returns:
            Presigned URL string.
        """
        if not _HAS_S3:
            raise ImportError("boto3 is required for presigned URLs")

        import boto3

        expiry = expiry or getattr(settings, "AWS_PRESIGNED_URL_EXPIRY", 3600)
        s3_client = boto3.client(
            "s3",
            region_name=getattr(settings, "AWS_S3_REGION_NAME", "ap-south-1"),
        )
        bucket = getattr(settings, "AWS_STORAGE_BUCKET_NAME", "")
        key = self.get_tenant_path(name)

        return s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=expiry,
        )


class TenantS3Storage:
    """
    S3 storage backend with tenant-scoped key prefixes.

    Only usable when ``django-storages[s3]`` and ``boto3`` are installed.
    Falls back gracefully at import time if unavailable.

    Usage::

        from apps.core.storage.backends import TenantS3Storage

        class ProductImage(models.Model):
            image = models.ImageField(storage=TenantS3Storage())
    """

    def __new__(cls, *args, **kwargs):
        if not _HAS_S3:
            raise ImportError(
                "django-storages[s3] and boto3 are required for S3 storage. "
                "Install them with: pip install django-storages[s3] boto3"
            )
        # Dynamically create the real class on first instantiation
        real_cls = type(
            "TenantS3Storage",
            (_TenantS3Mixin, S3Boto3Storage),
            {},
        )
        return real_cls(*args, **kwargs)


# ════════════════════════════════════════════════════════════════════════
# Private & Public S3 Storage — Tasks 42-43
# ════════════════════════════════════════════════════════════════════════


class PrivateTenantS3Storage:
    """
    Private S3 storage for sensitive tenant files.

    All files require signed URLs for access. Used for:
      - Invoices and receipts
      - Contracts and agreements
      - Financial reports
      - Sensitive documents

    Configuration:
      - ACL:  private (no public access)
      - querystring_auth:  True (signed URLs required)
      - file_overwrite:  False (prevent accidental overwrites)
      - Separate bucket via ``AWS_PRIVATE_BUCKET_NAME`` env var (optional)
    """

    def __new__(cls, *args, **kwargs):
        if not _HAS_S3:
            raise ImportError(
                "django-storages[s3] and boto3 are required for S3 storage. "
                "Install them with: pip install django-storages[s3] boto3"
            )

        class _PrivateS3(_TenantS3Mixin, S3Boto3Storage):
            default_acl = "private"
            querystring_auth = True
            file_overwrite = False

            def __init__(self, **kw):
                private_bucket = getattr(settings, "AWS_PRIVATE_BUCKET_NAME", "") or os.environ.get(
                    "AWS_PRIVATE_BUCKET_NAME", ""
                )
                if private_bucket:
                    kw["bucket_name"] = private_bucket
                super().__init__(**kw)

        return _PrivateS3(*args, **kwargs)


class PublicTenantS3Storage:
    """
    Public S3 storage for tenant files accessible without authentication.

    Optimised for CDN caching with aggressive Cache-Control headers.
    Used for:
      - Product images
      - Category images
      - User avatars
      - Public documents and catalogs

    Configuration:
      - ACL:  public-read (direct access)
      - querystring_auth:  False (no signed URLs)
      - file_overwrite:  False
      - CacheControl:  max-age=31536000, public, immutable
      - Separate bucket via ``AWS_PUBLIC_BUCKET_NAME`` env var (optional)
    """

    def __new__(cls, *args, **kwargs):
        if not _HAS_S3:
            raise ImportError(
                "django-storages[s3] and boto3 are required for S3 storage. "
                "Install them with: pip install django-storages[s3] boto3"
            )

        class _PublicS3(_TenantS3Mixin, S3Boto3Storage):
            default_acl = "public-read"
            querystring_auth = False
            file_overwrite = False
            object_parameters = {
                "CacheControl": "max-age=31536000, public, immutable",
            }

            def __init__(self, **kw):
                public_bucket = getattr(settings, "AWS_PUBLIC_BUCKET_NAME", "") or os.environ.get(
                    "AWS_PUBLIC_BUCKET_NAME", ""
                )
                if public_bucket:
                    kw["bucket_name"] = public_bucket
                super().__init__(**kw)

        return _PublicS3(*args, **kwargs)


# ════════════════════════════════════════════════════════════════════════
# Storage Class Helper — Task 58
# ════════════════════════════════════════════════════════════════════════


def get_storage_class(storage_type: str = "default"):
    """
    Return a ready-to-use storage backend instance.

    Args:
        storage_type: ``'default'``, ``'private'``, or ``'public'``.

    Returns:
        A Django storage backend instance appropriate for the current
        ``STORAGE_BACKEND`` setting.

    Examples::

        storage = get_storage_class()            # default backend
        storage = get_storage_class('private')   # private S3 / local
        storage = get_storage_class('public')    # public S3 / local
    """
    if storage_type == "private":
        backend_path = getattr(
            settings,
            "PRIVATE_FILE_STORAGE",
            "apps.core.storage.backends.TenantFileStorage",
        )
    elif storage_type == "public":
        backend_path = getattr(
            settings,
            "PUBLIC_FILE_STORAGE",
            "apps.core.storage.backends.TenantFileStorage",
        )
    else:
        # Return Django's default_storage directly
        return default_storage

    # Dynamically import and instantiate the backend class
    from django.utils.module_loading import import_string

    storage_cls = import_string(backend_path)
    return storage_cls()
