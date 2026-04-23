# LankaCommerce POS-ERP — System Startup Guide

This guide explains how to start the full application stack and access it in a browser.

---

## Prerequisites

- **WSL 2** installed and running
- **Docker** installed inside WSL (no Docker Desktop required)
- All environment files present (`.env.docker`, `docker-compose.override.yml`)

---

## Step-by-Step: Starting the System

### 1. Open a terminal (Git Bash or PowerShell on Windows)

All Docker commands go through WSL. The pattern is:

```bash
wsl bash -c "cd /mnt/c/git_repos/pos && docker compose <command>"
```

---

### 2. Start all services

```bash
wsl bash -c "cd /mnt/c/git_repos/pos && docker compose up -d"
```

This starts:
| Service | Role |
|---|---|
| `lcc-postgres` | PostgreSQL 15 database |
| `lcc-pgbouncer` | Connection pooler (port 6432) |
| `lcc-redis` | Cache & message broker |
| `lcc-backend` | Django REST API (port 8001) |
| `lcc-celery-worker` | Async task worker |
| `lcc-celery-beat` | Scheduled task runner |
| `lcc-flower` | Celery monitoring UI |
| `lcc-frontend` | Next.js frontend (port 3000) |

---

### 3. Wait for services to become healthy (~30–60 seconds)

```bash
wsl bash -c "cd /mnt/c/git_repos/pos && docker compose ps"
```

Wait until you see `(healthy)` next to `lcc-backend` and `lcc-frontend`. Example output:

```
NAME                STATUS
lcc-backend         Up 2 minutes (healthy)
lcc-celery-beat     Up 2 minutes
lcc-celery-worker   Up 2 minutes (healthy)
lcc-flower          Up 2 minutes
lcc-frontend        Up 2 minutes (healthy)
lcc-pgbouncer       Up 2 minutes (healthy)
lcc-postgres        Up 2 minutes (healthy)
lcc-redis           Up 2 minutes (healthy)
```

> **Note:** The frontend takes 30–90 seconds to compile on first start due to Turbopack.

---

### 4. Open the application in your browser

| URL                             | Purpose                      |
| ------------------------------- | ---------------------------- |
| **http://localhost:3000/login** | Main login page ✅           |
| http://localhost:3000/          | Storefront (public webstore) |
| http://localhost:3000/dashboard | ERP Dashboard (after login)  |
| http://localhost:8001/api/v1/   | Backend REST API             |
| http://localhost:8001/admin/    | Django admin panel           |

---

### 5. Log in

Use these superuser credentials:

| Field        | Value          |
| ------------ | -------------- |
| **Email**    | `admin@lcc.lk` |
| **Password** | `Admin1234x`   |

After login, you will be redirected to **http://localhost:3000/dashboard**.

---

## Stopping the System

```bash
wsl bash -c "cd /mnt/c/git_repos/pos && docker compose down"
```

To stop **without** losing database data, use the above. To also delete volumes (full reset):

```bash
wsl bash -c "cd /mnt/c/git_repos/pos && docker compose down -v"
```

---

## Troubleshooting

### Frontend shows 500 error on first start

The Next.js dev server compiles on first request. Wait 30–60 seconds and refresh.

### Login shows "An unexpected error occurred"

This was caused by a CORS misconfiguration. The backend must:

1. Have `CORS_ALLOW_ALL_ORIGINS = False` in `local.py` (cannot be `True` when `CORS_ALLOW_CREDENTIALS=True`)
2. Allow custom headers `x-request-id` and `x-tenant-id` via `CORS_ALLOW_HEADERS` in `base.py`
3. Have `CORS_ALLOWED_ORIGINS=http://localhost:3000` in the environment (see `.env.docker`)

The login page is at **`http://localhost:3000/login`** (not `/auth/login`).

### Sidebar only shows "Dashboard" after login

The backend login response doesn't include `role` or `permissions`. The frontend maps `isStaff: true` → `role: "admin"` and `permissions: ["*:*"]`. If you see only Dashboard in the sidebar, clear localStorage and log in again:

1. Open browser DevTools → Application → Local Storage → clear all `lcc-*` keys
2. Navigate to `http://localhost:3000/login` and log in

### Turbopack code changes not taking effect

Hot reload works for most changes. If changes don't appear after ~10 seconds:

```bash
wsl bash -c "cd /mnt/c/git_repos/pos && docker compose restart frontend"
```

Wait ~30 seconds for Turbopack to recompile, then refresh.

### pgbouncer crash loop (stale PID)

If pgbouncer fails to start after a crash:

```bash
wsl bash -c "cd /mnt/c/git_repos/pos && docker compose stop pgbouncer && docker compose rm -f pgbouncer && docker compose up -d pgbouncer"
```

Then restart the backend to reconnect:

```bash
wsl bash -c "cd /mnt/c/git_repos/pos && docker compose restart backend"
```

### Backend cannot connect to database

```bash
wsl bash -c "cd /mnt/c/git_repos/pos && docker compose restart backend"
```

### Check logs for a specific service

```bash
wsl bash -c "cd /mnt/c/git_repos/pos && docker compose logs <service-name> --tail=50"
```

Replace `<service-name>` with: `frontend`, `backend`, `pgbouncer`, `postgres`, `redis`, etc.

---

## Checking System Health

```bash
# All services status
wsl bash -c "cd /mnt/c/git_repos/pos && docker compose ps"

# Frontend health API
wsl bash -c "curl -s http://localhost:3000/api/health"

# Backend health
wsl bash -c "curl -s http://localhost:8001/api/v1/"
```

---

## Architecture Notes

- **Backend** is volume-mounted — code changes apply immediately without rebuild
- **Frontend** is volume-mounted — code changes apply immediately (Next.js hot reload)
- **Database URL**: `postgres://lcc_user:dev_password_change_me@pgbouncer:6432/lankacommerce`
- **Settings module**: `config.settings.local` (inside container)
- **Auth model**: `platform.PlatformUser` (email-based login, not username)
- **CORS**: `CORS_ALLOW_ALL_ORIGINS` must be `False`; allowed origins listed in `CORS_ALLOWED_ORIGINS` env var
- **Custom CORS headers**: `x-request-id` and `x-tenant-id` are allowed via `CORS_ALLOW_HEADERS` in `base.py`
- **Backend login response**: Returns `{accessToken, refreshToken, user}` — user object includes `isStaff` but not `role`/`permissions`. Frontend maps `isStaff=true` → `role="admin"`, `permissions=["*:*"]`
- **Axios client**: Uses `withCredentials: true`; custom headers require explicit CORS allow-list on backend

---

## Route Reference

| Route                 | Description                  |
| --------------------- | ---------------------------- |
| `/login`              | Login page                   |
| `/register`           | User registration            |
| `/dashboard`          | ERP dashboard home           |
| `/inventory/products` | Products list                |
| `/sales/orders`       | Sales orders                 |
| `/purchasing/orders`  | Purchase orders              |
| `/accounting`         | Accounting module            |
| `/hr/employees`       | HR — employees               |
| `/settings`           | System settings              |
| `/`                   | Storefront (public webstore) |
| `/shop`               | Shop/product listing         |
| `/account/dashboard`  | Customer portal              |
