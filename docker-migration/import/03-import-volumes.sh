#!/usr/bin/env bash
# ===========================================================================
# docker-migration/import/03-import-volumes.sh
# ---------------------------------------------------------------------------
# Run this on the DESTINATION PC to restore Docker named volumes
# (backend-media and backend-static).
# Docker must be running. Stack does NOT need to be fully up.
#
# Usage:
#   bash docker-migration/import/03-import-volumes.sh
# ===========================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
EXPORTS_DIR="${PROJECT_ROOT}/docker-migration/exports"

# Colours
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

log()    { echo -e "${GREEN}[import-volumes]${NC} $*"; }
warn()   { echo -e "${YELLOW}[import-volumes] WARN:${NC} $*"; }
error()  { echo -e "${RED}[import-volumes] ERROR:${NC} $*" >&2; exit 1; }

# ---------------------------------------------------------------------------
# Preflight checks
# ---------------------------------------------------------------------------
cd "${PROJECT_ROOT}"

[[ -d "${EXPORTS_DIR}" ]] || error "Exports directory not found: ${EXPORTS_DIR}"

docker info > /dev/null 2>&1 || error "Docker is not running or not accessible."

# ---------------------------------------------------------------------------
# Helper: restore one volume from a tar.gz archive
# ---------------------------------------------------------------------------
restore_volume() {
    local volume_name="$1"    # e.g. lcc-backend-media
    local label="$2"          # e.g. backend-media

    # Find the latest archive for this label
    local archive
    archive="$(ls -t "${EXPORTS_DIR}/${label}"_*.tar.gz 2>/dev/null | head -1)"

    if [[ -z "${archive}" ]]; then
        warn "No archive found for '${label}'. Skipping."
        return 0
    fi

    log "Restoring volume '${volume_name}'"
    log "  Using archive: $(basename "${archive}")"

    # Verify checksum
    local checksumfile="${archive}.sha256"
    if [[ -f "${checksumfile}" ]]; then
        log "  Verifying checksum..."
        sha256sum -c "${checksumfile}" || error "Checksum verification FAILED for ${archive}."
        log "  Checksum OK."
    else
        warn "  No checksum file found. Skipping checksum verification."
    fi

    # Ensure the Docker volume exists (create if not present)
    if ! docker volume ls --quiet | grep -q "^${volume_name}$"; then
        log "  Volume '${volume_name}' does not exist. Creating it..."
        docker volume create "${volume_name}"
    fi

    # Restore: mount the archive and the target volume into an Alpine container
    # The archive is on the host; use a bind mount to make it accessible.
    local archive_dir
    archive_dir="$(dirname "${archive}")"
    local archive_basename
    archive_basename="$(basename "${archive}")"

    log "  Extracting archive into volume..."
    docker run --rm \
        -v "${archive_dir}:/archives:ro" \
        -v "${volume_name}:/dest" \
        alpine \
        tar xzf "/archives/${archive_basename}" -C /dest

    # Count restored files
    local file_count
    file_count="$(docker run --rm -v "${volume_name}:/source:ro" alpine sh -c 'find /source -type f | wc -l' | tr -d ' ')"
    log "  Files restored: ${file_count}"
    log "  Done: ${volume_name}"
}

# ---------------------------------------------------------------------------
# Restore volumes
# ---------------------------------------------------------------------------
log "Starting volume restore..."

restore_volume "lcc-backend-media"  "backend-media"
restore_volume "lcc-backend-static" "backend-static"

echo ""
log "=========================================="
log "VOLUME IMPORT COMPLETE"
log "=========================================="
echo ""
log "NEXT STEPS:"
log "  1. Start the full stack:  docker compose up -d"
log "  2. Run migrations:        docker compose exec backend python manage.py migrate --no-input"
log "  3. Collect static:        docker compose exec backend python manage.py collectstatic --no-input"
log "  4. Verify migration:      bash docker-migration/import/04-verify-migration.sh"
