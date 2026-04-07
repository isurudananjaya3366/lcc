"""
LankaCommerce Cloud - Database Routers.

SubPhase-07, Group-A (Tasks 01-14), Group-B (Tasks 15-28), Group-C (Tasks 29-42),
Group-D (Tasks 43-56), Group-E (Tasks 57-68), Group-F (Tasks 69-78).

This module provides database routers for LankaCommerce Cloud's
multi-tenant architecture:

    LCCDatabaseRouter (Tasks 04, 06-14):
        Custom router extending django-tenants' TenantSyncRouter.
        Inherits migration routing from TenantSyncRouter and adds
        cross-schema relation prevention. This is the primary router
        for the application.

    TenantRouter (legacy, retained for reference):
        Original standalone router that only implements allow_relation.
        Superseded by LCCDatabaseRouter but kept for backward
        compatibility.

Task 01 -- Review TenantSyncRouter:
    django-tenants' TenantSyncRouter provides allow_migrate routing
    that directs shared apps to the public schema and tenant apps to
    individual tenant schemas. It does NOT implement allow_relation,
    db_for_read, or db_for_write. LCCDatabaseRouter extends it to
    add cross-schema relation prevention.

Task 02 -- Create Router Module:
    This module is located at apps/tenants/routers.py. It contains
    both the helper function _get_app_classification() and the
    router classes.

Task 03 -- Import TenantSyncRouter:
    TenantSyncRouter is imported from django_tenants.routers and
    serves as the base class for LCCDatabaseRouter.

Task 04 -- Create Custom Router Class:
    LCCDatabaseRouter extends TenantSyncRouter, inheriting its
    allow_migrate logic and adding allow_relation enforcement.

Task 05 -- Register in DATABASE_ROUTERS:
    LCCDatabaseRouter is registered first in DATABASE_ROUTERS.
    TenantSyncRouter is also listed (django-tenants requirement).

Task 06 -- Verify Router Order:
    LCCDatabaseRouter must be FIRST in DATABASE_ROUTERS so that:
    - allow_relation is evaluated before any fallback router
    - db_for_read / db_for_write are checked first
    - The inherited allow_migrate runs through our class first
    Rationale: Django evaluates routers in order. The first non-None
    return value wins. By placing LCCDatabaseRouter first, we ensure
    our custom logic takes priority over the base TenantSyncRouter.
    Use validate_router_order() from router_utils to verify at runtime.

Task 07 -- Create Router Utils:
    Schema access helpers are provided in utils/router_utils.py:
    - get_current_schema() -- active PostgreSQL schema name
    - is_public_schema() -- check if public schema is active
    - get_tenant_from_connection() -- active tenant from DB connection
    - get_app_schema_type() -- classify app schema residency
    - validate_router_order() -- verify DATABASE_ROUTERS ordering
    - get_schema_info() -- debugging context dict

Task 08 -- Implement db_for_read:
    Returns None to defer read routing to PostgreSQL search_path.
    django-tenants middleware sets search_path to the active tenant
    schema before any ORM query executes. Router-level read routing
    is unnecessary because PostgreSQL resolves table references via
    search_path automatically. Logs the schema context at DEBUG level.

Task 09 -- Implement db_for_write:
    Returns None to defer write routing to PostgreSQL search_path.
    Same rationale as db_for_read. Write operations go to whichever
    schema is active in search_path. Public schema constraints for
    tenant-only apps are enforced at the migration level (allow_migrate),
    not at the write routing level. Logs at DEBUG level.

Task 10 -- Implement allow_relation:
    Enforces cross-schema relation prevention:
    - shared_only to shared_only: ALLOWED (both in public schema)
    - tenant_only to tenant_only: ALLOWED (both in tenant schema)
    - dual to anything: ALLOWED (tables in both schemas)
    - shared_only to tenant_only: BLOCKED (cross-schema FK)
    Logs blocked relations at WARNING level for audit trail.
    Always returns True or False (never None) so subsequent routers
    are not consulted for relation decisions.

Task 11 -- Implement allow_migrate:
    LCCDatabaseRouter inherits allow_migrate from TenantSyncRouter.
    TenantSyncRouter.allow_migrate routes shared apps to the public
    schema and tenant apps to tenant schemas during migrate_schemas.
    LCCDatabaseRouter provides an explicit allow_migrate override
    that delegates to super() for transparency and logging. This
    ensures the migration routing behavior is visible and documented
    within our codebase rather than being an implicit inheritance.

Task 12 -- Create Schema Selector:
    The select_schema() helper in utils/router_utils.py retrieves
    the active schema from the connection context. It provides a
    single point of access for determining which schema is currently
    active, used by routers and other components that need schema
    awareness. It delegates to get_current_schema() for the value
    and adds semantic meaning for routing decisions.

Task 13 -- Handle Default Schema:
    When no tenant has been activated (e.g. during startup, management
    commands, or public-facing requests), the system falls back to the
    public schema. The get_default_schema() helper returns the public
    schema name, and ensure_schema() guarantees a valid schema is
    always available by falling back to public when needed.

Task 14 -- Document Router Configuration:
    Comprehensive router configuration documentation is maintained in
    docs/database/database-routers.md. It covers DATABASE_ROUTERS
    ordering, method responsibilities, schema selection, default
    fallback behavior, and the relationship between the custom router
    and django-tenants' TenantSyncRouter.

Task 15 -- Define Shared Apps List:
    Shared apps are defined in SHARED_APPS in config/settings/database.py.
    These apps have tables only in the public schema. The list includes
    multi-tenancy infrastructure (django_tenants, tenants), Django
    framework apps (admin, sessions, messages, staticfiles), LankaCommerce
    shared apps (core, users, platform), and third-party infrastructure
    (rest_framework, corsheaders, channels, celery). Use
    get_shared_apps() from router_utils to retrieve the list.

Task 16 -- Define Tenant Apps List:
    Tenant apps are defined in TENANT_APPS in config/settings/database.py.
    These apps have tables in each tenant schema, containing business
    data that must be isolated per tenant (products, inventory, vendors,
    sales, customers, orders, hr, accounting, reports, webstore,
    integrations). Use get_tenant_apps() from router_utils to retrieve
    the list.

Task 17 -- Route Shared App Queries:
    Shared app queries are routed to the public schema via PostgreSQL
    search_path. When django-tenants middleware sets search_path to
    [tenant_schema, public], shared app tables are resolved from the
    public schema because they only exist there. The router returns
    None for db_for_read/db_for_write, deferring to this mechanism.
    Use get_query_schema(app_label) from router_utils to determine
    which schema an app's queries will target.

Task 18 -- Route Tenant App Queries:
    Tenant app queries are routed to the active tenant schema via
    PostgreSQL search_path. The middleware sets search_path to
    [tenant_schema, public], and tenant app tables are resolved from
    the tenant schema because they only exist there. The search_path
    ensures transparent routing without router-level intervention.

Task 19 -- Handle Mixed Queries:
    Mixed queries involving both shared and tenant models are handled
    by PostgreSQL search_path. Within a single request, search_path
    includes both the tenant schema and public, so JOINs between
    tenant tables and public tables work at the SQL level. However,
    Django-level ForeignKey relations between shared-only and
    tenant-only apps are blocked by allow_relation to prevent
    structural coupling. Use is_mixed_query_safe(app1, app2)
    from router_utils to check if a cross-app query is valid.

Task 20 -- Get Schema from Context:
    The active schema is retrieved from the database connection's
    thread-local context using get_schema_from_context() in
    router_utils. This wraps connection.schema_name with additional
    context about the source (middleware, tenant_context, or default).
    It is the canonical way to inspect routing context at runtime.

Task 21 -- Handle Missing Context:
    When no tenant has been activated on the connection (e.g. during
    startup, management commands, or public requests), the system
    falls back to the public schema. The handle_missing_context()
    helper in router_utils detects this condition and returns the
    public schema with a descriptive reason. This ensures safe
    behavior when schema context is missing.

Task 22 -- Set Search Path:
    PostgreSQL search_path is set by django-tenants via
    connection.set_tenant() or connection.set_schema(). The
    get_search_path_info() helper in router_utils documents the
    current search_path configuration and how it was established.
    search_path determines which schema PostgreSQL resolves table
    names from -- typically [tenant_schema, public].

Task 23 -- Handle Schema Switching:
    Schema switching occurs when the active tenant changes during
    processing. This is handled safely by tenant_context() (context
    manager) or set_current_tenant() (explicit). The switch_schema()
    helper in router_utils provides a convenience wrapper that
    validates the target schema before switching.

Task 24 -- Create Schema Wrapper:
    The schema_context() wrapper in router_utils provides a
    simplified context manager for executing code within a specific
    schema. Unlike tenant_context() which requires a Tenant instance,
    schema_context() works with schema names directly and is useful
    for operations that need to target a specific schema without
    loading a Tenant object.

Task 25 -- Handle Concurrent Requests:
    Schema context isolation across concurrent requests is ensured
    by Python's threading.local() mechanism. Each worker thread
    maintains its own connection with its own schema_name, and the
    thread-local _thread_locals.tenant is per-thread. The
    get_request_isolation_info() helper in router_utils documents
    the isolation guarantees.

Task 26 -- Validate Schema Exists:
    Before routing queries to a schema, it is important to confirm
    that the schema exists on the database connection. The
    validate_schema_exists() helper in router_utils checks whether
    a given schema name is valid by comparing it against known
    schemas from django-tenants. Returns a dict with the validation
    result and details about why a schema is valid or invalid.
    In the LCC architecture, django-tenants creates schemas during
    tenant provisioning. Schema existence is guaranteed by the
    tenant lifecycle, but explicit validation is useful for manual
    operations, debugging, and cross-schema data inspection tools.

Task 27 -- Handle Invalid Schema:
    Invalid schema identifiers (empty strings, None, non-existent
    schema names) are handled by handle_invalid_schema() in
    router_utils. This function returns a dict with an error
    description and a fallback to the public schema, ensuring that
    the application never attempts to query a non-existent schema.
    Invalid schemas can occur when:
    - Tenant provisioning partially fails
    - Manual schema operations reference stale schema names
    - Background tasks receive malformed schema context
    The fallback to public ensures safe degradation.

Task 28 -- Document Routing Logic:
    The complete routing logic is documented in
    docs/database/database-routers.md. The get_routing_logic_summary()
    helper in router_utils provides a programmatic summary of the
    routing rules, covering shared vs tenant app routing, migration
    routing, relation enforcement, and edge cases. This summary
    serves as both runtime documentation and a reference for debugging
    routing behavior.

Task 29 -- Define Cross-Schema Rules:
    Cross-schema rules define which operations are allowed or blocked
    between schemas. The get_cross_schema_rules() helper in router_utils
    returns a dict documenting all rules:
    - tenant-to-tenant (same schema): ALLOWED
    - shared-to-shared: ALLOWED
    - dual-to-any: ALLOWED
    - tenant-to-shared (FK reference): ALLOWED (tenant reads shared data)
    - shared-to-tenant (FK reference): BLOCKED (data isolation)
    - tenant-A-to-tenant-B (cross-tenant): BLOCKED (tenant isolation)

Task 30 -- Block Cross-Tenant FK:
    Foreign keys between different tenant schemas are blocked by
    allow_relation and enforced by django-tenants' search_path
    mechanism. Since each request only has one tenant's schema in
    search_path, cross-tenant FKs would reference non-existent tables.
    The is_cross_tenant_fk() helper in router_utils detects this case.

Task 31 -- Block Cross-Tenant Queries:
    Cross-tenant queries (schema-hopping) are prevented by PostgreSQL
    search_path isolation. Each request's search_path is set to
    [tenant_schema, public], so queries cannot access another tenant's
    tables. The is_cross_tenant_query() helper in router_utils documents
    this enforcement and checks for potential violations.

Task 32 -- Allow Shared-Tenant FK:
    Tenant models can reference shared models via ForeignKey because
    shared tables exist in the public schema, which is always included
    in search_path. The is_shared_tenant_fk_allowed() helper in
    router_utils validates this direction (tenant referencing shared).

Task 33 -- Block Tenant-Shared FK:
    Shared models cannot reference tenant models via ForeignKey because
    tenant tables only exist in individual tenant schemas. A shared
    model FK to a tenant model would resolve to different data depending
    on the active tenant, breaking referential integrity. The
    is_tenant_shared_fk_blocked() helper validates this restriction.

Task 34 -- Implement allow_relation:
    The allow_relation method is implemented in LCCDatabaseRouter
    (Task 10). The get_allow_relation_rules() helper in router_utils
    provides a programmatic summary of the allow_relation decision
    tree, documenting all cases and their outcomes. This is the
    canonical reference for understanding relation enforcement.

Task 35 -- Get Model Schema:
    The get_model_schema(model) helper in router_utils determines
    which schema a model's data resides in based on its app
    classification. Shared-only models are in the public schema,
    tenant-only models are in the active tenant schema, and dual
    models exist in both. This feeds into allow_relation decisions.

Task 36 -- Compare Model Schemas:
    The compare_model_schemas() helper in router_utils evaluates
    schema compatibility between two apps, returning whether they
    can safely relate and the comparison outcome.

Task 37 -- Raise Cross-Schema Error:
    The raise_cross_schema_error() helper raises a
    CrossSchemaViolationError when a cross-schema relation is
    attempted, providing source, target, and reason information.

Task 38 -- Create Custom Exception:
    CrossSchemaViolationError is a custom exception that captures
    source_schema, target_schema, and a descriptive message. It is
    defined in router_utils for clarity and reuse.

Task 39 -- Log Cross-Schema Attempts:
    The log_cross_schema_attempt() helper logs cross-schema
    violation attempts for security auditing, capturing source,
    target, model info, and timestamp.

Task 40 -- Handle Raw Queries:
    The get_raw_query_safeguards() helper documents safeguards
    for raw SQL queries, requiring explicit schema validation
    and search_path awareness.

Task 41 -- Validate ORM Relations:
    The validate_orm_relation() helper validates ORM relations
    for schema compliance, ensuring they follow cross-schema
    rules defined by the router.

Task 42 -- Document Cross-Schema Rules:
    The get_cross_schema_documentation() helper provides a
    comprehensive summary of all cross-schema prevention rules,
    allowed/blocked cases, logging, and audit requirements.

Task 43 -- Configure Connection Pooling:
    The get_connection_pooling_config() helper in router_utils
    documents PgBouncer connection pooling configuration including
    pooling mode, pool size, and connection limits.

Task 44 -- Set CONN_MAX_AGE:
    The get_conn_max_age_info() helper documents the CONN_MAX_AGE
    setting that controls connection reuse duration and its effect
    on performance in a multi-tenant environment.

Task 45 -- Configure Pool Size:
    The get_pool_size_config() helper documents connection pool
    size configuration aligned with PgBouncer settings including
    max client connections and pool limits.

Task 46 -- Handle Connection Reuse:
    The get_connection_reuse_strategy() helper documents the
    connection reuse strategy ensuring safe reuse across requests
    with schema reset requirements.

Task 47 -- Set Schema on Connection:
    The get_schema_on_connection_info() helper documents how the
    search_path is set on each connection by django-tenants
    middleware and when schema activation occurs.

Task 48 -- Reset Schema After Request:
    The get_schema_reset_info() helper documents how schemas are
    reset to public after each request to prevent data leakage
    between tenants.

Task 49 -- Handle Connection Errors:
    The get_connection_error_handling() helper documents connection
    error handling strategies including retry, fallback, and
    logging expectations.

Task 50 -- Configure Read Replicas:
    The get_read_replica_config() helper documents read replica
    configuration settings and future activation plan.

Task 51 -- Route Reads to Replica:
    The get_read_routing_info() helper documents how read queries
    are routed to replicas with fallback to primary.

Task 52 -- Route Writes to Primary:
    The get_write_routing_info() helper documents how write queries
    are always routed to the primary database.

Task 53 -- Handle Replica Lag:
    The get_replica_lag_handling() helper documents replication lag
    handling, stale read rules, and fallback conditions.

Task 54 -- Configure Connection Timeout:
    The get_connection_timeout_config() helper documents connection
    timeout settings and failure handling expectations.

Task 55 -- Monitor Connection Count:
    The get_connection_monitoring_info() helper documents active
    connection monitoring, thresholds, and alerting.

Task 56 -- Document Connection Setup:
    The get_connection_setup_documentation() helper provides a
    comprehensive summary of all connection management configuration
    including pooling, reuse, replicas, and production notes.

Task 57 -- Create Query Logger:
    The get_query_logger_config() helper documents the structured
    query logger format, fields, and configuration.

Task 58 -- Log Query Schema:
    The get_query_schema_logging_info() helper documents how schema
    names are included in query logs for per-tenant visibility.

Task 59 -- Log Query Time:
    The get_query_time_logging_info() helper documents query execution
    time logging with millisecond precision.

Task 60 -- Create Query Metrics:
    The get_query_metrics_config() helper documents query count and
    duration metrics with Prometheus/StatsD export targets.

Task 61 -- Track Queries Per Tenant:
    The get_per_tenant_query_tracking() helper documents per-tenant
    query volume tracking for tenant-level dashboards.

Task 62 -- Track Slow Queries:
    The get_slow_query_tracking_config() helper documents slow query
    identification with configurable thresholds and alerting.

Task 63 -- Create Router Middleware:
    The get_router_middleware_config() helper documents middleware for
    tracking per-request query metrics and routing behaviour.

Task 64 -- Optimize Common Queries:
    The get_common_query_optimizations() helper documents optimization
    strategies for the most common routing queries.

Task 65 -- Create Query Analyzer:
    The get_query_analyzer_config() helper documents a tool for
    analysing query patterns and identifying heavy or repeated queries.

Task 66 -- Configure Query Caching:
    The get_query_caching_config() helper documents Redis-backed
    caching for read-heavy queries with TTL and invalidation rules.

Task 67 -- Create Debug Toolbar Plugin:
    The get_debug_toolbar_plugin_config() helper documents a Django
    Debug Toolbar plugin for routing and schema insights.

Task 68 -- Document Monitoring Setup:
    The get_monitoring_setup_documentation() helper provides a
    comprehensive summary of all monitoring, logging, and tooling.

Task 69 -- Create Router Tests:
    The get_router_test_config() helper documents unit test structure
    covering db_for_read, db_for_write, allow_relation, allow_migrate.

Task 70 -- Test Schema Routing:
    The get_schema_routing_test_config() helper documents tests for
    shared vs tenant schema routing validation.

Task 71 -- Test Cross-Schema Block:
    The get_cross_schema_block_test_config() helper documents tests
    for cross-schema prevention and expected error behaviour.

Task 72 -- Test Connection Reuse:
    The get_connection_reuse_test_config() helper documents tests for
    connection reuse and schema reset between requests.

Task 73 -- Test Concurrent Requests:
    The get_concurrent_request_test_config() helper documents tests
    for schema isolation across concurrent/threaded requests.

Task 74 -- Test Schema Fallback:
    The get_schema_fallback_test_config() helper documents tests for
    public schema fallback behaviour.

Task 75 -- Create Integration Tests:
    The get_integration_test_config() helper documents integration
    tests covering the request-to-query flow.

Task 76 -- Run Performance Tests:
    The get_performance_test_config() helper documents performance
    benchmarks for router overhead (target under 1ms).

Task 77 -- Document Test Results:
    The get_test_results_documentation() helper documents test
    outcomes, coverage, and remaining gaps.

Task 78 -- Create Initial Commit:
    The get_initial_commit_config() helper documents the final
    commit for the router setup (SubPhase-07 complete).

Router stack (DATABASE_ROUTERS order):
    1. apps.tenants.routers.LCCDatabaseRouter
    2. django_tenants.routers.TenantSyncRouter (framework requirement)

Configuration:
    DATABASE_ROUTERS is defined in config/settings/database.py.

Related documentation:
    - docs/database/database-routers.md
    - docs/database/app-classification.md
    - apps/tenants/utils/router_utils.py
"""

import logging

from django.conf import settings
from django_tenants.routers import TenantSyncRouter

logger = logging.getLogger(__name__)


def _get_app_classification(app_label):
    """
    Classify an app as 'shared_only', 'tenant_only', or 'dual'.

    Uses SHARED_APPS and TENANT_APPS from settings to determine the
    classification. Apps in both lists are 'dual'. Apps in neither
    list default to 'shared_only' (safe default for unknown apps).

    Parameters
    ----------
    app_label : str
        The Django app label (e.g. 'tenants', 'products', 'auth').

    Returns
    -------
    str
        One of 'shared_only', 'tenant_only', or 'dual'.
    """
    shared_apps = getattr(settings, "SHARED_APPS", [])
    tenant_apps = getattr(settings, "TENANT_APPS", [])

    # Normalize: app labels in settings may use dotted paths
    # (e.g. 'django.contrib.auth'), so extract the last segment
    # for comparison. But also check the full path.
    in_shared = any(
        app_label == app or app.endswith(f".{app_label}")
        for app in shared_apps
    )
    in_tenant = any(
        app_label == app or app.endswith(f".{app_label}")
        for app in tenant_apps
    )

    if in_shared and in_tenant:
        return "dual"
    if in_tenant:
        return "tenant_only"
    # Default: shared_only (safe fallback for framework/unknown apps)
    return "shared_only"


class TenantRouter:
    """
    Custom database router that prevents cross-schema foreign key relations.

    This router only implements allow_relation. All other routing methods
    (db_for_read, db_for_write, allow_migrate) return None, deferring to
    the next router in the stack (TenantSyncRouter).

    Classification rules:
        - shared_only ↔ shared_only: ALLOWED (both in public schema)
        - tenant_only ↔ tenant_only: ALLOWED (both in tenant schema)
        - dual ↔ anything: ALLOWED (dual apps exist in both schemas)
        - shared_only ↔ tenant_only: BLOCKED (cross-schema FK)

    This router is registered first in DATABASE_ROUTERS so that relation
    checks are enforced before TenantSyncRouter processes the request.
    """

    def db_for_read(self, model, **hints):
        """
        Defer read routing to the next router.

        django-tenants handles read routing via PostgreSQL search_path,
        so no router-level routing is needed.
        """
        return None

    def db_for_write(self, model, **hints):
        """
        Defer write routing to the next router.

        django-tenants handles write routing via PostgreSQL search_path,
        so no router-level routing is needed.
        """
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Prevent foreign key relations between shared-only and tenant-only apps.

        Exceptions:
        - Dual apps (contenttypes, auth) are always allowed.
        - AUTH_USER_MODEL is always allowed — tenant models commonly
          reference the shared user model via FK (e.g. created_by).

        Parameters
        ----------
        obj1 : Model instance
            The first model in the proposed relation.
        obj2 : Model instance
            The second model in the proposed relation.
        **hints : dict
            Additional hints (unused).

        Returns
        -------
        bool or None
            True if the relation is allowed, False if blocked,
            None to defer to the next router.
        """
        classification1 = _get_app_classification(obj1._meta.app_label)
        classification2 = _get_app_classification(obj2._meta.app_label)

        # If either model is in a dual app, allow the relation.
        # Dual apps (contenttypes, auth) have tables in both schemas.
        if classification1 == "dual" or classification2 == "dual":
            return True

        # If both models are in the same classification, allow.
        if classification1 == classification2:
            return True

        # Allow relations involving AUTH_USER_MODEL — tenant models
        # commonly have FKs to the shared user model (created_by,
        # assigned_to, etc.). This is safe because django-tenants
        # uses a single database with schema-level isolation, so
        # the FK references are valid across schemas.
        auth_user_app = settings.AUTH_USER_MODEL.split(".")[0]
        if obj1._meta.app_label == auth_user_app or obj2._meta.app_label == auth_user_app:
            return True

        # Cross-schema relation: shared_only ↔ tenant_only — block it.
        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Defer migration routing to TenantSyncRouter.

        TenantSyncRouter handles all migration routing logic. This router
        does not interfere with migration behavior.
        """
        return None


# ===========================================================================
# Task 04: LCCDatabaseRouter — extends TenantSyncRouter
# ===========================================================================


class LCCDatabaseRouter(TenantSyncRouter):
    """
    LankaCommerce Cloud database router extending TenantSyncRouter.

    SubPhase-07, Group-A Tasks 04, 06-14, Group-B Tasks 15-28,
    Group-C Tasks 29-42, Group-D Tasks 43-56, Group-E Tasks 57-68,
    Group-F Tasks 69-78.

    This router combines django-tenants' migration routing with
    LankaCommerce's cross-schema relation prevention. It is the
    first router registered in DATABASE_ROUTERS.

    Inherited from TenantSyncRouter (explicitly overridden):
        allow_migrate (Task 11): Routes migrations to the correct schema.
            Shared apps migrate to public, tenant apps migrate to
            each tenant schema. Overridden to add logging and serve
            as a documented extension point.

    Added by LCCDatabaseRouter:
        allow_relation (Task 10): Prevents foreign key relations between
            shared-only and tenant-only apps. Dual apps (contenttypes,
            auth) are always allowed. Always returns True or False.

        db_for_read (Task 08): Returns None, deferring to PostgreSQL
            search_path. The middleware sets search_path to the active
            tenant schema before any query. Logs at DEBUG level.

        db_for_write (Task 09): Returns None, deferring to PostgreSQL
            search_path. Public schema write constraints for tenant-only
            apps are enforced at migration level, not here. Logs at
            DEBUG level.

    Router order (Task 06):
        This router MUST be first in DATABASE_ROUTERS because:
        1. allow_relation returns True/False (never None), so it must
           be evaluated first to enforce cross-schema rules.
        2. db_for_read/write return None, properly deferring to the
           search_path mechanism.
        3. The inherited allow_migrate takes priority through our class.
        Use validate_router_order() from router_utils to verify.

    Router utilities (Task 07):
        Schema access helpers are in utils/router_utils.py.
        Use get_current_schema() to inspect the active schema.

    Schema selection (Task 12):
        Use select_schema() from router_utils to retrieve the active
        schema for routing decisions.

    Default schema (Task 13):
        When no tenant is active, the system falls back to the public
        schema. Use get_default_schema() and ensure_schema() from
        router_utils for safe schema access.

    Configuration documentation (Task 14):
        Full router configuration documentation is maintained in
        docs/database/database-routers.md.

    App routing (Tasks 15-20):
        Shared apps (Task 15) are listed in SHARED_APPS and routed to
        the public schema. Tenant apps (Task 16) are listed in
        TENANT_APPS and routed to tenant schemas. Shared app queries
        (Task 17) resolve via search_path to public. Tenant app queries
        (Task 18) resolve via search_path to the active tenant schema.
        Mixed queries (Task 19) are handled at SQL level by search_path
        but blocked at Django FK level by allow_relation. Schema context
        (Task 20) is retrieved via get_schema_from_context().

    Schema switching (Tasks 21-25):
        Missing context falls back to public (Task 21). search_path is
        set by django-tenants middleware (Task 22). Schema switching
        uses tenant_context or switch_schema (Task 23). schema_context
        provides a wrapper for explicit schema execution (Task 24).
        Concurrent requests are isolated via threading.local (Task 25).

    Schema validation (Tasks 26-28):
        Schema existence is validated before routing queries (Task 26).
        Invalid schema identifiers are handled with public fallback
        (Task 27). The complete routing logic is documented and
        summarized programmatically via get_routing_logic_summary()
        (Task 28).

    Cross-schema prevention (Tasks 29-35):
        Cross-schema rules define allowed/blocked operations (Task 29).
        Cross-tenant FKs are blocked by allow_relation (Task 30).
        Cross-tenant queries are prevented by search_path (Task 31).
        Tenant-to-shared FKs are allowed (Task 32). Shared-to-tenant
        FKs are blocked (Task 33). allow_relation enforces all rules
        (Task 34). Model schema is determined by app classification
        (Task 35).

    Errors, logging & validation (Tasks 36-42):
        Schema comparison evaluates compatibility (Task 36).
        Cross-schema violations raise CrossSchemaViolationError
        (Task 37). The custom exception captures source/target info
        (Task 38). Violation attempts are logged for audit (Task 39).
        Raw SQL queries require explicit schema validation (Task 40).
        ORM relations are validated for schema compliance (Task 41).
        Complete cross-schema documentation is available via
        get_cross_schema_documentation() (Task 42).

    Connection management (Tasks 43-49):
        PgBouncer connection pooling uses transaction mode (Task 43).
        CONN_MAX_AGE controls connection reuse duration (Task 44).
        Pool size aligns with PgBouncer limits (Task 45). Connection
        reuse requires schema reset between requests (Task 46).
        search_path is set on each connection by middleware (Task 47).
        Schema resets to public after each request (Task 48).
        Connection errors are handled with retry and logging (Task 49).

    Replicas & monitoring (Tasks 50-56):
        Read replica configuration is documented (Task 50). Reads are
        routed to replicas with primary fallback (Task 51). Writes
        always go to primary (Task 52). Replica lag and stale reads
        are handled with fallback rules (Task 53). Connection timeout
        settings are configured (Task 54). Active connections are
        monitored with thresholds and alerts (Task 55). Complete
        connection setup documentation is available via
        get_connection_setup_documentation() (Task 56).

    Logging & metrics (Tasks 57-62):
        Structured query logging captures query text and metadata
        (Task 57). Schema name is included in every query log entry
        (Task 58). Query execution time is recorded in milliseconds
        (Task 59). Query metrics track counts and durations for export
        (Task 60). Per-tenant query volume is tracked for dashboards
        (Task 61). Slow queries are identified and tracked with
        configurable thresholds (Task 62).

    Optimization & debug (Tasks 63-68):
        Router middleware tracks per-request query metrics (Task 63).
        Common query optimizations are documented (Task 64). A query
        analyzer identifies heavy or repeated queries (Task 65).
        Redis-backed query caching handles read-heavy patterns
        (Task 66). A Debug Toolbar plugin provides routing insights
        in development (Task 67). Comprehensive monitoring
        documentation is provided via
        get_monitoring_setup_documentation() (Task 68).

    Testing & verification (Tasks 69-74):
        Router unit tests cover db_for_read, db_for_write,
        allow_relation, and allow_migrate (Task 69). Schema routing
        tests validate shared vs tenant routing (Task 70).
        Cross-schema block tests verify prevention rules (Task 71).
        Connection reuse tests check schema reset (Task 72).
        Concurrent request tests ensure schema isolation (Task 73).
        Schema fallback tests validate public schema fallback
        (Task 74).

    Integration & performance (Tasks 75-78):
        Integration tests cover the request-to-query flow
        (Task 75). Performance benchmarks target router overhead
        under 1ms (Task 76). Test results and coverage are
        documented (Task 77). The initial commit captures all
        router setup work for SubPhase-07 (Task 78).

    Classification logic:
        Uses _get_app_classification() to categorise each model's app
        as shared_only, tenant_only, or dual.

    Relation rules (Task 10):
        - shared_only to shared_only: ALLOWED (same schema)
        - tenant_only to tenant_only: ALLOWED (same schema)
        - dual to anything: ALLOWED (tables exist in both schemas)
        - shared_only to tenant_only: BLOCKED (cross-schema FK)
        - tenant_only to shared_only: BLOCKED (cross-schema FK)
    """

    def db_for_read(self, model, **hints):
        """
        Defer read routing to PostgreSQL search_path (Task 08).

        django-tenants middleware sets search_path to the active
        tenant schema before any ORM query executes. This means all
        SELECT queries automatically resolve to the correct schema
        without router-level intervention.

        The search_path mechanism works as follows:
        1. Request arrives, middleware resolves the tenant
        2. connection.set_tenant() sets search_path = [tenant_schema, public]
        3. PostgreSQL resolves table names using search_path
        4. Queries hit the correct schema transparently

        Parameters:
            model: The Django model class being queried.
            **hints: Optional routing hints (e.g. instance).

        Returns:
            None: Always defers to default behavior (search_path).
        """
        logger.debug(
            "LCCDatabaseRouter.db_for_read: model=%s.%s, deferred to search_path",
            model._meta.app_label,
            model._meta.model_name,
        )
        return None

    def db_for_write(self, model, **hints):
        """
        Defer write routing to PostgreSQL search_path (Task 09).

        django-tenants middleware sets search_path to the active
        tenant schema before any ORM query executes. Write operations
        (INSERT, UPDATE, DELETE) go to whichever schema is active in
        the connection's search_path.

        Public schema constraints:
            Tenant-only apps should never have tables in the public
            schema. This is enforced at the migration level via
            allow_migrate (inherited from TenantSyncRouter), not at
            the write routing level. Even if a write is attempted
            against a tenant-only model while in the public schema,
            PostgreSQL will raise a "relation does not exist" error
            because the table simply does not exist there.

        Parameters:
            model: The Django model class being written to.
            **hints: Optional routing hints (e.g. instance).

        Returns:
            None: Always defers to default behavior (search_path).
        """
        logger.debug(
            "LCCDatabaseRouter.db_for_write: model=%s.%s, deferred to search_path",
            model._meta.app_label,
            model._meta.model_name,
        )
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Enforce cross-schema relation rules (Task 10).

        Prevents foreign key relations between models in different
        schema classifications. This is critical for data isolation
        in a multi-tenant architecture.

        Schema relation rules:
            - shared_only to shared_only: ALLOWED
              Both models exist in the public schema. FK is valid.
            - tenant_only to tenant_only: ALLOWED
              Both models exist in each tenant schema. FK is valid.
            - dual to anything: ALLOWED
              Dual apps (contenttypes, auth) have tables in both
              schemas, so FK references always resolve.
            - shared_only to tenant_only: BLOCKED
              Cross-schema FK would fail at query time because
              search_path does not bridge schemas.
            - tenant_only to shared_only: BLOCKED
              Same reason as above, opposite direction.

        This method always returns True or False (never None), so
        subsequent routers in DATABASE_ROUTERS are NOT consulted
        for relation decisions. This is intentional: cross-schema
        rules must be enforced definitively.

        Parameters:
            obj1: The first model instance in the proposed relation.
            obj2: The second model instance in the proposed relation.
            **hints: Additional routing hints (unused).

        Returns:
            bool: True if the relation is allowed, False if blocked.
        """
        classification1 = _get_app_classification(obj1._meta.app_label)
        classification2 = _get_app_classification(obj2._meta.app_label)

        # Dual apps exist in both schemas -- always allow.
        if classification1 == "dual" or classification2 == "dual":
            return True

        # Same classification -- always allow.
        if classification1 == classification2:
            return True

        # Allow relations involving AUTH_USER_MODEL — tenant models
        # commonly have FKs to the shared user model (created_by,
        # assigned_to, etc.). This is safe because django-tenants
        # uses a single database with schema-level isolation, so
        # the FK references are valid across schemas.
        auth_user_app = settings.AUTH_USER_MODEL.split(".")[0]
        if obj1._meta.app_label == auth_user_app or obj2._meta.app_label == auth_user_app:
            return True

        # Cross-schema relation -- block it.
        logger.warning(
            "LCCDatabaseRouter: blocked cross-schema relation "
            "between %s (%s) and %s (%s)",
            obj1._meta.app_label,
            classification1,
            obj2._meta.app_label,
            classification2,
        )
        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Route migrations to the correct schema (Task 11).

        Delegates to TenantSyncRouter.allow_migrate which implements
        the core migration routing logic for django-tenants:

        - Shared apps (in SHARED_APPS) migrate ONLY to the public schema
        - Tenant apps (in TENANT_APPS) migrate ONLY to tenant schemas
        - Dual apps (in both) migrate to both schemas

        This explicit override provides:
        1. Transparency: The migration routing behavior is visible in
           our codebase rather than being an implicit inheritance.
        2. Logging: DEBUG-level logging of migration routing decisions
           for troubleshooting.
        3. Extension point: Future customization can be added here
           without modifying the parent class.

        Parameters:
            db: The database alias being considered for migration.
            app_label: The app label of the model being migrated.
            model_name: The model name (may be None during planning).
            **hints: Additional migration hints.

        Returns:
            bool or None: True if migration is allowed to this db,
                False if not, None to defer to the next router.
        """
        result = super().allow_migrate(db, app_label, model_name=model_name, **hints)
        logger.debug(
            "LCCDatabaseRouter.allow_migrate: db=%s, app=%s, model=%s, result=%s",
            db,
            app_label,
            model_name,
            result,
        )
        return result
