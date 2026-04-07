#!/bin/bash
# ==================================================
# LankaCommerce Cloud - Celery Health Check
# ==================================================
# Purpose: Check Celery worker health
# Usage: Docker HEALTHCHECK instruction
# Exit: 0 = healthy, 1 = unhealthy
# ==================================================

set -e

APP_NAME="${CELERY_APP:-config.celery:app}"
TIMEOUT="${CELERY_HEALTH_TIMEOUT:-5}"

# Check if workers are responding
RESULT=$(celery -A "${APP_NAME}" inspect ping --timeout="${TIMEOUT}" 2>/dev/null)

if echo "${RESULT}" | grep -q "pong"; then
    echo "Celery workers are healthy"
    exit 0
else
    echo "Celery workers are unhealthy"
    exit 1
fi
