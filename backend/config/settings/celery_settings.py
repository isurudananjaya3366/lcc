"""
LankaCommerce Cloud - Dedicated Celery Settings Module.

Centralised constants and configuration for the Celery task queue.
Imported by ``config.settings.base`` to keep the main settings file
manageable.  Environment-specific overrides (e.g. ``ALWAYS_EAGER``
for tests) live in the corresponding settings module.

Constants defined here are **not** Django settings themselves — they
are plain Python values used either directly or referenced when
building the ``CELERY_*`` settings in ``base.py``.
"""

from kombu import Exchange, Queue


# ════════════════════════════════════════════════════════════════════════
# DEFAULT RETRY POLICY
# ════════════════════════════════════════════════════════════════════════
# These constants serve as project-wide defaults.  Individual tasks may
# override via their ``@shared_task(max_retries=…)`` decorator kwargs.

DEFAULT_RETRY_DELAY = 60           # seconds before first retry
MAX_RETRIES = 3                    # maximum retry attempts
RETRY_BACKOFF = True               # exponential back-off
RETRY_BACKOFF_MAX = 600            # cap at 10 minutes
RETRY_JITTER = True                # randomised jitter to avoid thundering herd


# ════════════════════════════════════════════════════════════════════════
# EXCHANGES & QUEUES
# ════════════════════════════════════════════════════════════════════════

default_exchange = Exchange("default", type="direct")

TASK_QUEUES = (
    Queue("high_priority", default_exchange, routing_key="high"),
    Queue("default", default_exchange, routing_key="default"),
    Queue("low_priority", default_exchange, routing_key="low"),
)

TASK_DEFAULT_QUEUE = "default"
TASK_DEFAULT_EXCHANGE = "default"
TASK_DEFAULT_ROUTING_KEY = "default"


# ════════════════════════════════════════════════════════════════════════
# TASK ROUTING
# ════════════════════════════════════════════════════════════════════════
# Maps task name patterns to queues.  Patterns ending with ``.*`` are
# matched by Celery's built-in glob router.

TASK_ROUTES = {
    "apps.core.tasks.email_tasks.*": {"queue": "default"},
    "apps.core.tasks.notification_tasks.*": {"queue": "default"},
    "apps.core.tasks.report_tasks.*": {"queue": "low_priority"},
    "apps.core.tasks.scheduled_tasks.*": {"queue": "low_priority"},
}
