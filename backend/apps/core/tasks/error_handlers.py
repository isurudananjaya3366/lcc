"""
LankaCommerce Cloud - Celery Task Error Handlers.

Signal-based handlers that fire on task failure and success events.
Connected via ``celery.signals.task_failure`` and ``celery.signals.task_success``
so they apply globally to **all** Celery tasks in the project.

Usage:
    Handlers are auto-registered on import.  The ``apps.core.tasks``
    package ``__init__.py`` re-exports this module, and Celery
    auto-discovers it via the standard ``autodiscover_tasks`` call
    in ``config/celery.py``.
"""

import logging

from celery.signals import task_failure, task_success

logger = logging.getLogger(__name__)

# ── Optional Sentry integration ───────────────────────────────────────
try:
    import sentry_sdk

    _HAS_SENTRY = True
except ImportError:  # pragma: no cover
    _HAS_SENTRY = False


@task_failure.connect
def task_failure_handler(
    task_id,
    exception,
    args,
    kwargs,
    traceback,
    einfo,
    sender=None,
    **kw,
):
    """Log every task failure with structured context.

    Fires for *all* tasks registered in the project. Individual tasks
    may also have their own ``on_failure`` hook (e.g. ``BaseTask``),
    but this signal handler provides a single centralised place for
    cross-cutting concerns like alerting or metrics.

    Args:
        task_id: Unique identifier of the failed task instance.
        exception: The exception that caused the failure.
        args: Positional arguments the task was called with.
        kwargs: Keyword arguments the task was called with.
        traceback: Python traceback object.
        einfo: Celery ``ExceptionInfo`` wrapper.
        sender: The task class that sent the signal.
    """
    task_name = getattr(sender, "name", "unknown")
    logger.error(
        "[TASK FAILURE] %s[%s] raised %s: %s | args=%s kwargs=%s",
        task_name,
        task_id,
        type(exception).__name__,
        exception,
        args,
        kwargs,
    )

    # ── Sentry alerting ────────────────────────────────────────────
    if _HAS_SENTRY:
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("celery.task_name", task_name)
            scope.set_tag("celery.task_id", str(task_id))
            scope.set_extra("celery.args", str(args))
            scope.set_extra("celery.kwargs", str(kwargs))
            sentry_sdk.capture_exception(exception)


@task_success.connect
def task_success_handler(sender=None, result=None, **kwargs):
    """Optionally track successful task completions.

    Kept lightweight — only logs at DEBUG level by default.
    Useful for metrics collection (Prometheus counters, StatsD, etc.).

    Args:
        sender: The task class that completed successfully.
        result: The return value of the task.
    """
    task_name = getattr(sender, "name", "unknown")
    logger.debug(
        "[TASK SUCCESS] %s completed | result=%s",
        task_name,
        result,
    )
