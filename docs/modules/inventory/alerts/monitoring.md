# Stock Monitoring

> Automated Celery-based stock level monitoring with configurable schedules
> and batch processing.

---

## How Monitoring Works

The main entry point is the `run_stock_monitoring` Celery task, scheduled via
Celery Beat (default: hourly).

### Execution Flow

```
run_stock_monitoring (Celery task)
  │
  ├─ Acquire concurrency lock (cache.add)
  ├─ Check monitoring window (start/end hours)
  ├─ Create MonitoringLog (status=running)
  │
  └─ monitor_stock(log)
       │
       ├─ filter_monitorable_products()
       │    └─ Active, track_inventory=True, not excluded
       │
       ├─ batch_process_products()  (100 per batch)
       │
       └─ For each product:
            generate_alerts_for_product(product)
              │
              ├─ ConfigResolver.resolve_for_product(product)
              ├─ Get all StockLevel records
              │
              └─ For each stock level:
                   process_stock_level(product, stock_level, config)
                     ├─ check_out_of_stock()
                     ├─ check_critical_stock()
                     ├─ check_low_stock()
                     ├─ determine_alert_type() → highest priority
                     ├─ create_alert_for_type() or auto_resolve_alerts()
                     └─ detect_back_in_stock()
```

---

## Celery Beat Schedule

| Task                          | Schedule      | Queue   |
| ----------------------------- | ------------- | ------- |
| `run_stock_monitoring`        | Every hour    | default |
| `auto_resolve_alerts_task`    | Every 30 min  | default |
| `check_expired_snoozes`       | Every 5 min   | default |
| `cleanup_old_monitoring_logs` | Daily 3:00 AM | default |

---

## Concurrency Protection

`run_stock_monitoring` uses a Redis cache lock (`stock_monitoring_lock`) to
prevent overlapping runs. Lock TTL: 1 hour. If a second run starts while one
is active, it returns `{"skipped": True, "reason": "concurrent_run"}`.

---

## Monitoring Window

`GlobalStockSettings.monitoring_start_hour` / `monitoring_end_hour` define
when monitoring is active (default 6–22). Outside this window, the task
returns early. `get_monitoring_schedule()` returns Celery crontab objects
based on the configured frequency.

---

## Product Exclusion

Products are excluded from monitoring when:

1. `ProductStockConfig.monitoring_enabled = False`
2. `exclude_from_monitoring = True` with active date range
3. Product has `track_inventory = False` or `is_active = False`

---

## Warehouse-Specific Monitoring

`monitor_warehouse_stock(product)` monitors per-warehouse:

- Creates warehouse-specific alerts for each stock level.
- Detects **company-wide OOS** when product is out of stock in ALL
  warehouses (creates alert with `warehouse=None`, `threshold_type="company_wide_oos"`).
- Checks **transfer opportunities** between warehouses when one is low
  and another has surplus (>2× threshold).

---

## Monitoring Logs

Each monitoring run creates a `MonitoringLog` record:

| Field                | Description                  |
| -------------------- | ---------------------------- |
| `status`             | running / completed / failed |
| `run_started_at`     | Timestamp                    |
| `run_completed_at`   | Timestamp                    |
| `products_checked`   | Count                        |
| `alerts_created`     | Count                        |
| `alerts_updated`     | Count                        |
| `alerts_resolved`    | Count                        |
| `errors_encountered` | Count                        |
| `execution_time`     | Decimal (seconds)            |
| `error_message`      | Failure details              |
| `statistics`         | JSON with full stats         |

Logs older than 30 days are cleaned up by `cleanup_old_monitoring_logs`.
