#!/bin/bash
# ==================================================
# LankaCommerce Cloud - Flower Entrypoint
# ==================================================
# Purpose: Start Flower web monitoring for Celery
# Dependencies: Redis
# ==================================================

set -e

# Flower settings
BROKER_URL="${CELERY_BROKER_URL:-redis://redis:6379/0}"
FLOWER_PORT="${FLOWER_PORT:-5555}"
FLOWER_BASIC_AUTH="${FLOWER_BASIC_AUTH:-admin:admin}"
FLOWER_URL_PREFIX="${FLOWER_URL_PREFIX:-}"

echo "=========================================="
echo "Starting Flower"
echo "=========================================="
echo "Broker: ${BROKER_URL}"
echo "Port: ${FLOWER_PORT}"
echo "URL Prefix: ${FLOWER_URL_PREFIX:-/}"
echo "=========================================="

# Wait for Redis
echo "Waiting for Redis..."
while ! nc -z redis 6379; do
    echo "Redis not ready, retrying..."
    sleep 1
done
echo "Redis is ready!"

# Start Flower
echo "Starting Flower monitoring..."
if [ -n "${FLOWER_URL_PREFIX}" ]; then
    exec celery --broker="${BROKER_URL}" flower \
        --port="${FLOWER_PORT}" \
        --basic_auth="${FLOWER_BASIC_AUTH}" \
        --url_prefix="${FLOWER_URL_PREFIX}"
else
    exec celery --broker="${BROKER_URL}" flower \
        --port="${FLOWER_PORT}" \
        --basic_auth="${FLOWER_BASIC_AUTH}"
fi
