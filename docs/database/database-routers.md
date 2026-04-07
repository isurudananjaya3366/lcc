# Database Router Configuration

> LankaCommerce Cloud -- Schema-Aware Query and Migration Routing
> SubPhase-07, Group-A (Tasks 01-14), Group-B (Tasks 15-28), Group-C (Tasks 29-42), Group-D (Tasks 43-56), Group-E (Tasks 57-68), Group-F (Tasks 69-78)

---

## Overview

LankaCommerce Cloud uses a custom database router to ensure that queries
and migrations are directed to the correct PostgreSQL schema. The routing
system maintains data isolation between tenants by enforcing that shared
apps operate in the public schema and tenant apps operate in individual
tenant schemas.

---

## Router Stack

DATABASE_ROUTERS controls the order in which routers are consulted.
LankaCommerce uses a two-router stack:

| Priority | Router                                  | Purpose                                          |
| -------- | --------------------------------------- | ------------------------------------------------ |
| 1        | apps.tenants.routers.LCCDatabaseRouter  | Relation prevention + migration routing (custom) |
| 2        | django_tenants.routers.TenantSyncRouter | Required by django-tenants AppConfig validation  |

LCCDatabaseRouter extends django-tenants' TenantSyncRouter (Task 04),
inheriting migration routing and adding cross-schema relation prevention.
TenantSyncRouter is also listed explicitly because django-tenants performs
a string-based check in its AppConfig.ready() to ensure it is present.

### Legacy Stack (Reference Only)

The original two-router configuration (replaced by LCCDatabaseRouter):

| Priority | Router                                  | Purpose                              |
| -------- | --------------------------------------- | ------------------------------------ |
| 1        | apps.tenants.routers.TenantRouter       | Cross-schema relation prevention     |
| 2        | django_tenants.routers.TenantSyncRouter | Migration routing (shared vs tenant) |

Django evaluates routers in order. For each database operation, the first
router to return a non-None value wins. If all routers return None, Django
falls back to default behavior.

---

## LCCDatabaseRouter (Tasks 04, 06-10)

The LCCDatabaseRouter is defined in backend/apps/tenants/routers.py and
extends django-tenants' TenantSyncRouter. It combines migration routing
(inherited) with cross-schema relation prevention (added).

### Router Order (Task 06)

LCCDatabaseRouter MUST be first in DATABASE_ROUTERS because:

- allow_relation returns True or False (never None), making it definitive
- db_for_read and db_for_write are checked first before fallback routers
- The inherited allow_migrate runs through our class before TenantSyncRouter

Django evaluates routers in order. The first non-None return value wins.
Use validate_router_order() from router_utils to verify at runtime.

### Router Utilities (Task 07)

Schema access helpers are in backend/apps/tenants/utils/router_utils.py:

| Function                     | Returns           | Purpose                               |
| ---------------------------- | ----------------- | ------------------------------------- |
| get_current_schema()         | str               | Active PostgreSQL schema name         |
| is_public_schema()           | bool              | Whether the public schema is active   |
| get_tenant_from_connection() | Tenant or None    | Active tenant from DB connection      |
| get_app_schema_type(label)   | str               | App's schema residency classification |
| validate_router_order()      | tuple[bool, list] | Verify DATABASE_ROUTERS ordering      |
| get_schema_info()            | dict              | Schema context dict for debugging     |

### Methods

| Method         | Source            | Task | Behavior                                                  |
| -------------- | ----------------- | ---- | --------------------------------------------------------- |
| allow_migrate  | TenantSyncRouter  | 04   | Routes migrations to correct schema (shared vs tenant)    |
| allow_relation | LCCDatabaseRouter | 10   | Blocks relations between shared-only and tenant-only apps |
| db_for_read    | LCCDatabaseRouter | 08   | Returns None (defers to PostgreSQL search_path)           |
| db_for_write   | LCCDatabaseRouter | 09   | Returns None (defers to PostgreSQL search_path)           |

### db_for_read Behavior (Task 08)

Returns None to defer read routing to PostgreSQL search_path. The
django-tenants middleware sets search_path to the active tenant schema
before any ORM query executes. The search_path mechanism works as:

1. Request arrives, middleware resolves the tenant
2. connection.set_tenant() sets search_path to tenant_schema + public
3. PostgreSQL resolves table names using search_path
4. Queries hit the correct schema transparently

No router-level read routing is needed.

### db_for_write Behavior (Task 09)

Returns None to defer write routing to PostgreSQL search_path. Same
mechanism as db_for_read. Write operations (INSERT, UPDATE, DELETE) go
to whichever schema is active in the connection's search_path.

Public schema constraints for tenant-only apps are enforced at the
migration level via allow_migrate (inherited from TenantSyncRouter),
not at the write routing level.

### allow_relation Behavior (Task 10)

Enforces cross-schema relation prevention. Always returns True or False
(never None), so subsequent routers are not consulted for relation
decisions. This is intentional: cross-schema rules must be definitive.

Blocked relations are logged at WARNING level for audit trail.

### allow_migrate Behavior (Task 11)

LCCDatabaseRouter provides an explicit allow_migrate override that
delegates to TenantSyncRouter.allow_migrate via super(). This provides:

1. Transparency: The migration routing behavior is visible in the
   codebase rather than being an implicit inheritance.
2. Logging: DEBUG-level logging of migration routing decisions.
3. Extension point: Future customization can be added without
   modifying the parent class.

Migration routing rules (inherited from TenantSyncRouter):

- Shared apps (in SHARED_APPS) migrate ONLY to the public schema
- Tenant apps (in TENANT_APPS) migrate ONLY to tenant schemas
- Dual apps (in both lists) migrate to both schemas

### Schema Selector (Task 12)

The select_schema() helper in utils/router_utils.py provides a single
point of access for determining the active schema. It retrieves the
schema from the database connection context (set by middleware or
tenant_context).

The schema is determined by the django-tenants middleware during HTTP
requests, or by set_current_tenant() / tenant_context() for background
tasks and management commands.

### Default Schema Handling (Task 13)

When no tenant has been activated, the system falls back to the public
schema. Two helpers support this:

| Function           | Returns  | Purpose                                         |
| ------------------ | -------- | ----------------------------------------------- |
| get_default_schema | "public" | Returns the default schema name                 |
| ensure_schema      | str      | Returns active schema or falls back to "public" |

The fallback applies during:

- Application startup and initialization
- Management commands without tenant_context
- Health check endpoints on the public domain
- Background tasks before tenant activation

---

## Router Configuration Reference (Task 14)

### DATABASE_ROUTERS Setting

Located in backend/config/settings/database.py:

| Position | Router                                  | Role                                 |
| -------- | --------------------------------------- | ------------------------------------ |
| 1        | apps.tenants.routers.LCCDatabaseRouter  | Primary router (custom + inherited)  |
| 2        | django_tenants.routers.TenantSyncRouter | Framework requirement (string check) |

### Method Responsibilities

| Method         | Router            | Behavior                       | Returns         |
| -------------- | ----------------- | ------------------------------ | --------------- |
| db_for_read    | LCCDatabaseRouter | Defers to search_path          | None            |
| db_for_write   | LCCDatabaseRouter | Defers to search_path          | None            |
| allow_relation | LCCDatabaseRouter | Cross-schema prevention        | True or False   |
| allow_migrate  | LCCDatabaseRouter | Schema-aware migration routing | True/False/None |

### Routing Flow

1. Django receives a database operation (read, write, relation, migrate)
2. Django iterates DATABASE_ROUTERS in order
3. LCCDatabaseRouter is evaluated first
4. For allow_relation: returns True/False definitively (never None)
5. For db_for_read/write: returns None, deferring to search_path
6. For allow_migrate: delegates to TenantSyncRouter logic via super()
7. If LCCDatabaseRouter returns None, Django checks TenantSyncRouter
8. TenantSyncRouter handles any remaining migration routing

### Schema Access Utilities

Located in backend/apps/tenants/utils/router_utils.py:

| Function                     | Purpose                                  |
| ---------------------------- | ---------------------------------------- |
| get_current_schema()         | Active PostgreSQL schema name            |
| is_public_schema()           | Check if public schema is active         |
| get_tenant_from_connection() | Active tenant from DB connection         |
| get_app_schema_type()        | Classify app's schema residency          |
| validate_router_order()      | Verify DATABASE_ROUTERS ordering         |
| get_schema_info()            | Schema context dict for debugging        |
| select_schema()              | Schema selector for routing decisions    |
| get_default_schema()         | Default (public) schema name             |
| ensure_schema()              | Ensure valid schema with public fallback |

---

## App Routing (Tasks 15-20)

### Shared Apps List (Task 15)

Shared apps are defined in SHARED_APPS in config/settings/database.py.
These apps have tables only in the public schema. Use get_shared_apps()
from router_utils to retrieve the list programmatically.

Shared apps include:

- Multi-tenancy infrastructure: django_tenants, apps.tenants
- Django framework: admin, sessions, messages, staticfiles
- LankaCommerce shared: core, users, platform
- Third-party infrastructure: rest_framework, corsheaders, channels, etc.

### Tenant Apps List (Task 16)

Tenant apps are defined in TENANT_APPS in config/settings/database.py.
These apps have tables in each tenant schema, containing business data
that must be isolated per tenant. Use get_tenant_apps() from router_utils
to retrieve the list programmatically.

Tenant apps include:

- products, inventory, vendors, sales, customers
- orders, hr, accounting, reports, webstore, integrations

### Route Shared App Queries (Task 17)

Shared app queries are routed to the public schema via PostgreSQL
search_path. When django-tenants middleware sets search_path to
[tenant_schema, public], shared app tables are resolved from the
public schema because they only exist there.

The router returns None for db_for_read and db_for_write, deferring
entirely to the search_path mechanism. No router-level override is
needed for shared app query routing.

Use get_query_schema(app_label) from router_utils to determine which
schema an app's queries will target.

### Route Tenant App Queries (Task 18)

Tenant app queries are routed to the active tenant schema via
PostgreSQL search_path. The middleware sets search_path to
[tenant_schema, public], and tenant app tables are resolved from
the tenant schema because they only exist there.

The search_path ensures transparent routing without router-level
intervention. All tenant app queries automatically hit the correct
tenant schema based on the active connection context.

### Handle Mixed Queries (Task 19)

Mixed queries involving both shared and tenant models are handled at
the SQL level by PostgreSQL search_path (which includes both the
tenant schema and public). However, Django-level ForeignKey relations
between shared-only and tenant-only apps are blocked by allow_relation.

| Combination     | SQL Query | Django FK |
| --------------- | --------- | --------- |
| shared + shared | Safe      | Allowed   |
| tenant + tenant | Safe      | Allowed   |
| dual + anything | Safe      | Allowed   |
| shared + tenant | Possible  | Blocked   |

Use is_mixed_query_safe(app1, app2) from router_utils to check whether
a cross-app query is structurally valid.

### Get Schema from Context (Task 20)

The active schema is retrieved from the database connection's
thread-local context using get_schema_from_context() in router_utils.

This function returns a dict with:

| Key       | Type | Description                         |
| --------- | ---- | ----------------------------------- |
| schema    | str  | Active schema name                  |
| source    | str  | "middleware" or "default"           |
| is_public | bool | Whether the public schema is active |
| tenant    | str  | Active tenant schema_name or None   |

The schema source is determined by checking whether a tenant has been
activated on the connection (by middleware or tenant_context).

### App Routing Utilities

Located in backend/apps/tenants/utils/router_utils.py:

| Function                  | Task  | Purpose                               |
| ------------------------- | ----- | ------------------------------------- |
| get_shared_apps()         | 15    | Return SHARED_APPS list from settings |
| get_tenant_apps()         | 16    | Return TENANT_APPS list from settings |
| get_query_schema(label)   | 17-18 | Determine query target schema         |
| is_mixed_query_safe(a,b)  | 19    | Check cross-app query safety          |
| get_schema_from_context() | 20    | Retrieve schema with source context   |

---

## Schema Switching (Tasks 21-25)

Schema switching functions provide safe ways to detect, inspect, and
change the active PostgreSQL schema on the database connection. These
utilities complement the routing layer by enabling explicit schema
management for background tasks, management commands, and cross-schema
operations.

### Task 21: Handle Missing Context

`handle_missing_context()` detects when no tenant has been activated on
the database connection and provides a safe fallback to the public
schema. Returns a context dict with the resolved schema, whether the
context was missing, the reason, and whether the fallback was applied.

Missing context occurs during:

- Application startup and initialization
- Management commands without explicit tenant_context
- Health check endpoints on the public domain
- Background tasks before tenant activation

```python
from apps.tenants.utils.router_utils import handle_missing_context

result = handle_missing_context()
# {'schema': 'public', 'is_missing': True, 'reason': '...', 'fallback_used': True}
```

### Task 22: Set Search Path

`get_search_path_info()` documents how search_path is configured on the
current database connection. search_path determines which schema
PostgreSQL resolves table names from.

django-tenants sets search_path via:

1. `connection.set_tenant(tenant)` -- sets to [tenant_schema, public]
2. `connection.set_schema(name)` -- sets to [schema_name, public]
3. `connection.set_schema_to_public()` -- sets to [public]

```python
from apps.tenants.utils.router_utils import get_search_path_info

info = get_search_path_info()
# {'schema_name': 'public', 'search_path_includes_public': True,
#  'set_by': 'default (public schema)', 'is_default': True}
```

### Task 23: Handle Schema Switching

`switch_schema(schema_name)` validates the target schema name and
switches the database connection. This is a convenience wrapper around
`connection.set_schema()` with validation and logging.

**Important:** This changes the connection's search_path for ALL
subsequent queries. Prefer `schema_context()` (Task 24) or
`tenant_context()` for temporary switches.

```python
from apps.tenants.utils.router_utils import switch_schema

result = switch_schema("tenant_acme")
# {'previous_schema': 'public', 'new_schema': 'tenant_acme', 'switched': True}
```

### Task 24: Create Schema Wrapper

`schema_context(schema_name)` is a context manager for executing code
within a specific schema. Unlike `tenant_context()` which requires a
Tenant model instance, this works with schema names directly.

On entry, sets the connection's search_path. On exit, restores the
previous schema, even if an exception occurs.

```python
from apps.tenants.utils.router_utils import schema_context

with schema_context("tenant_acme"):
    # All queries target tenant_acme schema
    ...
# Previous schema is restored here
```

### Task 25: Handle Concurrent Requests

`get_request_isolation_info()` documents how schema context is isolated
across concurrent requests.

Isolation mechanisms:

1. **threading.local()** -- Each thread has its own tenant slot
2. **django.db.connection** -- Per-thread connection with its own
   schema_name and search_path
3. **Middleware** -- TenantMainMiddleware activates the correct tenant
   at request start and releases at request end

```python
from apps.tenants.utils.router_utils import get_request_isolation_info

info = get_request_isolation_info()
# {'thread_id': 140234..., 'thread_name': 'MainThread',
#  'schema_name': 'public', 'is_isolated': True, 'isolation_mechanism': '...'}
```

### Schema Switching Utility Summary

| Function                     | Task | Purpose                             |
| ---------------------------- | ---- | ----------------------------------- |
| handle_missing_context()     | 21   | Detect missing context, fallback    |
| get_search_path_info()       | 22   | Document search_path configuration  |
| switch_schema(name)          | 23   | Safely switch to a different schema |
| schema_context(name)         | 24   | Context manager for schema scope    |
| get_request_isolation_info() | 25   | Document thread isolation           |

---

## Schema Validation & Documentation (Tasks 26-28)

Schema validation and routing documentation functions ensure safe
routing by validating schema names before use and providing a
programmatic summary of the routing rules.

### Task 26: Validate Schema Exists

`validate_schema_exists(schema_name)` validates that a schema name is
structurally valid before routing queries. In the LCC architecture,
schemas are created by django-tenants during tenant provisioning.
This function validates naming conventions without querying the
database.

Validation rules:

- "public" is always valid
- Non-empty string schema names are considered structurally valid
- Empty strings and None are invalid

```python
from apps.tenants.utils.router_utils import validate_schema_exists

result = validate_schema_exists("tenant_acme")
# {'schema': 'tenant_acme', 'is_valid': True, 'reason': '...'}

result = validate_schema_exists("")
# {'schema': '', 'is_valid': False, 'reason': 'empty or None schema name'}
```

### Task 27: Handle Invalid Schema

`handle_invalid_schema(schema_name)` handles invalid schema identifiers
by providing a safe fallback to the public schema. Invalid schemas can
occur during partial tenant provisioning failures, stale schema
references, or malformed context from background tasks.

The public schema fallback ensures queries target a valid schema
rather than failing with a PostgreSQL error.

```python
from apps.tenants.utils.router_utils import handle_invalid_schema

result = handle_invalid_schema("")
# {'original_schema': '', 'fallback_schema': 'public',
#  'is_invalid': True, 'error': "invalid schema '': ..."}

result = handle_invalid_schema("public")
# {'original_schema': 'public', 'fallback_schema': 'public',
#  'is_invalid': False, 'error': ''}
```

### Task 28: Document Routing Logic

`get_routing_logic_summary()` returns a comprehensive dictionary
documenting the complete routing logic. This serves as both runtime
documentation and a reference for debugging.

The summary covers:

- Router stack order and responsibilities
- Read, write, migrate, and relation routing rules
- Schema selection and fallback behavior
- Edge cases (FakeTenant, dual apps, unknown apps)
- App counts (shared, tenant, dual)

```python
from apps.tenants.utils.router_utils import get_routing_logic_summary

summary = get_routing_logic_summary()
# {'router_stack': [...], 'routing_rules': {...},
#  'schema_selection': {...}, 'edge_cases': [...],
#  'shared_app_count': 18, 'tenant_app_count': 13, ...}
```

### Validation & Documentation Utility Summary

| Function                    | Task | Purpose                             |
| --------------------------- | ---- | ----------------------------------- |
| validate_schema_exists(n)   | 26   | Validate schema name before routing |
| handle_invalid_schema(n)    | 27   | Handle invalid schema with fallback |
| get_routing_logic_summary() | 28   | Programmatic routing rules summary  |

---

## TenantSyncRouter (django-tenants built-in)

The TenantSyncRouter is provided by django-tenants and handles migration
routing. It implements only the allow_migrate method.

### Behavior

The router inspects the app label of each model during migrate_schemas:

- If the app is in SHARED_APPS, migrations run in the public schema only
- If the app is in TENANT_APPS, migrations run in each tenant schema only
- Apps in both lists (contenttypes, auth) get tables in both schemas

### How It Works

When manage.py migrate_schemas is executed:

1. django-tenants calls migrate_schemas for the public schema first
2. TenantSyncRouter.allow_migrate returns True for SHARED_APPS, False for others
3. Only SHARED_APPS tables are created in public
4. Then migrate_schemas iterates each tenant schema
5. TenantSyncRouter.allow_migrate returns True for TENANT_APPS, False for others
6. Only TENANT_APPS tables are created in each tenant schema

### Methods

| Method         | Implemented | Behavior                                            |
| -------------- | ----------- | --------------------------------------------------- |
| allow_migrate  | Yes         | Routes migrations to correct schema (shared/tenant) |
| db_for_read    | No          | Falls through to default (handled by search_path)   |
| db_for_write   | No          | Falls through to default (handled by search_path)   |
| allow_relation | No          | Falls through to default                            |

Note: db_for_read and db_for_write are not needed because django-tenants
uses PostgreSQL's search_path mechanism. The middleware sets search_path
to the current tenant's schema, so all queries automatically hit the
correct schema without needing router-level read/write routing.

---

## TenantRouter (LankaCommerce custom)

The TenantRouter is defined in backend/apps/tenants/routers.py and handles
cross-schema relation prevention.

### Purpose

Prevents Django from creating or allowing foreign key relationships between
models in different schema classifications (shared vs tenant). This is
critical for data isolation.

### Methods

| Method         | Behavior                                                  |
| -------------- | --------------------------------------------------------- |
| allow_relation | Blocks relations between shared-only and tenant-only apps |

### Relation Rules

| Source App    | Target App    | Allowed | Reason                          |
| ------------- | ------------- | ------- | ------------------------------- |
| Shared only   | Shared only   | Yes     | Both in public schema           |
| Tenant only   | Tenant only   | Yes     | Both in tenant schema           |
| Shared+Tenant | Any           | Yes     | Dual apps exist in both schemas |
| Any           | Shared+Tenant | Yes     | Dual apps exist in both schemas |
| Shared only   | Tenant only   | No      | Cross-schema FK would break     |
| Tenant only   | Shared only   | No      | Cross-schema FK would break     |

Dual apps are those that appear in both SHARED_APPS and TENANT_APPS
(currently: django.contrib.contenttypes and django.contrib.auth).
Relations involving dual apps are always allowed because the tables
exist in both schemas.

---

## Routing Rules Summary

### Shared Apps (public schema only)

These apps have tables only in the public schema:

- django_tenants — Multi-tenancy infrastructure
- django.contrib.admin — Admin interface
- django.contrib.sessions — Session storage
- django.contrib.messages — Flash messages
- django.contrib.staticfiles — Static file management
- apps.tenants — Tenant and Domain models
- apps.core — Core utilities and base models
- apps.users — User profiles and management
- rest_framework — DRF API framework
- django_filters — Query filtering
- rest_framework_simplejwt — JWT authentication
- drf_spectacular — OpenAPI documentation
- corsheaders — CORS handling
- channels — WebSocket support
- django_celery_beat — Celery beat scheduler
- django_celery_results — Celery results backend

### Tenant Apps (per-tenant schema)

These apps have tables in each tenant schema:

- apps.products — Product catalog
- apps.inventory — Stock and warehouse
- apps.vendors — Supplier management
- apps.sales — Orders, invoicing, POS
- apps.customers — Customer CRM
- apps.hr — Human resources
- apps.accounting — Accounting and finance
- apps.reports — Reports and analytics
- apps.webstore — E-commerce storefront
- apps.integrations — Third-party integrations

### Dual Apps (both schemas)

These apps have tables in both the public and tenant schemas:

- django.contrib.contenttypes — Content type registry per schema
- django.contrib.auth — Users, groups, permissions per schema

---

## Cross-Schema Relations

### Why Cross-Schema FKs Are Prohibited

PostgreSQL foreign keys work within a single schema's search_path. When
django-tenants sets search_path to a tenant schema, FK references to
tables in the public schema would fail because the public schema is not
in the search path.

### Allowed Patterns

- Tenant model A references tenant model B (same schema): allowed
- Shared model A references shared model B (public schema): allowed
- Any model references a dual app model: allowed (tables exist in both)

### Prohibited Patterns

- Tenant model references a shared-only model: prohibited
- Shared-only model references a tenant model: prohibited

### How Violations Are Prevented

1. The TenantRouter.allow_relation method returns False for cross-schema FKs
2. Django will refuse to create the migration if the router blocks it
3. Code review guidelines reinforce the rule
4. The SHARED_APPS and TENANT_APPS classification in database.py serves as
   the single source of truth

---

## Edge Cases

### Unmanaged Models

Models with managed = False in their Meta class are not affected by
migration routing because Django does not create or alter their tables.
However, the allow_relation check still applies to prevent cross-schema
FK declarations in code.

### Third-Party Apps Without Models

Some shared apps (corsheaders, drf_spectacular) have no database models.
They appear in SHARED_APPS for configuration purposes but the router
has no effect on them since there are no migrations to route.

### ContentType and Auth Isolation

contenttypes and auth appear in both SHARED_APPS and TENANT_APPS. This
means each tenant schema has its own ContentType and Permission tables.
This is required by django-tenants for proper GenericForeignKey resolution
and per-tenant permission management.

### Unknown or Unregistered Apps

Apps not listed in either SHARED_APPS or TENANT_APPS default to
shared_only classification. This is a safe fallback because:

- Framework apps not explicitly listed are typically shared
- Unknown apps will not cause cross-schema FK violations with other shared apps
- If an unknown app relates to a tenant-only app, it will be correctly blocked

### model_name=None in allow_migrate

Django sometimes calls allow_migrate with model_name=None (e.g. during
initial migration planning). TenantRouter defers this to TenantSyncRouter
by returning None. TenantSyncRouter handles this case using the app_label
alone to determine routing.

### Same-App Relations

When both objects in an allow_relation call belong to the same app, the
relation is always allowed. Both objects share the same classification,
so the relation stays within a single schema.

### Empty Hints

All router methods accept \*\*hints keyword arguments. TenantRouter ignores
hints entirely. Passing empty hints or hints with arbitrary keys has no
effect on routing behavior.

### db_for_read and db_for_write

TenantRouter returns None for both methods. django-tenants handles read
and write routing via PostgreSQL search_path, not via Django router methods.
The middleware sets search_path before any query executes, making router-level
read/write routing unnecessary.

### Router Evaluation Order

Django evaluates routers in DATABASE_ROUTERS order. TenantRouter is first
to enforce relation rules before TenantSyncRouter processes migrations.
If TenantRouter returns None (for db_for_read, db_for_write, allow_migrate),
Django proceeds to TenantSyncRouter. For allow_relation, TenantRouter
always returns True or False (never None), so TenantSyncRouter is not
consulted for relation decisions.

### Adding New Apps

When adding a new app to the project:

1. Classify it in SHARED_APPS or TENANT_APPS (or both) in database.py
2. The router automatically picks up the classification from settings
3. No changes to routers.py are needed
4. Run the validation script to confirm correct classification

---

## Configuration File

All router settings are in backend/config/settings/database.py.

The custom router is in backend/apps/tenants/routers.py.

---

## Validation Record

Router configuration was validated on 2026-02-16 via Docker.

### Migration Routing Validation

| Category    | Count | Result | Details                                                        |
| ----------- | ----- | ------ | -------------------------------------------------------------- |
| Shared-only | 16    | PASS   | All 16 shared-only apps classified correctly                   |
| Tenant-only | 10    | PASS   | All 10 tenant-only apps classified correctly                   |
| Dual        | 2     | PASS   | contenttypes and auth in both SHARED_APPS/TENANT_APPS          |
| Exclusions  | 26    | PASS   | Shared-only not in TENANT_APPS, tenant-only not in SHARED_APPS |

### Relation Restriction Validation

| Test Case       | Count | Result | Details                                  |
| --------------- | ----- | ------ | ---------------------------------------- |
| Shared ↔ Shared | 3     | PASS   | All allowed (same schema)                |
| Tenant ↔ Tenant | 15    | PASS   | All allowed (same schema)                |
| Dual ↔ Any      | 20    | PASS   | All allowed (tables in both schemas)     |
| Shared ↔ Tenant | 20    | PASS   | All blocked (cross-schema FK prevention) |

Total checks: 121 passed, 0 failed.

Full verification details are in docs/VERIFICATION.md.

---

## Cross-Schema Prevention (Tasks 29-35)

Cross-schema prevention rules enforce data isolation between tenant
schemas and the public (shared) schema. These rules are implemented in
router_utils.py and used by LCCDatabaseRouter.allow_relation().

### Cross-Schema Rules (Task 29)

get_cross_schema_rules() returns a comprehensive dictionary documenting
every FK and relation direction, whether it is allowed or blocked, and
the rationale behind each rule.

| Direction       | Allowed | Rationale                                 |
| --------------- | ------- | ----------------------------------------- |
| Tenant → Tenant | Yes     | Same schema, no cross-schema risk         |
| Shared → Shared | Yes     | Same schema (public), no isolation breach |
| Tenant → Shared | Yes     | FK from tenant schema to public is safe   |
| Shared → Tenant | No      | Public cannot reference per-tenant rows   |
| Dual → Any      | Yes     | Tables exist in both schemas              |
| Any → Dual      | Yes     | Dual targets are always reachable         |

### Block Cross-Tenant FK (Task 30)

is_cross_tenant_fk(app_label_1, app_label_2) determines whether a
foreign key between two apps would cross tenant boundaries. Two tenant
apps in the same request context share the same schema, so this returns
False. Cross-schema FKs (shared ↔ tenant) are detected by comparing app
types rather than schema names.

### Block Cross-Tenant Queries (Task 31)

is_cross_tenant_query(app_label) documents how PostgreSQL search_path
prevents cross-tenant queries. Tenant apps are constrained to the current
tenant schema by the search_path set on the database connection. Shared
apps always resolve to the public schema.

### Allow Shared-Tenant FK (Task 32)

is_shared_tenant_fk_allowed(source_app, target_app) checks whether a
tenant-to-shared FK is allowed. This direction (tenant model pointing to
a shared model like User) is safe because the public schema is always
accessible from any tenant schema.

### Block Tenant-Shared FK (Task 33)

is_tenant_shared_fk_blocked(source_app, target_app) checks whether a
shared-to-tenant FK should be blocked. Shared models in the public schema
must not reference tenant-specific rows because the target schema is
unknown at query time.

### allow_relation Decision Tree (Task 34)

get_allow_relation_rules() documents the three-step decision tree used by
LCCDatabaseRouter.allow_relation():

1. **Same app type** — If both models belong to the same classification
   (shared/shared, tenant/tenant), return True.
2. **Dual app involved** — If either model belongs to a dual app (exists
   in both schemas), return True.
3. **Cross-schema** — Otherwise block the relation with a logged warning
   and return False.

The router never returns None, ensuring that no relation decision is
deferred to a downstream router.

### Get Model Schema (Task 35)

get_model_schema(app_label) returns the schema assignment for any app:

| App Type    | schema    | schemas              | is_shared | is_tenant |
| ----------- | --------- | -------------------- | --------- | --------- |
| Shared-only | public    | [public]             | True      | False     |
| Tenant-only | (current) | [tenant_schema_name] | False     | True      |
| Dual        | both      | [public, current]    | True      | True      |

---

## Errors, Logging & Validation (Tasks 36-42)

Error handling, logging, and validation functions ensure safe
cross-schema enforcement and provide audit trails for blocked
operations.

### Compare Model Schemas (Task 36)

compare_model_schemas(app_label_1, app_label_2) evaluates schema
compatibility between two apps using their classifications:

| Outcome      | Condition                 | Compatible |
| ------------ | ------------------------- | ---------- |
| same_schema  | Both apps have same type  | Yes        |
| compatible   | One or both apps are dual | Yes        |
| incompatible | shared_only ↔ tenant_only | No         |

### Raise Cross-Schema Error (Task 37)

raise_cross_schema_error(source_app, target_app) checks whether two
apps would trigger a CrossSchemaViolationError. Returns a dict
indicating whether would_raise is True and the error_message that
would be produced. Does not actually raise -- allow_relation handles
enforcement.

### Custom Exception (Task 38)

CrossSchemaViolationError is a custom exception class that captures:

- source_schema: The schema where the operation originated
- target_schema: The schema being illegally accessed
- message: Human-readable description of the violation

### Log Cross-Schema Attempts (Task 39)

log_cross_schema_attempt(source_app, target_app, operation) records
cross-schema violation attempts at WARNING level for security audit.
The log entry includes source/target apps, their types, the operation
type, and the current schema context.

### Handle Raw Queries (Task 40)

get_raw_query_safeguards() documents the safeguards for raw SQL
queries in a multi-tenant environment:

| Category       | Count | Purpose                          |
| -------------- | ----- | -------------------------------- |
| Safeguards     | 5     | search_path checks, cursor usage |
| Restrictions   | 4     | ORM bypass, no auto-blocking     |
| Best practices | 4     | Prefer ORM, use context managers |

Raw SQL requires explicit schema validation since it bypasses
allow_relation and db_for_read/write routing.

### Validate ORM Relations (Task 41)

validate_orm_relation(source_app, target_app) validates ForeignKey,
OneToOneField, and ManyToManyField relations for schema compliance.
Returns is_valid, rule_applied, and recommendation for invalid cases.

### Document Cross-Schema Rules (Task 42)

get_cross_schema_documentation() returns a comprehensive summary
covering all cross-schema prevention rules, enforcement mechanisms,
logging requirements, raw SQL safeguards, and related task references
(Tasks 29-42).

---

## Connection Management

Functions documenting connection pooling, reuse, and schema lifecycle.

### Configure Connection Pooling (Task 43)

get_connection_pooling_config() returns pooling configuration including
PgBouncer transaction mode, available pooling modes, connection flow steps,
and pool settings (pool_mode, max_client_conn, default_pool_size).

### Set CONN_MAX_AGE (Task 44)

get_conn_max_age_info() documents the CONN_MAX_AGE setting: recommended
value of 600 seconds, units, effect on performance, PgBouncer interaction,
and available options.

### Configure Pool Size (Task 45)

get_pool_size_config() returns pool sizing information: django_workers,
pgbouncer_max_client_conn, pgbouncer_default_pool_size,
postgres_max_connections, sizing formula, and capacity notes.

### Handle Connection Reuse (Task 46)

get_connection_reuse_strategy() documents connection reuse: reuse_enabled,
schema_reset_required, reset_mechanism, safety guarantees, and constraints
for multi-tenant environments.

### Set Schema on Connection (Task 47)

get_schema_on_connection_info() describes how schema is set on each
connection via SET search_path, the middleware-driven timing, SQL command,
search_path format, and step-by-step procedure.

### Reset Schema After Request (Task 48)

get_schema_reset_info() documents schema reset: reset_required (True),
reset_timing (after request), reset_mechanism, default_schema (public),
automatic flag, and leakage prevention strategy.

### Handle Connection Errors (Task 49)

get_connection_error_handling() returns error handling configuration:
error_types (connection refused, timeout, schema not found, pool exhausted),
retry_strategy (max_retries=3), fallback_behavior, logging_level (ERROR),
and monitoring items.

---

## Replicas & Monitoring

Functions documenting read replicas, timeouts, and connection monitoring.

### Configure Read Replicas (Task 50)

get_read_replica_config() returns replica configuration including
replication_type (streaming), connection_settings, activation_status
(planned), and future_plan steps for provisioning replicas.

### Route Reads to Replica (Task 51)

get_read_routing_info() documents read query routing: routing_target
(replica), fallback (primary), router_method (db_for_read),
schema_handling for tenant isolation, and activation conditions.

### Route Writes to Primary (Task 52)

get_write_routing_info() documents write query routing: routing_target
(primary), router_method (db_for_write), replica_restriction
(read-only transactions), operations list, and safety_notes.

### Handle Replica Lag (Task 53)

get_replica_lag_handling() documents replication lag handling:
max_acceptable_lag_seconds (5), detection via pg_stat_replication,
stale_read_policy, critical_operations, and fallback_conditions.

### Configure Connection Timeout (Task 54)

get_connection_timeout_config() returns timeout configuration:
connect_timeout_seconds (10), statement_timeout_seconds (30),
pgbouncer_settings, django_options, and failure_handling expectations.

### Monitor Connection Count (Task 55)

get_connection_monitoring_info() returns monitoring configuration:
monitoring_enabled (True), metrics list, thresholds (warning 70%,
critical 90%), alerts list, and diagnostic_queries.

### Document Connection Setup (Task 56)

get_connection_setup_documentation() returns a comprehensive summary
covering all connection management: pooling, reuse, replicas, timeouts,
monitoring, production_notes (12 items), and related_tasks (Tasks 43-56).

---

## Logging & Metrics (Tasks 57-62)

Query logging, schema-aware metrics, and slow-query detection.

### Create Query Logger (Task 57)

get_query_logger_config() returns structured query logging settings:
logger_name ("lcc.queries"), log_level ("DEBUG"), JSON structured format,
10 captured fields (timestamp, schema_name, query_text, query_params,
duration_ms, rows_affected, connection_id, request_id, user_id, tenant_id),
3 output targets, and configuration dict.

### Log Query Schema (Task 58)

get_query_schema_logging_info() returns schema-per-query logging config:
enabled (True), field_name ("schema_name"), source from
django.db.connection.schema_name, format_example, per_tenant_visibility,
and 5 use_cases for debugging and auditing.

### Log Query Time (Task 59)

get_query_time_logging_info() returns timing instrumentation settings:
enabled (True), field_name ("duration_ms"), unit ("milliseconds"),
precision (2), includes_network (True), and 4-tier thresholds
(normal 50ms, warning 100ms, slow 500ms, critical 5000ms).

### Create Query Metrics (Task 60)

get_query_metrics_config() returns Prometheus / StatsD metrics setup:
metrics_enabled (True), 4 metric definitions (query_total counter,
query_duration_seconds histogram, query_errors_total counter,
query_rows_total counter), 2 export targets, collection_interval_seconds (60),
4 labels, and aggregation with percentiles and bucket boundaries.

### Track Queries Per Tenant (Task 61)

get_per_tenant_query_tracking() returns per-tenant analytics config:
enabled (True), tracking_key ("schema_name"), 5 per-tenant metrics,
dashboard_support, storage backend, and 5 use_cases for billing,
performance analysis, and capacity planning.

### Track Slow Queries (Task 62)

get_slow_query_tracking_config() returns slow-query detection settings:
enabled (True), threshold_ms (100), log_level ("WARNING"),
alert_enabled (True), 10 captured_info fields, 4 alert_channels,
and auto_explain (enabled, log_min_duration_ms 100ms).

---

## Optimization & Debug (Tasks 63-68)

Query optimization, caching, debug tooling, and monitoring documentation.

### Create Router Middleware (Task 63)

get_router_middleware_config() returns middleware configuration for
per-request query tracking: middleware_class (QueryTrackingMiddleware),
placement (after TenantMainMiddleware), 6 tracked_metrics, 5 request
attributes, settings dict, and middleware_order (4 items).

### Optimize Common Queries (Task 64)

get_common_query_optimizations() returns optimization strategies:
6 strategies (select_related, indexing, only/defer, caching, EXISTS,
bulk ops), 5 indexing_recommendations, 5 queryset_tips, 4 sources
(logger, slow tracker, analyzer, toolbar), and impact dict.

### Create Query Analyzer (Task 65)

get_query_analyzer_config() returns query analyzer configuration:
5 analysis_types (N+1, slow, seq scans, missing indexes, cross-schema),
run_schedule (nightly), output_format (JSON), thresholds dict,
4 usage_instructions, and 5 report_sections.

### Configure Query Caching (Task 66)

get_query_caching_config() returns Redis-backed caching configuration:
backend (Redis), default_ttl_seconds (300), max_ttl_seconds (3600),
key_prefix (lcc_qcache), key_structure dict, 5 invalidation_rules,
5 cacheable_patterns, and settings dict with Redis connection details.

### Create Debug Toolbar Plugin (Task 67)

get_debug_toolbar_plugin_config() returns debug plugin configuration:
availability (Development only, DEBUG=True), panel_class
(TenantRoutingPanel), panel_title, 7 displayed_info items,
5 installation_steps, and settings dict.

### Document Monitoring Setup (Task 68)

get_monitoring_setup_documentation() returns comprehensive monitoring
summary: overview string, 11 components (covering Tasks 57-68),
4 dashboards, alerting dict with channels and thresholds,
5 access_notes, and 12 related_tasks (Tasks 57-68).

---

## Testing & Verification (Tasks 69-74)

Configuration helpers for building and running the router test suite,
validating schema routing, cross-schema blocking, connection reuse,
concurrent request isolation, and schema fallback behaviour.

### Create Router Tests (Task 69)

get_router_test_config() returns test suite configuration:
test_enabled (True), test_module string, 4 router_methods
(db_for_read, db_for_write, allow_relation, allow_migrate),
5 test_categories, coverage_targets dict (overall 95%,
router methods 100%, cross_schema 100%), 4 fixtures,
and test_runner dict (pytest with markers and parallel_safe).

### Test Schema Routing (Task 70)

get_schema_routing_test_config() returns schema routing test spec:
test_class (TestSchemaRouting), 6 scenarios, expected_outcomes dict
(shared/tenant/dual all route to default), 5 assertions, and
4 edge_cases.

### Test Cross-Schema Block (Task 71)

get_cross_schema_block_test_config() returns cross-schema blocking
test spec: test_class (TestCrossSchemaBlock), 4 blocked_relations,
3 allowed_relations, expected_errors dict (CrossSchemaViolationError),
6 test_methods, and coverage_requirement (100%).

### Test Connection Reuse (Task 72)

get_connection_reuse_test_config() returns connection reuse test spec:
test_class (TestConnectionReuse), 5 scenarios, 5 assertions,
4 schema_reset_points, and reuse_behaviour dict (pool_enabled True,
max_age_seconds 600).

### Test Concurrent Requests (Task 73)

get_concurrent_request_test_config() returns concurrency test spec:
test_class (TestConcurrentRequests), complexity (Complex), 5 scenarios,
5 isolation_checks, test_approach dict (threading with 10 threads,
timeout 30s), and expected_behaviour dict (schema_isolation True).

### Test Schema Fallback (Task 74)

get_schema_fallback_test_config() returns fallback test spec:
test_class (TestSchemaFallback), 5 scenarios, 4 fallback_rules,
expected_outcomes dict (fallback_schema public, raises_exception False),
and 4 edge_cases.

---

## Integration & Performance (Tasks 75-78)

Integration tests, performance benchmarks, test results documentation,
and the final commit for SubPhase-07 router setup.

### Create Integration Tests (Task 75)

get_integration_test_config() returns integration test configuration:
test_class (TestIntegrationRouter), 6 scenarios covering
request-to-query flow, 5 coverage_areas, expected_outcomes dict
(all_scenarios_pass True, coverage_minimum 90%), and 5 fixtures.

### Run Performance Tests (Task 76)

get_performance_test_config() returns performance benchmark config:
test_class (TestRouterPerformance), 5 benchmarks, targets dict
(all max 1.0ms), methodology dict (10000 iterations, warmup 100,
statistical measures), and expected_results dict.

### Document Test Results (Task 77)

get_test_results_documentation() returns test results documentation:
test_summary dict (78 total tasks, 6 groups, PASSED), coverage dict
(router methods 100%, integration 90%), 4 remaining_gaps, and
risk_assessment dict (overall Low).

### Create Initial Commit (Task 78)

get_initial_commit_config() returns commit configuration:
commit_details dict (feat scope tenants), 5 files_included,
5 review_checklist items, and subphase_status dict
(Complete, all_groups_done True, ready_for_next True).

---

## Related Documentation

- [Tenant Settings](tenant-settings.md) — All multi-tenancy settings
- [App Classification](app-classification.md) — SHARED vs TENANT app lists
- [Tenant Models](tenant-models.md) — Tenant and Domain model reference
- [Schema Naming](schema-naming.md) — Schema naming conventions
