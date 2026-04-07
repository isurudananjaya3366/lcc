# Monitoring Queries

> PostgreSQL monitoring queries for database health, performance, and multi-tenant capacity management in LankaCommerce Cloud.

---

## Table of Contents

- [Connection Monitoring](#connection-monitoring)
- [Database Size Monitoring](#database-size-monitoring)
- [Schema Size Monitoring](#schema-size-monitoring)
- [Table Bloat and Autovacuum](#table-bloat-and-autovacuum)
- [Query Performance](#query-performance)
- [Lock Monitoring](#lock-monitoring)
- [Replication and WAL](#replication-and-wal)
- [Index Health](#index-health)
- [PgBouncer Pool Monitoring](#pgbouncer-pool-monitoring)
- [Monitoring Workflow](#monitoring-workflow)
- [Alerting Thresholds](#alerting-thresholds)

---

## Connection Monitoring

### Active Connections

Monitor the number of active connections to detect pool exhaustion or connection leaks.

| Metric                        | Source View      | Alert Threshold          |
| ----------------------------- | ---------------- | ------------------------ |
| Total connections             | pg_stat_activity | > 80% of max_connections |
| Active (non-idle) connections | pg_stat_activity | > 50% of max_connections |
| Idle connections              | pg_stat_activity | > 100 sustained          |
| Idle in transaction           | pg_stat_activity | Any lasting > 60 seconds |
| Waiting for lock              | pg_stat_activity | Any lasting > 10 seconds |

### Connection State Summary

Query pg_stat_activity grouped by state to get a snapshot of all connection states. The key states are active (executing a query), idle (waiting for a command), and idle in transaction (inside an open transaction but not running a query).

### Connections by Application

Group pg_stat_activity by application_name to see which applications consume the most connections. Django, Celery workers, and PgBouncer should each show a predictable pattern.

---

## Database Size Monitoring

### Overall Database Size

| Metric                  | What It Reveals                       |
| ----------------------- | ------------------------------------- |
| Total database size     | Storage consumption including indexes |
| Data size vs index size | Whether indexes dominate storage      |
| Growth rate per day     | Capacity planning metric              |
| Temporary file usage    | work_mem too low if frequent          |

### Database Size Breakdown

| Component          | How to Measure                         | Typical Range (Dev)  |
| ------------------ | -------------------------------------- | -------------------- |
| lankacommerce      | pg_database_size                       | 50 MB - 500 MB       |
| lankacommerce_test | pg_database_size                       | 10 MB - 100 MB       |
| WAL files          | pg_ls_waldir aggregate                 | 80 MB - 1 GB         |
| WAL archive        | ls -la /var/lib/postgresql/wal_archive | Varies with activity |

---

## Schema Size Monitoring

Schema size monitoring is essential for multi-tenant billing, capacity planning, and identifying tenants with disproportionate resource usage.

### Per-Tenant Schema Size

Each tenant schema (e.g. tenant_acme) contains tables, indexes, and sequences. The total size of all objects in a schema represents that tenant's storage footprint.

| Metric                   | Purpose                               |
| ------------------------ | ------------------------------------- |
| Total schema size        | Billing and quota enforcement         |
| Table count per schema   | Schema health verification            |
| Largest table per schema | Identifies storage-heavy tables       |
| Index size ratio         | Indexes should be 20-40% of data size |
| Growth rate per schema   | Capacity planning per tenant          |

### Schema Size Categories

| Category   | Size Range    | Action                                 |
| ---------- | ------------- | -------------------------------------- |
| Small      | < 10 MB       | Normal for new or low-activity tenants |
| Medium     | 10 - 100 MB   | Typical active tenant                  |
| Large      | 100 MB - 1 GB | Review for optimization opportunities  |
| Very large | > 1 GB        | Investigate bloat, archive old data    |

### Reporting Cadence

| Report                | Frequency | Audience                   |
| --------------------- | --------- | -------------------------- |
| Schema size snapshot  | Weekly    | DevOps, database team      |
| Growth trend analysis | Monthly   | Product, capacity planning |
| Quota utilization     | Daily     | Billing, tenant management |
| Bloat detection       | Weekly    | Database team              |

---

## Table Bloat and Autovacuum

### Autovacuum Health

| Metric                              | Source              | Concern Threshold        |
| ----------------------------------- | ------------------- | ------------------------ |
| Last autovacuum timestamp per table | pg_stat_user_tables | > 24 hours ago           |
| Last autoanalyze per table          | pg_stat_user_tables | > 24 hours ago           |
| Dead tuple count                    | pg_stat_user_tables | > 10% of live tuples     |
| Autovacuum workers running          | pg_stat_activity    | All workers busy         |
| Tables never vacuumed               | pg_stat_user_tables | Any (after first writes) |

### Bloat Indicators

| Signal                         | What It Means                          |
| ------------------------------ | -------------------------------------- |
| Table size >> data size        | Significant bloat present              |
| Sequential scan on large table | Missing index or bloated table         |
| Autovacuum running constantly  | High write rate or aggressive settings |
| Dead tuples accumulating       | Autovacuum falling behind              |

---

## Query Performance

### pg_stat_statements Analysis

pg_stat_statements tracks execution statistics for all SQL statements. Use it to identify the most impactful queries for optimization.

| Metric                        | What It Reveals                       |
| ----------------------------- | ------------------------------------- |
| Total execution time (top 10) | Queries consuming the most total CPU  |
| Mean execution time (top 10)  | Individually slow queries             |
| Calls count (top 10)          | Most frequently executed queries      |
| Rows returned / rows scanned  | Sequential scan candidates            |
| Shared blocks hit ratio       | Cache effectiveness (should be > 99%) |

### Slow Query Identification

| Category  | Threshold          | Action                        |
| --------- | ------------------ | ----------------------------- |
| Very slow | > 5 seconds mean   | Immediate investigation       |
| Slow      | 1 - 5 seconds mean | Review query plan and indexes |
| Moderate  | 100ms - 1s mean    | Monitor trend                 |
| Fast      | < 100ms mean       | No action needed              |

### Cache Hit Ratio

The shared buffer cache hit ratio should exceed 99% for a well-tuned database. A ratio below 95% indicates that shared_buffers may be too small or that working set exceeds available memory.

| Ratio     | Status    | Action                              |
| --------- | --------- | ----------------------------------- |
| > 99%     | Excellent | No action needed                    |
| 95% - 99% | Good      | Monitor trend                       |
| 90% - 95% | Warning   | Consider increasing shared_buffers  |
| < 90%     | Critical  | Increase shared_buffers immediately |

---

## Lock Monitoring

### Lock Types

| Lock Type           | Concern Level | Common Cause                  |
| ------------------- | ------------- | ----------------------------- |
| AccessShareLock     | Low           | Normal SELECT operations      |
| RowShareLock        | Low           | SELECT FOR UPDATE             |
| RowExclusiveLock    | Medium        | INSERT, UPDATE, DELETE        |
| ShareLock           | High          | CREATE INDEX (non-concurrent) |
| AccessExclusiveLock | Critical      | ALTER TABLE, DROP TABLE       |

### Lock Wait Detection

| Metric                  | Alert Threshold  |
| ----------------------- | ---------------- |
| Lock wait duration      | > 10 seconds     |
| Blocked queries count   | > 5 simultaneous |
| Deadlock count          | Any occurrence   |
| lock_timeout rejections | > 10 per hour    |

---

## Replication and WAL

### WAL Archive Health

| Metric                         | Source             | Alert Threshold     |
| ------------------------------ | ------------------ | ------------------- |
| Archive success count          | pg_stat_archiver   | Increasing (normal) |
| Archive failure count          | pg_stat_archiver   | Any failures        |
| Last successful archive        | pg_stat_archiver   | > 10 minutes ago    |
| WAL directory size             | pg_ls_waldir       | > 2x max_wal_size   |
| Archive lag (unarchived files) | pg_ls_waldir count | > 10 files          |

### Checkpoint Health

| Metric                        | Source           | Alert Threshold          |
| ----------------------------- | ---------------- | ------------------------ |
| Checkpoints timed             | pg_stat_bgwriter | Normal (expected)        |
| Checkpoints requested         | pg_stat_bgwriter | Frequent = WAL too small |
| Checkpoint write time         | pg_stat_bgwriter | > checkpoint_timeout     |
| Buffers written at checkpoint | pg_stat_bgwriter | High = memory pressure   |

---

## Index Health

### Index Usage Statistics

| Metric                          | Source               | Concern                        |
| ------------------------------- | -------------------- | ------------------------------ |
| Unused indexes (0 scans)        | pg_stat_user_indexes | Wasting storage and write perf |
| Index size vs table size        | pg_relation_size     | Indexes > 50% of data          |
| Index scans vs sequential scans | pg_stat_user_tables  | seq_scan >> idx_scan           |
| Most scanned indexes            | pg_stat_user_indexes | Informational                  |

### Index Maintenance Signals

| Signal                              | Action                              |
| ----------------------------------- | ----------------------------------- |
| Index never used after 30 days      | Consider dropping                   |
| Index larger than table             | Investigate bloat, consider REINDEX |
| Sequential scan on table with index | Check query plan (wrong index?)     |
| Many indexes on high-write table    | Reduce to essential indexes only    |

---

## PgBouncer Pool Monitoring

### Pool Health via Admin Console

Connect to PgBouncer admin console (port 6432, database pgbouncer) to monitor pool statistics.

| Metric                     | Source Command | Alert Threshold            |
| -------------------------- | -------------- | -------------------------- |
| Active server connections  | SHOW POOLS     | > 80% of default_pool_size |
| Waiting client connections | SHOW POOLS     | > 0 sustained              |
| Average query duration     | SHOW STATS     | Increasing trend           |
| Total queries per second   | SHOW STATS     | Baseline variance > 50%    |
| Free server connections    | SHOW POOLS     | 0 (pool exhausted)         |

### PgBouncer Configuration Review

| Check               | Expected Value | Impact if Wrong            |
| ------------------- | -------------- | -------------------------- |
| pool_mode           | transaction    | Session mode wastes conns  |
| default_pool_size   | 40             | Too low = waiting clients  |
| max_client_conn     | 400            | Too low = rejected clients |
| server_idle_timeout | 300            | Too low = churn            |

---

## Monitoring Workflow

### Daily Checks

| Check                            | Priority | Time Estimate |
| -------------------------------- | -------- | ------------- |
| Connection count vs limits       | High     | 1 minute      |
| Active locks and blocked queries | High     | 1 minute      |
| WAL archive status               | High     | 1 minute      |
| PgBouncer pool utilization       | Medium   | 1 minute      |
| Autovacuum activity              | Medium   | 2 minutes     |

### Weekly Checks

| Check                        | Priority | Time Estimate |
| ---------------------------- | -------- | ------------- |
| Top 10 queries by total time | High     | 5 minutes     |
| Unused index review          | Medium   | 5 minutes     |
| Schema size snapshot         | Medium   | 2 minutes     |
| Cache hit ratio              | Medium   | 1 minute      |
| Table bloat assessment       | Medium   | 5 minutes     |

### Monthly Checks

| Check                        | Priority | Time Estimate |
| ---------------------------- | -------- | ------------- |
| Database growth trend        | High     | 10 minutes    |
| Per-tenant size analysis     | High     | 10 minutes    |
| Query pattern changes        | Medium   | 15 minutes    |
| Connection pool right-sizing | Medium   | 10 minutes    |
| Backup restore test          | High     | 30 minutes    |

### Escalation Process

| Severity | Condition                 | Response Time | Action                    |
| -------- | ------------------------- | ------------- | ------------------------- |
| Critical | Database unreachable      | Immediate     | Page on-call engineer     |
| High     | Connection pool exhausted | 15 minutes    | Investigate and remediate |
| Medium   | Cache hit ratio < 95%     | 1 hour        | Investigate root cause    |
| Low      | Unused indexes detected   | Next sprint   | Clean up in maintenance   |

---

## Alerting Thresholds

### Summary of All Alert Thresholds

| Metric                 | Warning         | Critical      |
| ---------------------- | --------------- | ------------- |
| Connection utilization | > 70%           | > 90%         |
| Idle in transaction    | > 60 seconds    | > 300 seconds |
| Cache hit ratio        | < 97%           | < 95%         |
| Dead tuple ratio       | > 5%            | > 10%         |
| WAL archive lag        | > 5 files       | > 10 files    |
| Lock wait duration     | > 5 seconds     | > 30 seconds  |
| PgBouncer wait queue   | > 0 (sustained) | > 10 clients  |
| Schema size            | > 500 MB        | > 1 GB        |
| Backup age             | > 24 hours      | > 48 hours    |
| Query mean time        | > 1 second      | > 5 seconds   |

---

**Related Documentation**

- Performance Tuning Guide — see performance-tuning.md
- Indexing Guidelines — see indexing-guidelines.md
- Backup and Recovery Procedures — see backup-procedures.md
- PgBouncer Connection Pooling — see pgbouncer.md
