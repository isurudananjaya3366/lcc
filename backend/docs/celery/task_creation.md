# Creating New Celery Tasks

> LankaCommerce Cloud — guide for adding new asynchronous tasks.

## Quick Start

```python
# apps/<module>/tasks.py
from celery import shared_task
from apps.core.tasks.base import TenantAwareTask

@shared_task(
    bind=True,
    base=TenantAwareTask,
    name="apps.mymodule.tasks.do_work",
    max_retries=3,
    retry_backoff=True,
)
def do_work(self, *, tenant_id: int, item_id: int):
    """Process an item within a tenant schema."""
    # The DB connection is already set to the tenant schema
    # by TenantAwareTask.__call__.
    item = MyModel.objects.get(pk=item_id)
    item.process()
    return {"status": "done", "item_id": item_id}
```

---

## Base Classes

### `BaseTask`

Located in `apps.core.tasks.base`. Provides:

- **`on_success`** — logs completion time
- **`on_failure`** — logs exception + traceback
- **`on_retry`** — logs retry with reason
- **`before_start`** — records start timestamp for duration tracking

Use for tasks that do NOT need tenant context (e.g. maintenance,
cross-tenant aggregation).

### `TenantAwareTask`

Extends `BaseTask`. On every invocation:

1. Reads `tenant_id` from `kwargs`.
2. Loads the `Tenant` model instance.
3. Calls `connection.set_tenant(tenant)` to switch the DB schema.
4. Runs the task body with the correct schema active.

Also overrides `apply_async` to auto-propagate `tenant_id` from the
current request's tenant context.

**All domain-logic tasks should use `TenantAwareTask`.**

---

## Conventions

| Convention                                   | Reason                                              |
| -------------------------------------------- | --------------------------------------------------- |
| Always use `bind=True`                       | Access `self.retry()`, `self.request`               |
| Always set an explicit `name=`               | Avoids import-path surprises after refactoring      |
| Use `**kwargs` with `tenant_id: int`         | TenantAwareTask requires `tenant_id` as kwarg       |
| Return a dict                                | Stored in django-celery-results for inspection      |
| Raise `self.retry(exc=exc)` on transient err | Leverages the retry policy, preserves the exc chain |

---

## Retry Behaviour

Default retry policy (overridable per task):

```python
CELERY_TASK_DEFAULT_RETRY_DELAY = 60    # 1st retry after 60 s
CELERY_TASK_MAX_RETRIES = 3
CELERY_TASK_RETRY_BACKOFF = True        # exponential
CELERY_TASK_RETRY_BACKOFF_MAX = 600     # cap 10 min
CELERY_TASK_RETRY_JITTER = True         # randomised
```

To override on a specific task:

```python
@shared_task(bind=True, base=BaseTask, max_retries=5, retry_backoff=60)
def custom_retry_task(self, **kwargs):
    ...
```

---

## Queue Assignment

Tasks are routed by name pattern in `CELERY_TASK_ROUTES`:

| Pattern                                | Queue          |
| -------------------------------------- | -------------- |
| `apps.core.tasks.email_tasks.*`        | `default`      |
| `apps.core.tasks.notification_tasks.*` | `default`      |
| `apps.core.tasks.report_tasks.*`       | `low_priority` |
| `apps.core.tasks.scheduled_tasks.*`    | `low_priority` |

To send a task to a specific queue at call time:

```python
do_work.apply_async(
    kwargs={"tenant_id": 1, "item_id": 42},
    queue="high_priority",
)
```

---

## Testing Tasks

### Settings

Test settings enable Celery eager mode:

```python
# config/settings/test_pg.py
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
```

Tasks execute synchronously and exceptions propagate directly.

### Writing Tests

```python
from unittest.mock import MagicMock, patch

@patch("apps.tenants.models.Tenant.objects")
@patch("django.db.connection.set_tenant")
def test_my_task(mock_set_tenant, mock_tenant_qs):
    tenant = MagicMock(pk=1, schema_name="acme")
    mock_tenant_qs.get.return_value = tenant

    result = do_work(tenant_id=1, item_id=42)

    assert result["status"] == "done"
    mock_set_tenant.assert_called_once_with(tenant)
```

### Mocking Strategies

| What to mock                   | Why                               |
| ------------------------------ | --------------------------------- |
| `Tenant.objects.get`           | Avoid DB dependency               |
| `connection.set_tenant`        | Avoid PostgreSQL schema switching |
| `send_mail` / `send_mass_mail` | Avoid SMTP dependency             |
| External API clients           | Avoid network calls in tests      |

---

## Checklist for New Tasks

- [ ] Inherit from `BaseTask` or `TenantAwareTask`
- [ ] Set `bind=True` and explicit `name=`
- [ ] Define retry parameters
- [ ] Add routing rule in `base.py` `CELERY_TASK_ROUTES` if needed
- [ ] Re-export from `apps.core.tasks.__init__` (if in the core package)
- [ ] Write unit tests with mocks
- [ ] Document in this guide (if cross-cutting)
