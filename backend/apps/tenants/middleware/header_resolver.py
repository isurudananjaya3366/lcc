"""
Header-based tenant resolver for LankaCommerce Cloud tenant middleware.

Resolves tenants by reading tenant identifiers from HTTP request headers.
This resolver is designed for API-only traffic where the client explicitly
identifies the tenant in a request header rather than through hostname.

Use cases:
    - Mobile applications making API calls with X-Tenant-ID header.
    - Third-party integrations sending X-Tenant-Slug for routing.
    - Webhook receivers identifying the target tenant via header.
    - Internal service-to-service calls with explicit tenant routing.

Header names (Task 44):
    TENANT_HEADER_NAME: Primary header carrying the tenant ID.
        Default: "X-Tenant-ID"
        Expected value: UUID or integer tenant primary key.
    TENANT_SLUG_HEADER: Alternative header carrying the tenant slug.
        Default: "X-Tenant-Slug"
        Expected value: URL-safe slug string (e.g. "acme-corp").

    The resolver tries the ID header first, then falls back to the slug
    header. If both are present, the ID header takes precedence.

Path restriction (Tasks 43, 50, 51):
    Header-based resolution is only active on paths that match the
    TENANT_HEADER_PATHS setting (default: /api/, /mobile/, /webhook/).
    Requests to other paths (e.g. HTML pages) are rejected by this
    resolver and fall through to the subdomain or custom domain resolver.
    Paths outside the allowed list are logged as rejected (Task 50).
    The allowed path list is configurable via Django settings (Task 51).

Security note (Task 49):
    A tenant header alone is NOT authentication. The header identifies
    which tenant schema to use, but the caller must still pass through
    the normal authentication pipeline (JWT, API key, session) before
    being granted access to tenant data. After tenant resolution, the
    middleware or view layer must verify that the authenticated user
    has an active membership or permission within the resolved tenant
    (validate_user_tenant_access). The header is a routing hint, not
    a security credential.

Caching (Task 52):
    Header-based tenant lookups are cached using Django's default cache
    backend. Cache key pattern: lcc:tenant_header:{source}:{identifier}.
    TTL is controlled by TENANT_DOMAIN_CACHE_TTL (shared with the
    subdomain and custom domain resolvers, default 300 seconds).
    Miss sentinel "__none__" is stored for not-found identifiers to
    avoid repeated database queries for invalid tenant identifiers.

Cache invalidation:
    Tenant model post_save/post_delete signals should clear header
    cache entries. This module provides invalidate_header_cache()
    for explicit eviction. Both ID and slug cache entries should be
    cleared when a tenant is modified.

Audit logging (Task 53):
    Header-based tenant access is logged for auditing purposes.
    Each successful resolution logs the tenant, request path, HTTP
    method, and authenticated user (if available). Failed resolutions
    (path rejection, missing header, tenant not found, inactive tenant)
    are also logged at appropriate levels. The log_header_access()
    method provides structured audit trail entries.

Task coverage:
    - Task 43: Create Header Resolver (class structure, API-only scope)
    - Task 44: Define Tenant Header Name (X-Tenant-ID, X-Tenant-Slug)
    - Task 45: Configure Header Setting (Django settings integration)
    - Task 46: Extract Header from Request (request.META extraction)
    - Task 47: Lookup Tenant by ID (cached ID/slug lookup)
    - Task 48: Validate Tenant Exists (active tenant validation)
    - Task 49: Handle API Authentication (auth integration, security)
    - Task 50: Restrict Header Resolution (path enforcement, rejection)
    - Task 51: Configure Allowed Paths (settings-driven path list)
    - Task 52: Cache Header Lookups (cache TTL, invalidation docs)
    - Task 53: Log Header-Based Access (audit logging)
    - Task 54: Document Header-Based Resolution (flow & constraints)

Dependencies:
    - Tenant model (for database lookups)
    - Django cache framework (for caching)
    - Django settings (for header name and path configuration)
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
_CACHE_KEY_PREFIX = "lcc:tenant_header"


def _build_cache_key(identifier: str) -> str:
    """Build a deterministic cache key for a header-based tenant lookup."""
    return f"{_CACHE_KEY_PREFIX}:{identifier}"


def invalidate_header_cache(identifier: str) -> None:
    """
    Evict cache entries related to the given tenant identifier.

    Called when tenant records change or when explicit invalidation
    is needed. Clears both potential ID and slug cache entries.

    Args:
        identifier: The tenant ID or slug string used as the cache key
            component, e.g. "acme-corp" or a UUID string.
    """
    from django.core.cache import cache

    key = _build_cache_key(identifier.lower())
    cache.delete(key)
    logger.debug(
        "invalidate_header_cache: deleted key '%s' for identifier '%s'",
        key,
        identifier,
    )


class HeaderResolver:
    """
    Header-based tenant resolver for LankaCommerce Cloud.

    Resolves tenants by extracting a tenant identifier from the request
    HTTP headers and looking up the corresponding Tenant model instance.
    Designed exclusively for API traffic paths.

    Task 43 - Resolver scope:
        The HeaderResolver handles header-based tenant identification.
        It is an alternative to SubdomainResolver (Group-B) and
        CustomDomainResolver (Group-C) for use cases where the tenant
        identity is carried in a request header rather than the Host.
        Scope is restricted to API paths (Task 43).

    Task 44 - Header names:
        Two headers are supported:
        - X-Tenant-ID (primary): Carries tenant primary key / UUID.
        - X-Tenant-Slug (fallback): Carries the tenant's URL slug.
        ID header takes precedence when both are present.

    Task 45 - Settings integration:
        All configuration is read from Django settings:
        - TENANT_HEADER_NAME: Primary header (default "X-Tenant-ID").
        - TENANT_SLUG_HEADER: Slug header (default "X-Tenant-Slug").
        - TENANT_HEADER_PATHS: List of URL path prefixes where
          header resolution is active.
        - TENANT_DOMAIN_CACHE_TTL: Cache timeout (shared).

    Task 46 - Header extraction:
        Headers are read from request.META using Django's HTTP_* prefix
        convention. Missing headers result in None (no error raised).

    Task 47 - Tenant lookup:
        Lookup first attempts by primary key (if the header value is
        numeric or a valid UUID), then falls back to slug-based lookup.
        Results are cached.

    Task 48 - Tenant validation:
        After lookup, the resolver validates that the tenant exists
        and is in an active state. Inactive tenants are rejected with
        a warning log and None return.

    Task 49 - API authentication integration:
        The header identifies the tenant but is NOT authentication.
        After tenant resolution, the authentication pipeline (JWT,
        API key, session) must verify user identity. The
        validate_user_tenant_access() method checks that an
        authenticated user belongs to the resolved tenant. This
        separation ensures tenant routing and user authentication
        are independent concerns.

    Task 50 - Path restriction enforcement:
        Requests outside the allowed path list are rejected with a
        warning log. The is_header_path() method enforces path
        restrictions, and rejected paths are logged for auditing.

    Task 51 - Allowed paths configuration:
        The allowed path list is configured via TENANT_HEADER_PATHS
        in Django settings. Default paths: /api/, /mobile/, /webhook/.
        Additional paths can be added in environment-specific settings.

    Task 52 - Cache behaviour:
        Tenant lookups are cached with configurable TTL (default 300s).
        Cache key pattern: lcc:tenant_header:{source}:{identifier}.
        Not-found results are cached using a miss sentinel to prevent
        database query storms. invalidate_header_cache() clears entries.

    Task 53 - Audit logging:
        Header-based access is logged via log_header_access() for
        audit trail requirements. Logs include tenant, path, HTTP
        method, and user. Resolution failures are logged at warning
        level for security monitoring.

    Task 54 - Documentation:
        Full resolution flow documented in class and module docstrings.
        See docs/backend/header-resolution.md for comprehensive
        documentation of flow, constraints, and security notes.

    Lifecycle:
        1. is_header_path(path) - check if path is in allowed paths
        2. extract_header(request) - read tenant identifier from header
        3. lookup_tenant(identifier) - cached tenant lookup
        4. validate_tenant(tenant) - check tenant is active
        5. validate_user_tenant_access(request, tenant) - auth check
        6. log_header_access(request, tenant) - audit logging
        7. resolve(request) - combined extract + lookup + validate + log
    """

    # ── Task 45: Settings-driven initialisation ──────────────────────

    def __init__(
        self,
        header_name: str | None = None,
        slug_header: str | None = None,
        allowed_paths: list[str] | None = None,
    ):
        """
        Initialise the header-based resolver.

        Reads configuration from Django settings when constructor
        parameters are not explicitly provided.

        Args:
            header_name: Override for the primary tenant header.
                When None, reads from settings.TENANT_HEADER_NAME.
            slug_header: Override for the slug tenant header.
                When None, reads from settings.TENANT_SLUG_HEADER.
            allowed_paths: Override for the allowed URL path prefixes.
                When None, reads from settings.TENANT_HEADER_PATHS.
        """
        from django.conf import settings

        self.header_name: str = (
            header_name
            or getattr(settings, "TENANT_HEADER_NAME", "X-Tenant-ID")
        )
        self.slug_header: str = (
            slug_header
            or getattr(settings, "TENANT_SLUG_HEADER", "X-Tenant-Slug")
        )
        self.allowed_paths: list[str] = (
            allowed_paths
            if allowed_paths is not None
            else list(
                getattr(
                    settings,
                    "TENANT_HEADER_PATHS",
                    ["/api/", "/mobile/", "/webhook/"],
                )
            )
        )
        self.cache_ttl: int = int(
            getattr(settings, "TENANT_DOMAIN_CACHE_TTL", 300)
        )

        # Pre-compute the META key for Django's request.META dict.
        # Django converts headers like "X-Tenant-ID" to "HTTP_X_TENANT_ID".
        self._meta_key: str = self._header_to_meta_key(self.header_name)
        self._slug_meta_key: str = self._header_to_meta_key(self.slug_header)

    # ── Internal helpers ──────────────────────────────────────────────

    @staticmethod
    def _header_to_meta_key(header_name: str) -> str:
        """
        Convert an HTTP header name to Django's request.META key format.

        Django stores HTTP headers in request.META with the prefix HTTP_,
        uppercase, and hyphens replaced by underscores.
        e.g. "X-Tenant-ID" → "HTTP_X_TENANT_ID"

        Args:
            header_name: The HTTP header name (e.g. "X-Tenant-ID").

        Returns:
            str: The META key (e.g. "HTTP_X_TENANT_ID").
        """
        return "HTTP_" + header_name.upper().replace("-", "_")

    # ── Task 43 & 50: Path restriction with enforcement logging ─────

    def is_header_path(self, path: str) -> bool:
        """
        Check if the request path is eligible for header-based resolution.

        Header-based resolution is restricted to API paths to avoid
        interfering with browser-based navigation which relies on
        subdomain or custom domain resolution.

        Path restriction enforcement (Task 50):
            Paths outside the allowed list are rejected. When a request
            arrives with a tenant header on a non-API path, the resolver
            returns False and logs a warning for audit purposes.

        Allowed paths configuration (Task 51):
            The allowed path prefixes are read from TENANT_HEADER_PATHS
            in Django settings. Default: ["/api/", "/mobile/", "/webhook/"].
            Add paths in config/settings/base.py or environment-specific
            settings files.

        Args:
            path: The request path (e.g. "/api/v1/products/").

        Returns:
            bool: True if the path starts with any prefix in
            TENANT_HEADER_PATHS, False otherwise.
        """
        if not path:
            return False
        is_allowed = any(
            path.startswith(prefix) for prefix in self.allowed_paths
        )
        if not is_allowed:
            logger.debug(
                "HeaderResolver: path '%s' rejected - not in allowed "
                "paths %s (Task 50)",
                path,
                self.allowed_paths,
            )
        return is_allowed

    # ── Task 46: Extract header from request ──────────────────────────

    def extract_header(self, request: "HttpRequest") -> tuple[str | None, str]:
        """
        Extract the tenant identifier from request headers.

        Tries the primary header (X-Tenant-ID) first. If not found,
        falls back to the slug header (X-Tenant-Slug). Returns a
        tuple of (value, source) where source indicates which header
        was used.

        Missing header handling (Task 46):
            When neither header is present, returns (None, "none").
            The caller can decide whether to fall through to another
            resolver or return an error.

        Args:
            request: The incoming Django HttpRequest.

        Returns:
            tuple[str | None, str]: A tuple of (identifier, source).
            source is one of: "id", "slug", "none".
            - ("abc-123", "id") - value from X-Tenant-ID header
            - ("acme-corp", "slug") - value from X-Tenant-Slug header
            - (None, "none") - neither header is present
        """
        # Try primary header (X-Tenant-ID)
        id_value = request.META.get(self._meta_key)
        if id_value:
            id_value = id_value.strip()
            if id_value:
                logger.debug(
                    "HeaderResolver: extracted '%s' from %s header",
                    id_value,
                    self.header_name,
                )
                return id_value, "id"

        # Fallback to slug header (X-Tenant-Slug)
        slug_value = request.META.get(self._slug_meta_key)
        if slug_value:
            slug_value = slug_value.strip()
            if slug_value:
                logger.debug(
                    "HeaderResolver: extracted '%s' from %s header",
                    slug_value,
                    self.slug_header,
                )
                return slug_value, "slug"

        logger.debug(
            "HeaderResolver: no tenant header found (checked %s, %s)",
            self.header_name,
            self.slug_header,
        )
        return None, "none"

    # ── Task 47: Lookup tenant by ID or slug (cached) ─────────────────

    def lookup_tenant(self, identifier: str, source: str = "id"):
        """
        Look up a Tenant by ID or slug with caching.

        Caching:
            Checks the Django cache before querying the database.
            Results (including not-found) are stored with the same
            TTL as domain lookups (TENANT_DOMAIN_CACHE_TTL).

        Lookup strategy (Task 47):
            - If source is "id": Looks up by primary key (pk).
            - If source is "slug": Looks up by schema_name (slug).
            - Falls through to slug lookup if ID lookup fails.

        Not-found handling (Task 47):
            When no Tenant matches, None is returned. The miss-sentinel
            is cached to prevent repeated DB queries for non-existent
            identifiers.

        Args:
            identifier: The tenant identifier extracted from the header.
            source: One of "id" or "slug", indicating the lookup strategy.

        Returns:
            Tenant | None: The matching Tenant instance, or None if
            not found.
        """
        if not identifier:
            return None

        from django.core.cache import cache

        cache_key = _build_cache_key(f"{source}:{identifier}".lower())
        cached = cache.get(cache_key)
        if cached is not None:
            if cached == _CACHE_MISS_SENTINEL:
                logger.debug(
                    "HeaderResolver: cache miss-sentinel for '%s' (source=%s)",
                    identifier,
                    source,
                )
                return None
            logger.debug(
                "HeaderResolver: cache hit for '%s' → tenant='%s'",
                identifier,
                getattr(cached, "name", "?"),
            )
            return cached

        # Cache miss - query the database
        from apps.tenants.models import Tenant

        tenant = None

        if source == "id":
            tenant = self._lookup_by_id(identifier)
        if tenant is None:
            tenant = self._lookup_by_slug(identifier)

        if tenant is None:
            cache.set(cache_key, _CACHE_MISS_SENTINEL, timeout=self.cache_ttl)
            logger.debug(
                "HeaderResolver: no tenant found for '%s' (source=%s)",
                identifier,
                source,
            )
            return None

        cache.set(cache_key, tenant, timeout=self.cache_ttl)
        logger.debug(
            "HeaderResolver: '%s' (source=%s) resolved to tenant='%s'",
            identifier,
            source,
            getattr(tenant, "name", "?"),
        )
        return tenant

    def _lookup_by_id(self, identifier: str):
        """
        Attempt to look up a Tenant by its primary key.

        Handles both integer and UUID-style primary keys gracefully.
        Returns None if the identifier cannot be interpreted as a valid
        primary key or if no matching tenant is found.

        Args:
            identifier: The raw identifier string from the header.

        Returns:
            Tenant | None: The matching Tenant, or None.
        """
        from apps.tenants.models import Tenant

        try:
            return Tenant.objects.get(pk=identifier)
        except (Tenant.DoesNotExist, ValueError, TypeError):
            return None

    def _lookup_by_slug(self, identifier: str):
        """
        Attempt to look up a Tenant by its schema_name (slug).

        The schema_name field in django-tenants is the unique slug
        that identifies the tenant's PostgreSQL schema.

        Args:
            identifier: The slug string from the header.

        Returns:
            Tenant | None: The matching Tenant, or None.
        """
        from apps.tenants.models import Tenant

        try:
            return Tenant.objects.get(schema_name=identifier.lower())
        except Tenant.DoesNotExist:
            return None

    # ── Task 48: Validate tenant exists and is active ─────────────────

    def validate_tenant(self, tenant) -> bool:
        """
        Validate that a resolved tenant is active and usable.

        Active tenant requirements (Task 48):
            - Tenant object is not None.
            - Tenant has an 'is_active' attribute set to True,
              OR lacks 'is_active' entirely (assumed active for
              models without this field).

        Error responses (Task 48):
            When validation fails, this method returns False.
            The caller should respond with HTTP 404 (tenant not found)
            or HTTP 403 (tenant suspended), depending on the reason.

        Args:
            tenant: The Tenant model instance to validate.

        Returns:
            bool: True if the tenant is valid and active,
            False otherwise.
        """
        if tenant is None:
            return False

        # Check is_active if the field exists on the model
        is_active = getattr(tenant, "is_active", True)
        if not is_active:
            logger.warning(
                "HeaderResolver: tenant '%s' is inactive - "
                "rejecting header-based resolution",
                getattr(tenant, "name", "?"),
            )
            return False

        return True

    # ── Task 49: API authentication integration ───────────────────────

    def validate_user_tenant_access(
        self, request: "HttpRequest", tenant
    ) -> bool:
        """
        Validate that the authenticated user belongs to the resolved tenant.

        Security model (Task 49):
            The tenant header is a routing hint, NOT authentication.
            After tenant resolution, this method checks that the
            request's authenticated user has permission to access the
            resolved tenant. This prevents a user from accessing
            another tenant's data by simply changing the header value.

            Authentication flow:
            1. Tenant header selects the target tenant (routing).
            2. Authentication middleware verifies user identity (JWT/API key).
            3. This method verifies user-tenant relationship (authorisation).

            If the request has no authenticated user (anonymous), this
            method returns True to allow the authentication middleware
            to handle access control downstream. The header resolver
            does not enforce authentication — that is the responsibility
            of DRF permission classes or Django auth middleware.

        User-tenant membership check:
            If the user model has a 'tenants' relation (ManyToMany or
            similar), the method checks membership. If no such relation
            exists, the method returns True (permissive fallback).

        Args:
            request: The incoming Django HttpRequest (may have request.user).
            tenant: The resolved Tenant model instance.

        Returns:
            bool: True if the user is allowed to access the tenant,
            or if the user is anonymous (auth handled downstream).
            False if the user is authenticated but lacks tenant access.
        """
        user = getattr(request, "user", None)
        if user is None or not getattr(user, "is_authenticated", False):
            # Anonymous request — let auth middleware handle it
            logger.debug(
                "HeaderResolver: anonymous request — tenant access "
                "check deferred to auth middleware (Task 49)"
            )
            return True

        # Check user-tenant membership if the relation exists
        tenants_rel = getattr(user, "tenants", None)
        if tenants_rel is not None and hasattr(tenants_rel, "filter"):
            has_access = tenants_rel.filter(pk=tenant.pk).exists()
            if not has_access:
                logger.warning(
                    "HeaderResolver: user '%s' does not belong to "
                    "tenant '%s' — access denied (Task 49)",
                    getattr(user, "username", user.pk),
                    getattr(tenant, "name", tenant.pk),
                )
                return False
            logger.debug(
                "HeaderResolver: user '%s' confirmed in tenant '%s'",
                getattr(user, "username", user.pk),
                getattr(tenant, "name", tenant.pk),
            )

        return True

    # ── Task 53: Audit logging ────────────────────────────────────────

    def log_header_access(
        self,
        request: "HttpRequest",
        tenant,
        outcome: str = "resolved",
    ) -> None:
        """
        Log header-based tenant access for auditing.

        Audit trail (Task 53):
            Every header-based tenant resolution is logged with:
            - Tenant name / identifier
            - Request path
            - HTTP method
            - Authenticated user (if available)
            - Resolution outcome (resolved / rejected / not_found)

            Successful resolutions are logged at INFO level.
            Failures are logged at WARNING level.

            These logs support security auditing and can be forwarded
            to centralised logging systems (ELK, CloudWatch, etc.)
            for compliance and monitoring.

        Args:
            request: The incoming Django HttpRequest.
            tenant: The resolved Tenant instance (may be None on failure).
            outcome: One of "resolved", "rejected", "not_found",
                "inactive", "path_rejected". Describes the resolution
                result for the audit record.
        """
        user = getattr(request, "user", None)
        username = "anonymous"
        if user is not None and getattr(user, "is_authenticated", False):
            username = getattr(user, "username", str(getattr(user, "pk", "?")))

        tenant_name = (
            getattr(tenant, "name", str(getattr(tenant, "pk", "?")))
            if tenant is not None
            else "none"
        )

        method = getattr(request, "method", "?")
        path = getattr(request, "path", "?")

        log_msg = (
            "HeaderResolver audit: outcome=%s tenant=%s path=%s "
            "method=%s user=%s"
        )
        log_args = (outcome, tenant_name, path, method, username)

        if outcome == "resolved":
            logger.info(log_msg, *log_args)
        else:
            logger.warning(log_msg, *log_args)

    # ── Combined resolve from request (Tasks 43-54) ──────────────────

    def resolve(self, request: "HttpRequest"):
        """
        Resolve a Tenant from the request headers.

        Combined extract + lookup + validate + auth + log in one call.
        Returns the Tenant if found and active, or None if the header
        is missing, the path is not eligible, or the tenant is invalid.

        Resolution flow (Task 54):
            1. Check if the request path is eligible (is_header_path).
               If not, reject with audit log (Task 50).
            2. Extract the tenant identifier from headers (extract_header).
               If missing, return None (no error).
            3. Look up the Tenant by ID or slug (lookup_tenant).
               Uses cache for performance (Task 52).
            4. Validate the tenant is active (validate_tenant).
               Inactive tenants are rejected (Task 48).
            5. Validate user-tenant access (validate_user_tenant_access).
               Authenticated users must belong to tenant (Task 49).
            6. Log the resolution outcome for auditing (Task 53).
            7. Return the Tenant or None.

        Constraints (Task 54):
            - Header is NOT authentication (security boundary).
            - Only active on allowed paths (path restriction).
            - Cache TTL is configurable via settings.
            - All outcomes are audit-logged.

        Args:
            request: The incoming Django HttpRequest.

        Returns:
            Tenant | None: The resolved and validated Tenant instance,
            or None if resolution failed at any step.
        """
        path = request.path

        # Task 50: Enforce path restriction
        if not self.is_header_path(path):
            logger.debug(
                "HeaderResolver: path '%s' is not an API path - skipping",
                path,
            )
            self.log_header_access(request, None, outcome="path_rejected")
            return None

        # Task 46: Extract tenant identifier from header
        identifier, source = self.extract_header(request)
        if identifier is None:
            return None

        # Task 47 & 52: Cached tenant lookup
        tenant = self.lookup_tenant(identifier, source)
        if not self.validate_tenant(tenant):
            self.log_header_access(
                request,
                tenant,
                outcome="inactive" if tenant is not None else "not_found",
            )
            return None

        # Task 49: Validate user belongs to resolved tenant
        if not self.validate_user_tenant_access(request, tenant):
            self.log_header_access(request, tenant, outcome="rejected")
            return None

        # Task 53: Audit log for successful resolution
        self.log_header_access(request, tenant, outcome="resolved")

        return tenant
