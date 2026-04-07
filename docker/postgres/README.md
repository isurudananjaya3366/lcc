# PostgreSQL Docker Configuration

Configuration files for the PostgreSQL database container.

## Directory Structure

```
postgres/
├── init/                  # Initialization scripts
│   ├── 01-init.sql        # Database, user, and extension setup
│   ├── 02-schema-functions.sql  # Tenant schema lifecycle functions
│   └── 03-privileges.sql  # Schema privilege definitions
├── backup.sh              # Development backup script
├── restore.sh             # Development restore script
├── pg_hba.conf            # Host-based authentication rules
├── postgresql.conf        # Custom PostgreSQL configuration
└── README.md
```

## Initialization Scripts

Scripts in `init/` are mounted to `/docker-entrypoint-initdb.d/` and run automatically on the **first** container startup only, in alphabetical order.

### Script Naming Convention

- `01-init.sql` - Create databases, application user, and extensions
- `02-schema-functions.sql` - Tenant schema lifecycle functions
- `03-privileges.sql` - Schema privilege definitions and access control
- `04-*.sql` - Reserved for future setup (seed data, migrations)

### Extensions Installed

| Extension | Purpose                            | Installed In                                 |
| --------- | ---------------------------------- | -------------------------------------------- |
| uuid-ossp | UUID generation functions          | template1, lankacommerce, lankacommerce_test |
| hstore    | Key-value pair storage type        | template1, lankacommerce, lankacommerce_test |
| pg_trgm   | Trigram similarity and text search | template1, lankacommerce, lankacommerce_test |

Extensions are also installed in `template1` so that any new databases created afterwards inherit them automatically.

### Databases Created

| Database           | Purpose                                  |
| ------------------ | ---------------------------------------- |
| lankacommerce      | Main development database                |
| lankacommerce_test | Automated test database (used by pytest) |

### Application User

| Property   | Value                                                        |
| ---------- | ------------------------------------------------------------ |
| Username   | lcc_user                                                     |
| Password   | dev_password_change_me (development only)                    |
| Privileges | Full access to both databases, CREATEDB (for django-tenants) |

### Schema Functions (02-schema-functions.sql)

Tenant schema lifecycle functions installed in the main database:

| Function                    | Purpose                                     | Safeguards                                                  |
| --------------------------- | ------------------------------------------- | ----------------------------------------------------------- |
| create_tenant_schema(name)  | Create a new tenant schema with permissions | Validates tenant\_ prefix, checks for duplicates            |
| tenant_schema_exists(name)  | Check if a tenant schema exists             | Read-only, stable function                                  |
| cleanup_tenant_schema(name) | Soft-delete by renaming to _deleted_ prefix | Only renames tenant\_ schemas, timestamped for traceability |
| drop_deleted_schema(name)   | Permanently remove a soft-deleted schema    | Only drops _deleted_tenant_ schemas                         |
| list_tenant_schemas()       | List all active tenant schemas              | Read-only, returns sorted list                              |

These functions complement django-tenants, which manages schema creation through its ORM layer. The SQL functions provide a safety net for manual administration and emergency operations.

### Schema Privileges (03-privileges.sql)

The privileges script enforces tenant isolation and ensures the application user has the correct access for django-tenants operations.

#### Role Privilege Model

| Role     | Scope           | Privileges                                                   |
| -------- | --------------- | ------------------------------------------------------------ |
| postgres | Global          | Superuser, owns databases and all schemas                    |
| lcc_user | Public schema   | ALL on tables, sequences, functions; CREATE objects          |
| lcc_user | Tenant schemas  | ALL on tables, sequences, functions (via DEFAULT PRIVILEGES) |
| lcc_user | System catalogs | USAGE on information_schema and pg_catalog (read-only)       |
| lcc_user | Database level  | CREATE (required for django-tenants schema creation)         |
| PUBLIC   | Public schema   | No access (explicitly revoked)                               |

#### Tenant Schema Grants

When a tenant schema is created (either by django-tenants or by the `create_tenant_schema()` helper), the following grants apply:

| Grant Type           | Target   | Effect                                 |
| -------------------- | -------- | -------------------------------------- |
| SCHEMA ALL           | lcc_user | Full control over the schema namespace |
| DEFAULT ON TABLES    | lcc_user | Auto-grant ALL on any future tables    |
| DEFAULT ON SEQUENCES | lcc_user | Auto-grant ALL on any future sequences |
| DEFAULT ON FUNCTIONS | lcc_user | Auto-grant ALL on any future functions |
| DEFAULT ON TYPES     | lcc_user | Auto-grant USAGE on any future types   |

Default privileges are set at two levels:

1. **Schema-specific** — via `create_tenant_schema()` in 02-schema-functions.sql
2. **Global for postgres role** — via 03-privileges.sql (catches any objects created by superuser)

#### Public vs Tenant Schema Access

| Aspect               | Public Schema                          | Tenant Schema                     |
| -------------------- | -------------------------------------- | --------------------------------- |
| Contains             | Tenant registry, domains, shared data  | Per-tenant business data          |
| Created by           | Initial migration                      | django-tenants on tenant creation |
| Accessible by        | All connections (via search_path)      | Only when set in search_path      |
| lcc_user permissions | ALL (explicit grant)                   | ALL (default privileges)          |
| PUBLIC role access   | None (explicitly revoked)              | None (not granted)                |
| Extension functions  | Available (uuid-ossp, hstore, pg_trgm) | Inherited via search_path         |

## Multi-Tenant Setup

For django-tenants, the public schema contains:

- Tenant registry table
- Shared lookup tables

Each tenant gets their own schema automatically.

## Backup and Restore

### Container Scripts (Development)

Simple scripts included in the Docker image for quick local backups:

- `backup.sh` — pg_dump to compressed file, keeps last 5 backups
- `restore.sh` — Restores from a compressed backup file

### Project Scripts (Comprehensive)

Full-featured scripts in the project `scripts/` directory:

| Script                  | Purpose                                         |
| ----------------------- | ----------------------------------------------- |
| `scripts/db-backup.sh`  | Custom-format dump with checksums and retention |
| `scripts/db-restore.sh` | Full or schema-level restore with verification  |

### Retention Policy (7-4-3)

| Tier    | Frequency    | Copies | Max Age |
| ------- | ------------ | ------ | ------- |
| Daily   | Every day    | 7      | 7 days  |
| Weekly  | Sundays      | 4      | 28 days |
| Monthly | 1st of month | 3      | 90 days |

See `docs/database/backup-procedures.md` for full documentation.

## Connection Authentication

Authentication rules are defined in `pg_hba.conf` and mounted read-only into the container. Rules are evaluated top-to-bottom and the first matching rule applies.

| Connection   | User       | Network                      | Method                    |
| ------------ | ---------- | ---------------------------- | ------------------------- |
| Local socket | postgres   | —                            | trust (admin convenience) |
| Local socket | all others | —                            | scram-sha-256             |
| TCP/IPv4     | all        | Docker networks (10/172/192) | scram-sha-256             |
| TCP/IPv4     | all        | localhost (127.0.0.1)        | scram-sha-256             |
| TCP/IPv6     | all        | ::1                          | scram-sha-256             |
| TCP (any)    | all        | everything else              | reject                    |

SCRAM-SHA-256 is the recommended password method for PostgreSQL 15+ and replaces the older MD5 approach.

## WAL Configuration

Write-Ahead Log settings in `postgresql.conf` support replication and point-in-time recovery:

| Setting                      | Value   | Purpose                                    |
| ---------------------------- | ------- | ------------------------------------------ |
| wal_level                    | replica | Enables streaming replication and PITR     |
| max_wal_size                 | 1 GB    | Checkpoint forced when WAL exceeds this    |
| min_wal_size                 | 80 MB   | WAL files recycled instead of removed      |
| checkpoint_timeout           | 10 min  | Maximum interval between checkpoints       |
| checkpoint_completion_target | 0.9     | Spread checkpoint I/O over 90% of interval |

### WAL Archiving

WAL archiving is enabled to support point-in-time recovery. Completed WAL segments are copied to a Docker volume.

| Setting         | Value                                  | Purpose                           |
| --------------- | -------------------------------------- | --------------------------------- |
| archive_mode    | on                                     | Enable WAL archiving              |
| archive_command | cp to /var/lib/postgresql/wal_archive/ | Copy completed WAL segments       |
| archive_timeout | 300 (5 min)                            | Force archive of partial segments |

The `postgres-wal-archive` Docker volume stores archived WAL segments. In production, replace the archive_command with a command that sends WAL to object storage.

## SSL Configuration

| Environment | SSL | Rationale                                                                 |
| ----------- | --- | ------------------------------------------------------------------------- |
| Development | Off | Docker bridge network is internal; traffic stays on localhost             |
| Production  | On  | HTTPS termination at Nginx; database connections encrypted with TLS certs |

Production SSL requires mounting certificate files into the container and setting `ssl = on`, `ssl_cert_file`, `ssl_key_file`, and `ssl_ca_file` in `postgresql.conf`.

## Logging Configuration

Development logging captures all SQL statements and diagnostics:

| Setting                    | Value                         | Purpose                               |
| -------------------------- | ----------------------------- | ------------------------------------- |
| log_statement              | all                           | Log every SQL statement               |
| log_duration               | on                            | Duration of every completed statement |
| log_min_duration_statement | 100 ms                        | Highlight slow queries                |
| log_connections            | on                            | Log new connections                   |
| log_disconnections         | on                            | Log connection closures               |
| log_lock_waits             | on                            | Log lock contention                   |
| log_checkpoints            | on                            | Log checkpoint activity               |
| log_line_prefix            | timestamp, pid, user, db, app | Structured log lines                  |

Logs are collected into `pg_log/` inside the PostgreSQL data directory, rotated daily or at 100 MB.

## Performance Tuning

Settings optimized for SSD-backed Docker volumes and multi-tenant workloads.

### I/O Settings

| Setting                  | Value | Default | Rationale                                   |
| ------------------------ | ----- | ------- | ------------------------------------------- |
| random_page_cost         | 1.1   | 4.0     | SSD random I/O nearly as fast as sequential |
| effective_io_concurrency | 200   | 1       | SSD can handle many concurrent I/O requests |

### Parallel Query Settings

| Setting                          | Value | Default | Rationale                              |
| -------------------------------- | ----- | ------- | -------------------------------------- |
| max_parallel_workers_per_gather  | 2     | 2       | Conservative for Docker CPU allocation |
| max_worker_processes             | 8     | 8       | Total background workers available     |
| max_parallel_workers             | 4     | 8       | Cap on parallel query workers          |
| max_parallel_maintenance_workers | 2     | 2       | Parallel index creation and vacuum     |

### Autovacuum Configuration

Autovacuum is tuned aggressively for multi-tenant workloads where each tenant schema contains its own set of tables that accumulate dead tuples independently.

| Setting                         | Value | Default | Rationale                                     |
| ------------------------------- | ----- | ------- | --------------------------------------------- |
| autovacuum                      | on    | on      | Never disable in production                   |
| autovacuum_max_workers          | 4     | 3       | Extra capacity for multi-tenant schemas       |
| autovacuum_naptime              | 30s   | 1min    | Shorter interval detects bloat sooner         |
| autovacuum_vacuum_threshold     | 50    | 50      | Minimum dead tuples before vacuum             |
| autovacuum_vacuum_scale_factor  | 0.05  | 0.2     | 5% vs 20% — more aggressive for large tables  |
| autovacuum_analyze_threshold    | 50    | 50      | Minimum changed rows before analyze           |
| autovacuum_analyze_scale_factor | 0.02  | 0.1     | 2% keeps statistics fresh                     |
| autovacuum_vacuum_cost_delay    | 2ms   | 2ms     | Responsive vacuuming                          |
| autovacuum_vacuum_cost_limit    | 400   | 200     | Doubled throughput for multi-tenant workloads |

### Timeout Settings

Timeouts protect shared resources in a multi-tenant environment where one tenant's runaway query or abandoned transaction could block others.

| Setting                             | Value | Default | Rationale                                 |
| ----------------------------------- | ----- | ------- | ----------------------------------------- |
| statement_timeout                   | 30s   | 0 (off) | Prevents runaway queries                  |
| lock_timeout                        | 10s   | 0 (off) | Prevents indefinite lock waits            |
| idle_in_transaction_session_timeout | 300s  | 0 (off) | Prevents abandoned transactions and bloat |

### Query Statistics (pg_stat_statements)

pg_stat_statements tracks execution statistics for all SQL statements, enabling slow query identification and index optimization.

| Setting                           | Value              | Default | Rationale                             |
| --------------------------------- | ------------------ | ------- | ------------------------------------- |
| shared_preload_libraries          | pg_stat_statements | (none)  | Must be preloaded at startup          |
| pg_stat_statements.max            | 5000               | 5000    | Track up to 5000 distinct statements  |
| pg_stat_statements.track          | all                | top     | Includes statements inside functions  |
| pg_stat_statements.track_utility  | on                 | on      | Track DDL and utility commands        |
| pg_stat_statements.track_planning | on                 | off     | Separate planning from execution time |
