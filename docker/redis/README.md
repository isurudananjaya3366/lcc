# Redis Docker Configuration

Configuration files for the Redis container used for caching and Celery message broker.

## Usage

Redis serves two purposes in LCC:
1. **Caching** - Django cache backend
2. **Message Broker** - Celery task queue

## Configuration

For development, default Redis configuration is sufficient.
For production, custom redis.conf may be needed.

## Files (if needed)

- `redis.conf` - Custom Redis configuration (optional)

## Connection

- Host: redis (Docker network)
- Port: 6379
- Database 0: Django cache
- Database 1: Celery broker
