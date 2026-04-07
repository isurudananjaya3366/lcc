-- ==================================================
-- LankaCommerce Cloud - Schema Functions
-- ==================================================
-- File:    02-schema-functions.sql
-- Purpose: Helper functions for tenant schema
--          lifecycle management (create, verify,
--          cleanup). Used alongside django-tenants.
-- Runs:    Automatically on first container startup
--          (docker-entrypoint-initdb.d)
-- ==================================================

-- ---------------------------------------------------
-- 1. Tenant Schema Creation Helper
-- ---------------------------------------------------
-- django-tenants handles schema creation via its
-- Tenant model save() signal, but this function
-- provides a SQL-level helper for:
--   - Manual provisioning from psql or admin scripts
--   - Post-creation extension installation
--   - Verification of schema readiness
--
-- Parameters:
--   p_schema_name  — Full schema name (tenant_<slug>)
--
-- Returns: BOOLEAN (true if schema was created)
-- ---------------------------------------------------

CREATE OR REPLACE FUNCTION create_tenant_schema(p_schema_name TEXT)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    -- Validate naming convention
    IF p_schema_name !~ '^tenant_[a-z0-9][a-z0-9_]*$' THEN
        RAISE EXCEPTION 'Invalid tenant schema name: %. Must match tenant_<slug> pattern.', p_schema_name;
    END IF;

    -- Prevent reserved schema names
    IF p_schema_name IN ('tenant_public', 'tenant_pg_catalog', 'tenant_information_schema') THEN
        RAISE EXCEPTION 'Schema name % is reserved and cannot be used.', p_schema_name;
    END IF;

    -- Check if schema already exists
    IF EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = p_schema_name) THEN
        RAISE NOTICE 'Schema % already exists, skipping creation.', p_schema_name;
        RETURN FALSE;
    END IF;

    -- Create the schema
    EXECUTE format('CREATE SCHEMA %I', p_schema_name);

    -- Grant usage to the application user
    EXECUTE format('GRANT ALL ON SCHEMA %I TO lcc_user', p_schema_name);

    -- Set default privileges for future tables and sequences
    EXECUTE format(
        'ALTER DEFAULT PRIVILEGES IN SCHEMA %I GRANT ALL ON TABLES TO lcc_user',
        p_schema_name
    );
    EXECUTE format(
        'ALTER DEFAULT PRIVILEGES IN SCHEMA %I GRANT ALL ON SEQUENCES TO lcc_user',
        p_schema_name
    );

    RAISE NOTICE 'Tenant schema % created successfully.', p_schema_name;
    RETURN TRUE;
END;
$$;

-- ---------------------------------------------------
-- 2. Tenant Schema Existence Check
-- ---------------------------------------------------
-- Quick boolean check for whether a tenant schema
-- exists. Useful in application logic and scripts.
--
-- Parameters:
--   p_schema_name  — Full schema name to check
--
-- Returns: BOOLEAN
-- ---------------------------------------------------

CREATE OR REPLACE FUNCTION tenant_schema_exists(p_schema_name TEXT)
RETURNS BOOLEAN
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM pg_namespace WHERE nspname = p_schema_name
    );
END;
$$;

-- ---------------------------------------------------
-- 3. Tenant Schema Cleanup (Soft Delete)
-- ---------------------------------------------------
-- Renames a tenant schema to a "deleted" prefix
-- rather than dropping it immediately. This provides
-- a recovery window before permanent deletion.
--
-- Safeguards:
--   - Only schemas matching tenant_<slug> can be
--     renamed (prevents accidental public/system drops)
--   - The renamed schema is prefixed with _deleted_
--     and timestamped for traceability
--   - Actual DROP must be performed manually after
--     the recovery window expires
--
-- Parameters:
--   p_schema_name  — Full schema name (tenant_<slug>)
--
-- Returns: TEXT (new schema name after rename)
-- ---------------------------------------------------

CREATE OR REPLACE FUNCTION cleanup_tenant_schema(p_schema_name TEXT)
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_new_name TEXT;
BEGIN
    -- Validate naming convention
    IF p_schema_name !~ '^tenant_[a-z0-9][a-z0-9_]*$' THEN
        RAISE EXCEPTION 'Cannot clean up %: does not match tenant schema pattern.', p_schema_name;
    END IF;

    -- Verify schema exists
    IF NOT EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = p_schema_name) THEN
        RAISE EXCEPTION 'Schema % does not exist.', p_schema_name;
    END IF;

    -- Build timestamped deleted name
    v_new_name := '_deleted_' || p_schema_name || '_' || to_char(now(), 'YYYYMMDD_HH24MISS');

    -- Rename instead of drop
    EXECUTE format('ALTER SCHEMA %I RENAME TO %I', p_schema_name, v_new_name);

    RAISE NOTICE 'Schema % renamed to % for recovery. Drop manually after review.', p_schema_name, v_new_name;
    RETURN v_new_name;
END;
$$;

-- ---------------------------------------------------
-- 4. Permanent Schema Drop
-- ---------------------------------------------------
-- Permanently drops a previously soft-deleted schema.
-- Only schemas prefixed with _deleted_ can be dropped
-- to prevent accidental destruction of live tenants.
--
-- Parameters:
--   p_schema_name  — Schema name (must start with _deleted_)
--
-- Returns: BOOLEAN (true if dropped)
-- ---------------------------------------------------

CREATE OR REPLACE FUNCTION drop_deleted_schema(p_schema_name TEXT)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    -- Only allow dropping soft-deleted schemas
    IF p_schema_name !~ '^_deleted_tenant_' THEN
        RAISE EXCEPTION 'Cannot drop %: only _deleted_tenant_ schemas can be permanently removed.', p_schema_name;
    END IF;

    -- Verify schema exists
    IF NOT EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = p_schema_name) THEN
        RAISE EXCEPTION 'Schema % does not exist.', p_schema_name;
    END IF;

    -- Drop with CASCADE (all objects inside)
    EXECUTE format('DROP SCHEMA %I CASCADE', p_schema_name);

    RAISE NOTICE 'Schema % permanently dropped.', p_schema_name;
    RETURN TRUE;
END;
$$;

-- ---------------------------------------------------
-- 5. List All Tenant Schemas
-- ---------------------------------------------------
-- Returns a table of all active tenant schemas,
-- useful for admin dashboards and maintenance scripts.
--
-- Returns: TABLE (schema_name, created_at approximate)
-- ---------------------------------------------------

CREATE OR REPLACE FUNCTION list_tenant_schemas()
RETURNS TABLE (schema_name TEXT)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    RETURN QUERY
        SELECT nspname::TEXT
        FROM pg_namespace
        WHERE nspname LIKE 'tenant_%'
        ORDER BY nspname;
END;
$$;

-- ---------------------------------------------------
-- Grant execute permissions to application user
-- ---------------------------------------------------

GRANT EXECUTE ON FUNCTION create_tenant_schema(TEXT) TO lcc_user;
GRANT EXECUTE ON FUNCTION tenant_schema_exists(TEXT) TO lcc_user;
GRANT EXECUTE ON FUNCTION cleanup_tenant_schema(TEXT) TO lcc_user;
GRANT EXECUTE ON FUNCTION drop_deleted_schema(TEXT) TO lcc_user;
GRANT EXECUTE ON FUNCTION list_tenant_schemas() TO lcc_user;

SELECT 'Schema functions installed successfully' AS status;
