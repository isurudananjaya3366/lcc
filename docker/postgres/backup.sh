#!/bin/bash
# ==================================================
# LankaCommerce Cloud - PostgreSQL Backup Script
# ==================================================
# Purpose: Development backup (NOT for production)
# Usage: ./backup.sh [database_name]
# ==================================================

set -e

# Configuration
DB_NAME="${1:-lankacommerce}"
DB_USER="${POSTGRES_USER:-lcc_user}"
DB_HOST="${POSTGRES_HOST:-localhost}"
BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.sql"

# Ensure backup directory exists
mkdir -p "${BACKUP_DIR}"

echo "Starting backup of database: ${DB_NAME}"
echo "Backup file: ${BACKUP_FILE}"

# Perform backup
pg_dump \
    -h "${DB_HOST}" \
    -U "${DB_USER}" \
    -d "${DB_NAME}" \
    -F p \
    -f "${BACKUP_FILE}"

# Compress if successful
if [ -f "${BACKUP_FILE}" ]; then
    gzip "${BACKUP_FILE}"
    echo "Backup completed: ${BACKUP_FILE}.gz"

    # Show file size
    ls -lh "${BACKUP_FILE}.gz"
else
    echo "Backup failed!"
    exit 1
fi

# Optional: Cleanup old backups (keep last 5)
echo "Cleaning old backups..."
ls -t ${BACKUP_DIR}/${DB_NAME}_*.sql.gz 2>/dev/null | tail -n +6 | xargs -r rm

echo "Backup complete!"
