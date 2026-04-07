#!/bin/bash
# ==================================================
# LankaCommerce Cloud - Celery Worker Entrypoint
# ==================================================
# Purpose: Start Celery worker for background tasks
# Dependencies: Redis, PostgreSQL
# ==================================================

set -e

# Configuration from environment
APP_NAME="${CELERY_APP:-config.celery:app}"
CONCURRENCY="${CELERY_CONCURRENCY:-2}"
QUEUES="${CELERY_QUEUES:-default,high_priority,low_priority}"
LOG_LEVEL="${CELERY_LOG_LEVEL:-info}"
WORKER_NAME="${CELERY_WORKER_NAME:-worker@%h}"

echo "=========================================="
echo "Starting Celery Worker"
echo "=========================================="
echo "App: ${APP_NAME}"
echo "Concurrency: ${CONCURRENCY}"
echo "Queues: ${QUEUES}"
echo "Log Level: ${LOG_LEVEL}"
echo "Worker Name: ${WORKER_NAME}"
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
while ! nc -z postgres 5432; do
    echo "PostgreSQL not ready, retrying..."
    sleep 1
done
echo "PostgreSQL is ready!"

# Start Celery worker
echo "Starting Celery worker..."
exec celery -A "${APP_NAME}" worker \
    --loglevel="${LOG_LEVEL}" \
    --concurrency="${CONCURRENCY}" \
    --queues="${QUEUES}" \
    --hostname="${WORKER_NAME}" \
    --events
