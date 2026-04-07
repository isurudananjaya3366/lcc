"""
LankaCommerce Cloud – File Storage Configuration (SP10).

Centralises every file-storage knob: size limits, allowed extensions,
thumbnail presets, S3 credentials, and tenant quota definitions.

Settings are imported into ``base.py`` via::

    from config.settings.storage import *
"""

import logging
from pathlib import Path  # noqa: F401

from config.env import BASE_DIR, env

logger = logging.getLogger(__name__)

# ════════════════════════════════════════════════════════════════════════
# Storage Backend Switch
# ════════════════════════════════════════════════════════════════════════

STORAGE_BACKEND: str = env("STORAGE_BACKEND", default="local")  # "local" | "s3"


# ════════════════════════════════════════════════════════════════════════
# Local File Storage (Development)
# ════════════════════════════════════════════════════════════════════════
# MEDIA_URL: Base URL for user-uploaded media files.
# MEDIA_ROOT: Absolute filesystem path where uploads are stored.
#
# Directory structure:
#   media/
#     tenant-<schema>/  – Tenant-isolated uploads (e.g. tenant-shop123/)
#     public/            – Public shared files

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# ════════════════════════════════════════════════════════════════════════
# Static Files Configuration
# ════════════════════════════════════════════════════════════════════════
# STATIC_URL: Base URL for static files (CSS, JS, images).
# STATIC_ROOT: Where ``collectstatic`` gathers files for production.

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"


# ════════════════════════════════════════════════════════════════════════
# Storage Backend Selection (STORAGES dict)
# ════════════════════════════════════════════════════════════════════════
# Default: django-tenants local filesystem with WhiteNoise for static.
# When STORAGE_BACKEND="s3", the S3 section below overrides "default".

STORAGES: dict = {
    "default": {
        "BACKEND": "django_tenants.files.storage.TenantFileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# ════════════════════════════════════════════════════════════════════════
# Maximum File-Size Constants (bytes)
# ════════════════════════════════════════════════════════════════════════

MAX_IMAGE_SIZE: int = 5 * 1024 * 1024       # 5 MB
MAX_AVATAR_SIZE: int = 2 * 1024 * 1024      # 2 MB
MAX_DOCUMENT_SIZE: int = 25 * 1024 * 1024   # 25 MB
MAX_INVOICE_SIZE: int = 10 * 1024 * 1024    # 10 MB
MAX_REPORT_SIZE: int = 25 * 1024 * 1024     # 25 MB
MAX_CONTRACT_SIZE: int = 50 * 1024 * 1024   # 50 MB
MAX_BANNER_SIZE: int = 10 * 1024 * 1024     # 10 MB


# ════════════════════════════════════════════════════════════════════════
# Allowed File Extensions
# ════════════════════════════════════════════════════════════════════════

IMAGE_EXTENSIONS: set[str] = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".ico",
}
DOCUMENT_EXTENSIONS: set[str] = {
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".csv", ".txt", ".rtf",
}
ARCHIVE_EXTENSIONS: set[str] = {".zip", ".tar", ".gz", ".rar"}

ALL_ALLOWED_EXTENSIONS: set[str] = IMAGE_EXTENSIONS | DOCUMENT_EXTENSIONS | ARCHIVE_EXTENSIONS


# ════════════════════════════════════════════════════════════════════════
# Thumbnail Presets
# ════════════════════════════════════════════════════════════════════════

THUMB_SMALL: tuple[int, int] = (100, 100)
THUMB_MEDIUM: tuple[int, int] = (300, 300)
THUMB_LARGE: tuple[int, int] = (600, 600)
THUMB_PRODUCT: tuple[int, int] = (800, 800)

IMAGE_QUALITY: int = 85
IMAGE_FORMAT: str = "WEBP"


# ════════════════════════════════════════════════════════════════════════
# AWS / S3 Settings
# ════════════════════════════════════════════════════════════════════════

AWS_ACCESS_KEY_ID: str = env("AWS_ACCESS_KEY_ID", default="")
AWS_SECRET_ACCESS_KEY: str = env("AWS_SECRET_ACCESS_KEY", default="")
AWS_STORAGE_BUCKET_NAME: str = env("AWS_STORAGE_BUCKET_NAME", default="lankacommerce-media")
AWS_S3_REGION_NAME: str = env("AWS_S3_REGION_NAME", default="ap-south-1")
AWS_S3_CUSTOM_DOMAIN: str = env("AWS_S3_CUSTOM_DOMAIN", default="")
AWS_S3_OBJECT_PARAMETERS: dict = {"CacheControl": "max-age=86400"}
AWS_DEFAULT_ACL = None
AWS_S3_FILE_OVERWRITE: bool = False
AWS_QUERYSTRING_AUTH: bool = True
AWS_S3_SIGNATURE_VERSION: str = "s3v4"
AWS_PRESIGNED_URL_EXPIRY: int = 3600
AWS_PRIVATE_BUCKET_NAME: str = env("AWS_PRIVATE_BUCKET_NAME", default="")
AWS_PUBLIC_BUCKET_NAME: str = env("AWS_PUBLIC_BUCKET_NAME", default="")


# ════════════════════════════════════════════════════════════════════════
# STORAGES Override (S3 Mode)
# ════════════════════════════════════════════════════════════════════════

if STORAGE_BACKEND == "s3":
    # Validate required S3 credentials (Tasks 34-36)
    from django.core.exceptions import ImproperlyConfigured as _ImproperlyConfigured

    _required_s3_settings = {
        "AWS_ACCESS_KEY_ID": AWS_ACCESS_KEY_ID,
        "AWS_SECRET_ACCESS_KEY": AWS_SECRET_ACCESS_KEY,
        "AWS_STORAGE_BUCKET_NAME": AWS_STORAGE_BUCKET_NAME,
    }
    for _setting_name, _setting_value in _required_s3_settings.items():
        if not _setting_value:
            raise _ImproperlyConfigured(
                f"{_setting_name} environment variable is required "
                f"when STORAGE_BACKEND='s3'"
            )

    # Override the local STORAGES default with the S3 tenant backend.
    # Static files keep using WhiteNoise.
    try:
        STORAGES = {  # type: ignore[no-redef]
            "default": {
                "BACKEND": "apps.core.storage.backends.TenantS3Storage",
            },
            "staticfiles": {
                "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
            },
        }
        logger.info("File storage: S3 backend enabled (bucket=%s)", AWS_STORAGE_BUCKET_NAME)
    except Exception:
        logger.exception("Failed to configure S3 storage; falling back to local")

    # Named storage backend paths for model-level overrides (Task 46)
    PRIVATE_FILE_STORAGE: str = "apps.core.storage.backends.PrivateTenantS3Storage"
    PUBLIC_FILE_STORAGE: str = "apps.core.storage.backends.PublicTenantS3Storage"
else:
    # Development: local file system storage
    PRIVATE_FILE_STORAGE: str = "apps.core.storage.backends.TenantFileStorage"  # type: ignore[no-redef]
    PUBLIC_FILE_STORAGE: str = "apps.core.storage.backends.TenantFileStorage"  # type: ignore[no-redef]


# ════════════════════════════════════════════════════════════════════════
# Tenant Storage Quotas
# ════════════════════════════════════════════════════════════════════════

TENANT_STORAGE_QUOTAS: dict[str, int | None] = {
    "free": 1 * 1024**3,        # 1 GB
    "basic": 10 * 1024**3,      # 10 GB
    "pro": 50 * 1024**3,        # 50 GB
    "enterprise": None,          # Unlimited
}
