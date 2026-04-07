# PgBouncer Docker Configuration

Connection pooling configuration for the PostgreSQL database.

## Directory Structure

```
pgbouncer/
├── pgbouncer.ini    # Main PgBouncer configuration
├── userlist.txt     # User credentials for authentication
└── README.md
```

## Why PgBouncer?

LankaCommerce Cloud uses django-tenants for multi-tenancy, where each HTTP request sets a PostgreSQL `search_path` to the appropriate tenant schema. Without connection pooling:

- Each Django worker holds a persistent database connection
- Celery workers add additional persistent connections
- Under load, connections exhaust PostgreSQL `max_connections` (200)
- Connection setup overhead adds latency to every new worker

PgBouncer solves this by multiplexing many client connections onto a smaller pool of PostgreSQL connections, reducing resource usage and improving response times.

## Pooling Mode

| Mode        | Compatible with django-tenants? | Reason                                       |
| ----------- | ------------------------------- | -------------------------------------------- |
| Transaction | Yes (selected)                  | search_path is set per-transaction           |
| Session     | No                              | search_path persists, leaking tenant context |
| Statement   | No                              | Multi-statement transactions would fail      |

Transaction pooling releases the server connection back to the pool after each transaction completes. Since django-tenants sets `search_path` at the beginning of each request's transaction, tenant isolation is maintained.

## Connection Limits

| Setting              | Value | Rationale                                              |
| -------------------- | ----- | ------------------------------------------------------ |
| default_pool_size    | 40    | Connections per user/database pair                     |
| min_pool_size        | 5     | Warm connections to avoid setup latency                |
| reserve_pool_size    | 5     | Extra connections for burst traffic                    |
| reserve_pool_timeout | 3 s   | Wait before using reserve connections                  |
| max_client_conn      | 400   | Total client connections PgBouncer accepts             |
| max_db_connections   | 80    | Hard cap per database on the PostgreSQL side           |
| max_user_connections | 0     | Unlimited per user (controlled via max_db_connections) |

### Relationship to PostgreSQL max_connections

PostgreSQL is configured with `max_connections = 200`. PgBouncer's limits ensure:

- 2 databases × 80 max_db_connections = 160 maximum pooled connections
- Remaining 40 connections reserved for superuser, monitoring, and direct access
- Clients see up to 400 connections via PgBouncer, but only 160 reach PostgreSQL

## Databases

| PgBouncer Database | Upstream Host | Upstream Database  | Purpose                   |
| ------------------ | ------------- | ------------------ | ------------------------- |
| lankacommerce      | db            | lankacommerce      | Main development database |
| lankacommerce_test | db            | lankacommerce_test | Automated test database   |

## Authentication

PgBouncer authenticates clients using the `userlist.txt` file. Users listed in this file must correspond to real PostgreSQL roles.

| User     | Purpose                              |
| -------- | ------------------------------------ |
| lcc_user | Application user (Django, Celery)    |
| postgres | Admin console and maintenance access |

### Credential Rotation

1. Generate a new password hash
2. Update `userlist.txt` with the new entry
3. Reload PgBouncer configuration without downtime: `docker exec lcc-pgbouncer kill -HUP 1`
4. Update the application `DATABASE_URL` environment variable
5. Restart application services to pick up the new credentials

## Service Mapping

Applications connect through PgBouncer instead of directly to PostgreSQL:

| Connection Path              | Port | Used By                           |
| ---------------------------- | ---- | --------------------------------- |
| App → PgBouncer → PostgreSQL | 6432 | Django, Celery (via DATABASE_URL) |
| App → PostgreSQL (direct)    | 5432 | Admin tools, migrations, psql     |

In development, the `DATABASE_URL` can point to either port. For production, all application traffic should route through PgBouncer on port 6432.

## Timeouts

| Setting                | Value | Purpose                                         |
| ---------------------- | ----- | ----------------------------------------------- |
| server_idle_timeout    | 300 s | Close idle PostgreSQL connections after 5 min   |
| client_idle_timeout    | 0     | Disabled (let application manage idle clients)  |
| client_login_timeout   | 60 s  | Max time to complete authentication             |
| query_timeout          | 0     | Disabled (PostgreSQL statement_timeout handles) |
| query_wait_timeout     | 120 s | Max time a client waits for a pool connection   |
| server_connect_timeout | 15 s  | Max time to establish upstream connection       |
| server_login_retry     | 15 s  | Retry interval for failed upstream connections  |

## Admin Console

PgBouncer exposes an admin console on port 6432 using the virtual database `pgbouncer`:

```
psql -h localhost -p 6432 -U postgres pgbouncer
```

Useful commands:

- `SHOW POOLS;` — Current pool statistics
- `SHOW SERVERS;` — Active server connections
- `SHOW CLIENTS;` — Active client connections
- `SHOW CONFIG;` — Running configuration
- `RELOAD;` — Reload configuration without restart

## Health Checks

### Docker Health Check

The Docker Compose health check verifies PgBouncer is accepting connections:

| Property     | Value                                                        |
| ------------ | ------------------------------------------------------------ |
| Command      | pg_isready -h 127.0.0.1 -p 6432 -U lcc_user -d lankacommerce |
| Interval     | 10 seconds                                                   |
| Timeout      | 5 seconds                                                    |
| Retries      | 5                                                            |
| Start period | 10 seconds                                                   |

A service is considered healthy when `pg_isready` returns exit code 0, meaning PgBouncer is accepting connections on port 6432.

### Health Criteria

PgBouncer is considered healthy when all of the following are true:

| Criterion                     | How to Check                    | Expected Result           |
| ----------------------------- | ------------------------------- | ------------------------- |
| Process running               | Container status                | Running                   |
| Accepting connections         | pg_isready on port 6432         | Exit code 0               |
| Upstream PostgreSQL reachable | SHOW SERVERS from admin console | Active server connections |
| Pool not exhausted            | SHOW POOLS — cl_waiting column  | 0 or low                  |
| No auth errors                | Docker logs (pgbouncer)         | No auth failure messages  |

### Monitoring Signals

For external monitoring tools (Prometheus, Grafana, uptime checks):

| Signal                    | Source                     | Alert Threshold                 |
| ------------------------- | -------------------------- | ------------------------------- |
| PgBouncer process down    | Docker health check        | Unhealthy > 30 seconds          |
| Client wait queue growing | SHOW POOLS (cl_waiting)    | cl_waiting > 10 for > 60s       |
| Server connection errors  | Docker logs                | Any connection refused errors   |
| Pool saturation           | SHOW POOLS (sv_active)     | sv_active >= max_db_connections |
| Query wait time           | SHOW STATS (avg_wait_time) | avg_wait_time > 1000 ms         |

## Logging

### Log Settings

PgBouncer logging is configured for Docker container environments:

| Setting            | Value     | Purpose                                 |
| ------------------ | --------- | --------------------------------------- |
| log_connections    | 1         | Log every client connection             |
| log_disconnections | 1         | Log every client disconnection          |
| log_pooler_errors  | 1         | Log pooler-level errors                 |
| logfile            | /dev/null | Suppress file logging (use Docker logs) |
| syslog             | 0         | Disable syslog                          |

### Accessing Logs

All PgBouncer output goes to stdout/stderr, captured by Docker:

| Command                                  | Purpose                      |
| ---------------------------------------- | ---------------------------- |
| docker compose logs pgbouncer            | View all PgBouncer logs      |
| docker compose logs pgbouncer --tail 50  | View last 50 lines           |
| docker compose logs pgbouncer -f         | Follow live log output       |
| docker compose logs pgbouncer --since 1h | View logs from the last hour |

### Log Messages

| Message Pattern                      | Meaning                               | Severity |
| ------------------------------------ | ------------------------------------- | -------- |
| C-0x... login attempt                | Client connecting                     | Info     |
| S-0x... new connection to server     | New upstream connection to PostgreSQL | Info     |
| closing because: server idle timeout | Idle connection released              | Info     |
| auth failed                          | Password mismatch                     | Error    |
| cannot connect to server             | PostgreSQL unreachable                | Error    |
| pooler error                         | Internal pooler issue                 | Error    |
