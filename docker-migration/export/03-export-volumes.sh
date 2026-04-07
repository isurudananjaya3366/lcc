#!/usr/bin/env bash
# ===========================================================================
# docker-migration/export/03-export-volumes.sh
# ---------------------------------------------------------------------------
# Run this on the SOURCE PC to export Docker named volumes (media + static).
# Must be run from the project root. Docker stack can be running.
#
# Usage:
#   bash docker-migration/export/03-export-volumes.sh
# ===========================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
EXPORTS_DIR="${PROJECT_ROOT}/docker-migration/exports"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"

# Colours
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

log()    { echo -e "${GREEN}[export-volumes]${NC} $*"; }
warn()   { echo -e "${YELLOW}[export-volumes] WARN:${NC} $*"; }
error()  { echo -e "${RED}[export-volumes] ERROR:${NC} $*" >&2; exit 1; }

# ---------------------------------------------------------------------------
# Preflight checks
# ---------------------------------------------------------------------------
cd "${PROJECT_ROOT}"
mkdir -p "${EXPORTS_DIR}"

log "Checking Docker availability..."
docker info > /dev/null 2>&1 || error "Docker is not running or not accessible."

# ---------------------------------------------------------------------------
# Helper: export a named volume to a tar.gz archive
# ---------------------------------------------------------------------------
export_volume() {
    local volume_name="$1"       # e.g. lcc-backend-media
    local label="$2"             # e.g. backend-media
    local outfile="${EXPORTS_DIR}/${label}_${TIMESTAMP}.tar.gz"
    local checksumfile="${outfile}.sha256"

    log "Exporting volume '${volume_name}' → ${outfile}"

    # Verify the volume exists
    if ! docker volume ls --quiet | grep -q "^${volume_name}$"; then
        warn "Volume '${volume_name}' does not exist. Skipping."
        return 0
    fi

    # Count files for metadata
    local file_count
    file_count="$(docker run --rm \
        -v "${volume_name}:/source:ro" \
        alpine \
        sh -c 'find /source -type f | wc -l' 2>/dev/null | tr -d ' ')"
    log "  Files in volume: ${file_count}"

    # Create tar archive via a temporary Alpine container
    docker run --rm \
        -v "${volume_name}:/source:ro" \
        -v "${EXPORTS_DIR}:/dest" \
        alpine \
        tar czf "/dest/${label}_${TIMESTAMP}.tar.gz" -C /source .

    # Generate checksum
    sha256sum "${outfile}" > "${checksumfile}"
    log "  Checksum: $(cat "${checksumfile}")"

    local size
    size="$(du -sh "${outfile}" | cut -f1)"
    log "  Archive size: ${size}"
    log "  Done: ${volume_name}"

    # Append to metadata
    echo "${label}_file_count=${file_count}" >> "${EXPORTS_DIR}/export_metadata_"*.txt 2>/dev/null || true
}

# ---------------------------------------------------------------------------
# Export volumes
# ---------------------------------------------------------------------------
log "Starting volume exports at ${TIMESTAMP}..."

# Critical: user-uploaded media files
export_volume "lcc-backend-media"  "backend-media"

# Regeneratable but exported for convenience (saves collectstatic time)
export_volume "lcc-backend-static" "backend-static"

echo ""
log "=========================================="
log "VOLUME EXPORT COMPLETE"
log "Files in ${EXPORTS_DIR}/:"
ls -lh "${EXPORTS_DIR}/"
log "=========================================="
echo ""
log "NEXT STEPS:"
log "  1. Copy your .env.docker file:"
log "     cp .env.docker docker-migration/exports/.env.docker"
log "  2. Transfer the exports/ directory to the destination PC."
log "  3. On the destination PC, follow Phase C in DOCKER_MIGRATION_PROPOSAL.md"
