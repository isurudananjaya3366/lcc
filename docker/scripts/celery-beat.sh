#!/bin/bash
# ==================================================
# LankaCommerce Cloud - Celery Beat Entrypoint
# ==================================================
# Purpose: Start Celery Beat for scheduled tasks
# Dependencies: Redis, PostgreSQL
# ==================================================

set -e

# Configuration
APP_NAME="${CELERY_APP:-config.celery:app}"
LOG_LEVEL="${CELERY_LOG_LEVEL:-info}"
SCHEDULER="${CELERY_BEAT_SCHEDULER:-django_celery_beat.schedulers:DatabaseScheduler}"
PID_FILE="${CELERY_BEAT_PID:-/tmp/celerybeat.pid}"

echo "=========================================="
echo "Starting Celery Beat"
echo "=========================================="
echo "App: ${APP_NAME}"
echo "Scheduler: ${SCHEDULER}"
echo "Log Level: ${LOG_LEVEL}"
echo "=========================================="

# Wait for Redis
echo "Waiting for Redis..."
while ! nc -z redis 6379; do
    echo "Redis not ready, retrying..."
    sleep 1
done
echo "Redis is ready!"

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
    echo "PostgreSQL not ready, retrying..."
    sleep 1
done
echo "PostgreSQL is ready!"

# Clean up stale PID file
rm -f "${PID_FILE}"

# Start Celery Beat
echo "Starting Celery Beat..."
exec celery -A "${APP_NAME}" beat \
    --loglevel="${LOG_LEVEL}" \
    --scheduler="${SCHEDULER}" \
    --pidfile="${PID_FILE}"
