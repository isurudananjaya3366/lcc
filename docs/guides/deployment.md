# Deployment Guide

> Deployment steps, environment readiness, and production checklist for LankaCommerce Cloud.

**Navigation:** [Docker Development](docker-development.md) · [Troubleshooting](troubleshooting.md) · [Docs Index](../index.md)

---

## Overview

LankaCommerce Cloud is deployed as a set of Docker containers orchestrated with Docker Compose (production configuration). This guide covers the deployment workflow, environment readiness checks, and production hardening.

---

## Deployment Environments

| Environment    | Purpose                | Configuration                                        |
| -------------- | ---------------------- | ---------------------------------------------------- |
| **Local**      | Developer workstation  | `docker-compose.yml` + `docker-compose.override.yml` |
| **Staging**    | Pre-production testing | `docker-compose.prod.yml` with staging env vars      |
| **Production** | Live customer traffic  | `docker-compose.prod.yml` with production env vars   |

---

## Pre-Deployment Checklist

Before deploying to any environment, verify:

| Check                       | Status      | Description                                          |
| --------------------------- | ----------- | ---------------------------------------------------- |
| All tests pass              | Required    | Backend (pytest) and frontend (Jest) tests are green |
| Database migrations applied | Required    | No pending migrations                                |
| Environment variables set   | Required    | All required env vars are configured                 |
| Static files collected      | Required    | `python manage.py collectstatic --noinput`           |
| Secret key is unique        | Required    | `DJANGO_SECRET_KEY` is a strong random value         |
| DEBUG is False              | Required    | Debug mode must be disabled in production            |
| HTTPS configured            | Required    | SSL certificates and redirect rules are in place     |
| CORS origins set            | Required    | Only trusted frontend domains are allowed            |
| Sentry DSN configured       | Recommended | Error tracking for production monitoring             |

---

## Deployment Steps

### 1. Prepare the Release

1. Ensure all changes are merged to the `main` branch
2. Run the full test suite: `python -m pytest` and `pnpm test`
3. Update the changelog in `CHANGELOG.md`
4. Tag the release: `git tag -a v1.0.0 -m "Release v1.0.0"`
5. Push the tag: `git push origin v1.0.0`

### 2. Build Production Images

1. Build the backend image: `docker compose -f docker-compose.prod.yml build backend`
2. Build the frontend image: `docker compose -f docker-compose.prod.yml build frontend`
3. Verify images were created: `docker images | grep lankacommerce`

### 3. Configure Environment

1. Set all required environment variables on the target server
2. Ensure the database is accessible from the server
3. Ensure Redis is accessible from the server
4. Verify DNS records point to the correct server

### 4. Deploy

1. Pull the latest code on the server: `git pull origin main`
2. Build and start services: `docker compose -f docker-compose.prod.yml up -d --build`
3. Run database migrations: `docker compose -f docker-compose.prod.yml exec backend python manage.py migrate`
4. Collect static files: `docker compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput`
5. Verify services are running: `docker compose -f docker-compose.prod.yml ps`

### 5. Post-Deployment Verification

1. Check the health endpoint: `curl https://api.lankacommerce.lk/health/`
2. Verify the admin panel loads: visit `https://api.lankacommerce.lk/admin/`
3. Verify the frontend loads: visit `https://lankacommerce.lk/`
4. Check Sentry for any new errors
5. Monitor server logs for the first 30 minutes

---

## Production Configuration

### Security Settings

| Setting                          | Production Value    |
| -------------------------------- | ------------------- |
| `DEBUG`                          | `False`             |
| `SECURE_SSL_REDIRECT`            | `True`              |
| `SECURE_HSTS_SECONDS`            | `31536000` (1 year) |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS` | `True`              |
| `SECURE_HSTS_PRELOAD`            | `True`              |
| `CSRF_COOKIE_SECURE`             | `True`              |
| `SESSION_COOKIE_SECURE`          | `True`              |
| `SECURE_CONTENT_TYPE_NOSNIFF`    | `True`              |
| `X_FRAME_OPTIONS`                | `DENY`              |

### Database Settings

| Setting              | Production Value          |
| -------------------- | ------------------------- |
| `CONN_MAX_AGE`       | `60` (connection pooling) |
| `CONN_HEALTH_CHECKS` | `True`                    |
| `DB_SSLMODE`         | `require`                 |

### Caching

| Setting        | Production Value      |
| -------------- | --------------------- |
| Cache backend  | Redis                 |
| Session engine | Cache-backed sessions |
| Cache timeout  | 300 seconds           |

---

## Rollback Procedure

If a deployment causes issues:

1. Identify the problem from logs and monitoring
2. Stop the new containers: `docker compose -f docker-compose.prod.yml down`
3. Checkout the previous tag: `git checkout v0.9.0`
4. Rebuild and restart: `docker compose -f docker-compose.prod.yml up -d --build`
5. If database migrations were applied, revert them: `python manage.py migrate <app> <previous_migration>`
6. Verify the rollback resolved the issue
7. Document the incident and root cause

---

## Monitoring

| Tool            | Purpose                     | URL                                              |
| --------------- | --------------------------- | ------------------------------------------------ |
| Sentry          | Error tracking and alerting | Configured via `SENTRY_DSN`                      |
| Flower          | Celery task monitoring      | `http://server:5555/` (internal only)            |
| Health endpoint | Service availability        | `/health/`                                       |
| Docker logs     | Container output            | `docker compose -f docker-compose.prod.yml logs` |

---

## Related Documentation

- [Docker Development](docker-development.md) — Docker Compose development workflow
- [Troubleshooting Guide](troubleshooting.md) — Common issues and resolutions
- [Environment Variable Reference](../ENV_VARIABLES.md) — Complete variable documentation
- [Secrets Management](../SECRETS.md) — Secrets classification and rotation
- [Docs Index](../index.md) — Documentation hub
