# Docker Development Environment

## Overview

LankaCommerce Cloud uses Docker and Docker Compose to provide a consistent development environment across all platforms.

## Prerequisites

- Docker Desktop 24.x or later
- Docker Compose v2 (included with Docker Desktop)
- 8GB RAM minimum (16GB recommended)
- 20GB disk space

## Quick Start

```bash
# Clone repository
git clone <repository-url>
cd lankacommerce-cloud

# Copy Docker environment file
cp .env.docker.example .env.docker

# Start development environment
make dev

# Or using the dev script
./docker/scripts/dev-start.sh
```

## Services

| Service       | Container         | URL                   | Description                 |
| ------------- | ----------------- | --------------------- | --------------------------- |
| Backend       | lcc-backend       | http://localhost:8000 | Django REST API             |
| Frontend      | lcc-frontend      | http://localhost:3000 | Next.js Application         |
| PostgreSQL    | lcc-postgres      | localhost:5432        | Database                    |
| Redis         | lcc-redis         | localhost:6379        | Cache & Message Broker      |
| Celery Worker | lcc-celery-worker | -                     | Background Task Processing  |
| Celery Beat   | lcc-celery-beat   | -                     | Periodic Task Scheduler     |
| Flower        | lcc-flower        | http://localhost:5555 | Celery Monitoring Dashboard |

## Common Commands

### Using Makefile

```bash
# Start environment
make up

# Start with rebuild
make up-build

# Stop environment
make down

# View all logs
make logs

# View specific service logs
make logs-backend
make logs-frontend
make logs-service s=redis

# Backend shell
make shell-backend

# Database shell
make dbshell

# Run migrations
make migrate

# Create superuser
make createsuperuser

# Reset database (destroys all data)
make db-reset

# Run Django management command
make manage cmd="check"

# Show container status
make status

# Clean Docker resources
make docker-clean
```

### Using Docker Compose

```bash
# Start all services
docker compose up -d

# Build and start
docker compose up -d --build

# Stop all services
docker compose down

# Stop and remove volumes
docker compose down -v

# View logs
docker compose logs -f [service]

# Execute command in container
docker compose exec backend python manage.py <command>

# Open shell in container
docker compose exec backend bash
docker compose exec frontend sh
```

### Using Dev Scripts

```bash
# Start with health checks and status
./docker/scripts/dev-start.sh

# Start with build
./docker/scripts/dev-start.sh --build

# Start in detached mode
./docker/scripts/dev-start.sh --detach

# Stop gracefully
./docker/scripts/dev-stop.sh

# Stop and remove volumes
./docker/scripts/dev-stop.sh --clean

# Stop and prune Docker system
./docker/scripts/dev-stop.sh --prune

# Wait for a service to be ready
./docker/scripts/wait-for-it.sh db:5432 -t 60 -- echo "DB is ready"

# Reset database
./docker/scripts/db-reset.sh
```

## Environment Variables

Copy `.env.docker.example` to `.env.docker` and configure. See [DOCKER_ENV.md](DOCKER_ENV.md) for full documentation and [SECRETS.md](SECRETS.md) for secrets management policy.

> **Note:** Docker services use `.env.docker` (not `.env`). Service hostnames use Docker Compose service names (e.g., `db`, `redis`, `backend`). Never commit `.env.docker` — see [SECRETS.md](SECRETS.md) for handling guidelines.

| Variable                 | Default                                         | Description                  |
| ------------------------ | ----------------------------------------------- | ---------------------------- |
| `DJANGO_SECRET_KEY`      | (generated)                                     | Django secret key            |
| `DJANGO_SETTINGS_MODULE` | `config.settings.local`                         | Django settings module       |
| `DEBUG`                  | `True`                                          | Enable debug mode            |
| `DATABASE_URL`           | `postgres://lcc_user:...@db:5432/lankacommerce` | PostgreSQL connection        |
| `REDIS_URL`              | `redis://redis:6379/0`                          | Redis connection             |
| `CELERY_BROKER_URL`      | `redis://redis:6379/0`                          | Celery broker URL            |
| `CELERY_RESULT_BACKEND`  | `redis://redis:6379/1`                          | Celery result backend        |
| `CELERY_CONCURRENCY`     | `2`                                             | Celery worker concurrency    |
| `CELERY_LOG_LEVEL`       | `info`                                          | Celery log level             |
| `FLOWER_BASIC_AUTH`      | `admin:admin`                                   | Flower dashboard credentials |
| `TZ`                     | `Asia/Colombo`                                  | Container timezone           |

## Development Workflow

### Hot Reload

Both backend and frontend support hot reload in development:

- **Backend:** Django's runserver auto-reloads on Python file changes
- **Frontend:** Next.js Fast Refresh updates on save (with `WATCHPACK_POLLING=true` for Docker)

### Database Operations

```bash
# Run migrations
make migrate

# Create migrations
make makemigrations

# Reset database (destroys all data)
make db-reset

# Access PostgreSQL shell
make dbshell

# Backup database
docker compose exec db /docker-entrypoint-initdb.d/../backup.sh

# Restore database
docker compose exec db /docker-entrypoint-initdb.d/../restore.sh <backup-file>
```

### Running Tests

```bash
# All tests
make test

# Backend tests only
make test-backend

# Frontend tests only
make test-frontend

# Backend with coverage
make coverage
```

### Code Quality

```bash
# Run all linters
make lint

# Format all code
make format

# Check formatting
make format-check
```

## Docker File Structure

```
docker/
├── backend/
│   ├── Dockerfile.dev          # Development Dockerfile
│   ├── Dockerfile.prod         # Production Dockerfile
│   └── entrypoint.sh           # Backend entrypoint script
├── frontend/
│   ├── Dockerfile.dev          # Development Dockerfile
│   └── Dockerfile.prod         # Production Dockerfile
├── postgres/
│   ├── init.sql                # Database initialization
│   ├── postgresql.conf         # PostgreSQL configuration
│   ├── backup.sh               # Database backup script
│   └── restore.sh              # Database restore script
├── redis/
│   ├── redis.conf              # Redis configuration
│   └── healthcheck.sh          # Redis health check
├── nginx/
│   └── .gitkeep                # Placeholder for reverse proxy
└── scripts/
    ├── celery-worker.sh        # Celery worker entrypoint
    ├── celery-beat.sh          # Celery beat entrypoint
    ├── celery-health.sh        # Celery health check
    ├── flower.sh               # Flower entrypoint
    ├── dev-start.sh            # Development start script
    ├── dev-stop.sh             # Development stop script
    ├── wait-for-it.sh          # Wait for service utility
    └── db-reset.sh             # Database reset script

(root)/
├── docker-compose.yml                  # Main compose configuration
├── docker-compose.prod.yml             # Production overrides
├── docker-compose.override.example.yml # Local override template
├── .dockerignore                       # Docker build exclusions
├── .env.example                        # General environment template
├── .env.docker.example                 # Docker-specific env template (committed)
├── .env.docker                         # Docker-specific env file (gitignored)
└── Makefile                            # Make targets
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Docker Network (lankacommerce-network)       │
│                                                                 │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐    │
│  │ Backend  │   │ Frontend │   │  Redis   │   │ Postgres │    │
│  │  :8000   │◄──│  :3000   │   │  :6379   │   │  :5432   │    │
│  └────┬─────┘   └──────────┘   └────┬─────┘   └────┬─────┘    │
│       │                             │              │           │
│       ├─────────────────────────────┤              │           │
│       │                             │              │           │
│  ┌────┴─────┐   ┌──────────┐   ┌───┴──────┐      │           │
│  │  Celery  │   │  Celery  │   │  Flower  │      │           │
│  │  Worker  │   │   Beat   │   │  :5555   │      │           │
│  └────┬─────┘   └────┬─────┘   └──────────┘      │           │
│       │              │                            │           │
│       └──────────────┴────────────────────────────┘           │
│                                                                 │
│  Named Volumes:                                                 │
│  • lcc-postgres-data    • lcc-backend-static                   │
│  • lcc-redis-data       • lcc-backend-media                    │
└─────────────────────────────────────────────────────────────────┘
```

## Health Checks

| Service       | Method                                     | Interval |
| ------------- | ------------------------------------------ | -------- |
| PostgreSQL    | `pg_isready -U postgres`                   | 10s      |
| Redis         | `redis-cli ping`                           | 10s      |
| Backend       | `curl -f http://localhost:8000/health/`    | 30s      |
| Frontend      | `curl -f http://localhost:3000/api/health` | 30s      |
| Celery Worker | `celery -A config.celery inspect ping`     | 30s      |

## Troubleshooting

### Container Won't Start

```bash
# Check logs for the failing service
docker compose logs [service]

# Rebuild from scratch
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

### Port Already in Use

```bash
# Find process using the port (Windows)
netstat -ano | findstr :8000

# Find process using the port (Linux/Mac)
lsof -i :8000

# Use docker-compose.override.yml to change ports
cp docker-compose.override.example.yml docker-compose.override.yml
# Edit ports as needed
```

### Database Connection Error

1. Ensure PostgreSQL container is healthy: `docker compose ps db`
2. Check `DATABASE_URL` in `.env.docker`
3. Wait for initialization to complete (first run takes longer)
4. Try resetting: `make db-reset`

### Redis Connection Error

1. Check Redis container: `docker compose ps redis`
2. Test connectivity: `docker compose exec redis redis-cli ping`
3. Check `REDIS_URL` in `.env.docker`

### Celery Worker Not Processing Tasks

1. Check worker logs: `docker compose logs celery-worker`
2. Verify Redis is running: `docker compose exec redis redis-cli ping`
3. Check Flower dashboard: http://localhost:5555
4. Restart worker: `docker compose restart celery-worker`

### Build Failures

```bash
# Clear Docker build cache
docker builder prune

# Rebuild without cache
docker compose build --no-cache

# Check Dockerfile syntax
docker compose config
```

### Volume Permission Issues (Linux)

```bash
# Fix ownership
sudo chown -R $USER:$USER .

# Or run with current user
docker compose run --user $(id -u):$(id -g) backend <command>
```

## Production Deployment

For production, use the production compose file:

```bash
# Build production images
docker compose -f docker-compose.yml -f docker-compose.prod.yml build

# Start production services
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Or use Makefile
make prod-build
make prod-up
```

See the production compose file (`docker-compose.prod.yml`) for resource limits, replicas, and security settings.
