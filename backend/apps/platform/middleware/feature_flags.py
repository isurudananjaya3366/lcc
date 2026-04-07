"""
Feature flags middleware.

Resolves feature flag states for the current tenant and attaches
them to the request object. This makes feature flag checks available
throughout the request lifecycle without additional database queries.

Middleware position:
    This middleware should be placed after AuthenticationMiddleware
    and after any tenant resolution middleware (e.g.,
    TenantMainMiddleware from django-tenants). It requires the tenant
    to be resolved on the request before it can resolve flags.

Request attributes set:
    request.feature_flags: dict mapping flag keys to boolean states.
        Example: {"webstore.live_chat": True, "billing.multi_currency": False}

Usage in views:
    def my_view(request):
        if request.feature_flags.get("webstore.live_chat"):
            # Feature is enabled for the current tenant
            ...

Usage in templates:
    Feature flags can be passed to template context and used to
    conditionally render UI elements based on tenant capabilities.

Registration:
    Add to MIDDLEWARE in settings after AuthenticationMiddleware:
    "apps.platform.middleware.feature_flags.FeatureFlagMiddleware"

    This middleware will be registered during Phase 3 when tenant
    middleware is activated. Until then, request.feature_flags will
    be an empty dict since no tenant is resolved on the request.
"""

import logging

from apps.platform.utils.features import get_tenant_flags

logger = logging.getLogger(__name__)


class FeatureFlagMiddleware:
    """
    Middleware that resolves feature flags per tenant per request.

    Attaches a dictionary of resolved flag states to the request
    object as request.feature_flags. If no tenant is available on
    the request, an empty dictionary is attached.

    The resolved flags use the cached resolution from
    get_tenant_flags(), meaning no additional database queries
    are made when the cache is warm.
    """

    def __init__(self, get_response):
        """
        Initialize middleware with the next handler in the chain.

        Args:
            get_response: The next middleware or view in the chain.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Process the request and attach feature flags.

        Resolves the tenant from the request object (set by tenant
        middleware) and uses get_tenant_flags() to build the cached
        flag state dictionary. Attaches the result to
        request.feature_flags.

        If no tenant is available (e.g., public schema request or
        tenant middleware not yet active), an empty dictionary is
        attached to avoid AttributeError in downstream code.

        Args:
            request: The HTTP request object.

        Returns:
            HttpResponse: The response from the next handler.
        """
        tenant = getattr(request, "tenant", None)

        if tenant is not None:
            request.feature_flags = get_tenant_flags(tenant)
            logger.debug(
                "Resolved %d feature flags for tenant '%s'.",
                len(request.feature_flags),
                tenant.name,
            )
        else:
            request.feature_flags = {}

        return self.get_response(request)
