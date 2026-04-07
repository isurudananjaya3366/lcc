# Troubleshooting Guide

> Common issues, error messages, and resolution steps for LankaCommerce Cloud.

**Navigation:** [Debugging](debugging.md) · [Deployment](deployment.md) · [Docs Index](../index.md)

---

## Overview

This guide covers common issues encountered during development and production, organized by category. Each issue includes symptoms, likely causes, and step-by-step resolution.

---

## Environment Issues

### Python Virtual Environment Not Activated

**Symptoms:** `ModuleNotFoundError` when running Django commands.

| Step | Action                                                                                                            |
| ---- | ----------------------------------------------------------------------------------------------------------------- |
| 1    | Navigate to the backend directory: `cd backend`                                                                   |
| 2    | Activate the virtual environment: `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (macOS/Linux) |
| 3    | Verify activation: `which python` should point to the `.venv` directory                                           |

### Node Modules Missing

**Symptoms:** `Cannot find module` errors in the frontend.

| Step | Action                                                                                        |
| ---- | --------------------------------------------------------------------------------------------- |
| 1    | Navigate to the frontend directory: `cd frontend`                                             |
| 2    | Install dependencies: `pnpm install`                                                          |
| 3    | If issues persist, delete `node_modules` and reinstall: `rm -rf node_modules && pnpm install` |

### Environment Variables Not Set

**Symptoms:** `ImproperlyConfigured` or `KeyError` on startup.

| Step | Action                                                                        |
| ---- | ----------------------------------------------------------------------------- |
| 1    | Verify `.env` file exists in the backend directory                            |
| 2    | Compare your `.env` against `.env.example` for missing variables              |
| 3    | See [Environment Variable Reference](../ENV_VARIABLES.md) for required values |

---

## Database Issues

### Connection Refused

**Symptoms:** `could not connect to server: Connection refused`

| Step | Action                                                                             |
| ---- | ---------------------------------------------------------------------------------- |
| 1    | Verify PostgreSQL is running: `pg_isready` (local) or `docker compose ps` (Docker) |
| 2    | Check `DB_HOST` and `DB_PORT` in your `.env` file                                  |
| 3    | In Docker, ensure the `db` service is healthy before the backend starts            |
| 4    | Try restarting the database: `docker compose restart db`                           |

### Migration Conflicts

**Symptoms:** `django.db.migrations.exceptions.InconsistentMigrationHistory`

| Step | Action                                                                                               |
| ---- | ---------------------------------------------------------------------------------------------------- |
| 1    | Check migration status: `python manage.py showmigrations`                                            |
| 2    | If migrations are out of sync, try: `python manage.py migrate --run-syncdb`                          |
| 3    | In development, you can reset: `python manage.py migrate <app> zero` then `python manage.py migrate` |
| 4    | For persistent issues, drop and recreate the database (development only)                             |

### Database Does Not Exist

**Symptoms:** `FATAL: database "lcc_dev" does not exist`

| Step | Action                                                                    |
| ---- | ------------------------------------------------------------------------- |
| 1    | Create the database: `createdb lcc_dev` (local)                           |
| 2    | In Docker, the database is created automatically by the `init.sql` script |
| 3    | If using Docker, try: `docker compose down -v && docker compose up -d`    |

---

## Redis Issues

### Connection Error

**Symptoms:** `redis.exceptions.ConnectionError: Error connecting to Redis`

| Step | Action                                                                  |
| ---- | ----------------------------------------------------------------------- |
| 1    | Verify Redis is running: `redis-cli ping` should return `PONG`          |
| 2    | In Docker: `docker compose ps` should show the redis service as running |
| 3    | Check `REDIS_URL` in your `.env` file                                   |
| 4    | Restart Redis: `docker compose restart redis`                           |

---

## Backend Issues

### Import Errors on Startup

**Symptoms:** `ImportError` or `ModuleNotFoundError` when starting the server.

| Step | Action                                                                |
| ---- | --------------------------------------------------------------------- |
| 1    | Ensure the virtual environment is activated                           |
| 2    | Install missing dependencies: `pip install -r requirements/base.txt`  |
| 3    | For local development extras: `pip install -r requirements/local.txt` |
| 4    | Check for typos in `INSTALLED_APPS` in the settings                   |

### Static Files Not Loading

**Symptoms:** Admin panel appears unstyled, 404 errors for static files.

| Step | Action                                                           |
| ---- | ---------------------------------------------------------------- |
| 1    | Collect static files: `python manage.py collectstatic --noinput` |
| 2    | Verify `STATIC_URL` and `STATIC_ROOT` in settings                |
| 3    | In development, WhiteNoise serves static files automatically     |

### CORS Errors

**Symptoms:** Browser console shows `Access-Control-Allow-Origin` errors.

| Step | Action                                                                     |
| ---- | -------------------------------------------------------------------------- |
| 1    | In local development, verify `CORS_ALLOW_ALL_ORIGINS = True` in `local.py` |
| 2    | In production, verify `CORS_ALLOWED_ORIGINS` includes the frontend domain  |
| 3    | Verify `corsheaders.middleware.CorsMiddleware` is in `MIDDLEWARE`          |
| 4    | Clear the browser cache and retry                                          |

---

## Frontend Issues

### Build Failures

**Symptoms:** `pnpm build` fails with TypeScript or module errors.

| Step | Action                                                                     |
| ---- | -------------------------------------------------------------------------- |
| 1    | Delete `.next` directory: `rm -rf .next`                                   |
| 2    | Delete `node_modules` and reinstall: `rm -rf node_modules && pnpm install` |
| 3    | Check for TypeScript errors: `pnpm tsc --noEmit`                           |
| 4    | Verify environment variables in `.env.local`                               |

### Hot Reload Not Working

**Symptoms:** Changes to files do not appear in the browser automatically.

| Step | Action                                                                         |
| ---- | ------------------------------------------------------------------------------ |
| 1    | Verify the dev server is running: `pnpm dev`                                   |
| 2    | In Docker, ensure the frontend directory is volume-mounted                     |
| 3    | Check for file watchers limit on Linux: increase `fs.inotify.max_user_watches` |
| 4    | Restart the dev server                                                         |

### API Requests Failing

**Symptoms:** Network errors or 401/403 responses in the browser.

| Step | Action                                                     |
| ---- | ---------------------------------------------------------- |
| 1    | Verify the backend is running and accessible               |
| 2    | Check `NEXT_PUBLIC_API_URL` in `.env.local`                |
| 3    | Verify authentication tokens are being sent correctly      |
| 4    | Check the browser Network tab for request/response details |

---

## Docker Issues

### Port Already in Use

**Symptoms:** `Error starting userland proxy: listen tcp 0.0.0.0:8000: bind: address already in use`

| Step | Action                                                                          |
| ---- | ------------------------------------------------------------------------------- | ------------------------ |
| 1    | Find the process using the port: `lsof -i :8000` (Linux/macOS) or `netstat -ano | findstr :8000` (Windows) |
| 2    | Stop the conflicting process                                                    |
| 3    | Or change the port in `docker-compose.override.yml`                             |

### Container Keeps Restarting

**Symptoms:** `docker compose ps` shows a service restarting repeatedly.

| Step | Action                                                                              |
| ---- | ----------------------------------------------------------------------------------- |
| 1    | Check the container logs: `docker compose logs <service>`                           |
| 2    | Verify environment variables are set correctly                                      |
| 3    | Rebuild the image: `docker compose build <service>`                                 |
| 4    | Remove old containers and volumes: `docker compose down -v && docker compose up -d` |

### Permission Denied on Volumes

**Symptoms:** Permission errors when accessing mounted volumes (Linux).

| Step | Action                                                                   |
| ---- | ------------------------------------------------------------------------ |
| 1    | Ensure your user is in the Docker group: `sudo usermod -aG docker $USER` |
| 2    | Log out and back in for group changes to take effect                     |
| 3    | Check file ownership on the host matches the container user              |

---

## Celery Issues

### Tasks Not Executing

**Symptoms:** Queued tasks remain pending, nothing happens.

| Step | Action                                                                           |
| ---- | -------------------------------------------------------------------------------- |
| 1    | Verify the Celery worker is running: `docker compose ps` or check the terminal   |
| 2    | Verify Redis (broker) is accessible: `redis-cli ping`                            |
| 3    | Check worker logs: `docker compose logs -f celery-worker`                        |
| 4    | Verify the task is discovered: check the worker startup log for registered tasks |

### Scheduled Tasks Not Firing

**Symptoms:** Celery Beat tasks are not triggering on schedule.

| Step | Action                                                                        |
| ---- | ----------------------------------------------------------------------------- |
| 1    | Verify Celery Beat is running: `docker compose ps` or check the terminal      |
| 2    | Check beat logs: `docker compose logs -f celery-beat`                         |
| 3    | Verify schedules in the Django admin under Periodic Tasks                     |
| 4    | Ensure `django_celery_beat` is in `INSTALLED_APPS` and migrations are applied |

---

## Getting More Help

If the above solutions do not resolve your issue:

1. Search the project's GitHub Issues for similar problems
2. Check the [Debugging Guide](debugging.md) for more detailed diagnostic techniques
3. Open a new GitHub Issue with the full error message, steps to reproduce, and your environment details

---

## Related Documentation

- [Debugging Guide](debugging.md) — Debugging practices and tooling
- [Testing Guide](testing.md) — Test execution and coverage
- [Development Setup](development-setup.md) — Full local setup
- [Docker Development](docker-development.md) — Docker workflow
- [Docs Index](../index.md) — Documentation hub
