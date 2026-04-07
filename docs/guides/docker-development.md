# Docker Development

> Docker-based development workflow using Docker Compose.

**Navigation:** [Getting Started](getting-started.md) · [Development Setup](development-setup.md) · [Docs Index](../index.md)

---

## Overview

LankaCommerce Cloud provides a complete Docker Compose setup with 7 services for fully containerized development. This eliminates the need to install PostgreSQL, Redis, or other dependencies locally.

---

## Services

| Service           | Image                    | Port | Description                 |
| ----------------- | ------------------------ | ---- | --------------------------- |
| **backend**       | Custom (Dockerfile.dev)  | 8000 | Django development server   |
| **frontend**      | Custom (Dockerfile.dev)  | 3000 | Next.js development server  |
| **db**            | PostgreSQL 15            | 5432 | Primary database            |
| **redis**         | Redis 7                  | 6379 | Cache and message broker    |
| **celery-worker** | Custom (same as backend) | —    | Async task processing       |
| **celery-beat**   | Custom (same as backend) | —    | Scheduled task scheduling   |
| **flower**        | Custom (same as backend) | 5555 | Celery monitoring dashboard |

---

## Getting Started

### 1. Prerequisites

Ensure Docker (24+) and Docker Compose (2.20+) are installed:

1. Verify Docker: `docker --version`
2. Verify Docker Compose: `docker compose version`

### 2. Environment Configuration

1. Copy the override example: `cp docker-compose.override.example.yml docker-compose.override.yml`
2. Copy the backend env file: `cp backend/.env.example backend/.env`
3. Edit `backend/.env` to set any required values (defaults work for Docker)

### 3. Build and Start

1. Build all service images: `docker compose build`
2. Start all services in the background: `docker compose up -d`
3. Watch the logs: `docker compose logs -f`

### 4. Initial Setup

1. Run database migrations: `docker compose exec backend python manage.py migrate`
2. Create a superuser: `docker compose exec backend python manage.py createsuperuser`
3. Optionally load fixtures: `docker compose exec backend python manage.py loaddata fixtures/*.json`

---

## Common Commands

### Service Management

| Action                  | Command                          |
| ----------------------- | -------------------------------- |
| Start all services      | `docker compose up -d`           |
| Stop all services       | `docker compose down`            |
| Restart a service       | `docker compose restart backend` |
| View logs (all)         | `docker compose logs -f`         |
| View logs (one service) | `docker compose logs -f backend` |
| Check service status    | `docker compose ps`              |
| Rebuild images          | `docker compose build`           |
| Rebuild and restart     | `docker compose up -d --build`   |

### Backend Commands

| Action               | Command                                                                |
| -------------------- | ---------------------------------------------------------------------- |
| Run migrations       | `docker compose exec backend python manage.py migrate`                 |
| Create superuser     | `docker compose exec backend python manage.py createsuperuser`         |
| Make migrations      | `docker compose exec backend python manage.py makemigrations`          |
| Django shell         | `docker compose exec backend python manage.py shell`                   |
| Run tests            | `docker compose exec backend python -m pytest`                         |
| Collect static files | `docker compose exec backend python manage.py collectstatic --noinput` |

### Frontend Commands

| Action           | Command                                     |
| ---------------- | ------------------------------------------- |
| Install packages | `docker compose exec frontend pnpm install` |
| Run tests        | `docker compose exec frontend pnpm test`    |
| Build production | `docker compose exec frontend pnpm build`   |
| Lint             | `docker compose exec frontend pnpm lint`    |

### Database Commands

| Action                  | Command                                                                |
| ----------------------- | ---------------------------------------------------------------------- |
| Access PostgreSQL shell | `docker compose exec db psql -U postgres -d lcc-dev`                   |
| Dump database           | `docker compose exec db pg_dump -U postgres lcc-dev > backup.sql`      |
| Restore database        | `cat backup.sql \| docker compose exec -T db psql -U postgres lcc-dev` |

---

## Service URLs

Once running, access the services at:

| Service     | URL                                | Description               |
| ----------- | ---------------------------------- | ------------------------- |
| Backend API | `http://localhost:8000/`           | Django development server |
| Admin Panel | `http://localhost:8000/admin/`     | Django admin interface    |
| Swagger UI  | `http://localhost:8000/api/docs/`  | Interactive API docs      |
| ReDoc       | `http://localhost:8000/api/redoc/` | Read-only API docs        |
| Frontend    | `http://localhost:3000/`           | Next.js application       |
| Flower      | `http://localhost:5555/`           | Celery task monitoring    |

---

## Volume Mounts

Docker Compose mounts local directories into containers for live reloading:

| Local Path                     | Container Path              | Service  | Purpose              |
| ------------------------------ | --------------------------- | -------- | -------------------- |
| `./backend/`                   | `/app/`                     | backend  | Backend source code  |
| `./frontend/`                  | `/app/`                     | frontend | Frontend source code |
| `postgres_data` (named volume) | `/var/lib/postgresql/data/` | db       | Database persistence |
| `redis_data` (named volume)    | `/data/`                    | redis    | Redis persistence    |

---

## Troubleshooting

| Issue                           | Solution                                                                   |
| ------------------------------- | -------------------------------------------------------------------------- |
| Port already in use             | Stop conflicting services or change ports in `docker-compose.override.yml` |
| Database connection refused     | Wait for the db service to be healthy: `docker compose ps`                 |
| Permission denied on volumes    | On Linux, ensure your user has Docker group membership                     |
| Stale containers                | Remove all containers and volumes: `docker compose down -v`                |
| Build cache issues              | Force a clean build: `docker compose build --no-cache`                     |
| Frontend hot reload not working | Ensure the `frontend/` directory is mounted correctly                      |

---

## Production vs Development

| Aspect              | Development                       | Production                        |
| ------------------- | --------------------------------- | --------------------------------- |
| Compose file        | `docker-compose.yml` + `override` | `docker-compose.prod.yml`         |
| Backend Dockerfile  | `docker/backend/Dockerfile.dev`   | `docker/backend/Dockerfile.prod`  |
| Frontend Dockerfile | `docker/frontend/Dockerfile.dev`  | `docker/frontend/Dockerfile.prod` |
| Debug mode          | Enabled                           | Disabled                          |
| Hot reloading       | Enabled (volume mounts)           | Disabled (built images)           |
| Static files        | Django dev server                 | Nginx + WhiteNoise                |

---

## Related Documentation

- [Getting Started](getting-started.md) — Quick onboarding overview
- [Development Setup](development-setup.md) — Non-Docker local setup
- [Docker Setup Reference](../docker-setup.md) — Detailed Docker environment docs
- [Docker Environment Variables](../DOCKER_ENV.md) — Docker-specific env config
- [Docs Index](../index.md) — Documentation hub
