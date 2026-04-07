# Custom Domain Setup

> LankaCommerce Cloud - Custom Domain Resolution Documentation
> SubPhase-06, Group-C (Tasks 29-42)

---

## Overview

LankaCommerce Cloud supports custom domains for tenant storefronts and
dashboards. Tenants can map their own domains (e.g. shop.mybusiness.lk)
to their LankaCommerce account, providing a branded experience without
requiring the platform subdomain.

Custom domain resolution is handled by the CustomDomainResolver, which
complements the SubdomainResolver (Group-B) for subdomain-based tenants.

---

## Resolution Flow

1. HTTP request arrives with Host header (e.g. shop.mybusiness.lk).
2. LCCTenantMiddleware delegates to the resolver chain.
3. CustomDomainResolver checks if the host is NOT a platform domain.
4. If custom, looks up the full hostname in the Domain table.
5. Verifies the domain is DNS-verified (is_verified=True).
6. If verified, returns the associated Tenant and activates its schema.
7. If not verified or not found, returns None (falls through to 404).

---

## DNS Verification

Custom domains require DNS ownership verification before they can
resolve to a tenant. This prevents domain squatting and ensures
legitimate ownership.

### Verification Steps

1. Tenant requests a custom domain via the platform.
2. Platform generates a UUID4 verification token.
3. Token is stored in Domain.metadata with status "pending".
4. Tenant adds a DNS TXT record:
   - Record name: \_lcc-verification.{domain}
   - Record value: lcc-verify={token}
5. Tenant triggers verification check via the platform.
6. Platform queries DNS TXT records using dnspython.
7. If the TXT record matches, domain is marked as verified.

### Required DNS Records

For custom domain setup, tenants need to configure:

1. CNAME or A record pointing their domain to the LankaCommerce platform.
2. TXT record for domain ownership verification.

CNAME record example:

- Record name: shop.mybusiness.lk
- Record type: CNAME
- Record value: custom.lankacommerce.lk

TXT record example:

- Record name: \_lcc-verification.shop.mybusiness.lk
- Record type: TXT
- Record value: lcc-verify={token-from-platform}

### Verification States

- **pending**: Token generated, waiting for DNS propagation.
- **verified**: DNS check passed, domain ownership confirmed.
- **failed**: DNS check failed (wrong or missing TXT record).

---

## SSL Certificate Tracking (Task 36)

Custom domains have SSL certificate lifecycle tracking via the
Domain model's ssl_status field.

### SSL Status Values

- **none**: No SSL certificate configured (initial state).
- **pending**: Certificate provisioning in progress (e.g. Let's Encrypt ACME).
- **active**: Valid certificate installed and serving HTTPS traffic.
- **expired**: Certificate has expired; automated renewal should trigger.
- **failed**: Certificate provisioning or renewal failed.

### SSL Management Functions

- update_ssl_status(domain, status, ssl_expires_at): Update SSL state.
- check_ssl_expiry(domain): Check if certificate has expired and auto-update status.

### TLS Provisioning Expectations

The platform manages SSL certificates via automated ACME/Let's Encrypt
provisioning. After a custom domain is verified:

1. SSL status transitions from "none" to "pending".
2. ACME challenge is completed (HTTP-01 or DNS-01).
3. On success, status becomes "active" with ssl_expires_at set.
4. Automated renewal checks run before expiry.
5. On expiry, status transitions to "expired".

---

## Caching (Task 37)

Custom domain lookups are cached using Django's cache framework for
performance optimisation.

### Cache Configuration

- Cache key pattern: lcc:tenant_custom_domain:{domain}
- Cache TTL: Controlled by TENANT_DOMAIN_CACHE_TTL setting (default 300s).
- Miss sentinel: "**none**" stored for not-found domains to prevent DB miss loops.

### Cache Invalidation

- Domain post_save signal: Clears both subdomain and custom domain cache.
- Domain post_delete signal: Same invalidation on deletion.
- Explicit: invalidate_custom_domain_cache(domain_str) for manual eviction.

### Cache Behaviour

- First request: DB lookup, result cached.
- Subsequent requests within TTL: Served from cache (no DB hit).
- Not-found results: Cached with miss-sentinel to prevent repeated DB queries.
- Unverified domains: Cached as miss-sentinel until verification completes.
- On Domain save/delete: Cache automatically invalidated by signals.

---

## Not-Found Handling (Task 38)

When a custom domain is not found in the Domain table:

- resolve_by_domain() returns None.
- resolve_or_not_found() returns (None, "domain_not_found") for structured error handling.
- The result is cached with the miss-sentinel value.
- LCCTenantMiddleware handles the None by raising Http404 or falling back to public schema.
- A warning is logged with the unresolved hostname.

---

## Unverified Domain Handling (Task 39)

When a custom domain exists but is not verified:

- resolve_by_domain() returns None with a warning log.
- resolve_or_not_found() returns (None, "domain_not_verified").
- Access is blocked until DNS verification is completed.
- The unverified result is cached as miss-sentinel.
- Cache is invalidated when the domain is verified (via Domain save signal).
- Error response includes guidance to complete DNS verification.

---

## Multiple Domains Per Tenant (Task 40)

Each tenant may have multiple custom domains pointing to the same schema.

### Constraints

- All domains for a tenant resolve to the same PostgreSQL schema.
- One domain per tenant must be designated as primary (is_primary=True).
- Primary domain is used for canonical URLs and SEO redirects.
- Both verified and unverified domains are stored; only verified ones resolve.

### Management Functions

- get_tenant_domains(tenant): Returns all Domain records for a tenant.
- get_primary_domain(tenant): Returns the primary domain string.

---

## Primary Domain Redirect (Task 41)

Non-primary domains can redirect to the primary domain for SEO consistency.

### Redirect Conditions

A redirect is recommended when:

- The request host is a custom domain (not a platform subdomain).
- The request host is NOT the tenant's primary domain.
- The tenant has a primary domain configured.

### Redirect Behaviour

- HTTP 301 (permanent) redirect to the primary domain.
- Request path and query string are preserved.
- Only applies to custom domains; platform subdomains are not redirected.

### Redirect Functions

- should_redirect_to_primary(host, tenant): Returns True if redirect needed.
- get_redirect_url(request, tenant): Builds the full redirect URL.

---

## Custom Domain Resolver

The CustomDomainResolver class lives in:

    apps.tenants.middleware.domain_resolver

### Key Methods

- is_custom_domain(host): Checks if a host is a custom (non-platform) domain.
- resolve_by_domain(domain_str): Looks up a tenant by full domain with caching.
- resolve(request): Combined parse + lookup from an HTTP request.
- resolve_or_not_found(domain_str): Structured error handling for lookups.
- get_domain_info(domain_str): Full Domain object with SSL info.
- get_ssl_status(domain_str): SSL certificate status for a domain.
- get_tenant_domains(tenant): All domains for a tenant.
- get_primary_domain(tenant): Primary domain for a tenant.
- should_redirect_to_primary(host, tenant): Check if redirect needed.
- get_redirect_url(request, tenant): Build redirect URL.

---

## DNS Verification Utilities

The DNS verification module lives in:

    apps.tenants.utils.dns_verification

### Key Functions

- generate_verification_token(): Generates a UUID4 token.
- get_expected_txt_value(token): Builds the expected TXT record value.
- get_verification_record_name(domain): Builds the DNS record name.
- verify_domain_dns(domain, token): Checks DNS TXT records via dnspython.
- initiate_domain_verification(domain): Starts the verification workflow.
- check_domain_verification(domain): Checks DNS and updates status.
- update_verification_status(domain, status): Updates verification state.
- update_ssl_status(domain, status, ssl_expires_at): Updates SSL status.
- check_ssl_expiry(domain): Checks and auto-updates expired certificates.

### Dependencies

- dnspython: Required for DNS TXT record resolution.
- Falls back gracefully when not installed (returns False for all checks).

---

## Domain Model Fields

The Domain model (apps.tenants.models.Domain) includes fields for
custom domain management:

- domain: The full domain string (unique, from DomainMixin).
- is_primary: Whether this is the primary domain (from DomainMixin).
- domain_type: "platform" or "custom".
- is_verified: Boolean verification status.
- verified_at: Timestamp of last successful verification.
- metadata: JSON field storing verification tokens and status.
- ssl_status: SSL certificate lifecycle state.
- ssl_expires_at: Certificate expiry date.
- created_on / updated_on: Audit timestamps.

### Metadata Keys

- verification_token: The UUID4 token for DNS verification.
- verification_status: Current state (pending/verified/failed).
- verification_initiated_at: When verification was started.
- verification_last_checked_at: When DNS was last checked.
- verification_failure_reason: Reason for last failure.

---

## Cache Invalidation

Both subdomain and custom domain caches are invalidated when Domain
records change. Signal handlers in apps.tenants.signals handle this:

- invalidate_domain_cache_on_save: Clears subdomain cache on save.
- invalidate_domain_cache_on_delete: Clears subdomain cache on delete.
- invalidate_custom_domain_cache_on_save: Clears custom domain cache on save.
- invalidate_custom_domain_cache_on_delete: Clears custom domain cache on delete.

---

## Settings

No new Django settings are required for custom domain resolution. The
resolver reuses existing tenant settings:

- TENANT_BASE_DOMAIN: Used to distinguish platform vs custom domains.
- TENANT_DEV_DOMAINS: Development domains excluded from custom lookup.
- TENANT_DOMAIN_CACHE_TTL: Cache timeout for domain lookups.

---

## Custom Domain Setup Guide (Task 42)

### Step 1: Request Custom Domain

Navigate to tenant settings and enter the desired custom domain
(e.g. shop.mybusiness.lk).

### Step 2: Configure DNS

Add the following DNS records at your domain registrar:

1. CNAME record: Point your domain to the LankaCommerce platform.
2. TXT record: Add the verification token provided by the platform.

### Step 3: Verify Domain

Click "Verify Domain" in the platform to trigger DNS verification.
The platform checks for the TXT record and confirms ownership.

### Step 4: SSL Certificate

After verification, the platform automatically provisions an SSL
certificate. Monitor the SSL status in domain settings.

### Step 5: Go Live

Once verified and SSL is active, the custom domain will resolve
to the tenant's storefront or dashboard.
