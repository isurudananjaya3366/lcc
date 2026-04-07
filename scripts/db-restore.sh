#!/bin/bash
# ==================================================
# LankaCommerce Cloud — Database Restore Script
# ==================================================
# Purpose: Restore a PostgreSQL database from a
#          pg_dump custom-format backup file.
#
# Supports:
#   - Full database restore
#   - Checksum verification before restore
#   - Schema-only or data-only restore
#   - Drop and recreate target database
#   - Selective schema restore (single tenant)
#
# Usage:
#   ./db-restore.sh backup_file.dump               # Restore to default DB
#   ./db-restore.sh backup_file.dump my_database    # Restore to named DB
#   ./db-restore.sh --schema tenant_acme backup.dump # Restore one schema
#   ./db-restore.sh --list backup_file.dump          # List backup contents
#
# Environment Variables:
#   DB_HOST  — Database host (default: pgbouncer)
#   DB_PORT  — Database port (default: 6432)
#   DB_USER  — Database user (default: lcc_user)
#
# Warning: This script drops and recreates the target
#          database. All existing data will be lost.
# ==================================================

set -euo pipefail

# -------------------------------------------------
# Configuration
# -------------------------------------------------
DB_HOST="${DB_HOST:-pgbouncer}"
DB_PORT="${DB_PORT:-6432}"
DB_USER="${DB_USER:-lcc_user}"
DEFAULT_DB="lankacommerce"

# -------------------------------------------------
# Functions
# -------------------------------------------------

log_info() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] $1"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $1" >&2
}

log_success() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [OK] $1"
}

log_warn() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WARN] $1"
}

verify_checksum() {
    local backup_file="$1"
    local checksum_file="${backup_file}.sha256"

    if [ -f "${checksum_file}" ]; then
        log_info "Verifying checksum..."
        if sha256sum -c "${checksum_file}" --quiet 2>/dev/null; then
            log_success "Checksum verified"
            return 0
        else
            log_error "Checksum verification failed"
            return 1
        fi
    else
        log_warn "No checksum file found — skipping verification"
        return 0
    fi
}

list_backup_contents() {
    local backup_file="$1"

    log_info "Listing contents of: ${backup_file}"
    echo ""
    pg_restore --list "${backup_file}" 2>/dev/null | head -50
    echo ""
    log_info "(Showing first 50 entries. Use pg_restore --list directly for full output.)"
}

restore_full() {
    local backup_file="$1"
    local db_name="$2"

    log_warn "This will DROP and RECREATE database: ${db_name}"
    log_warn "All existing data in ${db_name} will be lost."
    echo ""

    # Prompt for confirmation unless running non-interactively
    if [ -t 0 ]; then
        read -rp "Type 'yes' to confirm: " confirmation
        if [ "${confirmation}" != "yes" ]; then
            log_info "Restore cancelled by user"
            exit 0
        fi
    fi

    log_info "Starting full restore to: ${db_name}"

    # Terminate existing connections to the target database
    log_info "Terminating active connections to ${db_name}..."
    psql \
        -h "${DB_HOST}" \
        -p "${DB_PORT}" \
        -U "${DB_USER}" \
        -d postgres \
        -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '${db_name}' AND pid <> pg_backend_pid();" \
        2>/dev/null || true

    # Drop and recreate the database
    log_info "Dropping database: ${db_name}"
    dropdb \
        -h "${DB_HOST}" \
        -p "${DB_PORT}" \
        -U "${DB_USER}" \
        --if-exists \
        "${db_name}"

    log_info "Creating database: ${db_name}"
    createdb \
        -h "${DB_HOST}" \
        -p "${DB_PORT}" \
        -U "${DB_USER}" \
        -O "${DB_USER}" \
        -E UTF8 \
        "${db_name}"

    # Restore from backup
    log_info "Restoring from: ${backup_file}"
    pg_restore \
        -h "${DB_HOST}" \
        -p "${DB_PORT}" \
        -U "${DB_USER}" \
        -d "${db_name}" \
        --no-owner \
        --no-privileges \
        --verbose \
        "${backup_file}" 2>&1 | while read -r line; do
            log_info "  pg_restore: ${line}"
        done

    log_success "Full restore completed for: ${db_name}"
}

restore_schema() {
    local schema_name="$1"
    local backup_file="$2"
    local db_name="${3:-${DEFAULT_DB}}"

    log_info "Restoring schema '${schema_name}' to database: ${db_name}"

    pg_restore \
        -h "${DB_HOST}" \
        -p "${DB_PORT}" \
        -U "${DB_USER}" \
        -d "${db_name}" \
        --schema="${schema_name}" \
        --no-owner \
        --no-privileges \
        --verbose \
        "${backup_file}" 2>&1 | while read -r line; do
            log_info "  pg_restore: ${line}"
        done

    log_success "Schema restore completed: ${schema_name}"
}

validate_restore() {
    local db_name="$1"

    log_info "Validating restore of: ${db_name}"

    # Count schemas
    local schema_count
    schema_count=$(psql \
        -h "${DB_HOST}" \
        -p "${DB_PORT}" \
        -U "${DB_USER}" \
        -d "${db_name}" \
        -t -A \
        -c "SELECT count(*) FROM information_schema.schemata WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast');" \
        2>/dev/null)
    log_info "  Schemas found: ${schema_count}"

    # Count tables in public schema
    local table_count
    table_count=$(psql \
        -h "${DB_HOST}" \
        -p "${DB_PORT}" \
        -U "${DB_USER}" \
        -d "${db_name}" \
        -t -A \
        -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';" \
        2>/dev/null)
    log_info "  Tables in public schema: ${table_count}"

    # Check extensions
    local extension_count
    extension_count=$(psql \
        -h "${DB_HOST}" \
        -p "${DB_PORT}" \
        -U "${DB_USER}" \
        -d "${db_name}" \
        -t -A \
        -c "SELECT count(*) FROM pg_extension WHERE extname IN ('uuid-ossp', 'hstore', 'pg_trgm', 'pg_stat_statements');" \
        2>/dev/null)
    log_info "  Extensions installed: ${extension_count}"

    log_success "Validation complete for: ${db_name}"
}

show_usage() {
    echo "Usage: $0 [options] backup_file [database_name]"
    echo ""
    echo "Options:"
    echo "  --list              List backup contents"
    echo "  --schema SCHEMA     Restore a specific schema only"
    echo "  --skip-verify       Skip checksum verification"
    echo "  -h, --help          Show this help message"
    echo ""
    echo "Arguments:"
    echo "  backup_file         Path to the .dump backup file"
    echo "  database_name       Target database (default: ${DEFAULT_DB})"
    echo ""
    echo "Environment:"
    echo "  DB_HOST   Database host (default: pgbouncer)"
    echo "  DB_PORT   Database port (default: 6432)"
    echo "  DB_USER   Database user (default: lcc_user)"
}

# -------------------------------------------------
# Main
# -------------------------------------------------

SKIP_VERIFY=false
SCHEMA_NAME=""
ACTION="restore"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h)
            show_usage
            exit 0
            ;;
        --list)
            ACTION="list"
            shift
            ;;
        --schema)
            SCHEMA_NAME="$2"
            ACTION="schema"
            shift 2
            ;;
        --skip-verify)
            SKIP_VERIFY=true
            shift
            ;;
        *)
            break
            ;;
    esac
done

BACKUP_FILE="${1:-}"
DB_NAME="${2:-${DEFAULT_DB}}"

if [ -z "${BACKUP_FILE}" ]; then
    log_error "No backup file specified"
    echo ""
    show_usage
    exit 1
fi

if [ ! -f "${BACKUP_FILE}" ]; then
    log_error "Backup file not found: ${BACKUP_FILE}"
    exit 1
fi

log_info "========================================"
log_info "LankaCommerce Cloud — Database Restore"
log_info "========================================"
log_info "Backup file: ${BACKUP_FILE}"
log_info "Host: ${DB_HOST}:${DB_PORT}"
log_info "User: ${DB_USER}"
log_info "----------------------------------------"

# Verify checksum unless skipped
if [ "${SKIP_VERIFY}" = false ]; then
    verify_checksum "${BACKUP_FILE}"
fi

case "${ACTION}" in
    list)
        list_backup_contents "${BACKUP_FILE}"
        ;;
    schema)
        restore_schema "${SCHEMA_NAME}" "${BACKUP_FILE}" "${DB_NAME}"
        validate_restore "${DB_NAME}"
        ;;
    restore)
        restore_full "${BACKUP_FILE}" "${DB_NAME}"
        validate_restore "${DB_NAME}"
        ;;
esac

log_info "========================================"
log_success "Restore operation completed"
log_info "========================================"
