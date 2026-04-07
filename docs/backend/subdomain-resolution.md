# Subdomain Resolution Flow

> **Phase:** 02 - Database Architecture & Multi-Tenancy
> **SubPhase:** 06 - Tenant Middleware Configuration
> **Group:** B - Subdomain Resolution
> **Document:** Architecture Reference

---

## Overview

Every multi-tenant request to LankaCommerce Cloud goes through subdomain
resolution before the tenant schema is activated. The `SubdomainResolver`
class (in `apps/tenants/middleware/subdomain_resolver.py`) is responsible
for parsing the HTTP `Host` header and mapping it to a `Tenant` instance
via the `Domain` model.

---

## Subdomain Validation Pattern (Task 26)

The module-level constant `SUBDOMAIN_PATTERN` defines the syntactic rules
for a valid tenant subdomain:

    Pattern: ^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$

### Permitted Characters

    lowercase ASCII letters    a–z
    digits                     0–9
    hyphen (middle only)       -

### Constraints

| Rule                     | Detail                                             |
| ------------------------ | -------------------------------------------------- |
| First character          | Must be a lowercase letter or digit                |
| Last character           | Must be a lowercase letter or digit                |
| Middle characters        | Lowercase letters, digits, and hyphens allowed     |
| Minimum length           | 1 character                                        |
| Maximum length           | 63 characters (RFC 1035 DNS label limit)           |
| Leading hyphen           | Prohibited — e.g. "-acme" is rejected              |
| Trailing hyphen          | Prohibited — e.g. "acme-" is rejected              |
| Uppercase letters        | Prohibited — input must be lowercased before check |
| Underscores              | Prohibited                                         |
| Dots (nested subdomains) | Prohibited — e.g. "a.b" is rejected at parse step  |
| Empty string             | Rejected                                           |

### Examples

Valid subdomains:
acme, my-store, store1, a, abc123, my-tenant-01, t

Invalid subdomains:
-acme (leading hyphen)
acme- (trailing hyphen)
my.sub (nested dot — rejected before SUBDOMAIN_PATTERN check)
ACME (uppercase — input must be lowercased first)
\_acme (underscore)
"" (empty string)

The `is_valid_subdomain(subdomain: str) -> bool` helper applies the pattern
and returns True/False. It is called inside `get_subdomain()` before returning
any extracted value.

---

## Reserved Subdomains (Task 27)

Certain subdomain names are permanently reserved for platform infrastructure
and are never resolved to a tenant, regardless of what the `Domain` table
contains.

### Reserved List (TENANT_RESERVED_SUBDOMAINS setting)

| Subdomain | Intended Purpose                       | Behavior on Request      |
| --------- | -------------------------------------- | ------------------------ |
| www       | Main website / marketing site          | Returns None (no tenant) |
| api       | Global REST/GraphQL API endpoint       | Returns None (no tenant) |
| admin     | Platform administration panel          | Returns None (no tenant) |
| app       | Main SaaS application entry point      | Returns None (no tenant) |
| static    | Static file delivery (CSS, JS, images) | Returns None (no tenant) |
| media     | Uploaded media file serving            | Returns None (no tenant) |
| mail      | Mail server / webmail interface        | Returns None (no tenant) |
| smtp      | SMTP relay endpoint                    | Returns None (no tenant) |
| cdn       | Content delivery network               | Returns None (no tenant) |
| docs      | Developer / API documentation          | Returns None (no tenant) |
| help      | Help centre                            | Returns None (no tenant) |
| support   | Customer support portal                | Returns None (no tenant) |
| status    | System status / uptime page            | Returns None (no tenant) |

### Reserved Subdomain Behavior

When `is_reserved(subdomain)` returns True:

1. `resolve_tenant()` logs a debug message:
   SubdomainResolver: 'www' is reserved - no tenant lookup
2. `resolve_tenant()` returns `None` immediately.
3. No cache read or write is performed.
4. No `Domain` model query is executed.
5. The HTTP layer (LCCTenantMiddleware or the view) receives `None` and
   is responsible for returning an appropriate response — typically 404
   or a redirect to the public schema URL.

### Extending the Reserved List

To add new reserved subdomains, update the `TENANT_RESERVED_SUBDOMAINS`
list in `config/settings/base.py`. The resolver reads this setting at
instantiation time.

---

## Full Resolution Flow (Task 28)

The following steps describe the complete path from an incoming HTTP request
to a resolved `Tenant` instance.

### Step 1: Host Header Extraction

`parse_host(host)` is called with the raw `Host` header value.

- Strips the port component: `acme.lcc.example.com:8000` → `acme.lcc.example.com`
- Converts to lowercase.
- Returns an empty string for blank input.

### Step 2: Bare Dev Host Check

If the normalised host is in `TENANT_DEV_DOMAINS` (default: `localhost`,
`127.0.0.1`), the host belongs to the platform itself and has no subdomain.
`get_subdomain()` returns `None`.

### Step 3: `.localhost` Dev Suffix Check

If the host ends with `.localhost` (e.g. `acme.localhost`), the prefix
before `.localhost` is treated as the subdomain. This supports local
development without requiring a full base-domain match.

### Step 4: WWW Prefix Stripping

If the host starts with `www.` (e.g. `www.acme.lcc.example.com`), the
`www.` prefix is stripped and resolution continues using the remaining
host (`acme.lcc.example.com`).

### Step 5: Base Domain Match

If the host ends with `.{TENANT_BASE_DOMAIN}` (e.g. `.lcc.example.com`),
the leading component is extracted as the subdomain.

Nested subdomains (containing a dot) are rejected at this step —
`a.b.lcc.example.com` would produce `a.b` which contains a dot and is
discarded.

### Step 6: Pattern Validation (Task 26)

The extracted subdomain string is validated against `SUBDOMAIN_PATTERN`.
Invalid strings (uppercase, underscores, leading/trailing hyphens,
empty) cause `get_subdomain()` to return `None`.

### Step 7: Reserved Subdomain Check (Task 27)

`resolve_tenant()` calls `is_reserved(subdomain)`. If the subdomain
appears in `TENANT_RESERVED_SUBDOMAINS`, `None` is returned immediately.

### Step 8: Cache Lookup (Task 23-24)

A cache key is constructed as `lcc:tenant_subdomain:{base_domain}:{subdomain}`.
The Django cache (typically Redis) is queried:

- **Cache hit (Tenant object)**: The `Tenant` instance is returned directly.
- **Cache hit (sentinel `"__none__"`)**: `None` is returned (previous miss).
- **Cache miss**: Execution continues to Step 9.

### Step 9: Database Lookup (Task 18)

The `Domain` model is queried for the following candidate domain strings
(in order):

1. `{subdomain}.{TENANT_BASE_DOMAIN}` — production format
2. `{subdomain}.localhost` — dev fallback

The first matching `Domain` record's linked `Tenant` is returned.
If no record matches, `tenant = None`.

### Step 10: Cache Population (Task 23-24)

The result is written to the cache:

- Found tenant: The `Tenant` object is cached with TTL = `TENANT_DOMAIN_CACHE_TTL`.
- Not found: The sentinel value `"__none__"` is cached to prevent repeated
  DB misses for the same subdomain.

### Step 11: Return

`resolve_tenant()` returns the `Tenant` instance or `None`.
`resolve(request)` wraps Steps 1–11 in a single call.

---

## Edge Cases

### Invalid Subdomain Syntax

A request for `https://_bad-.lcc.example.com/` produces host `_bad-.lcc.example.com`.

Step 5 extracts `_bad-`. Step 6 runs `is_valid_subdomain("_bad-")` → `False`
(contains underscore and trailing hyphen). `get_subdomain()` returns `None`.
No cache write, no DB query.

### Reserved Subdomain

A request for `https://admin.lcc.example.com/` produces subdomain `admin`.

Step 7 calls `is_reserved("admin")` → `True`. `resolve_tenant()` returns
`None` immediately. No cache write, no DB query.

### Unknown Subdomain (Not in Database)

A request for `https://unknown.lcc.example.com/` produces subdomain `unknown`.

Steps 1–7 pass. Step 8: cache miss. Step 9: no `Domain` record found.
Step 10: sentinel `"__none__"` cached. Step 11: returns `None`.

On a subsequent identical request the sentinel is read from the cache
(Step 8) and `None` is returned without another DB query.

### WWW Request

A request for `https://www.lcc.example.com/` has the `www.` stripped in
Step 4, leaving `lcc.example.com`. Step 5 attempts to match against
`.lcc.example.com` but the host is exactly the base domain with no leading
subdomain component. `get_subdomain()` returns `None`.

Alternatively, if `www` somehow passes to `resolve_tenant()`, Step 7
catches it as reserved and returns `None`.

### Localhost Bare Domain

A request for `http://localhost:8000/` — `parse_host()` strips the port,
yielding `localhost`. Step 2 recognises `localhost` as a dev domain and
`get_subdomain()` returns `None`.

### Nested Subdomain Attempt

A request for `https://a.b.lcc.example.com/` extracts `a.b` in Step 5.
The dot check (or SUBDOMAIN_PATTERN check in Step 6) rejects it.
`get_subdomain()` returns `None`.

---

## Cache Invalidation (Task 25)

When a `Domain` record is created, updated, or deleted, the `post_save`
and `post_delete` signals in `apps/tenants/signals.py` call
`invalidate_subdomain_cache(domain_str)`. This function:

1. Parses the stored domain string to extract the subdomain.
2. Builds the same cache key used during resolution.
3. Calls `cache.delete(key)` to evict the stale entry.

This ensures that the cache reflects the current state of the Domain table
immediately after any change.

---

## Related Files

| File                                            | Description                                                                                 |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `apps/tenants/middleware/subdomain_resolver.py` | SubdomainResolver implementation                                                            |
| `apps/tenants/middleware/tenant_middleware.py`  | LCCTenantMiddleware — calls SubdomainResolver                                               |
| `apps/tenants/middleware/__init__.py`           | Package exports (SubdomainResolver, SUBDOMAIN_PATTERN, is_valid_subdomain)                  |
| `apps/tenants/signals.py`                       | Domain cache invalidation signals                                                           |
| `config/settings/base.py`                       | TENANT_BASE_DOMAIN, TENANT_RESERVED_SUBDOMAINS, TENANT_DEV_DOMAINS, TENANT_DOMAIN_CACHE_TTL |
| `docs/backend/middleware-flow.md`               | Full LCCTenantMiddleware lifecycle                                                          |

---

## Settings Reference

| Setting                      | Default                      | Description                                                 |
| ---------------------------- | ---------------------------- | ----------------------------------------------------------- |
| `TENANT_BASE_DOMAIN`         | `"localhost"`                | Production base domain; subdomains resolve relative to this |
| `TENANT_RESERVED_SUBDOMAINS` | `["www", "api", ...]`        | Subdomains that never resolve to a tenant                   |
| `TENANT_DEV_DOMAINS`         | `["localhost", "127.0.0.1"]` | Bare dev hosts with no subdomain                            |
| `TENANT_DOMAIN_CACHE_TTL`    | `300`                        | Cache TTL in seconds for subdomain resolution results       |
