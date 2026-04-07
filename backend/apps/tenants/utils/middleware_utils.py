"""
Middleware utility helpers for LankaCommerce Cloud tenant middleware.

Provides request-level helpers that extract tenant information from
a resolved Django HttpRequest object. These functions assume the
LCCTenantMiddleware has already run (i.e., the middleware is active
and has injected request.tenant and request.schema_name).

Usage (in views, serializers, or downstream middleware):

    from apps.tenants.utils.middleware_utils import (
        get_tenant_from_request,
        get_schema_from_request,
        is_tenant_resolved,
        is_public_tenant,
    )

    def my_view(request):
        tenant = get_tenant_from_request(request)
        schema = get_schema_from_request(request)
        if is_public_tenant(request):
            ...

Note:
    For connection-level access (independent of a request object) use
    apps.tenants.utils.tenant_context.get_current_tenant() instead,
    which is implemented in Group-A Doc 03 (Tasks 11-14).
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.http import HttpRequest

logger = logging.getLogger(__name__)

# The schema name used by django-tenants for the shared (public) schema.
# Defined by PUBLIC_SCHEMA_NAME in settings (defaults to "public").
PUBLIC_SCHEMA_NAME: str = "public"


def get_tenant_from_request(request: "HttpRequest"):
    """
    Return the active Tenant instance attached to the request.

    LCCTenantMiddleware injects ``request.tenant`` during
    ``process_request``. This helper provides a safe accessor
    with an explicit None return if the attribute is absent.

    Args:
        request: A Django HttpRequest that has been processed by
            LCCTenantMiddleware.

    Returns:
        Tenant | None: The active Tenant model instance, or None
        if tenant resolution failed or the middleware has not run.
    """
    return getattr(request, "tenant", None)


def get_schema_from_request(request: "HttpRequest") -> str | None:
    """
    Return the active PostgreSQL schema name attached to the request.

    LCCTenantMiddleware injects ``request.schema_name`` during
    ``process_request`` after activating the tenant's schema via
    ``django.db.connection.set_tenant()``.

    Args:
        request: A Django HttpRequest that has been processed by
            LCCTenantMiddleware.

    Returns:
        str | None: The PostgreSQL schema name string (e.g. "tenant_abc"),
        or None if tenant resolution failed or the middleware has not run.
    """
    return getattr(request, "schema_name", None)


def is_tenant_resolved(request: "HttpRequest") -> bool:
    """
    Return True if a tenant was successfully resolved for this request.

    A request has a resolved tenant when LCCTenantMiddleware found a
    matching Domain and activated the corresponding schema. Returns
    False for public-schema requests (e.g. admin, API root) and for
    any request where tenant resolution failed.

    Args:
        request: A Django HttpRequest that has been processed by
            LCCTenantMiddleware.

    Returns:
        bool: True if request.tenant is not None, False otherwise.
    """
    return getattr(request, "tenant", None) is not None


def is_public_tenant(request: "HttpRequest") -> bool:
    """
    Return True if the request is operating under the public schema.

    The public schema holds shared objects (e.g. platform users, tenants,
    domains). Tenant-specific business data lives in private schemas.

    Args:
        request: A Django HttpRequest that has been processed by
            LCCTenantMiddleware.

    Returns:
        bool: True if the current schema is the public schema,
        True also if no tenant is resolved (fallback to public),
        False if the request is scoped to a private tenant schema.
    """
    schema = get_schema_from_request(request)
    return schema is None or schema == PUBLIC_SCHEMA_NAME
