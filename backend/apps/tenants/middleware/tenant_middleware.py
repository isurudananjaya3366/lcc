"""
Custom tenant middleware for LankaCommerce Cloud.

Extends django-tenants TenantMainMiddleware to provide tenant resolution
from the request hostname, schema activation, request attribute injection,
and structured logging for every request.

Usage:
    Set as the FIRST entry in Django's MIDDLEWARE list:

        MIDDLEWARE = [
            "apps.tenants.middleware.LCCTenantMiddleware",
            "django.middleware.security.SecurityMiddleware",
            ...
        ]

Base behaviour (inherited from TenantMainMiddleware):
    1. Extracts the hostname from the request Host header.
    2. Looks up the Domain model for that hostname.
    3. Retrieves the associated Tenant.
    4. Activates the tenant's PostgreSQL schema via connection.set_tenant().
    5. Delegates to the next middleware/view handler.
    6. Deactivates the schema after the response is generated.
"""

import logging

from django_tenants.middleware.main import TenantMainMiddleware

logger = logging.getLogger(__name__)


class LCCTenantMiddleware(TenantMainMiddleware):
    """
    Custom tenant middleware for LankaCommerce Cloud.

    Extends django-tenants TenantMainMiddleware with:
        - Structured debug/warning logging for every tenant resolution.
        - Request attribute injection: request.tenant and
          request.schema_name for convenient downstream access.
        - Transparent pass-through for all other base behaviour.

    Position:
        MUST be the FIRST entry in Django's MIDDLEWARE list. Placing it
        after security or session middleware will break schema isolation.

    Tenant resolution flow:
        Request → hostname extraction → Domain lookup → Tenant lookup
        → connection.set_tenant() → schema_name activated → next handler

    On resolution failure:
        TenantMainMiddleware raises Http404 or redirects to the fallback
        URL (SHOW_PUBLIC_IF_NO_TENANT_FOUND setting). This middleware
        adds a warning log entry before the exception propagates.
    """

    # ── Task 04: __init__ ─────────────────────────────────────────────

    def __init__(self, get_response):
        """
        Initialise the middleware.

        Stores the next callable in the WSGI chain and delegates
        to TenantMainMiddleware.__init__ for its own setup.

        Args:
            get_response: The next callable in the middleware chain.
                This is either the next middleware class or the
                Django view resolver (if this is the last middleware).
        """
        self.get_response = get_response
        super().__init__(get_response)
        logger.debug("LCCTenantMiddleware: initialised.")

    # ── Task 05: __call__ ─────────────────────────────────────────────

    def __call__(self, request):
        """
        Process the request through the tenant middleware chain.

        This method conforms to Django's new-style (callable) middleware
        interface. It delegates immediately to TenantMainMiddleware.__call__
        which internally:
            1. Calls self.process_request(request) — tenant resolution.
            2. Calls self.get_response(request) — downstream processing.
            3. Calls self.process_response(request, response) if defined.
            4. Returns the HttpResponse.

        Because TenantMainMiddleware extends MiddlewareMixin, the
        process_request/process_response hooks are invoked automatically
        inside __call__ via MiddlewareMixin's implementation.

        Args:
            request: The incoming Django HttpRequest object.

        Returns:
            HttpResponse: The response produced by the downstream handler.
        """
        return super().__call__(request)

    # ── Request Attribute Injection (Tasks 06-07) ─────────────────────

    def process_request(self, request):
        """
        Resolve the tenant from the request and activate its schema.

        Extends TenantMainMiddleware.process_request by:
            1. Delegating to the parent for Domain lookup and schema
               activation via connection.set_tenant().
            2. Injecting request.tenant and request.schema_name for
               convenient access in views and downstream middleware.
            3. Emitting structured log entries for observability.

        This method is called automatically by MiddlewareMixin.__call__
        before passing the request to get_response. It executes once
        per request, before any view or other middleware sees the request.

        Args:
            request: The incoming Django HttpRequest object.

        Raises:
            Http404: If no matching Domain is found and
                SHOW_PUBLIC_IF_NO_TENANT_FOUND is False.
        """
        # Parent resolves hostname → Domain → Tenant and activates schema.
        # After this call, django.db.connection.schema_name is set to the
        # tenant's schema name and connection.tenant holds the Tenant instance.
        super().process_request(request)

        # Inject convenience attributes for downstream code.
        # connection.tenant is set by django-tenants after resolution.
        from django.db import connection

        request.tenant = getattr(connection, "tenant", None)
        request.schema_name = getattr(connection, "schema_name", None)

        if request.tenant is not None:
            logger.debug(
                "LCCTenantMiddleware: tenant='%s' schema='%s' host='%s'",
                getattr(request.tenant, "name", "?"),
                request.schema_name,
                request.get_host(),
            )
        else:
            logger.warning(
                "LCCTenantMiddleware: no tenant resolved for host='%s'",
                request.get_host(),
            )
