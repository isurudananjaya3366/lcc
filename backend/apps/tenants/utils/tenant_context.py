"""
Tenant context module for LankaCommerce Cloud.

Provides thread-local tenant context storage and accessors for use in
code that runs outside of a normal HTTP request lifecycle, such as:
    - Celery background tasks
    - Management commands
    - Data migration scripts
    - Signal handlers
    - Multi-tenant test fixtures

Architecture:
    HTTP requests use LCCTenantMiddleware which activates the tenant
    schema via django.db.connection.set_tenant(). This module provides
    a complementary thread-local store (_thread_locals.tenant) so that
    the current tenant identity is always accessible via
    get_current_tenant(), regardless of whether the caller has access
    to a request object.

    The two stores are kept in sync:
        set_current_tenant(tenant)  ←→  connection.set_tenant(tenant)

Thread safety:
    threading.local() is used so each thread (each Django worker /
    Celery worker) has its own isolated tenant value.

Usage:
    # Reading the current tenant (request-independent)
    from apps.tenants.utils.tenant_context import get_current_tenant

    tenant = get_current_tenant()

    # Temporarily switching to another tenant (background tasks)
    from apps.tenants.utils.tenant_context import tenant_context

    with tenant_context(some_tenant):
        # All ORM queries in this block run against some_tenant's schema
        ...

    # Explicitly setting the tenant (Celery task setup)
    from apps.tenants.utils.tenant_context import set_current_tenant

    set_current_tenant(tenant_instance)
"""

from __future__ import annotations

import contextlib
import logging
import threading
from typing import TYPE_CHECKING, Generator

if TYPE_CHECKING:
    pass  # Avoid circular imports; Tenant imported lazily where needed

logger = logging.getLogger(__name__)

# ── Thread-local storage ──────────────────────────────────────────────
# One instance per Python process; each thread gets its own .tenant slot.
_thread_locals = threading.local()


# ── Task 12: get_current_tenant ───────────────────────────────────────

def get_current_tenant():
    """
    Return the currently active Tenant instance.

    Checks thread-local storage first (set by set_current_tenant or the
    tenant_context manager). Falls back to django.db.connection.tenant
    which is set by django-tenants during the request cycle via
    LCCTenantMiddleware.

    Returns:
        Tenant | None: The active Tenant model instance, or None when
        running in the public schema or when no tenant has been set.

    Example:
        tenant = get_current_tenant()
        if tenant is not None:
            print(tenant.schema_name)
    """
    # Prefer explicitly set thread-local value (background tasks).
    tenant = getattr(_thread_locals, "tenant", None)
    if tenant is not None:
        return tenant

    # Fall back to what django-tenants has activated on the connection.
    from django.db import connection

    return getattr(connection, "tenant", None)


# ── Task 13: set_current_tenant ───────────────────────────────────────

def set_current_tenant(tenant) -> None:
    """
    Activate a tenant by updating thread-local storage and the database
    connection schema.

    Calling this function:
        1. Stores the tenant instance in the current thread's local storage.
        2. Activates the tenant's PostgreSQL schema on the DB connection
           via connection.set_tenant(), ensuring all subsequent ORM
           queries run against the correct schema.

    When tenant is None the connection is reset to the public schema and
    the thread-local slot is cleared.

    Args:
        tenant: A Tenant model instance to activate, or None to
            deactivate and return to the public schema.

    Example:
        from apps.tenants.models import Tenant

        tenant = Tenant.objects.get(schema_name="acme")
        set_current_tenant(tenant)
        # All ORM queries now run against the "acme" schema.
    """
    if tenant is not None:
        _thread_locals.tenant = tenant

        from django.db import connection

        connection.set_tenant(tenant)
        logger.debug(
            "set_current_tenant: activated tenant='%s' schema='%s'",
            getattr(tenant, "name", "?"),
            getattr(tenant, "schema_name", "?"),
        )
    else:
        _thread_locals.tenant = None

        from django.db import connection

        connection.set_schema_to_public()
        logger.debug("set_current_tenant: reset to public schema")


# ── Task 11: Tenant context manager ──────────────────────────────────

@contextlib.contextmanager
def tenant_context(tenant) -> Generator[None, None, None]:
    """
    Context manager for temporary tenant schema switching.

    Activates the given tenant on entry and restores the previous tenant
    (or the public schema if none was active) on exit, even if an
    exception is raised inside the block.

    Primary use cases:
        - Running a block of ORM code for a specific tenant inside a
          Celery task that serves multiple tenants sequentially.
        - Management commands that iterate over all tenants.
        - Unit tests that need to assert schema-isolated behaviour.

    Args:
        tenant: A Tenant model instance to activate for the duration
            of the context block. Must not be None.

    Yields:
        None

    Raises:
        ValueError: If tenant is None (use set_current_tenant(None)
            directly to return to public schema).

    Example:
        from apps.tenants.models import Tenant
        from apps.tenants.utils.tenant_context import tenant_context

        for tenant in Tenant.objects.exclude(schema_name="public"):
            with tenant_context(tenant):
                process_tenant_data()
    """
    if tenant is None:
        raise ValueError(
            "tenant_context() requires a non-None Tenant instance. "
            "Call set_current_tenant(None) directly to reset to public schema."
        )

    # Capture whatever is active now so we can restore it on exit.
    previous_tenant = get_current_tenant()

    try:
        set_current_tenant(tenant)
        logger.debug(
            "tenant_context: entered for tenant='%s'",
            getattr(tenant, "name", "?"),
        )
        yield
    finally:
        # Always restore — even if an exception was raised.
        set_current_tenant(previous_tenant)
        logger.debug(
            "tenant_context: exited, restored to '%s'",
            getattr(previous_tenant, "name", "public") if previous_tenant else "public",
        )
