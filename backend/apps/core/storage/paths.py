"""
LankaCommerce Cloud – Upload Path Generators (SP10 Tasks 25-30).

Reusable ``upload_to`` callables for Django FileField / ImageField.
Each function returns a relative path that is combined with the
tenant prefix by the storage backend (TenantFileStorage / TenantMediaStorage).

Path Functions:
    - product_path:  products/YYYY/MM/DD/{uuid}.{ext}
    - invoice_path:  invoices/{invoice_number}.{ext}
    - document_path: documents/{type}/{uuid}.{ext}
    - avatar_path:   avatars/user_{id}.{ext}

Usage::

    from apps.core.storage import TenantMediaStorage, product_path

    class Product(models.Model):
        image = models.ImageField(
            upload_to=product_path,
            storage=TenantMediaStorage(),
        )
"""

import os
import uuid
from datetime import date

from django.db import connection


def _get_tenant_prefix() -> str:
    try:
        tenant = connection.tenant
        if tenant and hasattr(tenant, "schema_name"):
            return tenant.schema_name
    except Exception:
        pass
    return "public"


def _unique_filename(original: str) -> str:
    ext = os.path.splitext(original)[1].lower()
    return f"{uuid.uuid4().hex}{ext}"


def tenant_upload_path(instance, filename: str, subfolder: str = "uploads") -> str:
    """Generic tenant-scoped upload path."""
    prefix = _get_tenant_prefix()
    return os.path.join(prefix, subfolder, _unique_filename(filename))


def product_path(instance, filename: str) -> str:
    """
    Generate upload path for product images.

    Organizes product images by date in YYYY/MM/DD/ format
    with UUID-based filenames to prevent conflicts.

    Args:
        instance: Product model instance
        filename: Original uploaded filename

    Returns:
        Path: products/YYYY/MM/DD/{uuid}.{ext}

    Example:
        products/2026/01/22/a1b2c3d4e5f6.jpg
    """
    today = date.today()
    date_path = today.strftime("%Y/%m/%d")
    return os.path.join("products", date_path, _unique_filename(filename))


def invoice_path(instance, filename: str) -> str:
    """
    Generate upload path for invoice documents.

    Uses invoice number as filename for easy reference and lookup.
    Falls back to UUID-based filename if invoice number is unavailable.

    Args:
        instance: Invoice model instance
        filename: Original uploaded filename

    Returns:
        Path: invoices/{invoice_number}.{ext} or invoices/{uuid}.{ext}

    Example:
        invoices/INV-2026-001.pdf
    """
    ext = os.path.splitext(filename)[1].lower()
    invoice_number = getattr(instance, "invoice_number", None)
    if invoice_number:
        safe_name = invoice_number.replace("/", "-")
        invoice_filename = f"{safe_name}{ext}"
    else:
        invoice_filename = _unique_filename(filename)
    return os.path.join("invoices", invoice_filename)


def document_path(instance, filename: str) -> str:
    """
    Generate upload path for general documents.

    Organizes documents by type/category with UUID-based filenames.
    Falls back to 'general' if no ``document_type`` attribute on instance.

    Args:
        instance: Document model instance
        filename: Original uploaded filename

    Returns:
        Path: documents/{type}/{uuid}.{ext}

    Example:
        documents/reports/a1b2c3d4.pdf
    """
    doc_type = getattr(instance, "document_type", "general")
    safe_type = doc_type.lower().replace(" ", "_")
    return os.path.join("documents", safe_type, _unique_filename(filename))


def avatar_path(instance, filename: str) -> str:
    """
    Generate upload path for user avatar images.

    Uses user ID in filename for easy association and retrieval.
    Overwrites previous avatar on new upload (same filename per user).

    Args:
        instance: User model instance
        filename: Original uploaded filename

    Returns:
        Path: avatars/user_{id}.{ext}

    Example:
        avatars/user_42.jpg
    """
    ext = os.path.splitext(filename)[1].lower()
    user_id = getattr(instance, "pk", "unknown")
    avatar_filename = f"user_{user_id}{ext}"
    return os.path.join("avatars", avatar_filename)
