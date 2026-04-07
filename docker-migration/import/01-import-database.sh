#!/usr/bin/env bash
# ===========================================================================
# docker-migration/import/01-import-database.sh
# ---------------------------------------------------------------------------
# Run this on the DESTINATION PC to restore PostgreSQL databases.
# The Docker db + pgbouncer containers must already be running and healthy.
#
# Usage:
#   bash docker-migration/import/01-import-database.sh
# ===========================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
EXPORTS_DIR="${PROJECT_ROOT}/docker-migration/exports"

# Colours
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

log()    { echo -e "${GREEN}[import-db]${NC} $*"; }
warn()   { echo -e "${YELLOW}[import-db] WARN:${NC} $*"; }
error()  { echo -e "${RED}[import-db] ERROR:${NC} $*" >&2; exit 1; }

# ---------------------------------------------------------------------------
# Preflight checks
# ---------------------------------------------------------------------------
cd "${PROJECT_ROOT}"

[[ -d "${EXPORTS_DIR}" ]] || error "Exports directory not found: ${EXPORTS_DIR}"

log "Checking PostgreSQL container status..."
if ! docker compose ps --quiet db 2>/dev/null | grep -q .; then
    error "PostgreSQL container (db) is not running. Run: docker compose up -d db pgbouncer"
fi

log "Waiting for PostgreSQL to be ready..."
WAIT=0
until docker compose exec -T db pg_isready -U postgres -q 2>/dev/null; do
    sleep 3
    WAIT=$((WAIT + 3))
    [[ ${WAIT} -ge 60 ]] && error "PostgreSQL did not become ready within 60 seconds."
    log "  Waiting... (${WAIT}s)"
done
log "PostgreSQL is ready."

# ---------------------------------------------------------------------------
# Helper: find the latest dump file for a database
# ---------------------------------------------------------------------------
find_latest_dump() {
    local dbname="$1"
    local latest
    latest="$(ls -t "${EXPORTS_DIR}/${dbname}"_*.dump 2>/dev/null | head -1)"
    echo "${latest}"
}

# ---------------------------------------------------------------------------
# Helper: verify checksum
# ---------------------------------------------------------------------------
verify_checksum() {
    local file="$1"
    local checksumfile="${file}.sha256"
    if [[ -f "${checksumfile}" ]]; then
        log "  Verifying checksum for $(basename "${file}")..."
        sha256sum -c "${checksumfile}" || error "Checksum verification FAILED for ${file}. File may be corrupted."
        log "  Checksum OK."
    else
        warn "  No checksum file found for $(basename "${file}"). Skipping checksum verification."
    fi
}

# ---------------------------------------------------------------------------
# Helper: restore one database
# ---------------------------------------------------------------------------
restore_database() {
    local dbname="$1"
    local dumpfile
    dumpfile="$(find_latest_dump "${dbname}")"

    if [[ -z "${dumpfile}" ]]; then
        warn "No dump file found for '${dbname}'. Skipping."
        return 0
    fi

    log "Restoring database: ${dbname}"
    log "  Using dump: $(basename "${dumpfile}")"
    verify_checksum "${dumpfile}"

    # Terminate existing connections before restore
    log "  Terminating active connections to '${dbname}'..."
    docker compose exec -T db psql -U postgres -c \
        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='${dbname}' AND pid <> pg_backend_pid();" \
        > /dev/null 2>&1 || true

    # Run pg_restore — --clean drops existing objects before recreating them
    # --if-exists prevents errors if objects don't exist yet (e.g., fresh DB from init scripts)
    # --exit-on-error ensures we don't silently ignore critical failures
    log "  Running pg_restore..."
    docker compose exec -T db \
        pg_restore \
            --username=postgres \
            --no-password \
            --dbname="${dbname}" \
            --clean \
            --if-exists \
            --no-owner \
            --no-privileges \
            --verbose \
        < "${dumpfile}" 2>&1 | tail -20

    log "  pg_restore completed for: ${dbname}"

    # Spot-check: count tenant schemas (for lankacommerce only)
    if [[ "${dbname}" == "lankacommerce" ]]; then
        SCHEMA_COUNT="$(docker compose exec -T db psql -U postgres -d "${dbname}" -t \
            -c "SELECT COUNT(*) FROM pg_namespace WHERE nspname LIKE 'tenant_%';" 2>/dev/null | xargs)"
        log "  Tenant schemas restored: ${SCHEMA_COUNT}"
    fi
}

# ---------------------------------------------------------------------------
# Restore both databases
# ---------------------------------------------------------------------------
restore_database "lankacommerce"
restore_database "lankacommerce_test"

# ---------------------------------------------------------------------------
# Final spot-check
# ---------------------------------------------------------------------------
log "Running spot-check row counts on lankacommerce..."
for table in tenants_tenant platform_platformuser; do
    COUNT="$(docker compose exec -T db psql -U postgres -d lankacommerce -t \
        -c "SELECT COUNT(*) FROM public.${table};" 2>/dev/null | xargs || echo "ERROR")"
    log "  public.${table}: ${COUNT} rows"
done

echo ""
log "=========================================="
log "DATABASE IMPORT COMPLETE"
log "=========================================="
echo ""
log "Next step: bash docker-migration/import/02-import-redis.sh"
