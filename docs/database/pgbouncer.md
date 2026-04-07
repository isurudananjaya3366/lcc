# PgBouncer Connection Pooling

> Connection pooling configuration and usage guide for LankaCommerce Cloud.

---

## Table of Contents

- [Overview](#overview)
- [Why PgBouncer?](#why-pgbouncer)
- [Architecture](#architecture)
- [Transaction Pooling](#transaction-pooling)
- [Django Integration](#django-integration)
- [Connection Limits](#connection-limits)
- [Authentication](#authentication)
- [Operations](#operations)
- [Troubleshooting](#troubleshooting)

---

## Overview

PgBouncer sits between the application (Django, Celery) and PostgreSQL, multiplexing many client connections onto a smaller pool of database connections. This reduces PostgreSQL resource consumption and improves response times under concurrent load.

| Property    | Value                          |
| ----------- | ------------------------------ |
| Image       | edoburu/pgbouncer:1.23.1-p2    |
| Listen port | 6432                           |
| Pool mode   | Transaction                    |
| Upstream    | db:5432 (PostgreSQL 15)        |
| Config      | docker/pgbouncer/pgbouncer.ini |
| Userlist    | docker/pgbouncer/userlist.txt  |

---

## Why PgBouncer?

LankaCommerce Cloud uses django-tenants for multi-tenancy. Each HTTP request sets a PostgreSQL `search_path` to the tenant's schema. Without connection pooling:

| Problem                               | Impact                                    |
| ------------------------------------- | ----------------------------------------- |
| Each Django worker holds a connection | Exhausts max_connections (200) under load |
| Each Celery worker holds a connection | Further reduces available connections     |
| Connection setup per request          | Adds latency to every new worker          |
| No connection reuse                   | Wastes PostgreSQL memory (per-connection) |

With PgBouncer:

| Benefit                       | Detail                                      |
| ----------------------------- | ------------------------------------------- |
| Connection multiplexing       | 400 clients share 80 PostgreSQL connections |
| Reduced memory usage          | Fewer active PostgreSQL backend processes   |
| Faster connection acquisition | Pre-warmed pool avoids setup latency        |
| Graceful overload handling    | Queues clients instead of rejecting them    |

---

## Architecture

### Connection Flow

Requests flow through three layers:

| Layer    | Component     | Port | Role                          |
| -------- | ------------- | ---- | ----------------------------- |
| Client   | Django/Celery | —    | Issues SQL queries            |
| Pooler   | PgBouncer     | 6432 | Manages connection pool       |
| Database | PostgreSQL    | 5432 | Executes queries, stores data |

### Service Dependencies

| Service       | Depends On | Connection Path                 |
| ------------- | ---------- | ------------------------------- |
| backend       | pgbouncer  | Django → PgBouncer → PostgreSQL |
| celery-worker | pgbouncer  | Celery → PgBouncer → PostgreSQL |
| celery-beat   | pgbouncer  | Beat → PgBouncer → PostgreSQL   |
| pgbouncer     | db         | PgBouncer → PostgreSQL (direct) |

### Direct Access

For operations that bypass PgBouncer (migrations, psql, admin):

| Tool    | Connection               | When to Use                   |
| ------- | ------------------------ | ----------------------------- |
| psql    | db:5432                  | Direct SQL, schema inspection |
| migrate | db:5432 (recommended)    | Django migrations             |
| pgAdmin | localhost:5432 (exposed) | Visual database management    |

---

## Transaction Pooling

### Why Transaction Mode?

| Mode        | How It Works                        | django-tenants Compatible? |
| ----------- | ----------------------------------- | -------------------------- |
| Session     | Connection held for entire session  | No — search_path leaks     |
| Transaction | Connection released after each txn  | Yes — search_path per-txn  |
| Statement   | Connection released after each stmt | No — breaks transactions   |

django-tenants sets `search_path` at the beginning of each request's transaction. Transaction pooling ensures that when the connection returns to the pool after the transaction completes, the next request gets a clean connection with its own `search_path`.

### Important Constraints

| Constraint                    | Reason                                             |
| ----------------------------- | -------------------------------------------------- |
| CONN_MAX_AGE must be 0        | Persistent connections leak tenant search_path     |
| DISABLE_SERVER_SIDE_CURSORS   | Server-side cursors break with transaction pooling |
| No session-level SET commands | Settings reset when connection returns to pool     |
| No LISTEN/NOTIFY              | Notification channels are session-scoped           |
| No prepared statements        | Prepared statements are session-scoped             |

---

## Django Integration

### Settings Changes

The following Django database settings are configured for PgBouncer compatibility:

| Setting                     | Value     | Rationale                               |
| --------------------------- | --------- | --------------------------------------- |
| HOST                        | pgbouncer | Docker service name for PgBouncer       |
| PORT                        | 6432      | PgBouncer listen port                   |
| CONN_MAX_AGE                | 0         | Release connections after each request  |
| CONN_HEALTH_CHECKS          | True      | Verify connections are alive before use |
| DISABLE_SERVER_SIDE_CURSORS | True      | Required for transaction pooling        |

### Environment Variables

| Variable     | Value          | Notes                                       |
| ------------ | -------------- | ------------------------------------------- |
| DB_HOST      | pgbouncer      | Points to PgBouncer service, not PostgreSQL |
| DB_PORT      | 6432           | PgBouncer port, not PostgreSQL 5432         |
| DATABASE_URL | pgbouncer:6432 | Full connection string via PgBouncer        |

### Affected Files

| File                                  | Change                                   |
| ------------------------------------- | ---------------------------------------- |
| backend/config/settings/local.py      | DB_HOST default → pgbouncer, port → 6432 |
| backend/config/settings/production.py | Same + CONN_MAX_AGE 60 → 0               |
| .env.docker.example                   | DB_HOST=pgbouncer, DB_PORT=6432          |
| docker-compose.yml                    | backend depends_on pgbouncer, not db     |

---

## Connection Limits

### Pool Sizing

| Setting            | Value | Purpose                                    |
| ------------------ | ----- | ------------------------------------------ |
| default_pool_size  | 40    | Server connections per user/database pair  |
| min_pool_size      | 5     | Pre-warmed connections for low latency     |
| reserve_pool_size  | 5     | Extra connections for burst traffic        |
| max_client_conn    | 400   | Total client connections PgBouncer accepts |
| max_db_connections | 80    | Hard cap per database on PostgreSQL side   |

### Capacity Planning

| Metric                               | Calculation                          | Result |
| ------------------------------------ | ------------------------------------ | ------ |
| PostgreSQL max_connections           | Configured in postgresql.conf        | 200    |
| PgBouncer pooled connections (max)   | 2 databases × 80 max_db_connections  | 160    |
| Reserved for direct/superuser access | 200 − 160                            | 40     |
| Client-side capacity                 | max_client_conn                      | 400    |
| Multiplexing ratio                   | 400 clients : 160 server connections | 2.5:1  |

---

## Authentication

### Auth Method

PgBouncer uses MD5 authentication with a static userlist file. Clients authenticate to PgBouncer, which then connects to PostgreSQL using the same credentials.

| Aspect    | Detail                                                  |
| --------- | ------------------------------------------------------- |
| Auth type | MD5 (development)                                       |
| Auth file | /etc/pgbouncer/userlist.txt                             |
| Users     | lcc_user (application), postgres (admin)                |
| Sync      | Userlist passwords must match PostgreSQL role passwords |

### Credential Rotation

| Step | Action                                                  |
| ---- | ------------------------------------------------------- |
| 1    | Generate new password                                   |
| 2    | Update docker/pgbouncer/userlist.txt                    |
| 3    | Update PostgreSQL role (ALTER USER or 01-init.sql)      |
| 4    | Reload PgBouncer: docker exec lcc-pgbouncer kill -HUP 1 |
| 5    | Update .env.docker with new DB_PASSWORD                 |
| 6    | Restart application services                            |

---

## Operations

### Admin Console

Connect to the PgBouncer admin console for monitoring and management:

| Command      | Purpose                              |
| ------------ | ------------------------------------ |
| SHOW POOLS   | Current pool statistics              |
| SHOW SERVERS | Active server connections            |
| SHOW CLIENTS | Active client connections            |
| SHOW CONFIG  | Running configuration                |
| SHOW STATS   | Aggregate statistics                 |
| RELOAD       | Reload configuration without restart |
| PAUSE db     | Pause connections to a database      |
| RESUME db    | Resume connections to a database     |

### Configuration Reload

PgBouncer supports hot reload without dropping connections:

| Method                                | Effect                     |
| ------------------------------------- | -------------------------- |
| docker exec lcc-pgbouncer kill -HUP 1 | Reload from host           |
| RELOAD (from admin console)           | Reload from psql session   |
| docker compose restart pgbouncer      | Full restart (drops conns) |

### Health Monitoring

The Docker health check verifies PgBouncer is accepting connections:

| Check                   | Interval | Timeout | Retries |
| ----------------------- | -------- | ------- | ------- |
| pg_isready on port 6432 | 10s      | 5s      | 5       |

---

## Troubleshooting

### Common Issues

| Symptom                             | Cause                               | Fix                                      |
| ----------------------------------- | ----------------------------------- | ---------------------------------------- |
| Connection refused on 6432          | PgBouncer not running               | Check docker compose logs pgbouncer      |
| Auth failed                         | Userlist mismatch                   | Verify userlist.txt matches DB passwords |
| Tenant data from wrong tenant       | CONN_MAX_AGE not 0                  | Set CONN_MAX_AGE=0 in Django settings    |
| Server-side cursor errors           | DISABLE_SERVER_SIDE_CURSORS missing | Add to Django DATABASES config           |
| Pool exhausted (too many clients)   | max_client_conn too low             | Increase in pgbouncer.ini and reload     |
| Slow query (waiting for connection) | Pool saturated                      | Increase default_pool_size               |
| Cannot run migrations               | Migrations need direct DB access    | Use db:5432 for migrate commands         |

### Bypassing PgBouncer

For operations that require direct PostgreSQL access:

| Operation        | Environment Override                                     |
| ---------------- | -------------------------------------------------------- |
| Run migrations   | DB_HOST=db DB_PORT=5432 python manage.py migrate         |
| Create superuser | DB_HOST=db DB_PORT=5432 python manage.py createsuperuser |
| Direct psql      | psql -h localhost -p 5432 -U lcc_user lankacommerce      |

---

## Related Documentation

- [Schema Naming & Multi-Tenancy](schema-naming.md) — Schema isolation model
- [PostgreSQL Configuration](../../docker/pgbouncer/README.md) — PgBouncer Docker setup
- [ADR-0002: Multi-Tenancy Approach](../adr/0002-multi-tenancy-approach.md) — Architecture decision
