"""
Tenants middleware package.

Contains:
    LCCTenantMiddleware: Custom tenant middleware extending
    django-tenants TenantMainMiddleware. Resolves the active
    tenant from the request hostname, activates the PostgreSQL
    schema, and injects request.tenant / request.schema_name.

    Must be the FIRST entry in Django's MIDDLEWARE list.

    SubdomainResolver: Extracts the tenant subdomain from the
    request Host header and resolves the matching Tenant via
    Domain model lookup. Supports production subdomains,
    www stripping, and localhost development patterns.

    CustomDomainResolver: Resolves tenants by matching the full
    HTTP Host header against Domain records with domain_type='custom'.
    Only verified domains are allowed to resolve to a tenant (Task 29-31).

    HeaderResolver: Resolves tenants by reading tenant identifiers
    from HTTP request headers (X-Tenant-ID or X-Tenant-Slug).
    Restricted to API paths (/api/, /mobile/, /webhook/). Tasks 43-54.
    Includes API authentication integration (Task 49), path restriction
    enforcement (Task 50), configurable allowed paths (Task 51), cached
    lookups (Task 52), audit logging (Task 53), and comprehensive
    documentation (Task 54).

    Error handling (Tasks 55-68):
    tenant_not_found: Returns HTTP 404 for missing tenants (Tasks 55-57).
    tenant_suspended: Returns HTTP 403 for suspended tenants (Tasks 60-62).
    tenant_expired: Returns HTTP 403 for expired subscriptions (Tasks 63-65).
    is_public_path: Checks if a path uses the public schema (Tasks 58-59).
    is_tenant_suspended: Checks if a tenant is suspended (Task 60).
    is_tenant_expired: Checks if a tenant subscription is expired (Task 63).
    is_within_grace_period: Checks grace period for expired tenants (Task 63).
    get_tenant_status: Returns normalised tenant status string.
    log_resolution_error: Logs resolution errors with structured fields (Task 66).
    get_error_metrics: Returns error metrics counters (Task 67).
    reset_error_metrics: Resets error metrics counters (Task 67).

    SUBDOMAIN_PATTERN: Compiled regex for validating subdomain strings
    (Task 26). Enforces RFC 1035 label rules: lowercase alphanumerics
    and hyphens, 1-63 characters, no leading/trailing hyphens.

    is_valid_subdomain: Helper that applies SUBDOMAIN_PATTERN to a
    candidate string and returns True/False (Task 26).

    invalidate_custom_domain_cache: Evicts cache entries for custom
    domain lookups (Task 29).

    invalidate_header_cache: Evicts cache entries for header-based
    tenant lookups (Task 43).
"""

from apps.tenants.middleware.domain_resolver import (
    CustomDomainResolver,
    invalidate_custom_domain_cache,
)
from apps.tenants.middleware.error_handler import (
    get_error_metrics,
    get_tenant_status,
    is_public_path,
    is_tenant_expired,
    is_tenant_suspended,
    is_within_grace_period,
    log_resolution_error,
    reset_error_metrics,
    tenant_expired,
    tenant_not_found,
    tenant_suspended,
)
from apps.tenants.middleware.header_resolver import (
    HeaderResolver,
    invalidate_header_cache,
)
from apps.tenants.middleware.subdomain_resolver import (
    SUBDOMAIN_PATTERN,
    SubdomainResolver,
    is_valid_subdomain,
)
from apps.tenants.middleware.tenant_middleware import LCCTenantMiddleware

__all__ = [
    "LCCTenantMiddleware",
    "SubdomainResolver",
    "CustomDomainResolver",
    "HeaderResolver",
    "SUBDOMAIN_PATTERN",
    "is_valid_subdomain",
    "invalidate_custom_domain_cache",
    "invalidate_header_cache",
    "tenant_not_found",
    "tenant_suspended",
    "tenant_expired",
    "is_public_path",
    "is_tenant_suspended",
    "is_tenant_expired",
    "is_within_grace_period",
    "get_tenant_status",
    "log_resolution_error",
    "get_error_metrics",
    "reset_error_metrics",
]
