# Development Setup

> Full local development environment setup for backend, frontend, and database.

**Navigation:** [Getting Started](getting-started.md) · [Docker Development](docker-development.md) · [Docs Index](../index.md)

---

## Overview

This guide covers setting up the LankaCommerce Cloud project **without Docker** — running the backend, frontend, and database directly on your machine. For a Docker-based setup, see the [Docker Development Guide](docker-development.md).

---

## 1. Clone the Repository

1. Clone the project: `git clone https://github.com/your-org/lankacommerce-cloud.git`
2. Change into the project directory: `cd lankacommerce-cloud`

---

## 2. Backend Setup

### 2a. Create a Python Virtual Environment

1. Navigate to the backend directory: `cd backend`
2. Create a virtual environment: `python -m venv .venv`
3. Activate it on Windows: `.venv\Scripts\activate`
4. Activate it on macOS/Linux: `source .venv/bin/activate`

### 2b. Install Dependencies

1. Install base requirements: `pip install -r requirements/base.txt`
2. Install local development extras: `pip install -r requirements/local.txt`

### 2c. Configure Environment Variables

1. Copy the example env file: `cp .env.example .env`
2. Edit `.env` and set the following values:

| Variable            | Example Value              | Description                   |
| ------------------- | -------------------------- | ----------------------------- |
| `DJANGO_SECRET_KEY` | (generate a random key)    | Django secret key             |
| `DEBUG`             | `True`                     | Enable debug mode             |
| `ALLOWED_HOSTS`     | `localhost,127.0.0.1`      | Comma-separated allowed hosts |
| `DB_NAME`           | `lcc_dev`                  | PostgreSQL database name      |
| `DB_USER`           | `postgres`                 | Database user                 |
| `DB_PASSWORD`       | `postgres`                 | Database password             |
| `DB_HOST`           | `localhost`                | Database host                 |
| `DB_PORT`           | `5432`                     | Database port                 |
| `REDIS_URL`         | `redis://localhost:6379/0` | Redis connection URL          |
| `CELERY_BROKER_URL` | `redis://localhost:6379/1` | Celery broker URL             |

> See [Environment Variable Reference](../ENV_VARIABLES.md) for the complete list.

### 2d. Set Up the Database

1. Ensure PostgreSQL is running on your machine
2. Create the database: `createdb lcc_dev`
3. Run migrations: `python manage.py migrate`
4. Create a superuser: `python manage.py createsuperuser`
5. Optionally load fixtures: `python manage.py loaddata fixtures/*.json`

### 2e. Start the Backend Server

1. Run the development server: `python manage.py runserver`
2. The backend is now available at `http://localhost:8000/`
3. Visit the admin panel at `http://localhost:8000/admin/`
4. Visit the API docs at `http://localhost:8000/api/docs/`

---

## 3. Frontend Setup

### 3a. Install Dependencies

1. Navigate to the frontend directory: `cd frontend`
2. Install packages with pnpm: `pnpm install`

### 3b. Configure Environment Variables

1. Copy the example env file: `cp .env.example .env.local`
2. Edit `.env.local` and set the following:

| Variable               | Example Value                  | Description              |
| ---------------------- | ------------------------------ | ------------------------ |
| `NEXT_PUBLIC_API_URL`  | `http://localhost:8000/api/v1` | Backend API base URL     |
| `NEXT_PUBLIC_APP_NAME` | `LankaCommerce Cloud`          | Application display name |

### 3c. Start the Frontend Server

1. Run the development server: `pnpm dev`
2. The frontend is now available at `http://localhost:3000/`

---

## 4. Running Background Services

### 4a. Redis

1. Start Redis on your machine: `redis-server`
2. Verify it is running: `redis-cli ping` (should return PONG)

### 4b. Celery Worker

1. Navigate to the backend directory: `cd backend`
2. Activate the virtual environment
3. Start the Celery worker: `celery -A config worker -l info`

### 4c. Celery Beat (Scheduled Tasks)

1. In a separate terminal, navigate to the backend directory
2. Start Celery Beat: `celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler`

---

## 5. Verification

After setup, verify everything is working:

| Check          | Command / URL                           | Expected Result         |
| -------------- | --------------------------------------- | ----------------------- |
| Backend health | Visit `http://localhost:8000/health/`   | Health check response   |
| Admin panel    | Visit `http://localhost:8000/admin/`    | Django admin login page |
| API docs       | Visit `http://localhost:8000/api/docs/` | Swagger UI              |
| Frontend       | Visit `http://localhost:3000/`          | Next.js application     |
| Redis          | Run `redis-cli ping`                    | PONG                    |

---

## Troubleshooting

| Issue                       | Solution                                                                   |
| --------------------------- | -------------------------------------------------------------------------- |
| `ModuleNotFoundError`       | Ensure the virtual environment is activated and dependencies are installed |
| Database connection refused | Verify PostgreSQL is running and `.env` credentials are correct            |
| Redis connection error      | Ensure Redis is running on the configured port                             |
| Frontend build errors       | Delete `node_modules` and `.next`, then run `pnpm install` again           |
| Port already in use         | Check for other services on ports 8000/3000 and stop them                  |

---

## Related Documentation

- [Getting Started](getting-started.md) — Quick onboarding overview
- [Docker Development](docker-development.md) — Docker-based alternative setup
- [Database Guide](database.md) — Migrations, seeding, and backups
- [Environment Variable Reference](../ENV_VARIABLES.md) — Complete variable documentation
- [Docs Index](../index.md) — Documentation hub
