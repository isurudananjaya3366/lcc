-- ==================================================
-- LankaCommerce Cloud - Database Initialization
-- ==================================================
-- File:    01-init.sql
-- Purpose: Create databases, application user, and
--          install required PostgreSQL extensions
-- Runs:    Automatically on first container startup
--          (docker-entrypoint-initdb.d)
--
-- Extensions installed:
--   uuid-ossp          — UUID generation functions
--   hstore             — Key-value pair storage type
--   pg_trgm            — Trigram text similarity and search
--   pg_stat_statements — Query performance statistics
-- ==================================================

-- ---------------------------------------------------
-- 1. Install extensions in template1
-- ---------------------------------------------------
-- Extensions installed in template1 are inherited by
-- every database created afterwards with the default
-- template. This is especially important for
-- django-tenants, which creates new schemas but may
-- also need databases created via CREATE DATABASE.
-- ---------------------------------------------------
SELECT 'Installing extensions in template1' AS status;

\connect template1

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "hstore";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- ---------------------------------------------------
-- 2. Create main application database
-- ---------------------------------------------------
-- Note: POSTGRES_DB env var in docker-compose may
-- already create this database. The exception handler
-- skips creation gracefully if it already exists.
-- ---------------------------------------------------
\connect postgres

SELECT 'Creating main database: lankacommerce (if not exists)' AS status;

SELECT 'lankacommerce already exists — skipping' AS status
WHERE EXISTS (SELECT FROM pg_database WHERE datname = 'lankacommerce');

SELECT 'Creating lankacommerce...' AS status
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'lankacommerce');

-- CREATE DATABASE cannot run inside a transaction block,
-- so we use \gexec to conditionally execute it.
SELECT 'CREATE DATABASE lankacommerce WITH OWNER = postgres ENCODING = ''UTF8'' LC_COLLATE = ''C'' LC_CTYPE = ''C'' TEMPLATE = template0 CONNECTION LIMIT = -1'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'lankacommerce')
\gexec

-- ---------------------------------------------------
-- 3. Create test database
-- ---------------------------------------------------
SELECT 'Creating test database: lankacommerce_test (if not exists)' AS status;

SELECT 'lankacommerce_test already exists — skipping' AS status
WHERE EXISTS (SELECT FROM pg_database WHERE datname = 'lankacommerce_test');

SELECT 'Creating lankacommerce_test...' AS status
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'lankacommerce_test');

SELECT 'CREATE DATABASE lankacommerce_test WITH OWNER = postgres ENCODING = ''UTF8'' LC_COLLATE = ''C'' LC_CTYPE = ''C'' TEMPLATE = template0 CONNECTION LIMIT = -1'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'lankacommerce_test')
\gexec

-- Transfer test database ownership to lcc_user so pytest can
-- drop/recreate it when @pytest.mark.django_db tests run.
-- (This runs idempotently — safe if lcc_user is already owner.)
SELECT 'ALTER DATABASE lankacommerce_test OWNER TO lcc_user'
WHERE EXISTS (SELECT FROM pg_database WHERE datname = 'lankacommerce_test')
  AND EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'lcc_user')
\gexec

-- ---------------------------------------------------
-- 4. Create application user
-- ---------------------------------------------------
SELECT 'Creating application user: lcc_user' AS status;

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'lcc_user') THEN
        CREATE USER lcc_user WITH PASSWORD 'dev_password_change_me';
    END IF;
END
$$;

-- Grant database-level privileges
GRANT ALL PRIVILEGES ON DATABASE lankacommerce TO lcc_user;
GRANT ALL PRIVILEGES ON DATABASE lankacommerce_test TO lcc_user;

-- ---------------------------------------------------
-- 5. Main database — extensions and permissions
-- ---------------------------------------------------
\connect lankacommerce

SELECT 'Configuring main database extensions and permissions' AS status;

-- Required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "hstore";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Schema permissions for application user
GRANT ALL ON SCHEMA public TO lcc_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO lcc_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO lcc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO lcc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO lcc_user;

-- Allow lcc_user to create schemas (required by django-tenants)
ALTER USER lcc_user CREATEDB;

-- ---------------------------------------------------
-- 6. Test database — extensions and permissions
-- ---------------------------------------------------
\connect lankacommerce_test

SELECT 'Configuring test database extensions and permissions' AS status;

-- Required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "hstore";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Schema permissions for application user
GRANT ALL ON SCHEMA public TO lcc_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO lcc_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO lcc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO lcc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO lcc_user;

SELECT 'Database initialization complete' AS status;
