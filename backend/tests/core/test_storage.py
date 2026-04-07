"""
LankaCommerce Cloud – File Storage Tests (SP10 Group F, Tasks 75-82).

Covers:
    - Storage constants (signed URL expiry, thumbnails, extensions, sizes)
    - TenantFileStorage / TenantMediaStorage / PublicStorage backends
    - _TenantS3Mixin tenant-path logic
    - Path generators (product, invoice, document, avatar, tenant_upload)
    - FileValidator (extension, size, MIME type, malware scan)
    - Pre-built validators (image, document, avatar, invoice)
    - ImageProcessor (resize, compress, convert, thumbnails, web optimise)
    - Image utility helpers
    - Upload handlers (handle_image_upload, process_image_sync, generate_thumbnails)
    - S3 signed URL generation (generate_signed_url, generate_bulk_signed_urls)
    - FileCleanup (find orphaned, delete orphaned, cleanup convenience)
    - cleanmedia management command
    - Storage isolation between tenants

All tests are pure-mock — no database, filesystem, or AWS calls required.
"""

from __future__ import annotations

import os
from datetime import date, timedelta
from io import BytesIO, StringIO
from unittest.mock import MagicMock, PropertyMock, call, patch, ANY

import pytest
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.utils import timezone


# Every test in this module runs without a database connection.
pytestmark = pytest.mark.django_db(databases=[])


# ════════════════════════════════════════════════════════════════════════
# Fixtures  (Task 75 – Test Utilities / Test Fixtures)
# ════════════════════════════════════════════════════════════════════════


@pytest.fixture()
def mock_connection():
    """Patch ``django.db.connection.tenant`` with a mock tenant."""
    tenant = MagicMock()
    tenant.schema_name = "test_tenant"
    tenant.name = "Test Tenant"
    tenant.pk = 1
    with patch("django.db.connection") as conn:
        conn.tenant = tenant
        yield conn


@pytest.fixture()
def mock_connection_public():
    """Patch ``django.db.connection.tenant`` as ``None`` (public schema)."""
    with patch("django.db.connection") as conn:
        conn.tenant = None
        yield conn


@pytest.fixture()
def mock_tenant_a():
    """Return a mock tenant with schema 'shop_a'."""
    t = MagicMock()
    t.schema_name = "shop_a"
    t.name = "Shop A"
    t.pk = 10
    return t


@pytest.fixture()
def mock_tenant_b():
    """Return a mock tenant with schema 'shop_b'."""
    t = MagicMock()
    t.schema_name = "shop_b"
    t.name = "Shop B"
    t.pk = 20
    return t


@pytest.fixture()
def sample_image_bytes():
    """Return raw JPEG bytes for a tiny 2×2 image."""
    from PIL import Image

    img = Image.new("RGB", (2, 2), color="red")
    buf = BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf.read()


@pytest.fixture()
def sample_uploaded_image(sample_image_bytes):
    """Return a ``SimpleUploadedFile`` wrapping a tiny JPEG."""
    return SimpleUploadedFile(
        name="photo.jpg",
        content=sample_image_bytes,
        content_type="image/jpeg",
    )


@pytest.fixture()
def large_uploaded_image():
    """Return a ``SimpleUploadedFile`` that is >1 MB (triggers async path)."""
    from PIL import Image

    img = Image.new("RGB", (1500, 1500), color="blue")
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=100)
    buf.seek(0)
    data = buf.read()
    # If the generated image is still under 1 MB, pad it
    if len(data) < 1024 * 1024 + 1:
        data = data + b"\x00" * (1024 * 1024 + 1 - len(data))
    return SimpleUploadedFile(
        name="large_photo.jpg",
        content=data,
        content_type="image/jpeg",
    )


@pytest.fixture()
def sample_pdf():
    """Return a ``SimpleUploadedFile`` mimicking a small PDF."""
    return SimpleUploadedFile(
        name="report.pdf",
        content=b"%PDF-1.4 fake pdf content" * 10,
        content_type="application/pdf",
    )


# ════════════════════════════════════════════════════════════════════════
# Storage Constants  (Task 75/76 – constant sanity checks)
# ════════════════════════════════════════════════════════════════════════


class TestSignedUrlExpiryConstants:
    """Verify hard-coded signed-URL expiry values."""

    def test_short_expiry(self):
        from apps.core.storage.constants import SIGNED_URL_SHORT_EXPIRY

        assert SIGNED_URL_SHORT_EXPIRY == 1800

    def test_default_expiry(self):
        from apps.core.storage.constants import SIGNED_URL_DEFAULT_EXPIRY

        assert SIGNED_URL_DEFAULT_EXPIRY == 3600

    def test_medium_expiry(self):
        from apps.core.storage.constants import SIGNED_URL_MEDIUM_EXPIRY

        assert SIGNED_URL_MEDIUM_EXPIRY == 14400

    def test_long_expiry(self):
        from apps.core.storage.constants import SIGNED_URL_LONG_EXPIRY

        assert SIGNED_URL_LONG_EXPIRY == 86400

    def test_extended_expiry(self):
        from apps.core.storage.constants import SIGNED_URL_EXTENDED_EXPIRY

        assert SIGNED_URL_EXTENDED_EXPIRY == 604800

    def test_expiry_by_type_has_standard_keys(self):
        from apps.core.storage.constants import SIGNED_URL_EXPIRY_BY_TYPE

        for key in ("invoice", "receipt", "contract", "report", "image"):
            assert key in SIGNED_URL_EXPIRY_BY_TYPE


class TestGetSignedUrlExpiry:
    """Test ``get_signed_url_expiry`` resolution logic."""

    def test_explicit_file_type(self):
        from apps.core.storage.constants import (
            get_signed_url_expiry,
            SIGNED_URL_DEFAULT_EXPIRY,
        )

        assert get_signed_url_expiry(file_type="invoice") == SIGNED_URL_DEFAULT_EXPIRY

    def test_file_type_case_insensitive(self):
        from apps.core.storage.constants import get_signed_url_expiry

        assert get_signed_url_expiry(file_type="INVOICE") == get_signed_url_expiry(
            file_type="invoice"
        )

    def test_inferred_from_path(self):
        from apps.core.storage.constants import get_signed_url_expiry

        expiry = get_signed_url_expiry(file_path="invoices/2026/01/INV-001.pdf")
        assert isinstance(expiry, int) and expiry > 0

    def test_unknown_type_returns_default(self):
        from apps.core.storage.constants import (
            get_signed_url_expiry,
            SIGNED_URL_DEFAULT_EXPIRY,
        )

        assert get_signed_url_expiry(file_type="unknown") == SIGNED_URL_DEFAULT_EXPIRY

    def test_no_args_returns_default(self):
        from apps.core.storage.constants import (
            get_signed_url_expiry,
            SIGNED_URL_DEFAULT_EXPIRY,
        )

        assert get_signed_url_expiry() == SIGNED_URL_DEFAULT_EXPIRY


class TestThumbnailConstants:
    """Verify thumbnail size presets."""

    def test_thumb_small(self):
        from apps.core.storage.constants import THUMB_SMALL

        assert THUMB_SMALL == (100, 100)

    def test_thumb_medium(self):
        from apps.core.storage.constants import THUMB_MEDIUM

        assert THUMB_MEDIUM == (300, 300)

    def test_thumb_large(self):
        from apps.core.storage.constants import THUMB_LARGE

        assert THUMB_LARGE == (600, 600)

    def test_thumbnail_sizes_dict(self):
        from apps.core.storage.constants import THUMBNAIL_SIZES

        assert set(THUMBNAIL_SIZES.keys()) == {"small", "medium", "large"}

    def test_get_thumbnail_size_by_name(self):
        from apps.core.storage.constants import get_thumbnail_size

        assert get_thumbnail_size("small") == (100, 100)
        assert get_thumbnail_size("medium") == (300, 300)
        assert get_thumbnail_size("large") == (600, 600)

    def test_get_thumbnail_size_by_use_case(self):
        from apps.core.storage.constants import get_thumbnail_size

        assert get_thumbnail_size("product_list") == (100, 100)
        assert get_thumbnail_size("product_detail") == (600, 600)

    def test_get_thumbnail_size_unknown_returns_medium(self):
        from apps.core.storage.constants import get_thumbnail_size, THUMB_MEDIUM

        assert get_thumbnail_size("nonexistent_case") == THUMB_MEDIUM

    def test_validate_thumbnail_size_valid(self):
        from apps.core.storage.constants import validate_thumbnail_size

        assert validate_thumbnail_size((100, 100)) is True
        assert validate_thumbnail_size((300, 300)) is True

    def test_validate_thumbnail_size_invalid(self):
        from apps.core.storage.constants import validate_thumbnail_size

        assert validate_thumbnail_size((999, 999)) is False


class TestExtensionConstants:
    """Verify extension sets and helpers."""

    def test_image_extensions_contains_jpg(self):
        from apps.core.storage.constants import IMAGE_EXTENSIONS

        assert ".jpg" in IMAGE_EXTENSIONS
        assert ".png" in IMAGE_EXTENSIONS
        assert ".webp" in IMAGE_EXTENSIONS

    def test_document_extensions_contains_pdf(self):
        from apps.core.storage.constants import DOCUMENT_EXTENSIONS

        assert ".pdf" in DOCUMENT_EXTENSIONS
        assert ".xlsx" in DOCUMENT_EXTENSIONS

    def test_archive_extensions(self):
        from apps.core.storage.constants import ARCHIVE_EXTENSIONS

        assert ".zip" in ARCHIVE_EXTENSIONS

    def test_all_allowed_is_union(self):
        from apps.core.storage.constants import (
            IMAGE_EXTENSIONS,
            DOCUMENT_EXTENSIONS,
            ARCHIVE_EXTENSIONS,
            ALL_ALLOWED_EXTENSIONS,
        )

        union = IMAGE_EXTENSIONS | DOCUMENT_EXTENSIONS | ARCHIVE_EXTENSIONS
        assert ALL_ALLOWED_EXTENSIONS == union

    def test_is_image_extension(self):
        from apps.core.storage.constants import is_image_extension

        assert is_image_extension(".jpg") is True
        assert is_image_extension("png") is True
        assert is_image_extension(".exe") is False

    def test_is_document_extension(self):
        from apps.core.storage.constants import is_document_extension

        assert is_document_extension(".pdf") is True
        assert is_document_extension("xlsx") is True
        assert is_document_extension(".jpg") is False

    def test_is_archive_extension(self):
        from apps.core.storage.constants import is_archive_extension

        assert is_archive_extension(".zip") is True
        assert is_archive_extension(".pdf") is False

    def test_get_allowed_extensions_by_type(self):
        from apps.core.storage.constants import get_allowed_extensions_by_type

        imgs = get_allowed_extensions_by_type("image")
        assert isinstance(imgs, list)
        assert ".jpg" in imgs

        docs = get_allowed_extensions_by_type("document")
        assert ".pdf" in docs

        all_ext = get_allowed_extensions_by_type("all")
        assert set(all_ext) >= set(imgs) | set(docs)

    def test_get_allowed_extensions_unknown_type(self):
        from apps.core.storage.constants import get_allowed_extensions_by_type

        assert get_allowed_extensions_by_type("zzzz") == []


class TestSizeLimitConstants:
    """Verify KB/MB/GB helpers and size validators."""

    def test_unit_constants(self):
        from apps.core.storage.constants import KB, MB, GB

        assert KB == 1024
        assert MB == 1024 * 1024
        assert GB == 1024 * 1024 * 1024

    def test_validate_image_size_within_limit(self):
        from apps.core.storage.constants import validate_image_size

        ok, max_sz, err = validate_image_size(1_000_000)
        assert ok is True
        assert err is None

    def test_validate_image_size_over_limit(self):
        from apps.core.storage.constants import validate_image_size, MB

        ok, max_sz, err = validate_image_size(100 * MB)
        assert ok is False
        assert err is not None

    def test_validate_image_size_avatar(self):
        from apps.core.storage.constants import validate_image_size, MB

        ok, max_sz, _ = validate_image_size(1 * MB, image_type="avatar")
        assert ok is True

    def test_validate_document_size_within_limit(self):
        from apps.core.storage.constants import validate_document_size

        ok, _, err = validate_document_size(1_000_000)
        assert ok is True

    def test_validate_document_size_over_limit(self):
        from apps.core.storage.constants import validate_document_size, MB

        ok, _, err = validate_document_size(500 * MB)
        assert ok is False

    def test_get_max_size_for_extension_image(self):
        from apps.core.storage.constants import get_max_size_for_extension

        sz = get_max_size_for_extension(".jpg")
        assert isinstance(sz, int) and sz > 0

    def test_get_max_size_for_extension_document(self):
        from apps.core.storage.constants import get_max_size_for_extension

        sz = get_max_size_for_extension(".pdf")
        assert isinstance(sz, int) and sz > 0

    def test_get_max_size_for_extension_unknown(self):
        from apps.core.storage.constants import get_max_size_for_extension, MB

        sz = get_max_size_for_extension(".xyz")
        assert sz == 5 * MB


# ════════════════════════════════════════════════════════════════════════
# TenantFileStorage backend  (Task 77 – Test TenantFileStorage)
# ════════════════════════════════════════════════════════════════════════


class TestTenantFileStorageTenantPath:
    """Test ``TenantFileStorage.get_tenant_path`` and ``_get_tenant_schema``."""

    def test_get_tenant_schema_with_tenant(self, mock_connection):
        from apps.core.storage.backends import TenantFileStorage

        with patch("apps.core.storage.backends.connection", mock_connection):
            storage = TenantFileStorage()
            schema = storage._get_tenant_schema()
            assert schema == "test_tenant"

    def test_get_tenant_schema_no_tenant(self, mock_connection_public):
        from apps.core.storage.backends import TenantFileStorage

        with patch("apps.core.storage.backends.connection", mock_connection_public):
            storage = TenantFileStorage()
            schema = storage._get_tenant_schema()
            assert schema == "public"

    def test_get_tenant_path_prepends_prefix(self, mock_connection):
        from apps.core.storage.backends import TenantFileStorage

        with patch("apps.core.storage.backends.connection", mock_connection):
            storage = TenantFileStorage()
            path = storage.get_tenant_path("products/item.jpg")
            assert path.startswith("tenant-test_tenant")
            assert "products" in path

    def test_get_tenant_path_no_double_prefix(self, mock_connection):
        from apps.core.storage.backends import TenantFileStorage

        with patch("apps.core.storage.backends.connection", mock_connection):
            storage = TenantFileStorage()
            path = storage.get_tenant_path("tenant-test_tenant/products/item.jpg")
            assert path.count("tenant-test_tenant") == 1

    def test_get_tenant_path_public_fallback(self, mock_connection_public):
        from apps.core.storage.backends import TenantFileStorage

        with patch("apps.core.storage.backends.connection", mock_connection_public):
            storage = TenantFileStorage()
            path = storage.get_tenant_path("file.txt")
            assert "tenant-public" in path


class TestTenantFileStorageMethods:
    """Test overridden _save / url / path / delete / exists methods."""

    @patch("django.core.files.storage.FileSystemStorage._save")
    def test_save_prepends_tenant(self, mock_super_save, mock_connection):
        from apps.core.storage.backends import TenantFileStorage

        mock_super_save.return_value = "tenant-test_tenant/file.txt"

        with patch("apps.core.storage.backends.connection", mock_connection):
            storage = TenantFileStorage()
            result = storage._save("file.txt", ContentFile(b"data"))

        mock_super_save.assert_called_once()
        saved_name = mock_super_save.call_args[0][0]
        assert "tenant-test_tenant" in saved_name

    @patch("django.core.files.storage.FileSystemStorage.url")
    def test_url_prepends_tenant(self, mock_super_url, mock_connection):
        from apps.core.storage.backends import TenantFileStorage

        mock_super_url.return_value = "/media/tenant-test_tenant/file.txt"

        with patch("apps.core.storage.backends.connection", mock_connection):
            storage = TenantFileStorage()
            url = storage.url("file.txt")

        mock_super_url.assert_called_once()
        arg = mock_super_url.call_args[0][0]
        assert "tenant-test_tenant" in arg

    @patch("django.core.files.storage.FileSystemStorage.path")
    def test_path_prepends_tenant(self, mock_super_path, mock_connection):
        from apps.core.storage.backends import TenantFileStorage

        mock_super_path.return_value = "/media/tenant-test_tenant/file.txt"

        with patch("apps.core.storage.backends.connection", mock_connection):
            storage = TenantFileStorage()
            p = storage.path("file.txt")

        mock_super_path.assert_called_once()
        arg = mock_super_path.call_args[0][0]
        assert "tenant-test_tenant" in arg

    @patch("django.core.files.storage.FileSystemStorage.delete")
    def test_delete_prepends_tenant(self, mock_super_delete, mock_connection):
        from apps.core.storage.backends import TenantFileStorage

        with patch("apps.core.storage.backends.connection", mock_connection):
            storage = TenantFileStorage()
            storage.delete("file.txt")

        mock_super_delete.assert_called_once()
        arg = mock_super_delete.call_args[0][0]
        assert "tenant-test_tenant" in arg

    @patch("django.core.files.storage.FileSystemStorage.delete")
    def test_delete_suppresses_exception(self, mock_super_delete, mock_connection):
        from apps.core.storage.backends import TenantFileStorage

        mock_super_delete.side_effect = OSError("permission denied")

        with patch("apps.core.storage.backends.connection", mock_connection):
            storage = TenantFileStorage()
            # Should not raise
            storage.delete("file.txt")

    @patch("django.core.files.storage.FileSystemStorage.exists")
    def test_exists_prepends_tenant(self, mock_super_exists, mock_connection):
        from apps.core.storage.backends import TenantFileStorage

        mock_super_exists.return_value = True

        with patch("apps.core.storage.backends.connection", mock_connection):
            storage = TenantFileStorage()
            result = storage.exists("file.txt")

        assert result is True
        arg = mock_super_exists.call_args[0][0]
        assert "tenant-test_tenant" in arg


class TestTenantMediaStorage:
    """Test TenantMediaStorage sets sensible defaults."""

    def test_defaults_to_media_root(self, settings):
        from apps.core.storage.backends import TenantMediaStorage

        storage = TenantMediaStorage()
        assert storage.base_url == settings.MEDIA_URL


class TestPublicStorage:
    """Test PublicStorage writes to a public sub-directory."""

    def test_location_contains_public(self, settings):
        from apps.core.storage.backends import PublicStorage

        storage = PublicStorage()
        assert "public" in storage.location
        assert "public" in storage.base_url


# ════════════════════════════════════════════════════════════════════════
# S3 Mixin / S3 Backend Tests  (Task 81 – Test S3 Storage)
# ════════════════════════════════════════════════════════════════════════


class TestTenantS3MixinPaths:
    """Test _TenantS3Mixin tenant-path helpers (mocked, no real S3)."""

    def test_get_tenant_path(self, mock_connection):
        from apps.core.storage.backends import _TenantS3Mixin

        mixin = _TenantS3Mixin()
        with patch("apps.core.storage.backends.connection", mock_connection):
            path = mixin.get_tenant_path("products/img.jpg")

        assert path == "tenant-test_tenant/products/img.jpg"

    def test_get_tenant_path_no_double_prefix(self, mock_connection):
        from apps.core.storage.backends import _TenantS3Mixin

        mixin = _TenantS3Mixin()
        with patch("apps.core.storage.backends.connection", mock_connection):
            path = mixin.get_tenant_path("tenant-test_tenant/products/img.jpg")

        assert path.count("tenant-test_tenant") == 1

    def test_get_tenant_schema_fallback(self, mock_connection_public):
        from apps.core.storage.backends import _TenantS3Mixin

        mixin = _TenantS3Mixin()
        with patch("apps.core.storage.backends.connection", mock_connection_public):
            schema = mixin._get_tenant_schema()

        assert schema == "public"


class TestTenantS3StorageImport:
    """Test TenantS3Storage import guard."""

    def test_raises_without_storages(self):
        from apps.core.storage.backends import TenantS3Storage, _HAS_S3

        if not _HAS_S3:
            with pytest.raises(ImportError, match="django-storages"):
                TenantS3Storage()

    def test_private_raises_without_storages(self):
        from apps.core.storage.backends import PrivateTenantS3Storage, _HAS_S3

        if not _HAS_S3:
            with pytest.raises(ImportError, match="django-storages"):
                PrivateTenantS3Storage()


class TestPresignedUrlOnMixin:
    """Test _TenantS3Mixin.generate_presigned_url (mock boto3)."""

    @patch("apps.core.storage.backends._HAS_S3", True)
    def test_generate_presigned_url(self, mock_connection):
        from apps.core.storage.backends import _TenantS3Mixin

        mock_s3 = MagicMock()
        mock_s3.generate_presigned_url.return_value = "https://s3.example.com/signed"

        mock_boto3 = MagicMock()
        mock_boto3.client.return_value = mock_s3

        mixin = _TenantS3Mixin()
        with patch("apps.core.storage.backends.connection", mock_connection), \
             patch.dict("sys.modules", {"boto3": mock_boto3}):
            url = mixin.generate_presigned_url("invoices/INV-001.pdf", expiry=7200)

        assert url == "https://s3.example.com/signed"
        mock_s3.generate_presigned_url.assert_called_once()
        _, kwargs = mock_s3.generate_presigned_url.call_args
        assert kwargs["ExpiresIn"] == 7200


# ════════════════════════════════════════════════════════════════════════
# Storage Class Factory  (Task 76 – get_storage_class)
# ════════════════════════════════════════════════════════════════════════


class TestGetStorageClass:
    """Test ``get_storage_class`` factory function."""

    def test_default_returns_default_storage(self):
        from apps.core.storage.backends import get_storage_class

        storage = get_storage_class("default")
        assert storage is not None

    @patch("django.utils.module_loading.import_string")
    def test_private_returns_configured_backend(self, mock_import, settings):
        from apps.core.storage.backends import get_storage_class

        mock_cls = MagicMock(return_value=MagicMock())
        mock_import.return_value = mock_cls
        settings.PRIVATE_FILE_STORAGE = "apps.core.storage.backends.TenantFileStorage"

        storage = get_storage_class("private")
        mock_import.assert_called_once_with(settings.PRIVATE_FILE_STORAGE)

    @patch("django.utils.module_loading.import_string")
    def test_public_returns_configured_backend(self, mock_import, settings):
        from apps.core.storage.backends import get_storage_class

        mock_cls = MagicMock(return_value=MagicMock())
        mock_import.return_value = mock_cls
        settings.PUBLIC_FILE_STORAGE = "apps.core.storage.backends.TenantFileStorage"

        storage = get_storage_class("public")
        mock_import.assert_called_once_with(settings.PUBLIC_FILE_STORAGE)


# ════════════════════════════════════════════════════════════════════════
# Tenant Isolation  (Task 78 – Test Storage Isolation)
# ════════════════════════════════════════════════════════════════════════


class TestTenantPathIsolation:
    """Verify that different tenants receive different storage paths."""

    def test_different_tenants_different_paths(self, mock_tenant_a, mock_tenant_b):
        from apps.core.storage.backends import TenantFileStorage

        storage = TenantFileStorage()

        with patch("apps.core.storage.backends.connection") as conn:
            conn.tenant = mock_tenant_a
            path_a = storage.get_tenant_path("products/img.jpg")

        with patch("apps.core.storage.backends.connection") as conn:
            conn.tenant = mock_tenant_b
            path_b = storage.get_tenant_path("products/img.jpg")

        assert path_a != path_b
        assert "shop_a" in path_a
        assert "shop_b" in path_b

    def test_same_filename_different_tenant_paths(
        self, mock_tenant_a, mock_tenant_b
    ):
        from apps.core.storage.backends import TenantFileStorage

        storage = TenantFileStorage()
        filename = "shared-name.txt"

        with patch("apps.core.storage.backends.connection") as conn:
            conn.tenant = mock_tenant_a
            path_a = storage.get_tenant_path(filename)

        with patch("apps.core.storage.backends.connection") as conn:
            conn.tenant = mock_tenant_b
            path_b = storage.get_tenant_path(filename)

        assert path_a != path_b

    def test_path_traversal_normalised(self, mock_connection):
        """Paths with .. are still scoped to the tenant prefix."""
        from apps.core.storage.backends import TenantFileStorage

        with patch("apps.core.storage.backends.connection", mock_connection):
            storage = TenantFileStorage()
            path = storage.get_tenant_path("../../etc/passwd")

        # Must start with tenant prefix
        assert path.startswith("tenant-")

    @patch("django.core.files.storage.FileSystemStorage._save")
    def test_save_isolation(self, mock_save, mock_tenant_a, mock_tenant_b):
        """_save is called with tenant-scoped paths per tenant."""
        from apps.core.storage.backends import TenantFileStorage

        mock_save.return_value = "dummy"
        storage = TenantFileStorage()
        content = ContentFile(b"data")

        with patch("apps.core.storage.backends.connection") as conn:
            conn.tenant = mock_tenant_a
            storage._save("file.txt", content)

        saved_a = mock_save.call_args_list[0][0][0]

        with patch("apps.core.storage.backends.connection") as conn:
            conn.tenant = mock_tenant_b
            storage._save("file.txt", content)

        saved_b = mock_save.call_args_list[1][0][0]

        assert saved_a != saved_b
        assert "shop_a" in saved_a
        assert "shop_b" in saved_b

    @patch("django.core.files.storage.FileSystemStorage.exists")
    def test_exists_scoped_to_tenant(self, mock_exists, mock_tenant_a, mock_tenant_b):
        """exists() checks different physical paths for different tenants."""
        from apps.core.storage.backends import TenantFileStorage

        mock_exists.return_value = False
        storage = TenantFileStorage()

        with patch("apps.core.storage.backends.connection") as conn:
            conn.tenant = mock_tenant_a
            storage.exists("file.txt")

        checked_a = mock_exists.call_args_list[0][0][0]

        with patch("apps.core.storage.backends.connection") as conn:
            conn.tenant = mock_tenant_b
            storage.exists("file.txt")

        checked_b = mock_exists.call_args_list[1][0][0]

        assert checked_a != checked_b


# ════════════════════════════════════════════════════════════════════════
# Path Generators  (Task 77/79 – paths.py tests)
# ════════════════════════════════════════════════════════════════════════


class TestProductPath:
    """Test ``product_path`` upload-to callable."""

    def test_returns_products_prefix(self):
        from apps.core.storage.paths import product_path

        instance = MagicMock()
        path = product_path(instance, "item.jpg")
        assert path.startswith("products/")

    def test_has_date_component(self):
        from apps.core.storage.paths import product_path

        today = date.today().strftime("%Y/%m/%d")
        path = product_path(MagicMock(), "item.jpg")
        assert today in path

    def test_preserves_extension(self):
        from apps.core.storage.paths import product_path

        path = product_path(MagicMock(), "item.PNG")
        assert path.endswith(".png")

    def test_uuid_in_filename(self):
        from apps.core.storage.paths import product_path

        path = product_path(MagicMock(), "item.jpg")
        basename = os.path.basename(path)
        # UUID hex is 32 chars
        assert len(basename.split(".")[0]) == 32


class TestInvoicePath:
    """Test ``invoice_path`` upload-to callable."""

    def test_with_invoice_number(self):
        from apps.core.storage.paths import invoice_path

        inst = MagicMock(invoice_number="INV/2026/001")
        path = invoice_path(inst, "doc.pdf")
        assert path.startswith("invoices/")
        assert "INV-2026-001" in path  # / replaced with -

    def test_without_invoice_number(self):
        from apps.core.storage.paths import invoice_path

        inst = MagicMock(spec=[])  # no invoice_number attribute
        path = invoice_path(inst, "doc.pdf")
        assert path.startswith("invoices/")
        # Should use UUID fallback
        basename = os.path.basename(path)
        assert len(basename.split(".")[0]) == 32


class TestDocumentPath:
    """Test ``document_path`` upload-to callable."""

    def test_with_document_type(self):
        from apps.core.storage.paths import document_path

        inst = MagicMock(document_type="Reports")
        path = document_path(inst, "q1.pdf")
        assert "documents/reports/" in path

    def test_without_document_type_defaults_general(self):
        from apps.core.storage.paths import document_path

        inst = MagicMock(spec=[])
        path = document_path(inst, "q1.pdf")
        assert "documents/general/" in path


class TestAvatarPath:
    """Test ``avatar_path`` upload-to callable."""

    def test_contains_user_id(self):
        from apps.core.storage.paths import avatar_path

        inst = MagicMock(pk=42)
        path = avatar_path(inst, "me.jpg")
        assert path == "avatars/user_42.jpg"


class TestTenantUploadPath:
    """Test ``tenant_upload_path`` callable."""

    @patch("apps.core.storage.paths.connection")
    def test_contains_tenant_prefix(self, mock_conn):
        from apps.core.storage.paths import tenant_upload_path

        mock_conn.tenant = MagicMock(schema_name="shop1")
        path = tenant_upload_path(MagicMock(), "file.pdf")
        assert path.startswith("shop1/uploads/")

    @patch("apps.core.storage.paths.connection")
    def test_public_fallback(self, mock_conn):
        from apps.core.storage.paths import tenant_upload_path

        mock_conn.tenant = None
        path = tenant_upload_path(MagicMock(), "file.pdf")
        assert path.startswith("public/uploads/")


# ════════════════════════════════════════════════════════════════════════
# FileValidator  (Task 80 – Test File Validation)
# ════════════════════════════════════════════════════════════════════════


class TestFileValidatorExtension:
    """Test ``FileValidator.validate_extension``."""

    def test_allowed_extension_passes(self):
        from apps.core.storage.validators import FileValidator

        v = FileValidator(allowed_extensions={".jpg", ".png"})
        f = SimpleUploadedFile("test.jpg", b"x", "image/jpeg")
        v.validate_extension(f)  # should not raise

    def test_disallowed_extension_raises(self):
        from apps.core.storage.validators import FileValidator

        v = FileValidator(allowed_extensions={".jpg", ".png"})
        f = SimpleUploadedFile("test.exe", b"x", "application/octet-stream")
        with pytest.raises(ValidationError, match="not allowed"):
            v.validate_extension(f)

    def test_case_insensitive(self):
        from apps.core.storage.validators import FileValidator

        v = FileValidator(allowed_extensions={".jpg"})
        f = SimpleUploadedFile("test.JPG", b"x", "image/jpeg")
        v.validate_extension(f)

    def test_no_extension_raises(self):
        from apps.core.storage.validators import FileValidator

        v = FileValidator(allowed_extensions={".jpg"})
        f = SimpleUploadedFile("noext", b"x", "image/jpeg")
        with pytest.raises(ValidationError, match="no extension"):
            v.validate_extension(f)

    def test_none_allowed_set_falls_back_to_settings(self):
        """When None is passed, the validator uses settings.ALL_ALLOWED_EXTENSIONS."""
        from apps.core.storage.validators import FileValidator

        v = FileValidator(allowed_extensions=None)
        # .jpg is in ALL_ALLOWED_EXTENSIONS so it should pass
        f = SimpleUploadedFile("test.jpg", b"x", "image/jpeg")
        v.validate_extension(f)


class TestFileValidatorSize:
    """Test ``FileValidator.validate_size``."""

    def test_within_limit_passes(self):
        from apps.core.storage.validators import FileValidator

        v = FileValidator(max_size=1024)
        f = SimpleUploadedFile("f.txt", b"x" * 100, "text/plain")
        v.validate_size(f)

    def test_at_exact_limit_passes(self):
        from apps.core.storage.validators import FileValidator

        v = FileValidator(max_size=100)
        f = SimpleUploadedFile("f.txt", b"x" * 100, "text/plain")
        v.validate_size(f)

    def test_over_limit_raises(self):
        from apps.core.storage.validators import FileValidator

        v = FileValidator(max_size=50)
        f = SimpleUploadedFile("f.txt", b"x" * 100, "text/plain")
        with pytest.raises(ValidationError, match="exceeds"):
            v.validate_size(f)

    def test_empty_file_raises(self):
        from apps.core.storage.validators import FileValidator

        v = FileValidator(max_size=1024)
        f = SimpleUploadedFile("f.txt", b"", "text/plain")
        with pytest.raises(ValidationError, match="empty"):
            v.validate_size(f)

    def test_no_max_size_passes_anything(self):
        from apps.core.storage.validators import FileValidator

        v = FileValidator(max_size=None)
        f = SimpleUploadedFile("f.txt", b"x" * 10000, "text/plain")
        v.validate_size(f)


class TestFileValidatorMimeType:
    """Test ``FileValidator.validate_mime_type`` (mock python-magic)."""

    def test_matching_mime_passes(self):
        from apps.core.storage.validators import FileValidator

        mock_magic = MagicMock()
        mock_magic.from_buffer.return_value = "image/jpeg"

        v = FileValidator(allowed_extensions={".jpg"})
        f = SimpleUploadedFile("test.jpg", b"\xff\xd8\xff" + b"\x00" * 8000, "image/jpeg")

        with patch.dict("sys.modules", {"magic": mock_magic}):
            v.validate_mime_type(f)  # should not raise

    def test_mismatched_mime_raises(self):
        from apps.core.storage.validators import FileValidator

        mock_magic = MagicMock()
        mock_magic.from_buffer.return_value = "application/x-dosexec"

        v = FileValidator(allowed_extensions={".jpg"})
        f = SimpleUploadedFile("test.jpg", b"MZ" + b"\x00" * 8000, "image/jpeg")

        with patch.dict("sys.modules", {"magic": mock_magic}):
            with pytest.raises(ValidationError, match="mismatch"):
                v.validate_mime_type(f, strict=True)

    def test_skips_when_no_magic_library(self):
        """When python-magic is unavailable, MIME check is skipped."""
        from apps.core.storage.validators import FileValidator

        v = FileValidator(allowed_extensions={".jpg"})
        f = SimpleUploadedFile("test.jpg", b"data" * 2000, "image/jpeg")

        with patch.dict("sys.modules", {"magic": None}):
            # When magic is None in sys.modules, import magic raises ImportError
            v.validate_mime_type(f)  # should not raise, just skip


class TestFileValidatorMalwareScan:
    """Test ``FileValidator.scan_for_malware`` (mocked scanners)."""

    def test_scanning_disabled_returns_true(self, settings):
        from apps.core.storage.validators import FileValidator

        settings.ENABLE_MALWARE_SCANNING = False
        v = FileValidator()
        f = SimpleUploadedFile("f.txt", b"data", "text/plain")
        assert v.scan_for_malware(f) is True

    def test_scanner_none_returns_true(self, settings):
        from apps.core.storage.validators import FileValidator

        settings.ENABLE_MALWARE_SCANNING = True
        v = FileValidator()
        f = SimpleUploadedFile("f.txt", b"data", "text/plain")
        assert v.scan_for_malware(f, scanner="none") is True

    def test_unknown_scanner_returns_true(self, settings):
        from apps.core.storage.validators import FileValidator

        settings.ENABLE_MALWARE_SCANNING = True
        v = FileValidator()
        f = SimpleUploadedFile("f.txt", b"data", "text/plain")
        assert v.scan_for_malware(f, scanner="xyz") is True

    def test_clamav_clean_file(self, settings):
        from apps.core.storage.validators import FileValidator

        settings.ENABLE_MALWARE_SCANNING = True

        mock_cd = MagicMock()
        mock_cd.ping.return_value = True
        mock_cd.scan_stream.return_value = None  # clean

        mock_pyclamd = MagicMock()
        mock_pyclamd.ClamdUnixSocket.return_value = mock_cd

        v = FileValidator()
        f = SimpleUploadedFile("f.txt", b"safe content", "text/plain")

        with patch.dict("sys.modules", {"pyclamd": mock_pyclamd}):
            assert v.scan_for_malware(f, scanner="clamav") is True

    def test_clamav_infected_raises(self, settings):
        from apps.core.storage.validators import FileValidator

        settings.ENABLE_MALWARE_SCANNING = True

        mock_cd = MagicMock()
        mock_cd.ping.return_value = True
        mock_cd.scan_stream.return_value = {"stream": ("FOUND", "Eicar.Test")}

        mock_pyclamd = MagicMock()
        mock_pyclamd.ClamdUnixSocket.return_value = mock_cd

        v = FileValidator()
        f = SimpleUploadedFile("f.txt", b"virus", "text/plain")

        with patch.dict("sys.modules", {"pyclamd": mock_pyclamd}):
            with pytest.raises(ValidationError, match="malicious"):
                v.scan_for_malware(f, scanner="clamav")


class TestFileValidatorCallable:
    """Test ``FileValidator.__call__`` (Django field-validator interface)."""

    def test_call_runs_extension_and_size(self):
        from apps.core.storage.validators import FileValidator

        v = FileValidator(allowed_extensions={".txt"}, max_size=1024)
        f = SimpleUploadedFile("ok.txt", b"x" * 100, "text/plain")
        v(f)  # should not raise

    def test_call_raises_on_bad_extension(self):
        from apps.core.storage.validators import FileValidator

        v = FileValidator(allowed_extensions={".txt"}, max_size=1024)
        f = SimpleUploadedFile("bad.exe", b"x", "application/octet-stream")
        with pytest.raises(ValidationError):
            v(f)


class TestFileValidatorValidateAll:
    """Test ``FileValidator.validate_all`` pipeline."""

    def test_validate_all_passes(self, settings):
        from apps.core.storage.validators import FileValidator

        mock_magic = MagicMock()
        mock_magic.from_buffer.return_value = "image/jpeg"

        v = FileValidator(allowed_extensions={".jpg"}, max_size=5 * 1024 * 1024)
        f = SimpleUploadedFile("img.jpg", b"\xff\xd8\xff" + b"\x00" * 100, "image/jpeg")

        with patch.dict("sys.modules", {"magic": mock_magic}):
            assert v.validate_all(f) is True

    def test_validate_all_fails_on_extension(self):
        from apps.core.storage.validators import FileValidator

        v = FileValidator(allowed_extensions={".jpg"}, max_size=5 * 1024 * 1024)
        f = SimpleUploadedFile("bad.exe", b"x" * 100, "application/octet-stream")
        with pytest.raises(ValidationError):
            v.validate_all(f)


class TestFileValidatorHelpers:
    """Test static helper methods."""

    def test_get_file_extension(self):
        from apps.core.storage.validators import FileValidator

        assert FileValidator.get_file_extension("photo.JPG") == "jpg"
        assert FileValidator.get_file_extension("noext") == ""

    def test_format_file_size(self):
        from apps.core.storage.validators import FileValidator

        assert "bytes" in FileValidator.format_file_size(512)
        assert "KB" in FileValidator.format_file_size(1536)
        assert "MB" in FileValidator.format_file_size(5_242_880)
        assert "GB" in FileValidator.format_file_size(1_073_741_824)


class TestPrebuiltValidators:
    """Test convenience validator factories."""

    def test_get_image_validator(self, settings):
        from apps.core.storage.validators import get_image_validator

        settings.MAX_IMAGE_SIZE = 5 * 1024 * 1024
        settings.IMAGE_EXTENSIONS = {".jpg", ".png"}
        v = get_image_validator()
        assert v.max_size == 5 * 1024 * 1024
        assert ".jpg" in v.allowed_extensions

    def test_get_document_validator(self, settings):
        from apps.core.storage.validators import get_document_validator

        settings.MAX_DOCUMENT_SIZE = 25 * 1024 * 1024
        settings.DOCUMENT_EXTENSIONS = {".pdf", ".docx"}
        v = get_document_validator()
        assert v.max_size == 25 * 1024 * 1024

    def test_get_avatar_validator(self, settings):
        from apps.core.storage.validators import get_avatar_validator

        settings.MAX_AVATAR_SIZE = 2 * 1024 * 1024
        settings.IMAGE_EXTENSIONS = {".jpg", ".png"}
        v = get_avatar_validator()
        assert v.max_size == 2 * 1024 * 1024

    def test_get_invoice_validator(self, settings):
        from apps.core.storage.validators import get_invoice_validator

        settings.MAX_INVOICE_SIZE = 10 * 1024 * 1024
        settings.DOCUMENT_EXTENSIONS = {".pdf"}
        v = get_invoice_validator()
        assert v.max_size == 10 * 1024 * 1024


# ════════════════════════════════════════════════════════════════════════
# ImageProcessor  (Task 79 – Test Image Processing)
# ════════════════════════════════════════════════════════════════════════


class TestImageProcessorInit:
    """Test ImageProcessor construction and properties."""

    def test_init_from_file_object(self, sample_uploaded_image):
        from apps.core.storage.images import ImageProcessor

        proc = ImageProcessor(sample_uploaded_image)
        assert proc.width == 2
        assert proc.height == 2
        assert proc.format == "JPEG"

    def test_invalid_image_raises(self):
        from apps.core.storage.images import ImageProcessor

        bad = SimpleUploadedFile("bad.jpg", b"not an image", "image/jpeg")
        with pytest.raises(Exception):
            ImageProcessor(bad)

    def test_aspect_ratio(self, sample_uploaded_image):
        from apps.core.storage.images import ImageProcessor

        proc = ImageProcessor(sample_uploaded_image)
        assert proc.aspect_ratio == 1.0  # 2x2 square


class TestImageProcessorResize:
    """Test resize operations."""

    def _make_processor(self, width=800, height=600):
        from PIL import Image
        from apps.core.storage.images import ImageProcessor

        img = Image.new("RGB", (width, height), "green")
        buf = BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)
        return ImageProcessor(buf)

    def test_resize_fit(self):
        proc = self._make_processor(1000, 800)
        proc.resize(max_width=500, max_height=500, mode="fit")
        assert proc.width <= 500
        assert proc.height <= 500

    def test_resize_fill(self):
        proc = self._make_processor(1000, 800)
        proc.resize(max_width=400, max_height=400, mode="fill")
        assert proc.width == 400
        assert proc.height == 400

    def test_resize_exact(self):
        proc = self._make_processor(1000, 800)
        proc.resize(max_width=300, max_height=200, mode="exact")
        assert proc.width == 300
        assert proc.height == 200

    def test_resize_no_upscale_in_fit(self):
        """fit mode should not upscale a small image."""
        proc = self._make_processor(100, 80)
        proc.resize(max_width=500, max_height=500, mode="fit")
        # Should stay at original size (fit doesn't upscale)
        assert proc.width == 100
        assert proc.height == 80

    def test_resize_invalid_mode_raises(self):
        proc = self._make_processor()
        with pytest.raises(ValueError, match="Unknown resize mode"):
            proc.resize(max_width=100, max_height=100, mode="bogus")

    def test_resize_no_dimensions_returns_self(self):
        proc = self._make_processor()
        result = proc.resize()
        assert result is proc

    def test_resize_chaining(self):
        proc = self._make_processor(1000, 800)
        result = proc.resize(max_width=500, max_height=500, mode="fit")
        assert result is proc  # method chaining


class TestImageProcessorCompress:
    """Test compress / quality configuration."""

    def _make_processor(self):
        from PIL import Image
        from apps.core.storage.images import ImageProcessor

        img = Image.new("RGB", (200, 200), "yellow")
        buf = BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)
        return ImageProcessor(buf)

    def test_compress_sets_quality(self):
        proc = self._make_processor()
        proc.compress(quality=60, optimize=True)
        assert proc._compression_quality == 60

    def test_compress_clamps_quality(self):
        proc = self._make_processor()
        proc.compress(quality=200)
        assert proc._compression_quality == 100

        proc.compress(quality=-10)
        assert proc._compression_quality == 1

    def test_compress_chaining(self):
        proc = self._make_processor()
        result = proc.compress(quality=75)
        assert result is proc


class TestImageProcessorSave:
    """Test save output."""

    def _make_processor(self):
        from PIL import Image
        from apps.core.storage.images import ImageProcessor

        img = Image.new("RGB", (100, 100), "blue")
        buf = BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)
        return ImageProcessor(buf)

    def test_save_returns_bytesio(self):
        proc = self._make_processor()
        output = proc.save()
        assert isinstance(output, BytesIO)
        assert len(output.read()) > 0

    def test_save_jpeg(self):
        from PIL import Image

        proc = self._make_processor()
        output = proc.save(format="JPEG")
        img = Image.open(output)
        assert img.format == "JPEG"

    def test_save_png(self):
        from PIL import Image

        proc = self._make_processor()
        output = proc.save(format="PNG")
        img = Image.open(output)
        assert img.format == "PNG"

    def test_save_webp(self):
        from PIL import Image

        proc = self._make_processor()
        output = proc.save(format="WEBP")
        img = Image.open(output)
        assert img.format == "WEBP"


class TestImageProcessorConvertFormat:
    """Test format conversion."""

    def _make_rgba_processor(self):
        from PIL import Image
        from apps.core.storage.images import ImageProcessor

        img = Image.new("RGBA", (100, 100), (255, 0, 0, 128))
        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return ImageProcessor(buf)

    def _make_rgb_processor(self):
        from PIL import Image
        from apps.core.storage.images import ImageProcessor

        img = Image.new("RGB", (100, 100), "blue")
        buf = BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)
        return ImageProcessor(buf)

    def test_convert_to_jpeg_removes_alpha(self):
        proc = self._make_rgba_processor()
        proc.convert_format("JPEG")
        assert proc.format == "JPEG"
        assert proc.image.mode == "RGB"

    def test_convert_to_png(self):
        proc = self._make_rgb_processor()
        proc.convert_format("PNG")
        assert proc.format == "PNG"

    def test_convert_to_webp(self):
        proc = self._make_rgb_processor()
        proc.convert_format("WEBP")
        assert proc.format == "WEBP"

    def test_convert_unsupported_raises(self):
        proc = self._make_rgb_processor()
        with pytest.raises(ValueError, match="Unsupported format"):
            proc.convert_format("BMP")

    def test_convert_chaining(self):
        proc = self._make_rgb_processor()
        result = proc.convert_format("WEBP")
        assert result is proc


class TestImageProcessorThumbnails:
    """Test thumbnail generation."""

    def _make_processor(self):
        from PIL import Image
        from apps.core.storage.images import ImageProcessor

        img = Image.new("RGB", (800, 600), "red")
        buf = BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)
        return ImageProcessor(buf)

    def test_generate_thumbnail(self):
        proc = self._make_processor()
        thumb = proc.generate_thumbnail((100, 100))
        assert thumb.width == 100
        assert thumb.height == 100

    def test_generate_thumbnail_int_creates_square(self):
        proc = self._make_processor()
        thumb = proc.generate_thumbnail(50)
        assert thumb.width == 50
        assert thumb.height == 50

    def test_generate_thumbnail_returns_new_processor(self):
        proc = self._make_processor()
        thumb = proc.generate_thumbnail((100, 100))
        assert thumb is not proc

    def test_generate_thumbnails_dict(self):
        proc = self._make_processor()
        sizes = {"small": (100, 100), "medium": (300, 300), "large": (600, 600)}
        thumbs = proc.generate_thumbnails(sizes)
        assert set(thumbs.keys()) == {"small", "medium", "large"}
        assert thumbs["small"].width == 100
        assert thumbs["medium"].width == 300

    def test_generate_thumbnails_list(self):
        proc = self._make_processor()
        sizes = [(100, 100), (200, 200)]
        thumbs = proc.generate_thumbnails(sizes)
        assert "100x100" in thumbs
        assert "200x200" in thumbs


class TestImageProcessorWebOptimise:
    """Test optimize_for_web pipeline."""

    def _make_processor(self, width=3000, height=2000):
        from PIL import Image
        from apps.core.storage.images import ImageProcessor

        img = Image.new("RGB", (width, height), "green")
        buf = BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)
        return ImageProcessor(buf)

    def test_optimize_resizes_large_image(self):
        proc = self._make_processor(3000, 2000)
        proc.optimize_for_web(max_width=1920, max_height=1920)
        assert proc.width <= 1920
        assert proc.height <= 1920

    def test_optimize_converts_format(self):
        proc = self._make_processor()
        proc.optimize_for_web(target_format="WEBP")
        assert proc.format == "WEBP"

    def test_optimize_sets_compression(self):
        proc = self._make_processor()
        proc.optimize_for_web(quality=70)
        assert proc._compression_quality == 70

    def test_optimize_chaining(self):
        proc = self._make_processor()
        result = proc.optimize_for_web()
        assert result is proc

    def test_optimize_small_image_not_resized(self):
        proc = self._make_processor(500, 400)
        proc.optimize_for_web(max_width=1920, max_height=1920)
        # Should NOT be resized (already small)
        # format conversion still happens
        assert proc.format == "WEBP"


class TestImageProcessorResponsive:
    """Test optimize_for_responsive."""

    def _make_processor(self):
        from PIL import Image
        from apps.core.storage.images import ImageProcessor

        img = Image.new("RGB", (3000, 2000), "blue")
        buf = BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)
        return ImageProcessor(buf)

    def test_responsive_generates_variants(self):
        proc = self._make_processor()
        variants = proc.optimize_for_responsive()
        # At 3000px wide, we should get variants for widths < 3000
        assert len(variants) > 0
        for width, data in variants.items():
            assert isinstance(data, BytesIO)


class TestImageUtilities:
    """Test module-level utility functions in images.py."""

    def test_get_image_dimensions(self, sample_uploaded_image):
        from apps.core.storage.images import get_image_dimensions

        w, h = get_image_dimensions(sample_uploaded_image)
        assert w == 2
        assert h == 2

    def test_calculate_aspect_ratio(self):
        from apps.core.storage.images import calculate_aspect_ratio

        assert calculate_aspect_ratio(800, 600) == pytest.approx(800 / 600)
        assert calculate_aspect_ratio(100, 0) == 1.0

    def test_is_valid_image_true(self, sample_uploaded_image):
        from apps.core.storage.images import is_valid_image

        assert is_valid_image(sample_uploaded_image) is True

    def test_is_valid_image_false(self):
        from apps.core.storage.images import is_valid_image

        bad = SimpleUploadedFile("bad.jpg", b"not an image", "image/jpeg")
        assert is_valid_image(bad) is False

    def test_create_thumbnail_legacy(self, sample_uploaded_image):
        from apps.core.storage.images import ImageProcessor

        output = ImageProcessor.create_thumbnail(sample_uploaded_image)
        assert isinstance(output, BytesIO)
        assert len(output.read()) > 0


# ════════════════════════════════════════════════════════════════════════
# Upload Handlers  (Task 79 – handlers.py tests)
# ════════════════════════════════════════════════════════════════════════


class TestProcessImageSync:
    """Test ``process_image_sync``."""

    def test_returns_processed_file(self, sample_uploaded_image):
        from apps.core.storage.handlers import process_image_sync

        result = process_image_sync(sample_uploaded_image)
        # Should return an InMemoryUploadedFile
        assert hasattr(result, "read")
        assert result.size > 0

    def test_returns_original_on_error(self):
        from apps.core.storage.handlers import process_image_sync

        bad = SimpleUploadedFile("bad.jpg", b"not an image", "image/jpeg")
        result = process_image_sync(bad)
        # Should gracefully return the original file
        assert result is bad


class TestHandleImageUpload:
    """Test ``handle_image_upload`` sync/async dispatch."""

    def test_small_file_processed_sync(self, sample_uploaded_image):
        from apps.core.storage.handlers import handle_image_upload

        # Small file → synchronous processing
        result = handle_image_upload(sample_uploaded_image)
        assert hasattr(result, "read")

    @patch("apps.core.tasks.images.process_image_async")
    @patch("apps.core.storage.backends.get_storage_class")
    def test_large_file_queued_async(self, mock_get_storage, mock_task, large_uploaded_image):
        from apps.core.storage.handlers import handle_image_upload

        mock_storage = MagicMock()
        mock_storage.save.return_value = "tenant-t1/uploads/large.jpg"
        mock_get_storage.return_value = mock_storage

        result = handle_image_upload(large_uploaded_image, instance=MagicMock(pk=1, __class__=MagicMock(__name__="Product")))
        mock_task.delay.assert_called_once()

    def test_handles_error_gracefully(self):
        from apps.core.storage.handlers import handle_image_upload

        bad = SimpleUploadedFile("bad.jpg", b"not an image", "image/jpeg")
        result = handle_image_upload(bad)
        # On error, returns the original
        assert result is bad


class TestGenerateThumbnails:
    """Test ``generate_thumbnails`` handler function."""

    @patch("apps.core.storage.backends.get_storage_class")
    def test_generate_thumbnails_from_storage(self, mock_get_storage, sample_image_bytes):
        from apps.core.storage.handlers import generate_thumbnails

        mock_storage = MagicMock()
        mock_storage.open.return_value.__enter__ = MagicMock(
            return_value=BytesIO(sample_image_bytes)
        )
        mock_storage.open.return_value.__exit__ = MagicMock(return_value=False)
        mock_storage.save.return_value = "thumb_path.webp"
        mock_get_storage.return_value = mock_storage

        result = generate_thumbnails("products/img.jpg", save_to_storage=True)
        assert isinstance(result, dict)

    @patch("apps.core.storage.backends.get_storage_class")
    def test_generate_thumbnails_handles_error(self, mock_get_storage):
        from apps.core.storage.handlers import generate_thumbnails

        mock_get_storage.return_value.open.side_effect = FileNotFoundError
        result = generate_thumbnails("missing.jpg")
        assert result == {}


# ════════════════════════════════════════════════════════════════════════
# S3 Signed URLs  (Task 82 – Test Signed URLs)
# ════════════════════════════════════════════════════════════════════════


class TestGenerateSignedUrl:
    """Test ``generate_signed_url`` in s3.py."""

    def test_generates_url(self, settings):
        from apps.core.storage.s3 import generate_signed_url

        mock_client = MagicMock()
        mock_client.generate_presigned_url.return_value = "https://s3.example.com/signed"

        mock_boto3 = MagicMock()
        mock_boto3.client.return_value = mock_client

        mock_botocore_exc = MagicMock()

        settings.AWS_STORAGE_BUCKET_NAME = "test-bucket"
        settings.AWS_S3_REGION_NAME = "ap-south-1"

        mock_conn = MagicMock()
        mock_conn.tenant = MagicMock(schema_name="shop1")

        with patch.dict("sys.modules", {"boto3": mock_boto3, "botocore": MagicMock(), "botocore.exceptions": mock_botocore_exc}), \
             patch("apps.core.storage.s3.connection", mock_conn):
            url = generate_signed_url("invoices/INV-001.pdf", expiry=7200)

        assert url == "https://s3.example.com/signed"
        call_params = mock_client.generate_presigned_url.call_args
        assert call_params[1]["Params"]["Key"].startswith("tenant-shop1/")
        assert call_params[1]["ExpiresIn"] == 7200

    def test_default_expiry_from_settings(self, settings):
        from apps.core.storage.s3 import generate_signed_url

        mock_client = MagicMock()
        mock_client.generate_presigned_url.return_value = "https://signed"

        mock_boto3 = MagicMock()
        mock_boto3.client.return_value = mock_client

        settings.AWS_PRESIGNED_URL_EXPIRY = 1800
        settings.AWS_STORAGE_BUCKET_NAME = "bucket"
        settings.AWS_S3_REGION_NAME = "ap-south-1"

        mock_conn = MagicMock()
        mock_conn.tenant = MagicMock(schema_name="shop1")

        with patch.dict("sys.modules", {"boto3": mock_boto3, "botocore": MagicMock(), "botocore.exceptions": MagicMock()}), \
             patch("apps.core.storage.s3.connection", mock_conn):
            generate_signed_url("file.pdf")

        call_params = mock_client.generate_presigned_url.call_args
        assert call_params[1]["ExpiresIn"] == 1800

    def test_client_error_returns_none(self, settings):
        from apps.core.storage.s3 import generate_signed_url

        # Create a real exception class for botocore.exceptions.ClientError
        class FakeClientError(Exception):
            pass

        mock_boto3 = MagicMock()
        mock_boto3.client.side_effect = Exception("connection error")

        mock_botocore = MagicMock()
        mock_botocore_exc = MagicMock()
        mock_botocore_exc.ClientError = FakeClientError

        settings.AWS_STORAGE_BUCKET_NAME = "bucket"

        mock_conn = MagicMock()
        mock_conn.tenant = MagicMock(schema_name="shop1")

        with patch.dict("sys.modules", {"boto3": mock_boto3, "botocore": mock_botocore, "botocore.exceptions": mock_botocore_exc}), \
             patch("apps.core.storage.s3.connection", mock_conn):
            url = generate_signed_url("file.pdf")
        assert url is None

    def test_no_boto3_returns_none(self):
        """When boto3 is not installed, returns None."""
        import importlib
        import apps.core.storage.s3 as s3_mod

        mock_conn = MagicMock()
        mock_conn.tenant = MagicMock(schema_name="shop1")

        with patch("apps.core.storage.s3.connection", mock_conn), \
             patch("builtins.__import__", side_effect=ImportError("no boto3")):
            url = s3_mod.generate_signed_url("file.pdf")
            assert url is None

    @patch("apps.core.storage.s3.connection")
    def test_public_fallback_tenant(self, mock_conn):
        from apps.core.storage.s3 import _get_current_tenant_schema

        mock_conn.tenant = None
        assert _get_current_tenant_schema() == "public"


class TestGenerateBulkSignedUrls:
    """Test ``generate_bulk_signed_urls``."""

    @patch("apps.core.storage.s3.generate_signed_url")
    def test_generates_for_all_paths(self, mock_gen):
        from apps.core.storage.s3 import generate_bulk_signed_urls

        mock_gen.side_effect = lambda p, **kw: f"https://signed/{p}"
        paths = ["a.pdf", "b.pdf", "c.pdf"]
        result = generate_bulk_signed_urls(paths)
        assert len(result) == 3
        assert "a.pdf" in result

    @patch("apps.core.storage.s3.generate_signed_url")
    def test_skips_failed_urls(self, mock_gen):
        from apps.core.storage.s3 import generate_bulk_signed_urls

        mock_gen.side_effect = [None, "https://ok", None]
        result = generate_bulk_signed_urls(["a.pdf", "b.pdf", "c.pdf"])
        assert len(result) == 1
        assert "b.pdf" in result


# ════════════════════════════════════════════════════════════════════════
# FileCleanup  (Task 80/82 – cleanup & command tests)
# ════════════════════════════════════════════════════════════════════════


class TestFileCleanup:
    """Test ``FileCleanup`` utility class."""

    def test_init_defaults(self):
        from apps.core.storage.cleanup import FileCleanup

        fc = FileCleanup()
        assert fc.dry_run is True
        assert fc.deleted_count == 0

    def test_find_orphaned_files(self):
        from apps.core.storage.cleanup import FileCleanup

        mock_storage = MagicMock()
        mock_storage.listdir.return_value = ([], ["a.jpg", "b.jpg", "c.jpg"])
        mock_storage.get_modified_time.return_value = timezone.now() - timedelta(days=30)

        fc = FileCleanup(storage=mock_storage, dry_run=True)
        # Mock get_referenced_files to return only b.jpg
        fc.get_referenced_files = MagicMock(return_value={"b.jpg"})

        orphans = fc.find_orphaned_files(min_age_days=7)
        assert "a.jpg" in orphans
        assert "c.jpg" in orphans
        assert "b.jpg" not in orphans

    def test_delete_orphaned_dry_run(self):
        from apps.core.storage.cleanup import FileCleanup

        mock_storage = MagicMock()
        mock_storage.size.return_value = 1024

        fc = FileCleanup(storage=mock_storage, dry_run=True)
        result = fc.delete_orphaned_files(["a.jpg", "b.jpg"])

        assert result["deleted"] == 0
        assert result["skipped"] == 2
        mock_storage.delete.assert_not_called()

    def test_delete_orphaned_live(self):
        from apps.core.storage.cleanup import FileCleanup

        mock_storage = MagicMock()
        mock_storage.size.return_value = 512

        fc = FileCleanup(storage=mock_storage, dry_run=False)
        result = fc.delete_orphaned_files(["x.jpg", "y.jpg"])

        assert result["deleted"] == 2
        assert result["errors"] == 0
        assert mock_storage.delete.call_count == 2

    def test_delete_handles_errors(self):
        from apps.core.storage.cleanup import FileCleanup

        mock_storage = MagicMock()
        mock_storage.size.side_effect = OSError("disk error")
        mock_storage.delete.side_effect = OSError("delete error")

        fc = FileCleanup(storage=mock_storage, dry_run=False)
        result = fc.delete_orphaned_files(["a.jpg"])
        assert result["errors"] == 1

    def test_cleanup_combines_find_and_delete(self):
        from apps.core.storage.cleanup import FileCleanup

        mock_storage = MagicMock()
        mock_storage.listdir.return_value = ([], ["orphan.jpg"])
        mock_storage.get_modified_time.return_value = timezone.now() - timedelta(days=30)
        mock_storage.size.return_value = 100

        fc = FileCleanup(storage=mock_storage, dry_run=False)
        fc.get_referenced_files = MagicMock(return_value=set())

        result = fc.cleanup(min_age_days=7)
        assert result["deleted"] == 1

    def test_no_orphans_returns_clean_stats(self):
        from apps.core.storage.cleanup import FileCleanup

        mock_storage = MagicMock()
        mock_storage.listdir.return_value = ([], [])

        fc = FileCleanup(storage=mock_storage, dry_run=True)
        fc.get_referenced_files = MagicMock(return_value=set())

        orphans = fc.find_orphaned_files()
        assert orphans == []


class TestCleanupOldFiles:
    """Test module-level convenience function."""

    @patch("apps.core.storage.cleanup.FileCleanup.cleanup")
    def test_cleanup_old_files(self, mock_cleanup):
        from apps.core.storage.cleanup import cleanup_old_files

        mock_cleanup.return_value = {"deleted": 5, "skipped": 0, "errors": 0, "total_size_freed": 1024}

        result = cleanup_old_files(days_old=30, dry_run=False)
        assert result["deleted"] == 5
        mock_cleanup.assert_called_once_with(min_age_days=30)


class TestFileCleanupGetReferencedFiles:
    """Test ``FileCleanup.get_referenced_files`` with mocked models."""

    @patch("apps.core.storage.cleanup.apps")
    def test_collects_file_fields(self, mock_apps):
        from apps.core.storage.cleanup import FileCleanup
        from django.db import models

        # Create a mock model with a FileField
        mock_field = MagicMock(spec=models.FileField)
        mock_field.name = "document"

        mock_model = MagicMock()
        mock_model._meta.get_fields.return_value = [mock_field]
        mock_model._meta.app_label = "core"
        mock_model._meta.model_name = "invoice"

        mock_instance = MagicMock()
        mock_instance.document = MagicMock()
        mock_instance.document.name = "invoices/INV-001.pdf"

        mock_model.objects.using.return_value.all.return_value.iterator.return_value = [
            mock_instance
        ]

        mock_apps.get_models.return_value = [mock_model]

        fc = FileCleanup()
        refs = fc.get_referenced_files()
        assert "invoices/INV-001.pdf" in refs

    @patch("apps.core.storage.cleanup.apps")
    def test_handles_model_errors(self, mock_apps):
        from apps.core.storage.cleanup import FileCleanup
        from django.db import models

        mock_field = MagicMock(spec=models.FileField)
        mock_field.name = "document"

        mock_model = MagicMock()
        mock_model._meta.get_fields.return_value = [mock_field]
        mock_model._meta.app_label = "core"
        mock_model._meta.model_name = "broken"
        mock_model.objects.using.side_effect = Exception("db error")

        mock_apps.get_models.return_value = [mock_model]

        fc = FileCleanup()
        refs = fc.get_referenced_files()
        # Should not raise, just skip
        assert isinstance(refs, set)


# ════════════════════════════════════════════════════════════════════════
# cleanmedia Management Command  (Task 80 – command test)
# ════════════════════════════════════════════════════════════════════════


class TestCleanmediaCommand:
    """Test ``cleanmedia`` management command."""

    @patch("apps.core.management.commands.cleanmedia.FileCleanup")
    def test_dry_run_no_orphans(self, MockCleanup):
        mock_instance = MockCleanup.return_value
        mock_instance.find_orphaned_files.return_value = []

        out = StringIO()
        call_command("cleanmedia", stdout=out)
        output = out.getvalue()
        assert "No orphaned files found" in output or "DRY RUN" in output

    @patch("apps.core.management.commands.cleanmedia.FileCleanup")
    def test_dry_run_with_orphans(self, MockCleanup):
        mock_instance = MockCleanup.return_value
        mock_instance.find_orphaned_files.return_value = ["orphan1.jpg", "orphan2.jpg"]
        mock_instance.storage = MagicMock()
        mock_instance.storage.size.return_value = 1024

        out = StringIO()
        call_command("cleanmedia", stdout=out)
        output = out.getvalue()
        assert "orphaned" in output.lower() or "DRY RUN" in output

    @patch("apps.core.management.commands.cleanmedia.FileCleanup")
    @patch("builtins.input", return_value="yes")
    def test_force_deletes(self, mock_input, MockCleanup):
        mock_instance = MockCleanup.return_value
        mock_instance.find_orphaned_files.return_value = ["orphan.jpg"]
        mock_instance.storage = MagicMock()
        mock_instance.storage.size.return_value = 2048
        mock_instance.delete_orphaned_files.return_value = {
            "deleted": 1, "skipped": 0, "errors": 0, "total_size_freed": 2048,
        }

        out = StringIO()
        call_command("cleanmedia", "--force", stdout=out)
        mock_instance.delete_orphaned_files.assert_called_once()

    @patch("apps.core.management.commands.cleanmedia.FileCleanup")
    @patch("builtins.input", return_value="no")
    def test_force_cancelled(self, mock_input, MockCleanup):
        out = StringIO()
        call_command("cleanmedia", "--force", stdout=out)
        output = out.getvalue()
        assert "cancelled" in output.lower()

    @patch("apps.core.management.commands.cleanmedia.FileCleanup")
    def test_tenant_flag_sets_path(self, MockCleanup):
        mock_instance = MockCleanup.return_value
        mock_instance.find_orphaned_files.return_value = []

        out = StringIO()
        call_command("cleanmedia", "--tenant=shop123", stdout=out)
        mock_instance.find_orphaned_files.assert_called_once()
        call_path = mock_instance.find_orphaned_files.call_args[0][0]
        assert "tenant-shop123" in call_path

    @patch("apps.core.management.commands.cleanmedia.FileCleanup")
    def test_min_age_days_option(self, MockCleanup):
        mock_instance = MockCleanup.return_value
        mock_instance.find_orphaned_files.return_value = []

        out = StringIO()
        call_command("cleanmedia", "--min-age-days=30", stdout=out)
        call_days = mock_instance.find_orphaned_files.call_args[0][1]
        assert call_days == 30

    @patch("apps.core.management.commands.cleanmedia.FileCleanup")
    def test_error_raises_command_error(self, MockCleanup):
        from django.core.management.base import CommandError

        MockCleanup.side_effect = Exception("boom")
        with pytest.raises(CommandError):
            call_command("cleanmedia")


# ════════════════════════════════════════════════════════════════════════
# __init__.py exports  (Task 86 – integration smoke test)
# ════════════════════════════════════════════════════════════════════════


class TestStorageModuleExports:
    """Verify the public API surface of apps.core.storage."""

    def test_backends_importable(self):
        from apps.core.storage import (
            TenantFileStorage,
            TenantMediaStorage,
            PublicStorage,
            get_storage_class,
        )

    def test_path_generators_importable(self):
        from apps.core.storage import (
            product_path,
            invoice_path,
            document_path,
            avatar_path,
            tenant_upload_path,
        )

    def test_constants_importable(self):
        from apps.core.storage import (
            SIGNED_URL_DEFAULT_EXPIRY,
            THUMB_SMALL,
            THUMB_MEDIUM,
            THUMB_LARGE,
            THUMBNAIL_SIZES,
            IMAGE_EXTENSIONS,
            DOCUMENT_EXTENSIONS,
            ALL_ALLOWED_EXTENSIONS,
            KB, MB, GB,
        )

    def test_image_processor_importable(self):
        from apps.core.storage import ImageProcessor

    def test_validators_importable(self):
        from apps.core.storage import (
            FileValidator,
            get_image_validator,
            get_document_validator,
            get_avatar_validator,
            get_invoice_validator,
        )

    def test_handlers_importable(self):
        from apps.core.storage import (
            handle_image_upload,
            process_image_sync,
            generate_thumbnails,
        )

    def test_cleanup_importable(self):
        from apps.core.storage import FileCleanup, cleanup_old_files

    def test_s3_importable(self):
        from apps.core.storage import generate_signed_url, generate_bulk_signed_urls
