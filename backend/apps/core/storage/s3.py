"""
LankaCommerce Cloud – S3 Utility Functions (SP10 Task 44).

Standalone helpers for generating pre-signed S3 URLs outside the
storage-backend context (e.g. in views, serializers, or Celery tasks).

Usage::

    from apps.core.storage.s3 import generate_signed_url, generate_bulk_signed_urls

    url = generate_signed_url("invoices/INV-001.pdf", expiry=7200)

    urls = generate_bulk_signed_urls(
        ["invoices/INV-001.pdf", "reports/q1.pdf"],
        expiry=3600,
    )
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.conf import settings
from django.db import connection

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------


def generate_signed_url(
    file_path: str,
    expiry: int | None = None,
    *,
    bucket: str | None = None,
) -> str | None:
    """
    Generate a pre-signed URL for secure, temporary access to a private S3 file.

    Args:
        file_path: Path to file in S3 (*without* tenant prefix).
        expiry: URL expiry time in seconds.
                Defaults to ``settings.AWS_PRESIGNED_URL_EXPIRY`` (3600).
        bucket: Override bucket name (defaults to ``settings.AWS_STORAGE_BUCKET_NAME``).

    Returns:
        Presigned URL string, or ``None`` on error.

    Example::

        url = generate_signed_url("invoices/INV-001.pdf", expiry=7200)
    """
    try:
        import boto3
        from botocore.exceptions import ClientError
    except ImportError:
        logger.error("boto3 is required for generating signed URLs")
        return None

    try:
        # Determine tenant prefix
        tenant_schema = _get_current_tenant_schema()
        s3_key = f"tenant-{tenant_schema}/{file_path}"

        # Resolve settings
        expiry = expiry or getattr(settings, "AWS_PRESIGNED_URL_EXPIRY", 3600)
        bucket = bucket or getattr(settings, "AWS_STORAGE_BUCKET_NAME", "")
        region = getattr(settings, "AWS_S3_REGION_NAME", "ap-south-1")

        s3_client = boto3.client("s3", region_name=region)

        url: str = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": s3_key},
            ExpiresIn=expiry,
        )
        return url

    except ClientError:
        logger.error("S3 ClientError generating signed URL for %s", file_path, exc_info=True)
        return None
    except Exception:
        logger.error("Unexpected error generating signed URL for %s", file_path, exc_info=True)
        return None


def generate_bulk_signed_urls(
    file_paths: list[str],
    expiry: int | None = None,
    *,
    bucket: str | None = None,
) -> dict[str, str]:
    """
    Generate pre-signed URLs for multiple files in one call.

    Args:
        file_paths: List of file paths (without tenant prefix).
        expiry: URL expiry time in seconds.
        bucket: Override bucket name.

    Returns:
        Dict mapping each file path to its signed URL.
        Only paths for which a URL could be generated are included.

    Example::

        urls = generate_bulk_signed_urls(
            ["invoices/INV-001.pdf", "invoices/INV-002.pdf"],
            expiry=7200,
        )
    """
    urls: dict[str, str] = {}
    for path in file_paths:
        url = generate_signed_url(path, expiry=expiry, bucket=bucket)
        if url:
            urls[path] = url
    return urls


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _get_current_tenant_schema() -> str:
    """Return the current tenant schema name, falling back to ``public``."""
    try:
        tenant = connection.tenant
        if tenant and hasattr(tenant, "schema_name"):
            return tenant.schema_name
    except Exception:
        pass
    return "public"
