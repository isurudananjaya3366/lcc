#!/bin/bash
# ==================================================
# LankaCommerce Cloud - PostgreSQL Restore Script
# ==================================================
# Purpose: Restore from backup (development only)
# Usage: ./restore.sh backup_file.sql.gz [database_name]
# ==================================================

set -e

BACKUP_FILE="${1}"
DB_NAME="${2:-lankacommerce}"
DB_USER="${POSTGRES_USER:-lcc_user}"
DB_HOST="${POSTGRES_HOST:-localhost}"

if [ -z "${BACKUP_FILE}" ]; then
    echo "Usage: $0 <backup_file.sql.gz> [database_name]"
    exit 1
fi

echo "Restoring database: ${DB_NAME}"
echo "From backup: ${BACKUP_FILE}"

# Decompress and restore
gunzip -c "${BACKUP_FILE}" | psql \
    -h "${DB_HOST}" \
    -U "${DB_USER}" \
    -d "${DB_NAME}"

echo "Restore complete!"
