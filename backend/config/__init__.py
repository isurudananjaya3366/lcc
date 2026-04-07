"""
LankaCommerce Cloud - Config Package

This module ensures the Celery app is always imported when Django starts
so that shared_task will use this app.

References:
    https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html
"""

from config.celery import app as celery_app

__all__ = ("celery_app",)
