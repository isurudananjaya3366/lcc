# Indexing Guidelines

> Index strategy, naming conventions, and monitoring practices for LankaCommerce Cloud's multi-tenant PostgreSQL database.

---

## Table of Contents

- [Index Naming Convention](#index-naming-convention)
- [Index Strategy by Table Type](#index-strategy-by-table-type)
- [Multi-Tenant Index Considerations](#multi-tenant-index-considerations)
- [Common Index Patterns](#common-index-patterns)
- [Partial Indexes](#partial-indexes)
- [Composite Index Ordering](#composite-index-ordering)
- [Monitoring with pg_stat_statements](#monitoring-with-pg_stat_statements)
- [Index Maintenance](#index-maintenance)

---

## Index Naming Convention

All indexes follow a consistent naming scheme to make them identifiable across tenant schemas and the public schema.

### Naming Pattern

| Component  | Rule                                                       |
| ---------- | ---------------------------------------------------------- |
| Prefix     | `ix_` for regular indexes, `uq_` for unique indexes        |
| Table name | Abbreviated table name without the app prefix              |
| Column(s)  | Column name(s) joined by underscores                       |
| Suffix     | `_partial` for partial indexes, `_gin` or `_gist` for type |
| Max length | 63 characters total (PostgreSQL identifier limit)          |

### Examples

| Index Name                | Type    | Purpose                          |
| ------------------------- | ------- | -------------------------------- |
| `ix_product_sku`          | B-tree  | Lookup products by SKU           |
| `uq_product_sku`          | Unique  | Enforce unique SKU per tenant    |
| `ix_order_created_at`     | B-tree  | Sort orders by date              |
| `ix_order_status_partial` | Partial | Active orders only               |
| `ix_product_name_gin`     | GIN     | Full-text search on product name |
| `ix_customer_email_lower` | B-tree  | Case-insensitive email lookup    |

---

## Index Strategy by Table Type

### Public Schema Tables

Public schema tables are shared across all tenants. They typically have fewer rows but higher read frequency.

| Table Category    | Index Priority | Notes                                 |
| ----------------- | -------------- | ------------------------------------- |
| Tenant registry   | High           | Lookup by domain, slug, schema name   |
| Domain routing    | High           | Domain-to-tenant resolution           |
| Global config     | Low            | Small tables, sequential scan is fine |
| Shared references | Medium         | Country codes, currencies, tax codes  |

### Tenant Schema Tables

Each tenant schema contains an identical set of tables. Indexes are defined in Django models and replicated to every tenant schema by django-tenants during migration.

| Table Category | Index Priority | Notes                                    |
| -------------- | -------------- | ---------------------------------------- |
| Products       | High           | SKU lookup, category filtering, search   |
| Orders/Sales   | High           | Date range queries, status filtering     |
| Customers      | High           | Email lookup, name search                |
| Inventory      | High           | Stock level queries, warehouse filtering |
| Accounting     | Medium         | Journal entries by date and account      |
| HR             | Medium         | Employee lookup, payroll periods         |
| Audit logs     | Low            | Append-heavy, rarely queried in bulk     |

---

## Multi-Tenant Index Considerations

### Schema Isolation

Each tenant schema has its own copy of every index. This means index storage scales linearly with tenant count.

| Concern               | Recommendation                                   |
| --------------------- | ------------------------------------------------ |
| Index bloat           | Keep indexes minimal per table                   |
| Autovacuum contention | Fewer indexes means faster autovacuum per schema |
| Migration speed       | Each new index is created in every tenant schema |
| Storage per tenant    | Monitor with `pg_total_relation_size` per schema |

### Search Path Awareness

When Django sets the search_path to a tenant schema, PostgreSQL automatically uses the indexes in that schema. No special index configuration is needed for tenant isolation.

---

## Common Index Patterns

### Primary Key (Automatic)

Django creates a primary key index on every model's `id` field automatically. No manual action needed.

### Foreign Key Indexes

PostgreSQL does not automatically create indexes on foreign key columns. Django's `ForeignKey` field creates an index by default via `db_index=True`.

| Field Type                  | Auto-indexed | Notes                         |
| --------------------------- | ------------ | ----------------------------- |
| `ForeignKey`                | Yes          | Django adds `db_index=True`   |
| `OneToOneField`             | Yes          | Unique index created          |
| `ManyToManyField` (through) | Yes          | Composite index on join table |

### Text Search Indexes

For product search, customer lookup, and other text-heavy queries, use GIN indexes with `pg_trgm`.

| Use Case           | Index Type | Extension |
| ------------------ | ---------- | --------- |
| Trigram similarity | GIN        | pg_trgm   |
| Full-text search   | GIN        | Built-in  |
| Pattern matching   | GIN        | pg_trgm   |
| Exact match        | B-tree     | None      |

---

## Partial Indexes

Partial indexes cover a subset of rows, reducing storage and improving write performance.

### When to Use

| Scenario         | Example                                       |
| ---------------- | --------------------------------------------- |
| Status filtering | Active orders only (status != 'cancelled')    |
| Soft deletes     | Non-deleted records only (is_deleted = false) |
| Recent data      | Orders in the last 90 days                    |
| Null exclusion   | Rows where optional field is NOT NULL         |

### Sizing Benefit

A partial index on active orders (typically 20% of rows) uses roughly 20% of the storage of a full index while covering the majority of queries.

---

## Composite Index Ordering

Column order in composite indexes determines query planner effectiveness.

### Ordering Rules

| Rule                      | Explanation                                       |
| ------------------------- | ------------------------------------------------- |
| Equality columns first    | Columns used in `WHERE col = value`               |
| Range columns second      | Columns used in `WHERE col BETWEEN` or `ORDER BY` |
| Selectivity descending    | Most selective (fewest matching rows) first       |
| Include-only columns last | Columns only needed in SELECT, not WHERE          |

### Example

For the query "find pending orders for a customer sorted by date":

| Column Position | Column      | Usage in Query   |
| --------------- | ----------- | ---------------- |
| 1               | customer_id | Equality filter  |
| 2               | status      | Equality filter  |
| 3               | created_at  | Range / ORDER BY |

---

## Monitoring with pg_stat_statements

pg_stat_statements is enabled in the PostgreSQL configuration and tracks execution statistics for all SQL statements.

### Key Monitoring Queries

Use the following views to identify indexing opportunities.

| Metric                        | What It Reveals                                |
| ----------------------------- | ---------------------------------------------- |
| Total execution time          | Queries consuming the most cumulative time     |
| Mean execution time           | Queries that are individually slow             |
| Calls count                   | Most frequently executed queries               |
| Rows returned vs rows scanned | Queries doing sequential scans on large tables |
| Shared blocks read vs hit     | Queries with poor cache hit ratio              |

### Identifying Missing Indexes

| Signal                          | Action                                          |
| ------------------------------- | ----------------------------------------------- |
| High rows scanned, low returned | Add an index on the WHERE clause columns        |
| Sequential scan on large table  | Check if an index exists for the filter columns |
| High shared blocks read         | Index may reduce disk I/O                       |
| Frequent sort operations        | Add index matching ORDER BY clause              |

### Resetting Statistics

Statistics accumulate over time. Reset periodically to measure the impact of index changes.

| Action                   | When to Reset                       |
| ------------------------ | ----------------------------------- |
| After adding a new index | To measure before/after improvement |
| After a deployment       | To capture fresh query patterns     |
| Weekly in development    | To keep statistics relevant         |

---

## Index Maintenance

### Routine Tasks

| Task                    | Frequency | Method                       |
| ----------------------- | --------- | ---------------------------- |
| Check index usage       | Weekly    | Query pg_stat_user_indexes   |
| Remove unused indexes   | Monthly   | Drop indexes with zero scans |
| Reindex bloated indexes | As needed | REINDEX CONCURRENTLY         |
| Monitor index size      | Weekly    | Query pg_total_relation_size |

### Autovacuum Interaction

Autovacuum maintains index health by removing dead tuples. The autovacuum configuration in postgresql.conf is tuned for multi-tenant workloads with aggressive thresholds.

| Setting                        | Value | Impact on Indexes                      |
| ------------------------------ | ----- | -------------------------------------- |
| autovacuum_vacuum_scale_factor | 0.05  | Triggers cleanup at 5% dead tuples     |
| autovacuum_naptime             | 30s   | Checks tables every 30 seconds         |
| autovacuum_max_workers         | 4     | Parallel cleanup across tenant schemas |

---

**Related Documentation**

- Schema Naming and Multi-Tenancy Layout — see schema-naming.md
- PgBouncer Connection Pooling — see pgbouncer.md
- Performance Tuning Guide — see performance-tuning.md
