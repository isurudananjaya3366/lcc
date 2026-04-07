# Docker Environment Variables Guide

## Overview

LankaCommerce Cloud uses a dedicated Docker environment file (`.env.docker`) for containerized local development. This file provides Docker-specific values that differ from bare-metal local development (e.g., service hostnames use Docker Compose service names instead of `localhost`).

## Quick Start

```bash
# 1. Copy the example file
cp .env.docker.example .env.docker

# 2. (Optional) Customize values in .env.docker
#    - Generate DJANGO_SECRET_KEY
#    - Generate NEXTAUTH_SECRET

# 3. Start Docker services
docker compose up -d
```

## File Structure

| File                          | Purpose                                              | Committed?         |
| ----------------------------- | ---------------------------------------------------- | ------------------ |
| `.env.docker.example`         | Template with all Docker variables and documentation | ✅ Yes             |
| `.env.docker`                 | Active Docker env file (your local copy)             | ❌ No (gitignored) |
| `.env.example`                | Root environment template (general reference)        | ✅ Yes             |
| `backend/.env.example`        | Backend-specific env template (local dev)            | ✅ Yes             |
| `frontend/.env.example`       | Frontend-specific env template (local dev)           | ✅ Yes             |
| `frontend/.env.local.example` | Frontend detailed env template (local dev)           | ✅ Yes             |

## How Docker Env Loading Works

### Loading Order

1. **`env_file` directive** — Docker Compose loads all variables from `.env.docker` into the container environment.
2. **`environment` block** — Variables defined inline in `docker-compose.yml` override those from `env_file`. These use `${VAR:-default}` interpolation syntax.
3. **Docker Compose shell environment** — Variables set in your host shell override both of the above.

### Variable Interpolation

All services in `docker-compose.yml` use variable interpolation with defaults:

```yaml
environment:
  - DEBUG=${DEBUG:-True}
  - DATABASE_URL=${DATABASE_URL:-postgres://lcc_user:dev_password_change_me@db:5432/lankacommerce}
```

This means:

- If `DEBUG` is set in `.env.docker` → that value is used
- If `DEBUG` is **not** set → the default `True` is used

## Key Docker vs Local Differences

| Variable                      | Local Development                   | Docker Development                    |
| ----------------------------- | ----------------------------------- | ------------------------------------- |
| `DB_HOST`                     | `localhost`                         | `db` (service name)                   |
| `REDIS_HOST`                  | `localhost`                         | `redis` (service name)                |
| `REDIS_URL`                   | `redis://localhost:6379/0`          | `redis://redis:6379/0`                |
| `DATABASE_URL`                | `postgres://...@localhost:5432/...` | `postgres://...@db:5432/...`          |
| `CELERY_BROKER_URL`           | `redis://localhost:6379/0`          | `redis://redis:6379/0`                |
| `API_BASE_URL` (frontend SSR) | `http://localhost:8000/api/v1`      | `http://backend:8000/api/v1`          |
| `DJANGO_ALLOWED_HOSTS`        | `localhost,127.0.0.1`               | `localhost,127.0.0.1,backend,0.0.0.0` |

> **Why?** Inside the Docker network, containers communicate using service names defined in `docker-compose.yml` (e.g., `db`, `redis`, `backend`). The browser still accesses services via `localhost` because ports are mapped to the host.

## Service Environment Variable Mapping

### Backend (Django)

| Variable                 | Default                                         | Used By               |
| ------------------------ | ----------------------------------------------- | --------------------- |
| `DEBUG`                  | `True`                                          | Django debug mode     |
| `DJANGO_SETTINGS_MODULE` | `config.settings.local`                         | Settings module path  |
| `DJANGO_SECRET_KEY`      | (placeholder)                                   | Django secret key     |
| `DJANGO_ALLOWED_HOSTS`   | `localhost,127.0.0.1,backend,0.0.0.0`           | Allowed hosts         |
| `DATABASE_URL`           | `postgres://lcc_user:...@db:5432/lankacommerce` | Database connection   |
| `REDIS_URL`              | `redis://redis:6379/0`                          | Redis connection      |
| `CELERY_BROKER_URL`      | `redis://redis:6379/0`                          | Celery message broker |

### Frontend (Next.js)

| Variable               | Default                        | Exposed to Browser? |
| ---------------------- | ------------------------------ | ------------------- |
| `NODE_ENV`             | `development`                  | No (server)         |
| `NEXT_PUBLIC_API_URL`  | `http://localhost:8000/api/v1` | ✅ Yes (client)     |
| `NEXT_PUBLIC_SITE_URL` | `http://localhost:3000`        | ✅ Yes (client)     |
| `API_BASE_URL`         | `http://backend:8000/api/v1`   | ❌ No (SSR only)    |
| `WATCHPACK_POLLING`    | `true`                         | No (server)         |

> **Important:** Variables with `NEXT_PUBLIC_` prefix are exposed to the browser. Never put secrets in `NEXT_PUBLIC_` variables. Server-side variables like `API_BASE_URL` use the Docker service name (`backend`) for internal network communication.

### Database (PostgreSQL)

| Variable            | Default                  | Description        |
| ------------------- | ------------------------ | ------------------ |
| `POSTGRES_DB`       | `lankacommerce`          | Database name      |
| `POSTGRES_USER`     | `postgres`               | Superuser name     |
| `POSTGRES_PASSWORD` | `dev_password_change_me` | Superuser password |

> **Note:** These are Docker-only defaults for local development. Never use these credentials in production.

### Redis

Redis does not require environment variables in the default configuration. It uses the `redis.conf` file mounted from `docker/redis/redis.conf`.

Services that **depend on Redis**:

- `backend` — cache layer (`REDIS_URL`)
- `celery-worker` — message broker (`CELERY_BROKER_URL`)
- `celery-beat` — periodic task scheduler (via broker)
- `flower` — monitoring dashboard (`CELERY_BROKER_URL`)

### Celery (Worker, Beat, Flower)

| Variable                | Default                                           | Service              |
| ----------------------- | ------------------------------------------------- | -------------------- |
| `CELERY_APP`            | `config.celery:app`                               | Worker, Beat         |
| `CELERY_BROKER_URL`     | `redis://redis:6379/0`                            | Worker, Beat, Flower |
| `CELERY_RESULT_BACKEND` | `redis://redis:6379/0`                            | Worker               |
| `CELERY_CONCURRENCY`    | `2`                                               | Worker               |
| `CELERY_QUEUES`         | `default,high_priority,low_priority`              | Worker               |
| `CELERY_LOG_LEVEL`      | `info`                                            | Worker, Beat         |
| `CELERY_BEAT_SCHEDULER` | `django_celery_beat.schedulers:DatabaseScheduler` | Beat                 |
| `FLOWER_PORT`           | `5555`                                            | Flower               |
| `FLOWER_BASIC_AUTH`     | `admin:admin`                                     | Flower               |

## Verification

### Test Docker Env Loading

```bash
# 1. Start services
docker compose up -d

# 2. Verify backend reads env variables
docker compose exec backend env | grep -E "^(DEBUG|DJANGO_|DATABASE_URL|REDIS_URL|CELERY_)"

# 3. Verify frontend reads env variables
docker compose exec frontend env | grep -E "^(NODE_ENV|NEXT_PUBLIC_|API_BASE_URL)"

# 4. Verify database variables
docker compose exec db env | grep -E "^POSTGRES_"

# 5. Verify Celery worker connects to Redis
docker compose logs celery-worker | head -30

# 6. Verify Celery beat is scheduling
docker compose logs celery-beat | head -20

# 7. Check Flower dashboard
curl -s http://localhost:5555/api/workers | head -5
```

### Expected Results

- Backend container shows correct `DATABASE_URL` with host `db`
- Frontend container shows `NEXT_PUBLIC_API_URL` with `localhost:8000`
- Frontend container shows `API_BASE_URL` with `backend:8000` (SSR)
- Database container shows `POSTGRES_DB=lankacommerce`
- Celery worker logs show successful connection to Redis broker
- Flower dashboard is accessible at `http://localhost:5555`

### Troubleshooting

| Issue                               | Solution                                                               |
| ----------------------------------- | ---------------------------------------------------------------------- |
| `.env.docker` not found             | Run `cp .env.docker.example .env.docker`                               |
| Variables not loading               | Check `env_file: - .env.docker` in compose                             |
| Celery can't connect to Redis       | Verify `CELERY_BROKER_URL` uses `redis://redis:6379/0`                 |
| Frontend SSR fails to reach backend | Check `API_BASE_URL` uses `http://backend:8000/api/v1`                 |
| Database auth failure               | Ensure `POSTGRES_PASSWORD` matches in `.env.docker` and `DATABASE_URL` |

## Related Documentation

- [Docker Development Setup](docker-setup.md) — Full Docker development guide
- [Secrets Management](SECRETS.md) — Secrets classification, rotation, and security checklists
- [Root .env.example](../.env.example) — General environment template
- [Backend .env.example](../backend/.env.example) — Backend-specific variables
- [Frontend .env.local.example](../frontend/.env.local.example) — Frontend-specific variables
