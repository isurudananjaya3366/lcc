#!/bin/bash
# ==================================================
# LankaCommerce Cloud - Database Reset Script
# ==================================================
# Purpose: Reset development database completely
# Usage: ./db-reset.sh [--force]
# WARNING: This will destroy ALL data in the database
# ==================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
DB_NAME="${POSTGRES_DB:-lankacommerce}"
DB_TEST_NAME="${DB_NAME}_test"
DB_USER="${POSTGRES_USER:-lcc_user}"
DB_ADMIN_USER="postgres"
FORCE=0

# Parse arguments
while [ $# -gt 0 ]; do
    case "$1" in
        --force|-f)
            FORCE=1
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--force]"
            exit 1
            ;;
    esac
done

echo -e "${RED}"
echo "=========================================="
echo "  ⚠️  DATABASE RESET WARNING ⚠️"
echo "=========================================="
echo -e "${NC}"
echo "This will:"
echo "  • Drop database: ${DB_NAME}"
echo "  • Drop database: ${DB_TEST_NAME}"
echo "  • Recreate both databases"
echo "  • Recreate extensions"
echo "  • Run all migrations"
echo ""
echo -e "${RED}ALL DATA WILL BE PERMANENTLY LOST!${NC}"
echo ""

# Confirmation
if [ "$FORCE" -eq 0 ]; then
    echo -n "Type 'reset' to confirm: "
    read -r confirmation
    if [ "$confirmation" != "reset" ]; then
        echo -e "${YELLOW}Database reset cancelled.${NC}"
        exit 0
    fi
fi

echo ""
echo -e "${YELLOW}Starting database reset...${NC}"

# Stop Celery services to prevent DB connections
echo "Stopping Celery services..."
docker compose stop celery-worker celery-beat 2>/dev/null || true

# Wait for connections to close
sleep 2

# Drop and recreate databases
echo "Dropping existing databases..."
docker compose exec -T db psql -U "$DB_ADMIN_USER" -c "
    -- Terminate active connections
    SELECT pg_terminate_backend(pg_stat_activity.pid)
    FROM pg_stat_activity
    WHERE pg_stat_activity.datname IN ('${DB_NAME}', '${DB_TEST_NAME}')
    AND pid <> pg_backend_pid();
" 2>/dev/null || true

docker compose exec -T db psql -U "$DB_ADMIN_USER" -c "DROP DATABASE IF EXISTS ${DB_NAME};" 2>/dev/null || true
docker compose exec -T db psql -U "$DB_ADMIN_USER" -c "DROP DATABASE IF EXISTS ${DB_TEST_NAME};" 2>/dev/null || true

echo "Creating databases..."
docker compose exec -T db psql -U "$DB_ADMIN_USER" -c "CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};"
docker compose exec -T db psql -U "$DB_ADMIN_USER" -c "CREATE DATABASE ${DB_TEST_NAME} OWNER ${DB_USER};"

echo "Creating extensions..."
docker compose exec -T db psql -U "$DB_ADMIN_USER" -d "${DB_NAME}" -c '
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "hstore";
'
docker compose exec -T db psql -U "$DB_ADMIN_USER" -d "${DB_TEST_NAME}" -c '
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "hstore";
'

echo "Granting permissions..."
docker compose exec -T db psql -U "$DB_ADMIN_USER" -c "
    GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};
    GRANT ALL PRIVILEGES ON DATABASE ${DB_TEST_NAME} TO ${DB_USER};
    ALTER USER ${DB_USER} CREATEDB;
"

# Run migrations
echo "Running migrations..."
docker compose exec -T backend python manage.py migrate --noinput 2>/dev/null || {
    echo -e "${YELLOW}Note: Migrations skipped (backend may not be ready)${NC}"
}

# Restart Celery services
echo "Restarting Celery services..."
docker compose start celery-worker celery-beat 2>/dev/null || true

echo ""
echo -e "${GREEN}=========================================="
echo "  ✅ Database reset complete!"
echo "==========================================${NC}"
echo ""
echo "Databases recreated:"
echo "  • ${DB_NAME}"
echo "  • ${DB_TEST_NAME}"
echo ""
echo "You may want to:"
echo "  • Create a superuser: docker compose exec backend python manage.py createsuperuser"
echo "  • Load fixtures: docker compose exec backend python manage.py loaddata <fixture>"
