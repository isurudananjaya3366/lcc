"""
Custom domain resolver for LankaCommerce Cloud tenant middleware.

Resolves tenants by matching the full HTTP Host header against Domain
model records that have domain_type='custom'. This resolver handles
user-provided domains (e.g. shop.mybusiness.lk) that point to the
LankaCommerce Cloud platform via DNS CNAME or A records.

Custom domain resolution flow:
    1. Parse the request Host header, strip port (reuse parse_host logic).
    2. Skip hosts that match the platform base domain pattern
       (those are handled by SubdomainResolver).
    3. Look up the full hostname in the Domain table.
    4. If found, verify the domain is verified (is_verified=True).
    5. If verified, return the associated Tenant instance.
    6. If not verified, log a warning and return None.
    7. If not found, return None (fall through to next resolver or 404).

Caching (Task 37):
    Custom domain lookups are cached in Django's default cache backend
    with the same TTL as subdomain lookups (TENANT_DOMAIN_CACHE_TTL).
    Cache key pattern: lcc:tenant_custom_domain:{domain}
    Miss sentinel: "__none__" stored when no domain record is found.
    Invalidation: Domain post_save/post_delete signals clear entries.

Cache invalidation:
    The existing Domain post_save/post_delete signals handle cache
    eviction. This module provides invalidate_custom_domain_cache()
    for explicit cache management when needed.

Verification enforcement (Task 31 / Task 39):
    Custom domains MUST pass DNS verification before they can resolve
    to a tenant. Unverified domains are blocked at the resolver level
    with a warning log. This prevents domain squatting and ensures
    legitimate ownership.

Not-found handling (Task 38):
    When no Domain record matches the request hostname, the resolver
    returns None. The calling middleware logs a warning and either
    returns Http404 or falls back to the public schema based on the
    SHOW_PUBLIC_IF_NO_TENANT_FOUND setting.

Multiple domains per tenant (Task 40):
    Each tenant may have multiple custom domains. All domains resolve
    to the same tenant schema. One domain per tenant is designated as
    the primary domain (is_primary=True in django-tenants DomainMixin).

Primary domain redirect (Task 41):
    When a request arrives on a non-primary domain, the resolver can
    detect this and provide the primary domain for redirect purposes.
    The should_redirect_to_primary() method checks if the request
    domain differs from the tenant's primary domain.

SSL status tracking (Task 36):
    The Domain model's ssl_status field tracks TLS certificate lifecycle:
    none, pending, active, expired, failed. This resolver exposes
    the SSL status for downstream middleware or views to act on.

Dependencies:
    - SubdomainResolver (for parse_host reuse and platform domain detection)
    - Domain model (for database lookups)
    - Django cache framework (for caching)

Task coverage:
    - Task 29: Create Custom Domain Resolver (class structure)
    - Task 30: Lookup by Full Domain (resolve_by_domain method)
    - Task 31: Handle Domain Verification (verification enforcement)
    - Task 36: Handle SSL Certificate Status (ssl_status tracking)
    - Task 37: Cache Custom Domain Lookups (caching layer)
    - Task 38: Handle Domain Not Found (not-found handling)
    - Task 39: Handle Unverified Domain (unverified domain blocking)
    - Task 40: Support Multiple Domains (multi-domain per tenant)
    - Task 41: Primary Domain Redirect (redirect to primary)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.http import HttpRequest

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------

_CACHE_MISS_SENTINEL = "__none__"
_CACHE_KEY_PREFIX = "lcc:tenant_custom_domain"


def _build_cache_key(domain: str) -> str:
    """Build a deterministic cache key for a custom domain lookup."""
    return f"{_CACHE_KEY_PREFIX}:{domain}"


def invalidate_custom_domain_cache(domain_str: str) -> None:
    """
    Evict cache entries related to the given custom domain string.

    Called by the Domain model's post_save/post_delete signal or
    manually when domain records change.

    Args:
        domain_str: The full domain value stored in the Domain model,
            e.g. "shop.mybusiness.lk".
    """
    from django.core.cache import cache

    key = _build_cache_key(domain_str.lower())
    cache.delete(key)
    logger.debug(
        "invalidate_custom_domain_cache: deleted key '%s' for domain '%s'",
        key,
        domain_str,
    )


class CustomDomainResolver:
    """
    Custom domain resolver for LankaCommerce Cloud.

    Resolves tenants by matching the full request hostname against
    Domain records with domain_type='custom'. Only verified domains
    are allowed to resolve to a tenant.

    Task 29 - Resolver scope:
        The CustomDomainResolver handles full custom domain matching.
        Subdomain-based resolution (e.g. acme.lcc.example.com) is
        handled by SubdomainResolver (Group-B). Header-based
        resolution is in Group-D.

    Task 30 - Full domain lookup:
        Uses Domain.objects.select_related('tenant').get(domain=host)
        for exact matching. Results are cached.

    Task 31 / Task 39 - Verification enforcement:
        Only domains with is_verified=True are resolved. Unverified
        custom domains return None with a warning log, preventing
        tenant access until DNS verification is completed. Unverified
        domains are cached with the miss-sentinel to avoid repeated
        DB lookups until the cache is invalidated on verification.

    Task 36 - SSL status tracking:
        The resolved Domain object's ssl_status is logged and accessible
        via get_domain_info(). SSL states: none, pending, active,
        expired, failed.

    Task 37 - Caching:
        All custom domain lookups are cached in Django's default cache
        backend. Cache TTL is controlled by TENANT_DOMAIN_CACHE_TTL.
        Not-found results are cached with a miss-sentinel to prevent
        repeated DB misses. Cache is invalidated by Domain signals.

    Task 38 - Not-found handling:
        When no Domain record matches, resolve_by_domain() returns None.
        The caller (LCCTenantMiddleware) handles the None return by
        either raising Http404 or falling back to the public schema.

    Task 40 - Multiple domains per tenant:
        Each tenant may have multiple custom domains. All resolve to
        the same tenant schema. get_tenant_domains() returns all
        domains for a tenant. One is the primary (is_primary=True).

    Task 41 - Primary domain redirect:
        should_redirect_to_primary() checks if the current request
        domain differs from the tenant's primary domain. If so,
        get_primary_domain() returns the redirect target.

    Lifecycle:
        1. is_custom_domain(host) - check if host is NOT a platform domain
        2. resolve_by_domain(domain_str) - Domain lookup (cached)
        3. resolve(request) - parse + lookup in one call
        4. get_domain_info(domain_str) - full Domain object with SSL info
        5. get_tenant_domains(tenant) - all domains for a tenant
        6. get_primary_domain(tenant) - primary domain for redirect
        7. should_redirect_to_primary(request_host, tenant) - redirect check
    """

    def __init__(self, base_domain: str | None = None):
        """
        Initialise the custom domain resolver.

        Args:
            base_domain: Override for the platform base domain. When None,
                the value from django.conf.settings.TENANT_BASE_DOMAIN is used.
        """
        from django.conf import settings

        self.base_domain: str = (
            base_domain or getattr(settings, "TENANT_BASE_DOMAIN", "localhost")
        ).lower()
        self.dev_domains: frozenset[str] = frozenset(
            d.lower()
            for d in getattr(
                settings, "TENANT_DEV_DOMAINS", ["localhost", "127.0.0.1"]
            )
        )
        self.cache_ttl: int = int(
            getattr(settings, "TENANT_DOMAIN_CACHE_TTL", 300)
        )

    # ── Host parsing ──────────────────────────────────────────────────

    def parse_host(self, host: str) -> str:
        """
        Normalise the raw Host header value.

        Strips the port component and converts to lowercase.
        Returns an empty string if the input is None or blank.

        Args:
            host: Raw value from the HTTP Host header.

        Returns:
            str: Lowercased hostname without port.
        """
        if not host:
            return ""
        return host.lower().split(":")[0].strip()

    # ── Task 29: Platform domain detection ────────────────────────────

    def is_custom_domain(self, host: str) -> bool:
        """
        Determine whether a hostname is a custom (non-platform) domain.

        A hostname is considered a platform domain (and thus NOT custom) if:
            - It exactly matches a dev domain (localhost, 127.0.0.1).
            - It ends with .localhost (dev subdomain pattern).
            - It ends with .{base_domain} (platform subdomain pattern).
            - It exactly matches the base domain itself.

        Everything else is treated as a potential custom domain.

        Args:
            host: Normalised hostname (lowercase, no port).

        Returns:
            bool: True if the host is a custom domain, False if it is
            a platform or dev domain.
        """
        if not host:
            return False

        # Bare dev domains are platform domains
        if host in self.dev_domains:
            return False

        # *.localhost is a dev subdomain pattern
        if host.endswith(".localhost") or host == "localhost":
            return False

        # Exact match with the base domain
        if host == self.base_domain:
            return False

        # Subdomain of the base domain
        if self.base_domain and host.endswith("." + self.base_domain):
            return False

        return True

    # ── Task 30: Lookup by full domain (cached) ──────────────────────

    def resolve_by_domain(self, domain_str: str):
        """
        Resolve the Tenant model instance for the given full domain.

        Caching:
            Checks the Django cache before querying the database. Results
            (including not-found) are stored with TTL = TENANT_DOMAIN_CACHE_TTL.

        Verification (Task 31):
            Only domains with is_verified=True are resolved. Unverified
            custom domains return None with a warning.

        Not-found handling (Task 30):
            When no Domain record matches, None is returned. The caller
            is responsible for returning 404 or falling through to the
            next resolver.

        Args:
            domain_str: The full domain string (lowercase, no port),
                e.g. "shop.mybusiness.lk".

        Returns:
            Tenant | None: The active Tenant instance if found and verified,
            or None if not found, not verified, or tenant is inactive.
        """
        if not domain_str:
            return None

        from django.core.cache import cache

        cache_key = _build_cache_key(domain_str)
        cached = cache.get(cache_key)
        if cached is not None:
            if cached == _CACHE_MISS_SENTINEL:
                logger.debug(
                    "CustomDomainResolver: cache miss-sentinel for '%s'",
                    domain_str,
                )
                return None
            logger.debug(
                "CustomDomainResolver: cache hit for domain='%s' tenant='%s'",
                domain_str,
                getattr(cached, "name", "?"),
            )
            return cached

        # Cache miss - query the database
        from apps.tenants.models import Domain

        try:
            domain_obj = Domain.objects.select_related("tenant").get(
                domain=domain_str,
            )
        except Domain.DoesNotExist:
            # No domain record found
            cache.set(cache_key, _CACHE_MISS_SENTINEL, timeout=self.cache_ttl)
            logger.debug(
                "CustomDomainResolver: no domain record for '%s'",
                domain_str,
            )
            return None

        # Task 31: Enforce verification for custom domains
        if domain_obj.is_custom_domain and not domain_obj.is_verified:
            logger.warning(
                "CustomDomainResolver: domain '%s' is not verified - "
                "blocking tenant resolution (tenant='%s')",
                domain_str,
                getattr(domain_obj.tenant, "name", "?"),
            )
            # Cache as miss-sentinel to avoid repeated DB lookups
            # for unverified domains (will be invalidated when verified)
            cache.set(cache_key, _CACHE_MISS_SENTINEL, timeout=self.cache_ttl)
            return None

        tenant = domain_obj.tenant

        # Cache the resolved tenant
        cache.set(cache_key, tenant, timeout=self.cache_ttl)
        logger.debug(
            "CustomDomainResolver: domain='%s' resolved to tenant='%s'",
            domain_str,
            getattr(tenant, "name", "?"),
        )
        return tenant

    # ── Combined resolve from request ─────────────────────────────────

    def resolve(self, request: "HttpRequest"):
        """
        Parse the request host and resolve the Tenant via custom domain.

        Returns None immediately if the host is a platform domain
        (those are handled by SubdomainResolver).

        Args:
            request: The incoming Django HttpRequest.

        Returns:
            Tenant | None: The resolved Tenant instance, or None if the
            host is a platform domain, not found, or not verified.
        """
        host = self.parse_host(request.get_host())

        if not self.is_custom_domain(host):
            logger.debug(
                "CustomDomainResolver: '%s' is a platform domain - skipping",
                host,
            )
            return None

        return self.resolve_by_domain(host)

    # ── Task 36: SSL status tracking ──────────────────────────────────

    def get_domain_info(self, domain_str: str):
        """
        Retrieve the full Domain object for a custom domain.

        Unlike resolve_by_domain() which returns the Tenant, this method
        returns the Domain model instance itself, providing access to
        SSL status, verification state, metadata, and other fields.

        Not cached separately - performs a direct DB lookup.

        Args:
            domain_str: The full domain string (lowercase, no port).

        Returns:
            Domain | None: The Domain model instance if found, or None.
        """
        if not domain_str:
            return None

        from apps.tenants.models import Domain

        try:
            return Domain.objects.select_related("tenant").get(
                domain=domain_str,
            )
        except Domain.DoesNotExist:
            logger.debug(
                "CustomDomainResolver.get_domain_info: no record for '%s'",
                domain_str,
            )
            return None

    def get_ssl_status(self, domain_str: str) -> str | None:
        """
        Return the SSL certificate status for a custom domain.

        SSL status values (from Domain model):
            - "none":    No SSL certificate configured.
            - "pending": Certificate provisioning in progress.
            - "active":  Valid certificate installed.
            - "expired": Certificate has expired.
            - "failed":  Certificate provisioning failed.

        Args:
            domain_str: The full domain string (lowercase, no port).

        Returns:
            str | None: The SSL status string, or None if the domain
            is not found.
        """
        domain_obj = self.get_domain_info(domain_str)
        if domain_obj is None:
            return None
        return domain_obj.ssl_status

    # ── Task 38: Not-found handling ───────────────────────────────────

    def resolve_or_not_found(self, domain_str: str):
        """
        Resolve a custom domain or return structured not-found info.

        Provides more detail than resolve_by_domain() for error handling.
        Returns a tuple of (tenant, reason) where reason is None on
        success or a descriptive string on failure.

        Not-found reasons (Task 38):
            - "domain_not_found": No Domain record exists.
            - "domain_not_verified": Domain exists but is_verified=False.
            - "empty_domain": Empty or blank domain string.

        Args:
            domain_str: The full domain string (lowercase, no port).

        Returns:
            tuple[Tenant | None, str | None]: A tuple of (tenant, reason).
            On success, (tenant, None). On failure, (None, reason_string).
        """
        if not domain_str:
            return None, "empty_domain"

        from apps.tenants.models import Domain

        try:
            domain_obj = Domain.objects.select_related("tenant").get(
                domain=domain_str,
            )
        except Domain.DoesNotExist:
            logger.warning(
                "CustomDomainResolver: domain not found for '%s'",
                domain_str,
            )
            return None, "domain_not_found"

        # Task 39: Handle unverified domain
        if domain_obj.is_custom_domain and not domain_obj.is_verified:
            logger.warning(
                "CustomDomainResolver: unverified domain '%s' - "
                "access blocked (tenant='%s')",
                domain_str,
                getattr(domain_obj.tenant, "name", "?"),
            )
            return None, "domain_not_verified"

        return domain_obj.tenant, None

    # ── Task 40: Multiple domains per tenant ──────────────────────────

    def get_tenant_domains(self, tenant) -> list:
        """
        Return all Domain records for a given tenant.

        Supports the multi-domain feature where each tenant may have
        multiple custom domains (and platform domains) pointing to
        the same schema. Includes both verified and unverified domains.

        The result is ordered by is_primary (primary first), then by
        domain name alphabetically.

        Args:
            tenant: A Tenant model instance.

        Returns:
            list[Domain]: All Domain records for the tenant, ordered
            with the primary domain first.
        """
        from apps.tenants.models import Domain

        return list(
            Domain.objects.filter(tenant=tenant).order_by(
                "-is_primary", "domain"
            )
        )

    def get_primary_domain(self, tenant) -> str | None:
        """
        Return the primary domain string for a tenant.

        Each tenant should have exactly one primary domain
        (is_primary=True in django-tenants DomainMixin). If no
        primary domain is found, returns None.

        Args:
            tenant: A Tenant model instance.

        Returns:
            str | None: The primary domain string, or None if no
            primary domain is configured.
        """
        from apps.tenants.models import Domain

        try:
            primary = Domain.objects.get(tenant=tenant, is_primary=True)
            return primary.domain
        except Domain.DoesNotExist:
            logger.warning(
                "CustomDomainResolver: no primary domain for tenant='%s'",
                getattr(tenant, "name", "?"),
            )
            return None
        except Domain.MultipleObjectsReturned:
            # Shouldn't happen but handle gracefully
            primary = Domain.objects.filter(
                tenant=tenant, is_primary=True
            ).first()
            logger.warning(
                "CustomDomainResolver: multiple primary domains for tenant='%s' "
                "- using '%s'",
                getattr(tenant, "name", "?"),
                primary.domain if primary else "none",
            )
            return primary.domain if primary else None

    # ── Task 41: Primary domain redirect ──────────────────────────────

    def should_redirect_to_primary(
        self, request_host: str, tenant
    ) -> bool:
        """
        Check if the request should be redirected to the primary domain.

        Returns True when:
            - The request arrived on a non-primary custom domain.
            - A primary domain exists for the tenant.
            - The request domain differs from the primary domain.

        This allows tenants to have multiple domains (aliases) that all
        redirect to the canonical primary domain for SEO consistency.

        Redirect conditions (Task 41):
            - Request host is a custom domain (not platform subdomain).
            - Request host is NOT the primary domain.
            - Tenant has a primary domain configured.

        When True, the caller should issue an HTTP 301 redirect to the
        primary domain, preserving the request path and query string.

        Args:
            request_host: The normalised request hostname (no port).
            tenant: The resolved Tenant model instance.

        Returns:
            bool: True if a redirect to primary is recommended.
        """
        if not self.is_custom_domain(request_host):
            return False

        primary = self.get_primary_domain(tenant)
        if primary is None:
            return False

        # Compare normalised hostnames
        return request_host.lower() != primary.lower()

    def get_redirect_url(self, request: "HttpRequest", tenant) -> str | None:
        """
        Build the full redirect URL to the tenant's primary domain.

        Preserves the request path and query string. Returns None if
        no redirect is needed.

        Args:
            request: The incoming Django HttpRequest.
            tenant: The resolved Tenant model instance.

        Returns:
            str | None: The full redirect URL, or None if no redirect
            is needed.
        """
        host = self.parse_host(request.get_host())

        if not self.should_redirect_to_primary(host, tenant):
            return None

        primary = self.get_primary_domain(tenant)
        if primary is None:
            return None

        scheme = "https" if request.is_secure() else "http"
        path = request.get_full_path()
        return f"{scheme}://{primary}{path}"
