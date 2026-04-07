# ADR-0004: Per-Tenant Authentication

> **Status:** Accepted
> **Date:** 2026-02-16
> **Authors:** LankaCommerce Cloud Team

---

## Context

LankaCommerce Cloud uses schema-based multi-tenancy via django-tenants (see ADR-0002). Each tenant gets a dedicated PostgreSQL schema, while shared infrastructure lives in the public schema.

Django's auth app (django.contrib.auth) provides User, Group, and Permission models. In a multi-tenant system, there are two approaches to authentication:

| Approach        | Description                                                                                   |
| --------------- | --------------------------------------------------------------------------------------------- |
| Shared auth     | All users live in the public schema; tenant access is controlled via roles or foreign keys    |
| Per-tenant auth | Each tenant schema has its own auth tables; users, groups, and permissions are fully isolated |

The team needed to decide how authentication and authorization should work across tenants, considering data isolation, compliance, and operational simplicity.

---

## Decision

We will use **per-tenant authentication**. The django.contrib.auth app appears in both SHARED_APPS and TENANT_APPS:

- **SHARED_APPS** — Auth tables in the public schema serve superusers and platform administrators
- **TENANT_APPS** — Auth tables in each tenant schema serve tenant-specific users, groups, and permissions

This means:

- Each tenant has its own User table with completely isolated user accounts
- Each tenant has its own Group and Permission tables for role-based access control
- A user in tenant A cannot see or authenticate as a user in tenant B
- Platform superusers exist in the public schema for cross-tenant administration
- django.contrib.contenttypes is also in both lists, because the auth Permission model has a foreign key to ContentType

---

## Consequences

### Positive

- Complete user isolation between tenants — no risk of cross-tenant authentication
- Each tenant can define custom groups and permissions independently
- Tenant administrators can manage their own users without affecting other tenants
- Password policies, user counts, and access patterns are fully isolated
- Compliance-friendly — Sri Lankan data protection requirements are easier to meet when user data is schema-isolated
- Tenant deletion cleanly removes all associated user accounts with the schema

### Negative

- A person working for multiple tenants needs separate user accounts in each tenant schema
- Password resets and account recovery are per-tenant; no single sign-on across tenants without additional infrastructure
- Platform-wide user analytics require querying across multiple schemas
- Slightly more storage overhead — auth tables are replicated in every tenant schema

### Neutral

- django-tenants handles the schema switching transparently; application code does not need to be aware of per-tenant auth isolation
- The contenttypes app must also be per-tenant to support the Permission foreign key to ContentType
- Future single sign-on or cross-tenant identity federation can be layered on top without changing this foundation

---

## Alternatives Considered

| Alternative                         | Reason for Rejection                                                                                              |
| ----------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| Shared auth with tenant foreign key | Weaker isolation — a missing tenant filter on user queries could expose other tenants' user data                  |
| Shared auth with row-level security | More complex to implement and test with Django ORM; does not integrate cleanly with django-tenants schema routing |
| External identity provider only     | Adds infrastructure complexity; not all Sri Lankan SMEs use external identity providers                           |

---

## References

- [ADR-0002: Multi-Tenancy Approach](0002-multi-tenancy-approach.md) — Schema-based isolation decision
- [App Classification Guide](../database/app-classification.md) — SHARED_APPS and TENANT_APPS lists
- [Tenant Settings Reference](../database/tenant-settings.md) — django-tenants configuration
- [django-tenants documentation on shared and tenant apps](https://django-tenants.readthedocs.io/en/latest/install.html)
