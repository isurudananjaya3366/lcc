# Performance Tuning Guide

> Complete reference for PostgreSQL performance settings in LankaCommerce Cloud, with rationale for each parameter and a tuning checklist.

---

## Table of Contents

- [Overview](#overview)
- [Connection Settings](#connection-settings)
- [Memory Settings](#memory-settings)
- [I/O and Planner Settings](#io-and-planner-settings)
- [Parallel Query Settings](#parallel-query-settings)
- [Background Writer Settings](#background-writer-settings)
- [Autovacuum Settings](#autovacuum-settings)
- [Timeout Settings](#timeout-settings)
- [Query Statistics](#query-statistics)
- [WAL Settings](#wal-settings)
- [Logging Settings](#logging-settings)
- [Production Scaling Guide](#production-scaling-guide)
- [Tuning Checklist](#tuning-checklist)

---

## Overview

All PostgreSQL performance parameters are defined in `docker/postgres/postgresql.conf`, which is mounted read-only into the database container. The configuration targets a development Docker environment with 2-4 GB of memory available to the database container.

### Configuration File Location

| Environment | Path                              |
| ----------- | --------------------------------- |
| Docker      | `/etc/postgresql/postgresql.conf` |
| Source      | `docker/postgres/postgresql.conf` |
| Mount mode  | Read-only                         |

---

## Connection Settings

| Parameter                        | Value | Rationale                                 |
| -------------------------------- | ----- | ----------------------------------------- |
| `listen_addresses`               | `*`   | Accept connections from Docker network    |
| `port`                           | 5432  | Standard PostgreSQL port                  |
| `max_connections`                | 200   | Accommodates Django, Celery, monitoring   |
| `superuser_reserved_connections` | 3     | Reserves slots for emergency admin access |

Applications connect through PgBouncer on port 6432, which multiplexes many client connections onto a smaller pool of PostgreSQL connections.

---

## Memory Settings

| Parameter              | Value | Rationale                                        |
| ---------------------- | ----- | ------------------------------------------------ |
| `shared_buffers`       | 256MB | ~25% of 1-2 GB container memory                  |
| `work_mem`             | 16MB  | Per-sort/hash memory, conservative for 200 conns |
| `maintenance_work_mem` | 64MB  | Speeds VACUUM and CREATE INDEX operations        |
| `effective_cache_size` | 512MB | Planner hint for total available cache           |

### Memory Budget

| Component                  | Calculation                 | Estimate |
| -------------------------- | --------------------------- | -------- |
| Shared buffers             | Fixed allocation            | 256 MB   |
| Per-connection work_mem    | 200 connections x 16 MB max | 3.2 GB   |
| Maintenance work_mem       | 1 operation at a time       | 64 MB    |
| OS and PostgreSQL overhead | Varies                      | ~200 MB  |

The worst-case memory scenario (all connections sorting simultaneously) is unlikely in practice. Typical usage is well within 2 GB.

---

## I/O and Planner Settings

| Parameter                  | Value | Rationale                                      |
| -------------------------- | ----- | ---------------------------------------------- |
| `random_page_cost`         | 1.1   | SSD storage — random I/O nearly as fast as seq |
| `effective_io_concurrency` | 200   | SSD can handle 200 concurrent I/O requests     |

### Storage Assumptions

| Storage Type | random_page_cost | effective_io_concurrency |
| ------------ | ---------------- | ------------------------ |
| HDD          | 4.0              | 2                        |
| SSD          | 1.1              | 200                      |
| NVMe         | 1.0              | 200+                     |

The development environment assumes SSD-backed Docker volumes. Adjust for production hardware.

---

## Parallel Query Settings

| Parameter                          | Value | Rationale                            |
| ---------------------------------- | ----- | ------------------------------------ |
| `max_parallel_workers_per_gather`  | 2     | Conservative for Docker CPU limits   |
| `max_worker_processes`             | 8     | Total background workers (default)   |
| `max_parallel_workers`             | 4     | Cap on parallel query workers        |
| `max_parallel_maintenance_workers` | 2     | Parallel index and vacuum operations |

### Worker Budget

| Worker Type              | Count  | Purpose                                   |
| ------------------------ | ------ | ----------------------------------------- |
| Parallel query workers   | 4 max  | Shared across concurrent parallel queries |
| Autovacuum workers       | 4      | Dedicated vacuum processes                |
| Other background workers | varies | Extensions, logical replication           |
| Total budget             | 8      | max_worker_processes                      |

---

## Background Writer Settings

| Parameter                 | Value | Rationale                        |
| ------------------------- | ----- | -------------------------------- |
| `bgwriter_lru_maxpages`   | 100   | Pages written per bgwriter cycle |
| `bgwriter_lru_multiplier` | 2.0   | Anticipates future buffer demand |

---

## Autovacuum Settings

Autovacuum is critical for multi-tenant databases where each tenant schema accumulates dead tuples independently.

| Parameter                         | Value | Default | Rationale                          |
| --------------------------------- | ----- | ------- | ---------------------------------- |
| `autovacuum`                      | on    | on      | Never disable                      |
| `autovacuum_max_workers`          | 4     | 3       | Extra capacity for many schemas    |
| `autovacuum_naptime`              | 30s   | 1min    | Faster detection of bloated tables |
| `autovacuum_vacuum_threshold`     | 50    | 50      | Minimum dead tuples to trigger     |
| `autovacuum_vacuum_scale_factor`  | 0.05  | 0.2     | 5% dead rows instead of 20%        |
| `autovacuum_analyze_threshold`    | 50    | 50      | Minimum changed rows for analyze   |
| `autovacuum_analyze_scale_factor` | 0.02  | 0.1     | 2% changed rows for fresh stats    |
| `autovacuum_vacuum_cost_delay`    | 2ms   | 2ms     | Fast vacuuming with minimal pause  |
| `autovacuum_vacuum_cost_limit`    | 400   | -1(200) | Double throughput for multi-tenant |

### Multi-Tenant Impact

With N tenant schemas, autovacuum must process N copies of each table. Aggressive settings ensure vacuuming keeps pace with tenant growth.

| Tenant Count | Tables per Tenant | Total Tables | Recommended Workers |
| ------------ | ----------------- | ------------ | ------------------- |
| 1-10         | 50                | 50-500       | 3 (default)         |
| 10-50        | 50                | 500-2,500    | 4 (current)         |
| 50-100       | 50                | 2,500-5,000  | 5-6                 |
| 100+         | 50                | 5,000+       | 6-8                 |

---

## Timeout Settings

Timeouts protect shared resources in a multi-tenant environment.

| Parameter                             | Value | Rationale                       |
| ------------------------------------- | ----- | ------------------------------- |
| `statement_timeout`                   | 30s   | Prevents runaway queries        |
| `lock_timeout`                        | 10s   | Prevents indefinite lock waits  |
| `idle_in_transaction_session_timeout` | 300s  | Prevents abandoned transactions |

### Timeout Hierarchy

| Timeout                               | Scope         | Override Method             |
| ------------------------------------- | ------------- | --------------------------- |
| `statement_timeout`                   | Per statement | SET LOCAL statement_timeout |
| `lock_timeout`                        | Per statement | SET LOCAL lock_timeout      |
| `idle_in_transaction_session_timeout` | Per session   | SET idle_in_transaction...  |

For long-running reports or migrations, override timeouts per session rather than increasing the global defaults.

---

## Query Statistics

pg_stat_statements is preloaded at server startup and tracks execution statistics for all SQL statements.

| Parameter                           | Value              | Rationale                             |
| ----------------------------------- | ------------------ | ------------------------------------- |
| `shared_preload_libraries`          | pg_stat_statements | Must be preloaded                     |
| `pg_stat_statements.max`            | 5000               | Track up to 5000 distinct statements  |
| `pg_stat_statements.track`          | all                | Includes statements inside functions  |
| `pg_stat_statements.track_utility`  | on                 | Track DDL and utility commands        |
| `pg_stat_statements.track_planning` | on                 | Separate planning from execution time |

### Memory Usage

Each tracked statement uses approximately 6 KB of shared memory. With 5000 tracked statements, total memory usage is approximately 30 MB.

### Top Queries by Total Time

To find the slowest queries, query the pg_stat_statements view and sort by total_exec_time. This reveals which queries benefit most from optimization.

### Index Optimization Workflow

1. Identify slow queries via pg_stat_statements
2. Check query plans with EXPLAIN ANALYZE
3. Add or modify indexes per the indexing guidelines
4. Reset statistics and measure improvement

See indexing-guidelines.md for detailed index strategy.

---

## WAL Settings

| Parameter                      | Value   | Rationale                          |
| ------------------------------ | ------- | ---------------------------------- |
| `wal_level`                    | replica | Supports streaming replication     |
| `max_wal_size`                 | 1GB     | Checkpoint interval upper bound    |
| `min_wal_size`                 | 80MB    | Minimum WAL retained               |
| `checkpoint_timeout`           | 10min   | Time between automatic checkpoints |
| `checkpoint_completion_target` | 0.9     | Spread I/O over 90% of interval    |

---

## Logging Settings

Development logging is configured for maximum visibility. Production should reduce verbosity.

| Parameter                    | Dev Value | Production Notes              |
| ---------------------------- | --------- | ----------------------------- |
| `log_statement`              | all       | Reduce to ddl or none         |
| `log_duration`               | on        | Keep on for slow query detect |
| `log_min_duration_statement` | 0         | Raise to 100-500ms            |
| `log_connections`            | on        | Keep on                       |
| `log_disconnections`         | on        | Keep on                       |
| `log_lock_waits`             | on        | Keep on                       |
| `log_temp_files`             | 0         | Keep — reveals sort spills    |

---

## Production Scaling Guide

When moving from development to production, adjust parameters based on actual hardware resources.

### Memory Scaling

| Container Memory | shared_buffers | work_mem | effective_cache_size | maintenance_work_mem |
| ---------------- | -------------- | -------- | -------------------- | -------------------- |
| 2 GB             | 256 MB         | 16 MB    | 512 MB               | 64 MB                |
| 4 GB             | 1 GB           | 32 MB    | 3 GB                 | 256 MB               |
| 8 GB             | 2 GB           | 64 MB    | 6 GB                 | 512 MB               |
| 16 GB            | 4 GB           | 64 MB    | 12 GB                | 1 GB                 |

### Connection Scaling

| Deployment Size   | max_connections | PgBouncer default_pool_size | max_client_conn |
| ----------------- | --------------- | --------------------------- | --------------- |
| Development       | 200             | 40                          | 400             |
| Small production  | 200             | 50                          | 500             |
| Medium production | 300             | 75                          | 1000            |
| Large production  | 500             | 100                         | 2000            |

### Timeout Adjustments

| Environment | statement_timeout | idle_in_transaction | lock_timeout |
| ----------- | ----------------- | ------------------- | ------------ |
| Development | 30s               | 300s (5 min)        | 10s          |
| Production  | 15s               | 60s (1 min)         | 5s           |

---

## Tuning Checklist

Use this checklist when setting up a new environment or reviewing performance.

### Connection and Memory

| Check | Setting              | Action                                     |
| ----- | -------------------- | ------------------------------------------ |
| [ ]   | max_connections      | Set based on application pool + headroom   |
| [ ]   | shared_buffers       | Set to 25% of container memory             |
| [ ]   | work_mem             | Validate max_connections x work_mem budget |
| [ ]   | effective_cache_size | Set to 50-75% of container memory          |
| [ ]   | maintenance_work_mem | Set based on largest expected index        |

### I/O and Parallelism

| Check | Setting                         | Action                             |
| ----- | ------------------------------- | ---------------------------------- |
| [ ]   | random_page_cost                | Confirm storage type (SSD vs HDD)  |
| [ ]   | effective_io_concurrency        | Match to storage capabilities      |
| [ ]   | max_parallel_workers_per_gather | Set based on available CPU cores   |
| [ ]   | max_parallel_workers            | Do not exceed max_worker_processes |

### Autovacuum

| Check | Setting                         | Action                                 |
| ----- | ------------------------------- | -------------------------------------- |
| [ ]   | autovacuum                      | Verify it is ON                        |
| [ ]   | autovacuum_max_workers          | Scale with tenant count                |
| [ ]   | autovacuum_vacuum_scale_factor  | Use 0.05 or lower for multi-tenant     |
| [ ]   | autovacuum_analyze_scale_factor | Use 0.02 or lower for fresh statistics |

### Timeouts

| Check | Setting                             | Action                                |
| ----- | ----------------------------------- | ------------------------------------- |
| [ ]   | statement_timeout                   | Set appropriate ceiling               |
| [ ]   | lock_timeout                        | Set to prevent indefinite waits       |
| [ ]   | idle_in_transaction_session_timeout | Set to prevent abandoned transactions |

### Monitoring

| Check | Setting                    | Action                               |
| ----- | -------------------------- | ------------------------------------ |
| [ ]   | pg_stat_statements         | Verify extension is loaded           |
| [ ]   | log_min_duration_statement | Set threshold for slow query logging |
| [ ]   | log_lock_waits             | Enable to detect contention          |

---

**Related Documentation**

- Schema Naming and Multi-Tenancy Layout — see schema-naming.md
- Indexing Guidelines — see indexing-guidelines.md
- PgBouncer Connection Pooling — see pgbouncer.md
- PostgreSQL Docker Configuration — see docker/postgres/README.md
