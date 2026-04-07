#!/bin/bash
set -e

# ==================================================
# LankaCommerce Cloud - Backend Entrypoint
# ==================================================

echo "🚀 Starting LankaCommerce Cloud Backend..."

# Wait for PostgreSQL to be ready
if [ -n "$DATABASE_HOST" ]; then
    echo "⏳ Waiting for PostgreSQL at $DATABASE_HOST:${DATABASE_PORT:-5432}..."
    while ! nc -z "$DATABASE_HOST" "${DATABASE_PORT:-5432}"; do
        sleep 1
    done
    echo "✅ PostgreSQL is ready!"
fi

# Wait for Redis to be ready
if [ -n "$REDIS_HOST" ]; then
    echo "⏳ Waiting for Redis at $REDIS_HOST:${REDIS_PORT:-6379}..."
    while ! nc -z "$REDIS_HOST" "${REDIS_PORT:-6379}"; do
        sleep 1
    done
    echo "✅ Redis is ready!"
fi

# Run database migrations
if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "🔄 Running database migrations..."
    python manage.py migrate --noinput
fi

# Collect static files (production)
if [ "$COLLECT_STATIC" = "true" ]; then
    echo "📦 Collecting static files..."
    python manage.py collectstatic --noinput
fi

# Create superuser if not exists (development)
if [ "$CREATE_SUPERUSER" = "true" ]; then
    echo "👤 Creating superuser if not exists..."
    python manage.py createsuperuser --noinput 2>/dev/null || true
fi

echo "✅ Initialization complete!"
echo "🎯 Executing command: $@"

# Execute the main command
exec "$@"
