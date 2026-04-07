#!/usr/bin/env bash
# ===========================================================================
# docker-migration/export/01-export-database.sh
# ---------------------------------------------------------------------------
# Run this on the SOURCE PC to export both PostgreSQL databases.
# Must be run from the project root with the Docker stack running.
#
# Usage:
#   bash docker-migration/export/01-export-database.sh
# ===========================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
EXPORTS_DIR="${PROJECT_ROOT}/docker-migration/exports"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"

# Colours
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

log()    { echo -e "${GREEN}[export-db]${NC} $*"; }
warn()   { echo -e "${YELLOW}[export-db] WARN:${NC} $*"; }
error()  { echo -e "${RED}[export-db] ERROR:${NC} $*" >&2; exit 1; }

# ---------------------------------------------------------------------------
# Preflight checks
# ---------------------------------------------------------------------------
cd "${PROJECT_ROOT}"

mkdir -p "${EXPORTS_DIR}"

log "Checking Docker stack status..."
if ! docker compose ps --quiet db 2>/dev/null | grep -q .; then
    error "PostgreSQL container (db) is not running. Start the stack first: docker compose up -d db"
fi

if ! docker compose exec -T db pg_isready -U postgres -q 2>/dev/null; then
    error "PostgreSQL is not ready. Wait for the container to become healthy."
fi

log "PostgreSQL is ready. Starting export at ${TIMESTAMP}..."

# ---------------------------------------------------------------------------
# Helper: export one database
# ---------------------------------------------------------------------------
export_database() {
    local dbname="$1"
    local outfile="${EXPORTS_DIR}/${dbname}_${TIMESTAMP}.dump"
    local checksumfile="${outfile}.sha256"

    log "  Exporting database: ${dbname} → ${outfile}"

    # pg_dump inside the container, streamed out to the host file
    docker compose exec -T db \
        pg_dump \
            --username=postgres \
            --no-password \
            --format=custom \
            --compress=6 \
            --verbose \
            "${dbname}" \
        > "${outfile}"

    # Generate checksum
    sha256sum "${outfile}" > "${checksumfile}"
    log "  Checksum: $(cat "${checksumfile}")"

    local size
    size="$(du -sh "${outfile}" | cut -f1)"
    log "  Size: ${size}"
    log "  Done: ${dbname}"
}

# ---------------------------------------------------------------------------
# Export both databases
# ---------------------------------------------------------------------------
export_database "lankacommerce"
export_database "lankacommerce_test"

# ---------------------------------------------------------------------------
# Write export metadata
# ---------------------------------------------------------------------------
METADATA_FILE="${EXPORTS_DIR}/export_metadata_${TIMESTAMP}.txt"
{
    echo "# LankaCommerce Docker Migration — Export Metadata"
    echo "timestamp=${TIMESTAMP}"
    echo "source_host=$(hostname)"
    echo "postgres_version=$(docker compose exec -T db psql -U postgres -c 'SELECT version();' -t 2>/dev/null | head -1 | xargs)"
    echo ""
    echo "# Tenant schema count (for verification on destination)"
    echo "tenant_schema_count=$(docker compose exec -T db psql -U postgres -d lankacommerce -t -c "SELECT COUNT(*) FROM pg_namespace WHERE nspname LIKE 'tenant_%';" 2>/dev/null | xargs)"
    echo ""
    echo "# Key table row counts"
    for table in tenants_tenant platform_platformuser orders_order inventory_product; do
        count=$(docker compose exec -T db psql -U postgres -d lankacommerce -t \
            -c "SELECT COALESCE((SELECT reltuples::bigint FROM pg_class JOIN pg_namespace ON pg_class.relnamespace=pg_namespace.oid WHERE relname='${table}' AND nspname='public'), -1);" \
            2>/dev/null | xargs || echo "N/A")
        echo "${table}=${count}"
    done
} > "${METADATA_FILE}"

log "Metadata written to: ${METADATA_FILE}"

echo ""
log "=========================================="
log "DATABASE EXPORT COMPLETE"
log "=========================================="
log "Files in ${EXPORTS_DIR}/:"
ls -lh "${EXPORTS_DIR}/"
echo ""
log "Next step: bash docker-migration/export/02-export-redis.sh"
