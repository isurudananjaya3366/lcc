# Test Execution Guide

> LankaCommerce Cloud — How to run tests efficiently

---

## Quick Start

Run all accounting tests (inside Docker):

```bash
wsl bash -c "cd /mnt/c/git_repos/pos && docker compose exec -T backend bash -c 'DJANGO_SETTINGS_MODULE=config.settings.test_pg python -m pytest tests/accounting/ -p no:warnings -q --no-header 2>&1'"
```

Run a single test file:

```bash
wsl bash -c "cd /mnt/c/git_repos/pos && docker compose exec -T backend bash -c 'DJANGO_SETTINGS_MODULE=config.settings.test_pg python -m pytest tests/accounting/test_models.py -p no:warnings -q --no-header 2>&1'"
```

Run a specific test by name:

```bash
wsl bash -c "cd /mnt/c/git_repos/pos && docker compose exec -T backend bash -c 'DJANGO_SETTINGS_MODULE=config.settings.test_pg python -m pytest tests/accounting/test_models.py -k test_account_creation -p no:warnings -q --no-header 2>&1'"
```

---

## Settings

| Setting                | Value                                        | File                                 |
| ---------------------- | -------------------------------------------- | ------------------------------------ |
| Django settings module | `config.settings.test_pg`                    | `backend/config/settings/test_pg.py` |
| Database host          | `db` (direct PostgreSQL, bypasses pgbouncer) | Hardcoded in `test_pg.py`            |
| Test database name     | `lankacommerce_test`                         | `test_pg.py` DATABASES → TEST → NAME |
| pytest config          | `backend/pytest.ini`                         | `--reuse-db` enabled by default      |

### Why `test_pg` and not `test`?

`config.settings.test` uses SQLite in-memory, which is incompatible with `django-tenants`. Any test that triggers `migrate_schemas` or `SET search_path` will fail on SQLite. Always use `test_pg` for tenant-aware tests.

---

## Speed Optimizations

### 1. `--reuse-db` (pytest-django)

Configured in `backend/pytest.ini`:

```ini
addopts = -v --tb=short --reuse-db
```

This tells pytest-django to **keep the test database between runs** instead of destroying and recreating it. The database persists across test sessions, so migrations only run once.

**Result:** Full 299 accounting tests run in ~95 seconds instead of ~15-20 minutes.

### 2. Tenant Schema Reuse (`conftest.py`)

The `setup_test_tenant` fixture in `backend/tests/accounting/conftest.py` checks if the tenant schema (`test_accounting`) already exists before creating it:

```python
cur.execute("SELECT nspname FROM pg_catalog.pg_namespace WHERE nspname = %s", [SCHEMA_NAME])
schema_exists = cur.fetchone() is not None
```

If the schema and tenant record already exist, the fixture reuses them instead of running the expensive DROP → CREATE → migrate cycle.

### Performance Comparison

| Metric                     | Before Optimization | After Optimization | Improvement          |
| -------------------------- | ------------------- | ------------------ | -------------------- |
| Full 299 accounting tests  | ~15-20 min          | ~95 seconds        | ~10-12x faster       |
| Single test file           | ~13 min             | ~17 sec            | ~46x faster          |
| First run (no existing DB) | ~15-20 min          | ~15-20 min         | Same (one-time cost) |

---

## When to Force Database Recreation

Use `--create-db` to force a fresh database when:

- **Migrations changed**: New models or altered fields require migration rerun
- **Test fixtures corrupted**: Unexpected data leaking between tests
- **Schema structure changed**: django-tenants schema modifications

```bash
wsl bash -c "cd /mnt/c/git_repos/pos && docker compose exec -T backend bash -c 'DJANGO_SETTINGS_MODULE=config.settings.test_pg python -m pytest tests/accounting/ --create-db -p no:warnings -q --no-header 2>&1'"
```

> **Note:** `--create-db` overrides `--reuse-db`. The first run after `--create-db` will take the full 15-20 minutes to build the schema, but subsequent runs with `--reuse-db` (the default) will be fast again.

---

## Container Requirements

| Container       | Required? | Purpose                                                        |
| --------------- | --------- | -------------------------------------------------------------- |
| `lcc-backend`   | Yes       | Runs pytest                                                    |
| `lcc-postgres`  | Yes       | Test database                                                  |
| `lcc-redis`     | Yes       | Celery broker (eager mode in tests, but Django still connects) |
| `lcc-pgbouncer` | No        | Tests connect directly to `db`, not through pgbouncer          |

If `lcc-pgbouncer` is in a restart loop, it does **not** affect test execution. The test settings hardcode `HOST: "db"` to bypass pgbouncer entirely.

---

## Troubleshooting

### `relation "X" already exists`

The tenant schema has stale state. Force recreation:

```bash
--create-db
```

### `failed to resolve host 'pgbouncer'`

This happens if the wrong settings module is used. Ensure you're using `config.settings.test_pg` (which hardcodes `HOST: "db"`), not `local` or `production` (which read `DB_HOST` from env).

### Tests hang or take too long

1. Verify `--reuse-db` is in `pytest.ini` addopts
2. Check that the `lcc-postgres` container is healthy: `docker compose ps`
3. If the test DB was dropped, the first run will take longer (rebuilding schema)

### `connection refused` errors

Ensure Docker containers are running:

```bash
wsl bash -c "cd /mnt/c/git_repos/pos && docker compose ps"
```

---

## Useful pytest Flags

| Flag             | Purpose                          |
| ---------------- | -------------------------------- |
| `-q --no-header` | Minimal output                   |
| `-p no:warnings` | Suppress warnings                |
| `-x`             | Stop on first failure            |
| `-k "test_name"` | Run tests matching a pattern     |
| `--tb=long`      | Full tracebacks                  |
| `--reuse-db`     | Reuse existing test DB (default) |
| `--create-db`    | Force recreate test DB           |
| `-v`             | Verbose test names               |

---

## Other Test Suites

The accounting `conftest.py` has been optimized for schema reuse. Other test suites still use the DROP+CREATE pattern. If you need to optimize them, apply the same `pg_catalog.pg_namespace` check pattern from `tests/accounting/conftest.py` to their respective `conftest.py` files:

- `tests/vendor_bills/conftest.py`
- `tests/vendors/conftest.py`
- `tests/purchases/conftest.py`
- `tests/payslip/conftest.py`
- `tests/payroll/conftest.py`
- `tests/payments/conftest.py`
- `tests/organization/conftest.py`
- `tests/orders/conftest.py`
- `tests/leave/conftest.py`
- `tests/invoices/conftest.py`
- `tests/employees/conftest.py`
- `tests/credit/conftest.py`
- `tests/attendance/conftest.py`
- `apps/quotes/tests/conftest.py`
- `apps/customers/tests/conftest.py`
