# LankaCommerce POS — Laptop Migration Guide

> **Purpose:** Move the entire development environment (code, Docker containers, database) from your current machine to a dedicated project laptop.  
> **Target Laptop:** i3 7th Gen, 8 GB RAM, 1 TB SSD, Fresh Windows 11  
> **Date:** 2025-07-18

---

## Table of Contents

1. [Hardware Assessment](#1-hardware-assessment)
2. [Software to Install on New Laptop](#2-software-to-install-on-new-laptop)
3. [Transfer the Codebase](#3-transfer-the-codebase)
4. [Transfer Docker Data (Database, Volumes)](#4-transfer-docker-data-database-volumes)
5. [Set Up on New Laptop](#5-set-up-on-new-laptop)
6. [Verify Everything Works](#6-verify-everything-works)
7. [Performance Tuning for 8 GB RAM](#7-performance-tuning-for-8-gb-ram)
8. [Quick Reference Commands](#8-quick-reference-commands)

---

## 1. Hardware Assessment

### Your Specs vs Requirements

| Resource | Your Laptop        | Minimum Required | Verdict                                          |
| -------- | ------------------ | ---------------- | ------------------------------------------------ |
| CPU      | i3 7th Gen (2C/4T) | Any modern x64   | **OK** — Docker runs fine; builds will be slower |
| RAM      | 8 GB               | 8 GB             | **Tight** — Needs tuning (see Section 7)         |
| Storage  | 1 TB SSD           | 50 GB free       | **Excellent** — SSD is critical for Docker perf  |
| OS       | Windows 11 (fresh) | Windows 10/11    | **OK**                                           |

### What to Expect

- **Build times** will be ~2–3x slower than a modern i5/i7 (one-time cost when building images).
- **Running all 8 containers** will use ~3–4 GB RAM with tuning. That leaves ~4 GB for Windows + VS Code.
- **SSD is the key advantage** — Docker filesystem performance depends heavily on disk I/O.
- **Day-to-day development** (editing, testing, running server) will feel normal once containers are up.

---

## 2. Software to Install on New Laptop

Install these in order. **Nothing else is needed.**

| #   | Software             | Version | Download                                        | Notes                                                                |
| --- | -------------------- | ------- | ----------------------------------------------- | -------------------------------------------------------------------- |
| 1   | **Git for Windows**  | Latest  | https://git-scm.com/download/win                | Check "Git Bash" option                                              |
| 2   | **Docker Desktop**   | 4.x+    | https://www.docker.com/products/docker-desktop/ | Enable WSL 2 backend (see below)                                     |
| 3   | **VS Code**          | Latest  | https://code.visualstudio.com/                  | Install extensions: Python, ESLint, Prettier, Docker, GitHub Copilot |
| 4   | **Windows Terminal** | Latest  | Microsoft Store (pre-installed on Win 11)       | Optional but recommended                                             |

### Docker Desktop + WSL 2 Setup

1. Open PowerShell as Admin:
   ```powershell
   wsl --install
   ```
2. Restart your laptop.
3. Install Docker Desktop. During setup:
   - Check **"Use WSL 2 instead of Hyper-V"**
   - Check **"Add shortcut to desktop"**
4. Open Docker Desktop → Settings → Resources:
   - Memory: **4 GB** (see Section 7)
   - CPUs: **2**
   - Swap: **2 GB**
   - Disk image size: **100 GB**

> **Important:** WSL 2 backend is required. Hyper-V backend performs worse on i3 processors.

### What You Do NOT Need to Install

- ~~Python~~ — Runs inside Docker container (`python:3.12-slim`)
- ~~Node.js / npm / pnpm~~ — Runs inside Docker container (`node:20-alpine`)
- ~~PostgreSQL~~ — Runs inside Docker container (`postgres:15-alpine`)
- ~~Redis~~ — Runs inside Docker container (`redis:7-alpine`)

Everything runs inside Docker. The new laptop is just a host for Docker and your code editor.

---

## 3. Transfer the Codebase

### Option A: Clone from Git (Recommended)

If your code is pushed to GitHub/GitLab:

```bash
# On the NEW laptop
git clone https://github.com/YOUR_USERNAME/pos.git
cd pos
```

### Option B: Copy the Entire Folder

If you have unpushed changes or prefer a direct copy:

1. **On OLD laptop** — Copy the project folder to a USB drive or network share:

   ```bash
   # Exclude node_modules, .next, __pycache__, and Docker data
   # Use robocopy (built-in Windows):
   robocopy E:\work_git_repos\pos D:\USB_DRIVE\pos /E /XD node_modules .next __pycache__ .git\objects mediafiles staticfiles
   ```

2. **On NEW laptop** — Copy from USB to your workspace:
   ```bash
   robocopy D:\USB_DRIVE\pos E:\work_git_repos\pos /E
   ```

> **Note:** Do NOT copy Docker volumes this way. See Section 4 for database transfer.

### Option C: Git Bundle (Full Repo with History, No Network Needed)

```bash
# On OLD laptop — create a single file containing the entire git repo
cd E:\work_git_repos\pos
git bundle create pos-repo.bundle --all

# Copy pos-repo.bundle to USB drive
# On NEW laptop:
git clone D:\USB_DRIVE\pos-repo.bundle E:\work_git_repos\pos
cd E:\work_git_repos\pos
git remote set-url origin https://github.com/YOUR_USERNAME/pos.git
```

---

## 4. Transfer Docker Data (Database, Volumes)

### Can You Just Export the Container?

**Short answer: Yes, but it's not the best approach.**

Docker has `docker export` / `docker import` for containers, but this only captures the container's filesystem — it does NOT include named volumes (where your PostgreSQL database lives). The better approach is to **export the database separately** and **rebuild the containers from docker-compose.yml** (which is fast and reproducible).

### Method 1: Database Dump + Restore (Recommended)

This is the cleanest, most reliable approach.

#### On the OLD Laptop — Export Database

```bash
cd E:\work_git_repos\pos

# 1. Dump the ENTIRE PostgreSQL instance (all schemas, all tenants)
docker compose exec -T db pg_dumpall -U postgres > lankacommerce_full_backup.sql

# 2. Verify the dump file was created and has content
wc -l lankacommerce_full_backup.sql
# Should show thousands of lines

# 3. Copy this file to USB drive
copy lankacommerce_full_backup.sql D:\USB_DRIVE\
```

#### On the NEW Laptop — Import Database

```bash
cd E:\work_git_repos\pos

# 1. Copy .env.docker.example to .env.docker
copy .env.docker.example .env.docker
# Edit .env.docker to set DJANGO_SECRET_KEY and NEXTAUTH_SECRET

# 2. Start ONLY the database container first
docker compose up -d db
# Wait 10 seconds for PostgreSQL to initialize
timeout /t 10

# 3. Import the database dump
docker compose exec -T db psql -U postgres < lankacommerce_full_backup.sql

# 4. Now start everything else
docker compose up -d
```

### Method 2: Volume Export/Import (Alternative)

If you want an exact byte-for-byte copy of the Docker volume:

#### On the OLD Laptop — Export Volume

```bash
# Export PostgreSQL data volume to a tar archive
docker run --rm -v lcc-postgres-data:/data -v %CD%:/backup alpine tar czf /backup/postgres-data.tar.gz -C /data .

# Export media volume (if you have uploaded files)
docker run --rm -v lcc-backend-media:/data -v %CD%:/backup alpine tar czf /backup/media-data.tar.gz -C /data .

# Copy these tar.gz files to USB drive
```

#### On the NEW Laptop — Import Volume

```bash
cd E:\work_git_repos\pos

# 1. Start containers once to create volumes
docker compose up -d db
docker compose down

# 2. Import PostgreSQL data
docker run --rm -v lcc-postgres-data:/data -v %CD%:/backup alpine sh -c "rm -rf /data/* && tar xzf /backup/postgres-data.tar.gz -C /data"

# 3. Import media files
docker run --rm -v lcc-backend-media:/data -v %CD%:/backup alpine sh -c "rm -rf /data/* && tar xzf /backup/media-data.tar.gz -C /data"

# 4. Start everything
docker compose up -d
```

### Method 3: Docker Image Export (Not Recommended)

```bash
# This exports the CONTAINER, not the volumes
docker export lcc-backend > lcc-backend.tar
docker export lcc-postgres > lcc-postgres.tar

# Import on new machine
docker import lcc-backend.tar lankacommerce/backend:migrated
docker import lcc-postgres.tar lankacommerce/postgres:migrated
```

**Why this is NOT recommended:**

- Does **NOT** include database data (volumes are separate)
- Does **NOT** include environment variables or compose config
- You'd need to manually rewire everything
- Method 1 (pg_dumpall + rebuild) is faster, cleaner, and more reliable

### What to Transfer — Summary

| What              | How                   | Size Estimate |
| ----------------- | --------------------- | ------------- |
| Codebase          | Git clone or USB copy | ~500 MB       |
| Database dump     | `pg_dumpall` SQL file | ~10–50 MB     |
| Media uploads     | Volume tar or USB     | ~50–500 MB    |
| Docker images     | Auto-downloaded       | ~2 GB (auto)  |
| **Total to copy** | **USB drive**         | **~1 GB**     |

---

## 5. Set Up on New Laptop

### Step-by-Step First Boot

```bash
# 1. Navigate to project
cd E:\work_git_repos\pos

# 2. Create environment file
copy .env.docker.example .env.docker

# 3. Generate secrets (run in Git Bash)
python -c "import secrets; print(secrets.token_urlsafe(50))"
# Copy output → paste into .env.docker as DJANGO_SECRET_KEY

openssl rand -base64 32
# Copy output → paste into .env.docker as NEXTAUTH_SECRET

# 4. Build all Docker images (first time — takes 10-20 min on i3)
docker compose build

# 5. Start all services
docker compose up -d

# 6. Wait for all containers to be healthy
docker compose ps

# 7. If you imported a database dump, skip this step.
#    Otherwise, run migrations to create fresh database:
docker compose exec backend python manage.py migrate_schemas

# 8. Create superuser (if fresh DB)
docker compose exec backend python manage.py createsuperuser

# 9. Verify
docker compose exec backend python manage.py check
```

### Using the Makefile (Shorter)

```bash
make build        # Build images
make up           # Start all services
make migrate      # Run migrations
make status       # Check health
```

### Verify All Services

| Service        | URL                           | Expected         |
| -------------- | ----------------------------- | ---------------- |
| Backend API    | http://localhost:8000/api/v1/ | JSON response    |
| Frontend       | http://localhost:3000         | Next.js page     |
| Flower Monitor | http://localhost:5555         | Celery dashboard |
| Database       | `make dbshell`                | psql prompt      |

---

## 6. Verify Everything Works

### Run the Full Test Suite

```bash
# Backend tests (all ~10,000+ tests)
docker compose exec -T backend env DJANGO_SETTINGS_MODULE=config.settings.test_pg \
    python -m pytest --tb=short -q 2>&1 | tail -5

# Customer module tests (90 tests)
docker compose exec -T backend env DJANGO_SETTINGS_MODULE=config.settings.test_pg \
    python -m pytest apps/customers/tests/ -v --tb=short -p no:cacheprovider

# Frontend tests
docker compose exec frontend pnpm test

# Or use Makefile shortcuts
make test-backend
make test-frontend
```

### Check Database Has Your Data

```bash
# Connect to database
make dbshell

# Inside psql:
\dt                          -- List tables
SELECT count(*) FROM tenants_tenant;   -- Count tenants
\dn                          -- List schemas (should show tenant schemas)
\q                           -- Exit
```

---

## 7. Performance Tuning for 8 GB RAM

Your laptop has 8 GB which is tight. Here's how to optimize:

### Docker Desktop Settings

Open Docker Desktop → Settings → Resources:

| Setting | Value      | Why                                                  |
| ------- | ---------- | ---------------------------------------------------- |
| Memory  | **4 GB**   | Leaves 4 GB for Windows + VS Code                    |
| CPUs    | **2**      | All 4 threads available but limit to 2 for stability |
| Swap    | **2 GB**   | Safety net for memory spikes                         |
| Disk    | **100 GB** | Plenty of SSD space                                  |

### Reduce Container Memory Usage

Create a `docker-compose.override.yml` in the project root:

```yaml
# docker-compose.override.yml — Memory-constrained development
services:
  db:
    command: >
      postgres
      -c shared_buffers=128MB
      -c work_mem=8MB
      -c maintenance_work_mem=64MB
      -c effective_cache_size=512MB
      -c max_connections=50
    deploy:
      resources:
        limits:
          memory: 512M

  redis:
    command: redis-server --maxmemory 64mb --maxmemory-policy allkeys-lru
    deploy:
      resources:
        limits:
          memory: 128M

  pgbouncer:
    deploy:
      resources:
        limits:
          memory: 64M

  backend:
    deploy:
      resources:
        limits:
          memory: 1G

  frontend:
    deploy:
      resources:
        limits:
          memory: 1G

  celery-worker:
    deploy:
      resources:
        limits:
          memory: 512M

  celery-beat:
    deploy:
      resources:
        limits:
          memory: 128M

  flower:
    deploy:
      resources:
        limits:
          memory: 128M
```

### Estimated Memory Usage (Tuned)

| Container     | Memory Limit | Typical Usage |
| ------------- | ------------ | ------------- |
| PostgreSQL    | 512 MB       | ~200-300 MB   |
| Backend       | 1 GB         | ~300-500 MB   |
| Frontend      | 1 GB         | ~300-600 MB   |
| Redis         | 128 MB       | ~20-50 MB     |
| PgBouncer     | 64 MB        | ~10-20 MB     |
| Celery Worker | 512 MB       | ~100-200 MB   |
| Celery Beat   | 128 MB       | ~50-80 MB     |
| Flower        | 128 MB       | ~50-80 MB     |
| **Total**     | **~3.5 GB**  | **~1.5-2 GB** |

### If RAM Gets Too Tight

You can skip non-essential services during active development:

```bash
# Start only what you need for backend development
docker compose up -d db pgbouncer redis backend

# Add frontend when needed
docker compose up -d frontend

# Skip Celery entirely (tasks will fail silently, but CRUD works)
# Don't start: celery-worker, celery-beat, flower
```

### Windows Optimizations

1. **Disable unnecessary startup programs** — Task Manager → Startup → Disable all non-essential
2. **Disable Windows Search indexing** for the project folder:
   - Settings → Privacy & Security → Searching Windows → Exclude `E:\work_git_repos\pos`
3. **Set power plan to "High Performance"** — Settings → Power → High Performance
4. **Close other apps** when running Docker — Chrome alone can use 1-2 GB

---

## 8. Quick Reference Commands

### Daily Development Workflow

```bash
# Morning — Start dev environment
docker compose up -d                     # or: make up

# Code, test, repeat
docker compose exec backend python -m pytest apps/customers/tests/ -v

# Evening — Stop to free resources
docker compose down                      # or: make down
```

### Useful Commands

```bash
# Check what's running
docker compose ps                        # or: make ps

# View logs
docker compose logs -f backend           # or: make logs-backend

# Open Django shell
docker compose exec backend python manage.py shell  # or: make shell

# Open database shell
docker compose exec db psql -U lcc_user lankacommerce  # or: make dbshell

# Run migrations
docker compose exec backend python manage.py migrate_schemas  # or: make migrate

# Rebuild after Dockerfile changes
docker compose build                     # or: make build
```

### Emergency Commands

```bash
# Everything is broken — full reset (DESTROYS DATABASE)
docker compose down -v
docker compose up -d

# Container won't start — check logs
docker compose logs backend

# Out of disk space
docker system prune -a
```

---

## Migration Checklist

Use this checklist when performing the migration:

- [ ] Install Git for Windows on new laptop
- [ ] Install Docker Desktop with WSL 2 backend
- [ ] Install VS Code with extensions
- [ ] Configure Docker Desktop resources (4 GB RAM, 2 CPUs)
- [ ] Transfer codebase (git clone, USB, or git bundle)
- [ ] Create `.env.docker` from `.env.docker.example`
- [ ] Generate `DJANGO_SECRET_KEY` and `NEXTAUTH_SECRET`
- [ ] Export database from old laptop (`pg_dumpall`)
- [ ] Build Docker images (`docker compose build`)
- [ ] Start services (`docker compose up -d`)
- [ ] Import database dump (`psql < backup.sql`)
- [ ] Verify all containers healthy (`docker compose ps`)
- [ ] Run test suite to confirm everything works
- [ ] Create `docker-compose.override.yml` for RAM limits
- [ ] Optional: Transfer media uploads volume

---

## FAQ

**Q: How long will the initial build take on i3?**  
A: About 10–20 minutes for all images. After that, rebuilds are fast (Docker caches layers).

**Q: Can I run everything with just 8 GB RAM?**  
A: Yes, with the tuning from Section 7. Skip Celery services during active development if needed.

**Q: What if I forget to export the database?**  
A: Just run `make migrate` on the new laptop. You'll get a fresh empty database. The schema and tables will be created from Django migrations — you only lose existing data.

**Q: Do I need to install Python or Node.js?**  
A: No. Everything runs inside Docker containers. The only software you need on the laptop is Git, Docker Desktop, and VS Code.

**Q: Can I use the same `.env.docker` file?**  
A: Yes for development. Just copy it along with your codebase. For production, generate new secrets.

**Q: What about VS Code extensions and settings?**  
A: Sign in to VS Code with your GitHub/Microsoft account — Settings Sync will restore your extensions and settings automatically.
