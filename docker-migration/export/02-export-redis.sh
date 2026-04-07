#!/usr/bin/env bash
# ===========================================================================
# docker-migration/export/02-export-redis.sh
# ---------------------------------------------------------------------------
# Run this on the SOURCE PC to export the Redis RDB snapshot.
# Must be run from the project root with the Docker stack running.
#
# Usage:
#   bash docker-migration/export/02-export-redis.sh
# ===========================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
EXPORTS_DIR="${PROJECT_ROOT}/docker-migration/exports"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"

# Colours
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

log()    { echo -e "${GREEN}[export-redis]${NC} $*"; }
warn()   { echo -e "${YELLOW}[export-redis] WARN:${NC} $*"; }
error()  { echo -e "${RED}[export-redis] ERROR:${NC} $*" >&2; exit 1; }

# ---------------------------------------------------------------------------
# Preflight checks
# ---------------------------------------------------------------------------
cd "${PROJECT_ROOT}"
mkdir -p "${EXPORTS_DIR}"

log "Checking Redis container status..."
if ! docker compose ps --quiet redis 2>/dev/null | grep -q .; then
    error "Redis container is not running. Start the stack first: docker compose up -d redis"
fi

if ! docker compose exec -T redis redis-cli ping 2>/dev/null | grep -q "PONG"; then
    error "Redis is not responding to PING."
fi

log "Redis is ready. Starting export..."

# ---------------------------------------------------------------------------
# Trigger a background save and wait for completion
# ---------------------------------------------------------------------------
log "Sending BGSAVE to Redis..."
docker compose exec -T redis redis-cli BGSAVE

# Poll until the save is complete
log "Waiting for RDB snapshot to complete..."
WAIT_SECONDS=0
MAX_WAIT=60
while true; do
    STATUS="$(docker compose exec -T redis redis-cli LASTSAVE 2>/dev/null | tr -d '\r')"
    BGSAVE_STATUS="$(docker compose exec -T redis redis-cli INFO persistence 2>/dev/null | grep rdb_bgsave_in_progress | cut -d: -f2 | tr -d '\r\n ')"

    if [[ "${BGSAVE_STATUS}" == "0" ]]; then
        log "  RDB save complete (LASTSAVE epoch: ${STATUS})"
        break
    fi

    if [[ ${WAIT_SECONDS} -ge ${MAX_WAIT} ]]; then
        warn "Timed out waiting for BGSAVE. Copying current dump.rdb anyway."
        break
    fi

    sleep 2
    WAIT_SECONDS=$((WAIT_SECONDS + 2))
    log "  Still saving... (${WAIT_SECONDS}s elapsed)"
done

# ---------------------------------------------------------------------------
# Copy the RDB file from the container to the exports directory
# ---------------------------------------------------------------------------
OUTFILE="${EXPORTS_DIR}/redis_dump_${TIMESTAMP}.rdb"
CHECKSUMFILE="${OUTFILE}.sha256"

log "Copying dump.rdb from lcc-redis container..."
docker cp lcc-redis:/data/dump.rdb "${OUTFILE}"

# Generate checksum
sha256sum "${OUTFILE}" > "${CHECKSUMFILE}"
log "Checksum: $(cat "${CHECKSUMFILE}")"

SIZE="$(du -sh "${OUTFILE}" | cut -f1)"
log "Size: ${SIZE}"

# ---------------------------------------------------------------------------
# Log key count for verification
# ---------------------------------------------------------------------------
KEY_COUNT="$(docker compose exec -T redis redis-cli DBSIZE 2>/dev/null | tr -d '\r')"
log "Redis key count at export time: ${KEY_COUNT}"
echo "redis_key_count=${KEY_COUNT}" >> "${EXPORTS_DIR}/export_metadata_"*.txt 2>/dev/null || true

echo ""
log "=========================================="
log "REDIS EXPORT COMPLETE"
log "  File: ${OUTFILE}"
log "  Keys: ${KEY_COUNT}"
log "=========================================="
echo ""
log "Next step: bash docker-migration/export/03-export-volumes.sh"
