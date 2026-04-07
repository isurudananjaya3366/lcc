# Celery Configuration

> LankaCommerce Cloud — Celery task queue configuration reference.

## Overview

LankaCommerce uses [Celery](https://docs.celeryq.dev/) with a
**Redis** broker and **django-db** result backend. Configuration
lives in:

| File                                     | Purpose                                  |
| ---------------------------------------- | ---------------------------------------- |
| `config/celery.py`                       | Celery app instance & autodiscovery      |
| `config/settings/base.py`                | `CELERY_*` Django settings               |
| `config/settings/celery_settings.py`     | Shared constants (retry, queues, routes) |
| `config/settings/test.py` / `test_pg.py` | Eager mode for tests                     |

---

## Broker & Result Backend

```python
# base.py
CELERY_BROKER_URL = env("CELERY_BROKER_URL")   # redis://redis:6379/0
CELERY_RESULT_BACKEND = "django-db"             # django-celery-results
CELERY_RESULT_EXTENDED = True                   # store task args/kwargs
```

Redis database allocation:

| DB  | Usage          |
| --- | -------------- |
| 0   | Celery broker  |
| 1   | Django cache   |
| 2   | Channels layer |
| 15  | Testing        |

---

## Serialisation

```python
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
```

Only JSON is accepted — no pickle. This is a security best practice.

---

## Task Execution Safeguards

```python
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60        # 30 min hard kill
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60   # 25 min graceful
```

---

## Retry Policy

```python
CELERY_TASK_DEFAULT_RETRY_DELAY = 60       # first retry after 60 s
CELERY_TASK_MAX_RETRIES = 3
CELERY_TASK_RETRY_BACKOFF = True           # exponential
CELERY_TASK_RETRY_BACKOFF_MAX = 600        # cap at 10 min
CELERY_TASK_RETRY_JITTER = True            # avoid thundering herd
```

Individual tasks may override via the `@shared_task()` decorator.

---

## Queues & Routing

Three priority queues are configured:

| Queue           | Routing Key | Use Case                         |
| --------------- | ----------- | -------------------------------- |
| `high_priority` | `high`      | Critical tasks (future use)      |
| `default`       | `default`   | Email, notifications             |
| `low_priority`  | `low`       | Reports, scheduled / batch tasks |

### Routing Rules

```python
CELERY_TASK_ROUTES = {
    "apps.core.tasks.email_tasks.*":        {"queue": "default"},
    "apps.core.tasks.notification_tasks.*":  {"queue": "default"},
    "apps.core.tasks.report_tasks.*":        {"queue": "low_priority"},
    "apps.core.tasks.scheduled_tasks.*":     {"queue": "low_priority"},
}
```

### Running Workers Per Queue

```bash
# Single worker consuming all queues
celery -A config.celery worker -Q high_priority,default,low_priority -l info

# Dedicated workers
celery -A config.celery worker -Q high_priority -c 2 -n high@%h
celery -A config.celery worker -Q default -c 4 -n default@%h
celery -A config.celery worker -Q low_priority -c 2 -n low@%h
```

---

## Beat Schedule

Periodic tasks are configured in `CELERY_BEAT_SCHEDULE`:

| Name                 | Task                                      | Schedule      |
| -------------------- | ----------------------------------------- | ------------- |
| `daily-sales-report` | `…scheduled_tasks.daily_sales_report`     | 06:00 daily   |
| `check-low-stock`    | `…scheduled_tasks.check_low_stock`        | Every 4 hours |
| `cleanup-sessions`   | `…scheduled_tasks.cleanup_old_sessions`   | 00:00 daily   |
| `cleanup-tokens`     | `…scheduled_tasks.cleanup_expired_tokens` | 02:00 daily   |

The scheduler uses `django_celery_beat.schedulers:DatabaseScheduler`,
allowing schedule edits via Django Admin without redeploying.

---

## Error Handling

Global signal handlers in `apps.core.tasks.error_handlers`:

- **`task_failure_handler`** — logs every failure with structured context.
- **`task_success_handler`** — optional DEBUG-level success tracking.

These complement the per-task `on_failure` / `on_success` hooks in
`BaseTask`.

---

## Environment Variables

| Variable            | Example                | Description           |
| ------------------- | ---------------------- | --------------------- |
| `CELERY_BROKER_URL` | `redis://redis:6379/0` | Broker connection URL |
| `TIME_ZONE`         | `Asia/Colombo`         | Celery timezone       |
| `FLOWER_USER`       | `admin`                | Flower UI username    |
| `FLOWER_PASSWORD`   | `changeme`             | Flower UI password    |

---

## Test Settings

```python
# config/settings/test_pg.py (and test.py)
CELERY_TASK_ALWAYS_EAGER = True       # run tasks synchronously
CELERY_TASK_EAGER_PROPAGATES = True   # propagate exceptions
```

See [task_creation.md](task_creation.md) for testing guidance.
