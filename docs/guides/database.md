# Database Guide

> Database migrations, seeding, backups, and maintenance for LankaCommerce Cloud.

**Navigation:** [Getting Started](getting-started.md) · [Development Setup](development-setup.md) · [Multi-Tenancy](multi-tenancy.md) · [Docs Index](../index.md)

---

## Overview

LankaCommerce Cloud uses **PostgreSQL 15** as its primary database, managed through Django's ORM and migration system. In production, multi-tenancy is handled by `django-tenants` with schema-based isolation (Phase 2).

---

## Database Configuration

| Setting            | Development                         | Production                               |
| ------------------ | ----------------------------------- | ---------------------------------------- |
| Engine             | `django.db.backends.postgresql`     | `django.db.backends.postgresql`          |
| Database Name      | `lcc-dev`                           | `lankacommerce`                          |
| Host               | `db` (Docker) / `localhost` (local) | Configured via `DB_HOST`                 |
| Port               | 5432                                | Configured via `DB_PORT`                 |
| SSL Mode           | Disabled                            | `require`                                |
| Connection Pooling | Disabled                            | `CONN_MAX_AGE=60`, health checks enabled |

Environment variables for database configuration:

| Variable      | Description                           |
| ------------- | ------------------------------------- |
| `DB_ENGINE`   | Database engine (default: postgresql) |
| `DB_NAME`     | Database name                         |
| `DB_USER`     | Database username                     |
| `DB_PASSWORD` | Database password                     |
| `DB_HOST`     | Database host                         |
| `DB_PORT`     | Database port (default: 5432)         |

---

## Migrations

### Creating Migrations

After modifying a model, generate the migration file:

1. Run: `python manage.py makemigrations`
2. Review the generated migration file in the app's `migrations/` directory
3. Verify it looks correct before committing

For a specific app: `python manage.py makemigrations <app_name>`

### Applying Migrations

1. Apply all pending migrations: `python manage.py migrate`
2. Apply migrations for a specific app: `python manage.py migrate <app_name>`
3. In Docker: `docker compose exec backend python manage.py migrate`

### Migration Status

1. Check which migrations have been applied: `python manage.py showmigrations`
2. Show migration plan: `python manage.py migrate --plan`

### Reverting Migrations

1. Revert to a specific migration: `python manage.py migrate <app_name> <migration_number>`
2. Revert all migrations for an app: `python manage.py migrate <app_name> zero`

### Multi-Tenant Migrations (Phase 2)

When `django-tenants` is active, use tenant-aware commands:

1. Migrate all schemas: `python manage.py migrate_schemas`
2. Migrate the shared schema only: `python manage.py migrate_schemas --shared`
3. Migrate a specific tenant: `python manage.py migrate_schemas --tenant`

> See [Multi-Tenancy Guide](multi-tenancy.md) for more details.

---

## Migration Best Practices

| Practice                      | Description                                                                    |
| ----------------------------- | ------------------------------------------------------------------------------ |
| One migration per change      | Keep migrations focused on a single logical change                             |
| Never edit applied migrations | Create a new migration instead of modifying an applied one                     |
| Review before committing      | Always review auto-generated migrations for correctness                        |
| Test migrations               | Run migrations on a fresh database to verify they apply cleanly                |
| Add data migrations carefully | Use `RunPython` for data migrations and always include a reverse               |
| Name migrations descriptively | Use `--name` flag: `python manage.py makemigrations --name add_sku_to_product` |

---

## Database Seeding

### Fixtures

Fixture files live in `backend/fixtures/` and can be loaded in any order:

1. Load all fixtures: `python manage.py loaddata fixtures/*.json`
2. Load a specific fixture: `python manage.py loaddata fixtures/products.json`
3. In Docker: `docker compose exec backend python manage.py loaddata fixtures/*.json`

### Creating Fixtures

1. Dump data from an app: `python manage.py dumpdata <app_name> --indent 2 > fixtures/<app_name>.json`
2. Dump specific models: `python manage.py dumpdata <app_name>.<Model> --indent 2 > fixtures/<model>.json`

---

## Backups

### Manual Backup

1. Local: `pg_dump -U postgres -h localhost lcc_dev > backup_$(date +%Y%m%d).sql`
2. Docker: `docker compose exec db pg_dump -U postgres lcc-dev > backup.sql`

### Manual Restore

1. Local: `psql -U postgres -h localhost lcc_dev < backup.sql`
2. Docker: `cat backup.sql | docker compose exec -T db psql -U postgres lcc-dev`

### Automated Backups

A backup script is provided at `docker/postgres/backup.sh` for scheduled backups in production.

---

## Database Maintenance

| Task                  | Command                                                                    | Frequency |
| --------------------- | -------------------------------------------------------------------------- | --------- |
| Vacuum analyze        | `VACUUM ANALYZE;` in psql                                                  | Weekly    |
| Reindex               | `REINDEX DATABASE lcc_dev;`                                                | Monthly   |
| Check table sizes     | `SELECT pg_size_pretty(pg_total_relation_size(tablename)) FROM pg_tables;` | As needed |
| Connection monitoring | `SELECT count(*) FROM pg_stat_activity;`                                   | As needed |

---

## Test Database

For testing, LankaCommerce Cloud uses an **in-memory SQLite** database to maximize speed:

| Setting       | Value                        |
| ------------- | ---------------------------- |
| Engine        | `django.db.backends.sqlite3` |
| Name          | `:memory:`                   |
| Configured in | `config/settings/test.py`    |

This is automatically used when running tests with `DJANGO_ENV=test`.

---

## Related Documentation

- [Getting Started](getting-started.md) — Quick onboarding overview
- [Development Setup](development-setup.md) — Full local setup
- [Multi-Tenancy Guide](multi-tenancy.md) — Tenant schema management
- [Backend README](../../backend/README.md) — Backend reference
- [Models Documentation](../backend/models.md) — Model conventions and structure
- [Docs Index](../index.md) — Documentation hub
