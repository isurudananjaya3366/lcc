#!/usr/bin/env bash
# ===========================================================================
# docker-migration/import/02-import-redis.sh
# ---------------------------------------------------------------------------
# Run this on the DESTINATION PC to restore the Redis RDB snapshot.
# The Redis container must be running before this script starts.
#
# Usage:
#   bash docker-migration/import/02-import-redis.sh
# ===========================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
EXPORTS_DIR="${PROJECT_ROOT}/docker-migration/exports"

# Colours
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

log()    { echo -e "${GREEN}[import-redis]${NC} $*"; }
warn()   { echo -e "${YELLOW}[import-redis] WARN:${NC} $*"; }
error()  { echo -e "${RED}[import-redis] ERROR:${NC} $*" >&2; exit 1; }

# ---------------------------------------------------------------------------
# Preflight checks
# ---------------------------------------------------------------------------
cd "${PROJECT_ROOT}"

[[ -d "${EXPORTS_DIR}" ]] || error "Exports directory not found: ${EXPORTS_DIR}"

log "Checking Redis container status..."
if ! docker compose ps --quiet redis 2>/dev/null | grep -q .; then
    error "Redis container is not running. Run: docker compose up -d redis"
fi

# ---------------------------------------------------------------------------
# Find the latest RDB file
# ---------------------------------------------------------------------------
RDB_FILE="$(ls -t "${EXPORTS_DIR}"/redis_dump_*.rdb 2>/dev/null | head -1)"
[[ -n "${RDB_FILE}" ]] || error "No Redis RDB file found in ${EXPORTS_DIR}/"

log "Using RDB file: $(basename "${RDB_FILE}")"

# ---------------------------------------------------------------------------
# Verify checksum
# ---------------------------------------------------------------------------
CHECKSUMFILE="${RDB_FILE}.sha256"
if [[ -f "${CHECKSUMFILE}" ]]; then
    log "Verifying checksum..."
    sha256sum -c "${CHECKSUMFILE}" || error "Checksum verification FAILED. File may be corrupted."
    log "Checksum OK."
else
    warn "No checksum file found. Skipping checksum verification."
fi

# ---------------------------------------------------------------------------
# Restore: stop Redis → copy RDB → start Redis
# ---------------------------------------------------------------------------
log "Stopping Redis container to replace RDB..."
docker compose stop redis

log "Copying RDB file into lcc-redis container volume..."
# Use a temporary Alpine container to write directly into the Redis volume
docker run --rm \
    -v "${RDB_FILE}:/source/dump.rdb:ro" \
    -v lcc-redis-data:/dest \
    alpine \
    sh -c 'cp /source/dump.rdb /dest/dump.rdb && chmod 644 /dest/dump.rdb'

log "Starting Redis..."
docker compose start redis

# Wait for Redis to be ready
WAIT=0
until docker compose exec -T redis redis-cli ping 2>/dev/null | grep -q "PONG"; do
    sleep 2
    WAIT=$((WAIT + 2))
    [[ ${WAIT} -ge 30 ]] && error "Redis did not start within 30 seconds."
done

KEY_COUNT="$(docker compose exec -T redis redis-cli DBSIZE 2>/dev/null | tr -d '\r')"
log "Redis key count after restore: ${KEY_COUNT}"

echo ""
log "=========================================="
log "REDIS IMPORT COMPLETE"
log "  Keys loaded: ${KEY_COUNT}"
log "=========================================="
echo ""
log "Next step: bash docker-migration/import/03-import-volumes.sh"
