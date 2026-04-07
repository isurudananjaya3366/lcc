"""
LankaCommerce Cloud - Celery Configuration

This module configures the Celery application for asynchronous task processing.
It integrates with Django settings using the CELERY_ namespace prefix and
auto-discovers tasks from all installed Django apps.

Usage:
    Tasks defined in any app's `tasks.py` are auto-discovered.
    Celery Beat (periodic tasks) is configured via django-celery-beat.

References:
    https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html
"""

import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("lankacommerce")

# Load task modules from all registered Django apps.
# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix in Django settings.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks from all installed apps.
# Each app can define tasks in a `tasks.py` module.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """A debug task that prints the current request info."""
    print(f"Request: {self.request!r}")
