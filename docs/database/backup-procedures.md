# Backup and Recovery Procedures

> Backup strategy, restore workflows, retention policy, and WAL archiving for LankaCommerce Cloud's PostgreSQL database.

---

## Table of Contents

- [Backup Strategy Overview](#backup-strategy-overview)
- [Backup Types](#backup-types)
- [Backup Script](#backup-script)
- [Restore Script](#restore-script)
- [Retention Policy](#retention-policy)
- [WAL Archiving](#wal-archiving)
- [Point-in-Time Recovery](#point-in-time-recovery)
- [Multi-Tenant Backup Considerations](#multi-tenant-backup-considerations)
- [Production Backup Recommendations](#production-backup-recommendations)
- [Disaster Recovery Runbook](#disaster-recovery-runbook)

---

## Backup Strategy Overview

LankaCommerce Cloud uses a layered backup strategy combining logical dumps with WAL archiving for development and staging environments.

### Strategy Layers

| Layer          | Method                | Recovery Speed   | Data Loss Window  |
| -------------- | --------------------- | ---------------- | ----------------- |
| Logical backup | pg_dump custom format | Minutes          | Since last backup |
| WAL archiving  | Continuous WAL copy   | Minutes          | Up to 5 minutes   |
| PITR           | Base backup + WAL     | Minutes to hours | Seconds           |

### Backup Schedule

| Backup Type | Frequency    | Retention | Purpose                |
| ----------- | ------------ | --------- | ---------------------- |
| Daily       | Every day    | 7 copies  | Routine protection     |
| Weekly      | Every Sunday | 4 copies  | Weekly recovery points |
| Monthly     | 1st of month | 3 copies  | Long-term archive      |
| WAL archive | Continuous   | 7 days    | Point-in-time recovery |

---

## Backup Types

### Logical Backup (pg_dump)

The primary backup method uses pg_dump with custom format, which provides compression, selective restore, and parallel restore support.

| Feature           | Custom Format (-F c) | Plain SQL (-F p) | Directory (-F d) |
| ----------------- | -------------------- | ---------------- | ---------------- |
| Compression       | Built-in             | Manual gzip      | Built-in         |
| Selective restore | Yes                  | No               | Yes              |
| Parallel restore  | Yes                  | No               | Yes              |
| Human readable    | No                   | Yes              | No               |
| Recommended       | Yes (primary)        | For debugging    | For large DBs    |

### Physical Backup (pg_basebackup)

For production environments, pg_basebackup creates a binary copy of the entire data directory. Combined with WAL archiving, this enables point-in-time recovery.

| Feature               | pg_basebackup      | pg_dump             |
| --------------------- | ------------------ | ------------------- |
| Backup speed          | Fast (binary copy) | Slower (SQL export) |
| Includes WAL          | Optional           | No                  |
| Cross-version restore | No                 | Yes                 |
| Selective restore     | No                 | Yes                 |
| PITR support          | Yes (with WAL)     | No                  |

---

## Backup Script

The backup script is located at `scripts/db-backup.sh`.

### Script Capabilities

| Capability             | Description                                             |
| ---------------------- | ------------------------------------------------------- |
| Custom format dump     | pg_dump with -F c for compression and selective restore |
| Checksum generation    | SHA-256 checksum for each backup file                   |
| Retention cleanup      | Automatic removal of backups beyond retention limits    |
| Multi-database support | Backup individual or all databases                      |
| Classified storage     | Separate directories for daily, weekly, monthly backups |
| Latest symlink         | Always maintains a latest backup copy                   |

### Usage

| Command                                     | Action                  |
| ------------------------------------------- | ----------------------- |
| `./scripts/db-backup.sh`                    | Backup default database |
| `./scripts/db-backup.sh --all`              | Backup all databases    |
| `./scripts/db-backup.sh lankacommerce_test` | Backup test database    |
| `./scripts/db-backup.sh --help`             | Show usage information  |

### Configuration

| Variable          | Default   | Description               |
| ----------------- | --------- | ------------------------- |
| DB_HOST           | pgbouncer | Database host             |
| DB_PORT           | 6432      | Database port             |
| DB_USER           | lcc_user  | Database user             |
| BACKUP_DIR        | ./backups | Backup storage directory  |
| RETENTION_DAILY   | 7         | Daily backups to retain   |
| RETENTION_WEEKLY  | 4         | Weekly backups to retain  |
| RETENTION_MONTHLY | 3         | Monthly backups to retain |

### Backup Directory Structure

| Path             | Contents                           |
| ---------------- | ---------------------------------- |
| backups/daily/   | Daily backup files and checksums   |
| backups/weekly/  | Weekly backup files and checksums  |
| backups/monthly/ | Monthly backup files and checksums |
| backups/latest/  | Most recent backup copy            |

---

## Restore Script

The restore script is located at `scripts/db-restore.sh`.

### Script Capabilities

| Capability              | Description                                            |
| ----------------------- | ------------------------------------------------------ |
| Full restore            | Drop and recreate database, then restore               |
| Schema-only restore     | Restore a single tenant schema                         |
| Checksum verification   | Verify backup integrity before restoring               |
| Content listing         | List backup contents without restoring                 |
| Post-restore validation | Automatic schema, table, and extension count check     |
| Safety confirmation     | Interactive confirmation before destructive operations |

### Usage

| Command                                                    | Action                      |
| ---------------------------------------------------------- | --------------------------- |
| `./scripts/db-restore.sh backup.dump`                      | Restore to default database |
| `./scripts/db-restore.sh backup.dump mydb`                 | Restore to named database   |
| `./scripts/db-restore.sh --schema tenant_acme backup.dump` | Restore single schema       |
| `./scripts/db-restore.sh --list backup.dump`               | List backup contents        |
| `./scripts/db-restore.sh --skip-verify backup.dump`        | Skip checksum verification  |

### Restore Workflow

| Step | Action                        | Details                            |
| ---- | ----------------------------- | ---------------------------------- |
| 1    | Verify checksum               | Compare SHA-256 hash               |
| 2    | Confirm destructive operation | Interactive prompt (skipped in CI) |
| 3    | Terminate active connections  | pg_terminate_backend on target DB  |
| 4    | Drop existing database        | dropdb --if-exists                 |
| 5    | Create fresh database         | createdb with UTF-8 encoding       |
| 6    | Restore from backup           | pg_restore with --no-owner         |
| 7    | Validate restore              | Count schemas, tables, extensions  |

---

## Retention Policy

The retention policy follows a 7-4-3 rotation scheme to balance storage usage with recovery flexibility.

### Retention Schedule

| Tier    | Frequency    | Copies Kept | Max Age  | Storage Impact |
| ------- | ------------ | ----------- | -------- | -------------- |
| Daily   | Every day    | 7           | 7 days   | Low            |
| Weekly  | Sundays      | 4           | ~28 days | Medium         |
| Monthly | 1st of month | 3           | ~90 days | Medium         |

### Storage Capacity Planning

| Factor                  | Estimate                          |
| ----------------------- | --------------------------------- |
| Typical database size   | 50 MB - 500 MB (development)      |
| Compression ratio       | ~3:1 with pg_dump custom format   |
| Daily backup size       | 15 MB - 170 MB compressed         |
| Total daily retention   | 7 x backup size (105 MB - 1.2 GB) |
| Total weekly retention  | 4 x backup size (60 MB - 680 MB)  |
| Total monthly retention | 3 x backup size (45 MB - 510 MB)  |
| Maximum total storage   | ~2.4 GB for a 500 MB database     |

### Cleanup Rules

| Rule                    | Implementation                   |
| ----------------------- | -------------------------------- |
| Daily beyond 7 copies   | Oldest daily files deleted       |
| Weekly beyond 4 copies  | Oldest weekly files deleted      |
| Monthly beyond 3 copies | Oldest monthly files deleted     |
| Checksum files          | Deleted alongside their backup   |
| Latest copy             | Always replaced by newest backup |

---

## WAL Archiving

WAL (Write-Ahead Log) archiving continuously copies completed WAL segments to an archive location, enabling point-in-time recovery to any moment between the oldest archived WAL and the present.

### Configuration

| Setting         | Value                                  | Purpose                           |
| --------------- | -------------------------------------- | --------------------------------- |
| wal_level       | replica                                | Required for archiving            |
| archive_mode    | on                                     | Enable WAL archiving              |
| archive_command | cp to /var/lib/postgresql/wal_archive/ | Copy completed WAL segments       |
| archive_timeout | 300 (5 minutes)                        | Force archive of partial segments |

### Archive Storage

| Environment | Location                             | Retention |
| ----------- | ------------------------------------ | --------- |
| Development | Docker volume (postgres-wal-archive) | 7 days    |
| Production  | Object storage (S3, GCS, Azure Blob) | 30 days   |

### WAL Segment Details

| Property         | Value                                             |
| ---------------- | ------------------------------------------------- |
| Segment size     | 16 MB (default)                                   |
| Archive trigger  | Segment full OR archive_timeout reached           |
| Failure handling | PostgreSQL retries until archive_command succeeds |
| Max data loss    | Up to archive_timeout (5 minutes)                 |

---

## Point-in-Time Recovery

PITR combines a base backup with WAL archives to restore the database to any specific point in time.

### PITR Prerequisites

| Requirement         | Status                                           |
| ------------------- | ------------------------------------------------ |
| wal_level = replica | Configured in postgresql.conf                    |
| archive_mode = on   | Configured in postgresql.conf                    |
| archive_command set | Configured in postgresql.conf                    |
| Base backup         | Created with pg_basebackup                       |
| WAL archive intact  | Continuous chain from base backup to target time |

### PITR Recovery Steps

| Step | Action                            | Details                            |
| ---- | --------------------------------- | ---------------------------------- |
| 1    | Stop PostgreSQL                   | Prevent further WAL generation     |
| 2    | Move current data directory aside | Preserve for investigation         |
| 3    | Restore base backup               | Copy base backup to data directory |
| 4    | Configure recovery target         | Set recovery_target_time in config |
| 5    | Copy WAL archives to pg_wal       | Or set restore_command in config   |
| 6    | Start PostgreSQL                  | Recovery proceeds automatically    |
| 7    | Validate restored data            | Check tenant schemas and tables    |

### Recovery Target Options

| Target Type         | PostgreSQL Setting            | Use Case                   |
| ------------------- | ----------------------------- | -------------------------- |
| Specific time       | recovery_target_time          | Recover to before an error |
| Transaction ID      | recovery_target_xid           | Recover to specific commit |
| Named restore point | recovery_target_name          | Pre-deployment checkpoint  |
| Immediate           | recovery_target = 'immediate' | Latest consistent state    |

---

## Multi-Tenant Backup Considerations

### Schema-Aware Backups

Each tenant has its own PostgreSQL schema. The backup scripts capture all schemas in a single dump, but restore supports per-schema granularity.

| Scenario                      | Approach                                     |
| ----------------------------- | -------------------------------------------- |
| Full disaster recovery        | Restore entire database from backup          |
| Single tenant data corruption | Restore single schema with --schema flag     |
| Tenant data export            | pg_dump --schema=tenant_slug for one tenant  |
| Tenant migration              | Dump one schema, restore to another database |

### Backup Scope

| Component        | Included in Backup | Notes                            |
| ---------------- | ------------------ | -------------------------------- |
| Public schema    | Yes                | Tenant registry, shared config   |
| Tenant schemas   | Yes (all)          | All tenant data and structures   |
| Extensions       | Metadata only      | Must be recreated before restore |
| Roles/privileges | No (--no-owner)    | Recreated by init scripts        |
| WAL data         | Separate (archive) | Continuous archiving             |

---

## Production Backup Recommendations

### Recommended Production Stack

| Component     | Tool                                   |
| ------------- | -------------------------------------- |
| Base backups  | pg_basebackup on schedule              |
| WAL archiving | pgBackRest or WAL-G to object storage  |
| Monitoring    | Alert on archive lag and backup age    |
| Encryption    | Encrypt backups at rest and in transit |
| Testing       | Automated restore tests weekly         |

### Production Checklist

| Check                      | Priority | Notes                            |
| -------------------------- | -------- | -------------------------------- |
| Backups run on schedule    | Critical | Monitor via alerting             |
| WAL archiving has no gaps  | Critical | Check archive_command exit codes |
| Restore tested recently    | High     | Test monthly at minimum          |
| Backup encryption enabled  | High     | Especially for tenant data       |
| Offsite backup copy exists | High     | Different region or provider     |
| Retention policy enforced  | Medium   | Automated cleanup                |
| Backup size monitored      | Medium   | Alert on unexpected growth       |

---

## Disaster Recovery Runbook

### Scenario Response Matrix

| Scenario                 | Recovery Method            | Expected RTO   | Expected RPO      |
| ------------------------ | -------------------------- | -------------- | ----------------- |
| Accidental table drop    | PITR to before the DROP    | 15-30 minutes  | Seconds           |
| Single tenant corruption | Schema restore from backup | 5-15 minutes   | Since last backup |
| Full database failure    | Full restore from backup   | 15-60 minutes  | Since last backup |
| Storage failure          | PITR from base + WAL       | 30-120 minutes | Up to 5 minutes   |
| Complete host failure    | Restore to new host        | 1-4 hours      | Up to 5 minutes   |

### Recovery Decision Tree

| Question                              | Yes                  | No                        |
| ------------------------------------- | -------------------- | ------------------------- |
| Is the database server running?       | Check data integrity | Restore from backup       |
| Is the data directory intact?         | Attempt PITR         | Restore base backup + WAL |
| Is only one tenant affected?          | Schema-level restore | Full database restore     |
| Do you need data from the last 5 min? | Use PITR with WAL    | Use latest logical backup |
| Is the WAL archive chain complete?    | Proceed with PITR    | Fall back to logical dump |

---

**Related Documentation**

- Performance Tuning Guide — see performance-tuning.md
- PgBouncer Connection Pooling — see pgbouncer.md
- Schema Naming and Multi-Tenancy Layout — see schema-naming.md
- PostgreSQL Docker Configuration — see docker/postgres/README.md
