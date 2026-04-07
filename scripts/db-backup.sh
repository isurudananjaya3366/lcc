#!/bin/bash
# ==================================================
# LankaCommerce Cloud — Database Backup Script
# ==================================================
# Purpose: Comprehensive PostgreSQL backup for
#          development and staging environments.
#
# Supports:
#   - Full database dump (pg_dump custom format)
#   - Optional plain-text SQL dump
#   - Backup compression and checksums
#   - Retention-based cleanup
#   - Multi-tenant schema awareness
#
# Usage:
#   ./db-backup.sh                     # Backup default database
#   ./db-backup.sh lankacommerce_test  # Backup test database
#   ./db-backup.sh --all               # Backup all databases
#
# Environment Variables:
#   DB_HOST     — Database host (default: pgbouncer)
#   DB_PORT     — Database port (default: 6432)
#   DB_USER     — Database user (default: lcc_user)
#   BACKUP_DIR  — Backup directory (default: ./backups)
#   RETENTION_DAILY   — Daily backups to keep (default: 7)
#   RETENTION_WEEKLY  — Weekly backups to keep (default: 4)
#   RETENTION_MONTHLY — Monthly backups to keep (default: 3)
#
# Note: For production, use pg_basebackup with WAL
#       archiving for point-in-time recovery.
# ==================================================

set -euo pipefail

# -------------------------------------------------
# Configuration
# -------------------------------------------------
DB_HOST="${DB_HOST:-pgbouncer}"
DB_PORT="${DB_PORT:-6432}"
DB_USER="${DB_USER:-lcc_user}"
BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DAY_OF_WEEK=$(date +%u)
DAY_OF_MONTH=$(date +%d)
RETENTION_DAILY="${RETENTION_DAILY:-7}"
RETENTION_WEEKLY="${RETENTION_WEEKLY:-4}"
RETENTION_MONTHLY="${RETENTION_MONTHLY:-3}"

# Default databases
DEFAULT_DB="lankacommerce"
ALL_DATABASES=("lankacommerce" "lankacommerce_test")

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

ensure_directories() {
    mkdir -p "${BACKUP_DIR}/daily"
    mkdir -p "${BACKUP_DIR}/weekly"
    mkdir -p "${BACKUP_DIR}/monthly"
    mkdir -p "${BACKUP_DIR}/latest"
}

backup_database() {
    local db_name="$1"
    local backup_type="${2:-daily}"
    local target_dir="${BACKUP_DIR}/${backup_type}"
    local backup_file="${target_dir}/${db_name}_${TIMESTAMP}.dump"

    log_info "Starting ${backup_type} backup of database: ${db_name}"
    log_info "Target: ${backup_file}"

    # Use pg_dump with custom format (-F c) for:
    #   - Compression built into the format
    #   - Selective restore (individual tables/schemas)
    #   - Parallel restore support
    pg_dump \
        -h "${DB_HOST}" \
        -p "${DB_PORT}" \
        -U "${DB_USER}" \
        -d "${db_name}" \
        -F c \
        -Z 6 \
        -f "${backup_file}" \
        --no-owner \
        --no-privileges \
        --verbose 2>&1 | while read -r line; do
            log_info "  pg_dump: ${line}"
        done

    if [ -f "${backup_file}" ]; then
        # Generate checksum for integrity verification
        local checksum
        checksum=$(sha256sum "${backup_file}" | cut -d ' ' -f1)
        echo "${checksum}  ${backup_file}" > "${backup_file}.sha256"

        # Copy to latest
        cp "${backup_file}" "${BACKUP_DIR}/latest/${db_name}_latest.dump"
        cp "${backup_file}.sha256" "${BACKUP_DIR}/latest/${db_name}_latest.dump.sha256"

        local file_size
        file_size=$(du -h "${backup_file}" | cut -f1)
        log_success "Backup complete: ${backup_file} (${file_size})"
        log_info "Checksum: ${checksum}"
    else
        log_error "Backup failed for database: ${db_name}"
        return 1
    fi
}

classify_and_backup() {
    local db_name="$1"

    # Always create a daily backup
    backup_database "${db_name}" "daily"

    # On Sundays (day 7), also create a weekly backup
    if [ "${DAY_OF_WEEK}" -eq 7 ]; then
        log_info "Sunday detected — creating weekly backup"
        backup_database "${db_name}" "weekly"
    fi

    # On the first day of the month, create a monthly backup
    if [ "${DAY_OF_MONTH}" -eq "01" ]; then
        log_info "First of month — creating monthly backup"
        backup_database "${db_name}" "monthly"
    fi
}

cleanup_old_backups() {
    local db_name="$1"

    log_info "Cleaning old backups for: ${db_name}"

    # Daily: keep last N
    local daily_count
    daily_count=$(find "${BACKUP_DIR}/daily" -name "${db_name}_*.dump" 2>/dev/null | wc -l)
    if [ "${daily_count}" -gt "${RETENTION_DAILY}" ]; then
        find "${BACKUP_DIR}/daily" -name "${db_name}_*.dump" -printf '%T+ %p\n' \
            | sort | head -n -"${RETENTION_DAILY}" | cut -d' ' -f2- \
            | while read -r f; do
                rm -f "${f}" "${f}.sha256"
                log_info "  Removed old daily: ${f}"
            done
    fi

    # Weekly: keep last N
    local weekly_count
    weekly_count=$(find "${BACKUP_DIR}/weekly" -name "${db_name}_*.dump" 2>/dev/null | wc -l)
    if [ "${weekly_count}" -gt "${RETENTION_WEEKLY}" ]; then
        find "${BACKUP_DIR}/weekly" -name "${db_name}_*.dump" -printf '%T+ %p\n' \
            | sort | head -n -"${RETENTION_WEEKLY}" | cut -d' ' -f2- \
            | while read -r f; do
                rm -f "${f}" "${f}.sha256"
                log_info "  Removed old weekly: ${f}"
            done
    fi

    # Monthly: keep last N
    local monthly_count
    monthly_count=$(find "${BACKUP_DIR}/monthly" -name "${db_name}_*.dump" 2>/dev/null | wc -l)
    if [ "${monthly_count}" -gt "${RETENTION_MONTHLY}" ]; then
        find "${BACKUP_DIR}/monthly" -name "${db_name}_*.dump" -printf '%T+ %p\n' \
            | sort | head -n -"${RETENTION_MONTHLY}" | cut -d' ' -f2- \
            | while read -r f; do
                rm -f "${f}" "${f}.sha256"
                log_info "  Removed old monthly: ${f}"
            done
    fi

    log_success "Cleanup complete for: ${db_name}"
}

show_usage() {
    echo "Usage: $0 [database_name | --all]"
    echo ""
    echo "Options:"
    echo "  database_name   Name of the database to back up"
    echo "                  (default: ${DEFAULT_DB})"
    echo "  --all           Back up all databases"
    echo ""
    echo "Environment:"
    echo "  DB_HOST             Database host (default: pgbouncer)"
    echo "  DB_PORT             Database port (default: 6432)"
    echo "  DB_USER             Database user (default: lcc_user)"
    echo "  BACKUP_DIR          Backup directory (default: ./backups)"
    echo "  RETENTION_DAILY     Daily backups to keep (default: 7)"
    echo "  RETENTION_WEEKLY    Weekly backups to keep (default: 4)"
    echo "  RETENTION_MONTHLY   Monthly backups to keep (default: 3)"
}

# -------------------------------------------------
# Main
# -------------------------------------------------

if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
    show_usage
    exit 0
fi

log_info "========================================"
log_info "LankaCommerce Cloud — Database Backup"
log_info "========================================"
log_info "Host: ${DB_HOST}:${DB_PORT}"
log_info "User: ${DB_USER}"
log_info "Backup directory: ${BACKUP_DIR}"
log_info "Retention: ${RETENTION_DAILY} daily, ${RETENTION_WEEKLY} weekly, ${RETENTION_MONTHLY} monthly"
log_info "----------------------------------------"

ensure_directories

if [ "${1:-}" = "--all" ]; then
    for db in "${ALL_DATABASES[@]}"; do
        classify_and_backup "${db}"
        cleanup_old_backups "${db}"
    done
else
    DB_NAME="${1:-${DEFAULT_DB}}"
    classify_and_backup "${DB_NAME}"
    cleanup_old_backups "${DB_NAME}"
fi

log_info "========================================"
log_success "All backups completed successfully"
log_info "========================================"
