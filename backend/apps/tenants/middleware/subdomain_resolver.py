"""
Subdomain resolver for LankaCommerce Cloud tenant middleware.

Parses the HTTP request's Host header to extract the subdomain
component and resolves the corresponding Tenant via Domain model lookup.

Supported host formats (Task 17):
    {subdomain}.{base_domain}         - acme.lcc.example.com
    {subdomain}.{base_domain}:{port}  - acme.lcc.example.com:8000
    {subdomain}.localhost             - acme.localhost       (Task 20 dev)
    {subdomain}.localhost:{port}      - acme.localhost:8000  (Task 20 dev)
    www.{subdomain}.{base_domain}     - www.acme.lcc.example.com (Task 19 www)

Base domain (Task 16):
    Controlled by the TENANT_BASE_DOMAIN Django setting (default: "localhost").
    Override per environment:
        local.py      - TENANT_BASE_DOMAIN = "localhost"
        staging.py    - TENANT_BASE_DOMAIN = "staging.lcc.io"
        production.py - TENANT_BASE_DOMAIN = "lcc.example.com"

Development domains (Task 21):
    Hosts in TENANT_DEV_DOMAINS (default: localhost, 127.0.0.1) use
    simplified .localhost subdomain detection instead of requiring a
    full base-domain match.

Port handling (Task 22):
    The port component (e.g. :8000) is stripped in parse_host()
    before any matching occurs. Stripping is always applied regardless
    of whether the request comes from a development or production host.

Caching (Task 23-24):
    Domain model lookups are cached in Django's default cache backend
    (typically Redis). Cache TTL is controlled by TENANT_DOMAIN_CACHE_TTL
    (default: 300 seconds). Sentinel value "__none__" is stored when
    no tenant is found, preventing repeated DB misses.

Cache invalidation (Task 25):
    The Domain post_save and post_delete signals call
    invalidate_subdomain_cache() to evict stale entries immediately
    when a Domain record is created, updated, or deleted.

Not-found handling (Task 18):
    When no Domain record matches the extracted subdomain, resolve_tenant()
    returns None. The caller (LCCTenantMiddleware or view) is responsible
    for returning Http404 or falling back to the public schema.

Reserved subdomains (Task 27):
    Subdomains listed in TENANT_RESERVED_SUBDOMAINS are never resolved
    to a tenant regardless of Domain table content. The is_reserved()
    method performs this check. On a positive match, resolve_tenant()
    returns None immediately without hitting the cache or the database.
    Reserved subdomains include: www, api, admin, app, static, media,
    mail, smtp, cdn, docs, help, support, status.

Subdomain validation (Task 26):
    Before being returned from get_subdomain(), extracted subdomain
    strings are validated against SUBDOMAIN_PATTERN (see module-level
    constant). Syntactically invalid subdomains (e.g. containing dots,
    underscores, or leading/trailing hyphens) are rejected and None
    is returned, preventing any DB lookup or cache write.
"""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.http import HttpRequest

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Task 26: Subdomain Regex Pattern
# ---------------------------------------------------------------------------
# Valid subdomain rules:
#   - Starts and ends with an alphanumeric character (a-z, 0-9).
#   - May contain hyphens (-) in the middle, but not as the first or last char.
#   - Length: 1 to 63 characters (RFC 1035 label limit).
#   - Only lowercase ASCII letters, digits, and hyphens are permitted.
#   - No underscores, dots, or other special characters.
#
# Examples of valid subdomains:
#   acme, my-store, store1, a, abc123, my-tenant-01
#
# Examples of invalid subdomains:
#   -acme   (leading hyphen)
#   acme-   (trailing hyphen)
#   my.sub  (contains dot - nested subdomain, not allowed)
#   ACMe    (uppercase letters, not allowed - use .lower() before matching)
#   _acme   (underscore, not allowed)
#   a--b    (consecutive hyphens - discouraged but technically RFC-legal;
#            this pattern allows them for flexibility)
#   ""      (empty string, not allowed)
SUBDOMAIN_PATTERN: re.Pattern[str] = re.compile(
    r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$"
)
"""
Compiled regex for validating tenant subdomain strings.

Character set:
    [a-z0-9-]  - lowercase letters, digits, and hyphens only.

Anchors:
    ^  - must match from the start of the string.
    $  - must match to the end of the string.

Structure:
    [a-z0-9]                  - first character must be alphanumeric.
    (?:[a-z0-9-]{0,61}[a-z0-9])?  - optional middle+end section:
        [a-z0-9-]{0,61}       - up to 61 chars of letters/digits/hyphens,
        [a-z0-9]              - ending with an alphanumeric character.
    Total max length = 1 + 61 + 1 = 63 characters (RFC 1035 label limit).

Single-character subdomains (e.g. "a") are valid - the optional group
may be absent when the string length is exactly 1.
"""


def is_valid_subdomain(subdomain: str) -> bool:
    """
    Return True if subdomain matches the SUBDOMAIN_PATTERN constraints.

    Args:
        subdomain: The subdomain string to validate (should already be lowercase).

    Returns:
        bool: True if the subdomain is syntactically valid, False otherwise.
    """
    if not subdomain:
        return False
    return bool(SUBDOMAIN_PATTERN.match(subdomain))


# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------

# Sentinel stored in cache to represent "no tenant found" (avoids DB miss loops).
_CACHE_MISS_SENTINEL = "__none__"

# Cache key prefix - all subdomain resolver cache keys share this prefix.
_CACHE_KEY_PREFIX = "lcc:tenant_subdomain"


def _build_cache_key(base_domain: str, subdomain: str) -> str:
    """Build a deterministic cache key for a (base_domain, subdomain) pair."""
    return f"{_CACHE_KEY_PREFIX}:{base_domain}:{subdomain}"


def invalidate_subdomain_cache(domain_str: str) -> None:
    """
    Evict cache entries related to the given full domain string.

    Called by the Domain model's post_save/post_delete signal (Task 25).
    Parses domain_str to extract the subdomain and deletes the
    corresponding cache key.

    Args:
        domain_str: The full domain value stored in the Domain model,
            e.g. "acme.lcc.example.com" or "acme.localhost".
    """
    from django.core.cache import cache
    from django.conf import settings

    base_domain = getattr(settings, "TENANT_BASE_DOMAIN", "localhost")

    # Use a minimal resolver to extract subdomain without full init
    resolver = SubdomainResolver(base_domain=base_domain)
    subdomain = resolver.get_subdomain(domain_str)
    if subdomain:
        key = _build_cache_key(base_domain, subdomain)
        cache.delete(key)
        logger.debug(
            "invalidate_subdomain_cache: deleted key '%s' for domain '%s'",
            key,
            domain_str,
        )
    else:
        logger.debug(
            "invalidate_subdomain_cache: could not extract subdomain from '%s'",
            domain_str,
        )


class SubdomainResolver:
    """
    Subdomain-based tenant resolver for LankaCommerce Cloud.

    Extracts the tenant subdomain from an HTTP Host header and resolves
    the matching Tenant instance via the Domain model, with Redis caching.

    Lifecycle:
        1. get_subdomain(host) - parse host, return subdomain str
        2. resolve_tenant(subdomain) - Domain lookup (cached), return Tenant
        3. resolve(request) - parse + lookup in one call (combined)

    Task 15 - Resolver scope:
        The SubdomainResolver handles subdomain-to-tenant mapping only.
        Custom domain resolution (e.g. tenant.io) is handled separately
        in Group-C. Header-based resolution is in Group-D.

    Task 16 - Base domain dependency:
        All subdomain parsing is relative to TENANT_BASE_DOMAIN. The
        resolver reads this setting at instantiation time.

    Task 19 - WWW prefix:
        A "www." prefix is stripped before subdomain extraction.
        "www.acme.lcc.example.com" becomes subdomain "acme".
        A bare "www" subdomain is treated as reserved (no tenant).

    Task 20 - Localhost dev support:
        When the host ends with ".localhost", the subdomain component
        before ".localhost" is used directly, without requiring
        TENANT_BASE_DOMAIN to match. Supports local development.

    Task 21 - Dev domain config:
        The set of dev-mode bare hosts is read from TENANT_DEV_DOMAINS setting.

    Task 22 - Port numbers:
        Port is always stripped in parse_host() before any matching.

    Task 23-24 - Caching:
        Resolved (and not-found) lookups are cached via Django's cache
        framework. TTL from TENANT_DOMAIN_CACHE_TTL setting.
    """

    def __init__(self, base_domain: str | None = None):
        """
        Initialise the resolver.

        Args:
            base_domain: Override for the base domain. When None the
                value from django.conf.settings.TENANT_BASE_DOMAIN is used.
        """
        from django.conf import settings

        self.base_domain: str = (
            base_domain or getattr(settings, "TENANT_BASE_DOMAIN", "localhost")
        ).lower()
        self.reserved: frozenset[str] = frozenset(
            s.lower()
            for s in getattr(
                settings,
                "TENANT_RESERVED_SUBDOMAINS",
                ["www", "api", "admin", "static", "media"],
            )
        )
        # Task 21: dev domains from settings
        self.dev_domains: frozenset[str] = frozenset(
            d.lower()
            for d in getattr(settings, "TENANT_DEV_DOMAINS", ["localhost", "127.0.0.1"])
        )
        # Task 24: cache TTL from settings
        self.cache_ttl: int = int(getattr(settings, "TENANT_DOMAIN_CACHE_TTL", 300))

    # ── Task 17 / Task 22: Parse request host ─────────────────────────

    def parse_host(self, host: str) -> str:
        """
        Normalise the raw Host header value.

        Strips the port component (Task 22) and converts to lowercase.
        Returns an empty string if the input is None or blank.

        Args:
            host: Raw value from the HTTP Host header, e.g.
                "acme.lcc.example.com:8000" or "acme.localhost".

        Returns:
            str: Lowercased hostname without port.
        """
        if not host:
            return ""
        return host.lower().split(":")[0].strip()

    def get_subdomain(self, host: str) -> str | None:
        """
        Extract the tenant subdomain from a hostname.

        Resolution order:
            1. Bare dev host (Task 21) - returns None (no subdomain).
            2. "*.localhost" suffix - extracts prefix as subdomain (Task 20).
            3. "www." prefix - strips www, then re-applies standard parsing (Task 19).
            4. "*.{base_domain}" suffix - extracts the subdomain component.
            5. SUBDOMAIN_PATTERN validation (Task 26) - rejects syntactically
               invalid subdomains (e.g. leading/trailing hyphens, underscores,
               uppercase letters, or dot-separated nested parts).

        Only single-level subdomains are accepted (no nested dots).

        Args:
            host: Raw hostname (port will be stripped internally via parse_host).

        Returns:
            str | None: The subdomain string (validated), or None if none
            can be extracted or the extracted value fails SUBDOMAIN_PATTERN.
        """
        host = self.parse_host(host)

        if not host:
            return None

        # Task 21: bare dev hosts - no tenant subdomain
        if host in self.dev_domains:
            return None

        # Task 20: *.localhost dev support
        if host.endswith(".localhost"):
            subdomain = host[: -len(".localhost")]
            if subdomain and is_valid_subdomain(subdomain):
                return subdomain
            return None

        # Task 19: strip leading www. before further parsing
        if host.startswith("www."):
            host = host[4:]

        # Standard: {subdomain}.{base_domain}
        if self.base_domain and host.endswith("." + self.base_domain):
            subdomain = host[: -(len(self.base_domain) + 1)]
            # Reject nested subdomains (contains a dot) and validate pattern
            # (Task 26): SUBDOMAIN_PATTERN ensures alphanumeric start/end,
            # hyphens only in the middle, max 63 chars.
            if subdomain and "." not in subdomain and is_valid_subdomain(subdomain):
                return subdomain

        return None

    def get_subdomain_from_request(self, request: "HttpRequest") -> str | None:
        """
        Convenience wrapper: extract subdomain from a Django request.

        Args:
            request: The incoming Django HttpRequest.

        Returns:
            str | None: The tenant subdomain string, or None.
        """
        host = request.get_host()
        return self.get_subdomain(host)

    # ── Task 18 + Task 23: Lookup tenant by subdomain (cached) ────────

    def is_reserved(self, subdomain: str) -> bool:
        """
        Return True if the subdomain is in the reserved list (Task 27).

        Reserved subdomains are defined in TENANT_RESERVED_SUBDOMAINS (settings)
        and are checked case-insensitively. When a subdomain is reserved,
        resolve_tenant() returns None immediately - no cache read, no DB query.

        Reserved subdomains and their intended purpose:
            www     - main website (maps to public schema, not a tenant)
            api     - global API endpoint
            admin   - platform administration panel
            app     - main SaaS application entry point
            static  - static asset delivery
            media   - uploaded media files
            mail    - mail server (MX / webmail)
            smtp    - SMTP relay
            cdn     - content delivery network
            docs    - developer documentation
            help    - help centre
            support - customer support portal
            status  - system status page

        Behavior on match:
            - resolve_tenant() logs a debug message and returns None.
            - HTTP layer (LCCTenantMiddleware / view) receives None and is
              responsible for returning 404 or routing to the public schema.

        Args:
            subdomain: The subdomain string to check (case-insensitive).

        Returns:
            bool: True if reserved, False otherwise.
        """
        return subdomain.lower() in self.reserved

    def resolve_tenant(self, subdomain: str):
        """
        Resolve the Tenant model instance for the given subdomain.

        Caching (Task 23-24):
            Checks the Django cache before querying the database. Results
            (including not-found) are stored with TTL = TENANT_DOMAIN_CACHE_TTL.

        Database lookup (Task 18):
            Queries the Domain table for matching domain strings, trying
            both the production pattern ({subdomain}.{base_domain}) and
            the localhost dev pattern ({subdomain}.localhost).

        Args:
            subdomain: The subdomain component extracted from the Host header.

        Returns:
            Tenant | None: The active Tenant instance if found, or None
            if the subdomain is reserved, blank, or not in the Domain table.
        """
        if not subdomain or self.is_reserved(subdomain):
            if subdomain:
                logger.debug(
                    "SubdomainResolver: '%s' is reserved - no tenant lookup", subdomain
                )
            return None

        # Task 23: check cache first
        from django.core.cache import cache

        cache_key = _build_cache_key(self.base_domain, subdomain)
        cached = cache.get(cache_key)
        if cached is not None:
            if cached == _CACHE_MISS_SENTINEL:
                logger.debug(
                    "SubdomainResolver: cache miss-sentinel for '%s'", subdomain
                )
                return None
            logger.debug(
                "SubdomainResolver: cache hit for subdomain='%s' tenant='%s'",
                subdomain,
                getattr(cached, "name", "?"),
            )
            return cached

        # Cache miss - query the database
        from apps.tenants.models import Domain

        candidates: list[str] = []
        if self.base_domain and self.base_domain != "localhost":
            candidates.append(f"{subdomain}.{self.base_domain}")
        candidates.append(f"{subdomain}.localhost")

        tenant = None
        for domain_str in candidates:
            try:
                domain = Domain.objects.select_related("tenant").get(domain=domain_str)
                tenant = domain.tenant
                logger.debug(
                    "SubdomainResolver: subdomain='%s' resolved to tenant='%s' via domain='%s'",
                    subdomain,
                    getattr(tenant, "name", "?"),
                    domain_str,
                )
                break
            except Domain.DoesNotExist:
                continue

        # Task 23-24: cache the result (use sentinel for not-found)
        cache.set(
            cache_key,
            tenant if tenant is not None else _CACHE_MISS_SENTINEL,
            timeout=self.cache_ttl,
        )
        if tenant is None:
            logger.debug(
                "SubdomainResolver: no tenant found for subdomain='%s' (candidates: %s)",
                subdomain,
                candidates,
            )

        return tenant

    def resolve(self, request: "HttpRequest"):
        """
        Parse the request host and resolve the Tenant in one step.

        Combines get_subdomain_from_request() and resolve_tenant() for
        convenience. Returns None if either step fails.

        Args:
            request: The incoming Django HttpRequest.

        Returns:
            Tenant | None: The resolved Tenant instance, or None.
        """
        subdomain = self.get_subdomain_from_request(request)
        if subdomain is None:
            return None
        return self.resolve_tenant(subdomain)
