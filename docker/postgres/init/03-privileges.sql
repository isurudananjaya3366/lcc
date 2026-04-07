-- ==================================================
-- LankaCommerce Cloud - Schema Privileges
-- ==================================================
-- File:    03-privileges.sql
-- Purpose: Define and grant privileges for tenant
--          operations, ensuring proper isolation
--          between public and tenant schemas.
-- Runs:    Automatically on first container startup
--          (docker-entrypoint-initdb.d)
--
-- Privilege Model:
--   postgres   — Superuser, owns databases and schemas
--   lcc_user   — Application user, full CRUD on
--                 public and tenant schemas
--
-- Isolation Rules:
--   - Public schema: shared tables only (tenants,
--     domains, global lookups)
--   - Tenant schemas: per-tenant data (products,
--     sales, inventory, etc.)
--   - lcc_user accesses tenant schemas via
--     search_path set by django-tenants middleware
-- ==================================================

\connect lankacommerce

SELECT 'Configuring schema privileges' AS status;

-- ---------------------------------------------------
-- 1. Public Schema Privileges
-- ---------------------------------------------------
-- The public schema holds the tenant registry and
-- shared lookup tables. lcc_user needs full access
-- to manage tenants and shared data.
-- ---------------------------------------------------

-- Ensure lcc_user owns objects it creates in public
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
    GRANT ALL ON TABLES TO lcc_user;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
    GRANT ALL ON SEQUENCES TO lcc_user;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
    GRANT ALL ON FUNCTIONS TO lcc_user;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
    GRANT USAGE ON TYPES TO lcc_user;

-- ---------------------------------------------------
-- 2. Tenant Schema Default Privileges
-- ---------------------------------------------------
-- When postgres (or SECURITY DEFINER functions) creates
-- objects inside tenant schemas, lcc_user must
-- automatically receive full access. These defaults
-- apply to any schema where postgres creates objects.
-- ---------------------------------------------------

ALTER DEFAULT PRIVILEGES FOR ROLE postgres
    GRANT ALL ON TABLES TO lcc_user;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres
    GRANT ALL ON SEQUENCES TO lcc_user;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres
    GRANT ALL ON FUNCTIONS TO lcc_user;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres
    GRANT USAGE ON TYPES TO lcc_user;

-- ---------------------------------------------------
-- 3. Schema Creation Privilege
-- ---------------------------------------------------
-- django-tenants creates new schemas when a Tenant
-- model instance is saved. The application user
-- needs the CREATE privilege on the database.
-- ---------------------------------------------------

-- CREATEDB was already granted in 01-init.sql
-- Ensure schema creation in current database
GRANT CREATE ON DATABASE lankacommerce TO lcc_user;

-- ---------------------------------------------------
-- 4. Information Schema & pg_catalog Access
-- ---------------------------------------------------
-- lcc_user needs read access to system catalogs for
-- django-tenants schema introspection (checking if a
-- schema exists, listing tables, etc.).
-- ---------------------------------------------------

GRANT USAGE ON SCHEMA information_schema TO lcc_user;
GRANT USAGE ON SCHEMA pg_catalog TO lcc_user;

-- ---------------------------------------------------
-- 5. Extension Schema Access
-- ---------------------------------------------------
-- Extensions installed in the public schema must be
-- accessible from tenant schemas via search_path.
-- This is already implicit for public, but we
-- ensure explicit USAGE is granted.
-- ---------------------------------------------------

GRANT USAGE ON SCHEMA public TO lcc_user;

-- ---------------------------------------------------
-- 6. Revoke Dangerous Defaults
-- ---------------------------------------------------
-- PostgreSQL 15 revokes CREATE on public schema from
-- PUBLIC role by default, but we explicitly ensure
-- only lcc_user and postgres can create objects.
-- ---------------------------------------------------

REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO lcc_user;

-- ---------------------------------------------------
-- 7. Apply Same Privileges to Test Database
-- ---------------------------------------------------

\connect lankacommerce_test

SELECT 'Configuring test database schema privileges' AS status;

-- Public schema defaults for test database
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
    GRANT ALL ON TABLES TO lcc_user;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
    GRANT ALL ON SEQUENCES TO lcc_user;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
    GRANT ALL ON FUNCTIONS TO lcc_user;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
    GRANT USAGE ON TYPES TO lcc_user;

-- Global defaults for tenant schemas in test database
ALTER DEFAULT PRIVILEGES FOR ROLE postgres
    GRANT ALL ON TABLES TO lcc_user;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres
    GRANT ALL ON SEQUENCES TO lcc_user;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres
    GRANT ALL ON FUNCTIONS TO lcc_user;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres
    GRANT USAGE ON TYPES TO lcc_user;

-- Schema creation privilege
GRANT CREATE ON DATABASE lankacommerce_test TO lcc_user;

-- System catalog access
GRANT USAGE ON SCHEMA information_schema TO lcc_user;
GRANT USAGE ON SCHEMA pg_catalog TO lcc_user;
GRANT USAGE ON SCHEMA public TO lcc_user;

-- Lock down public schema
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO lcc_user;

SELECT 'Schema privileges configured successfully' AS status;
