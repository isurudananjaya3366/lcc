"""
LankaCommerce Cloud - Core Task Package.

Re-exports all task classes and shared tasks so that callers can import
directly from ``apps.core.tasks`` without knowing the internal module
layout::

    from apps.core.tasks import send_email_task, BaseTask
"""

from apps.core.tasks.base import BaseTask, TenantAwareTask
from apps.core.tasks.email_tasks import send_bulk_email_task, send_email_task
from apps.core.tasks.error_handlers import task_failure_handler, task_success_handler
from apps.core.tasks.images import (
    cleanup_temp_images,
    process_bulk_images,
    process_image_async,
)
from apps.core.tasks.notification_tasks import (
    send_notification_task,
    send_push_notification_task,
)
from apps.core.tasks.report_tasks import generate_report_task
from apps.core.tasks.scheduled_tasks import (
    check_low_stock_task,
    cleanup_expired_tokens_task,
    cleanup_old_sessions_task,
    daily_sales_report_task,
    database_backup_task,
)

__all__ = [
    # Base classes
    "BaseTask",
    "TenantAwareTask",
    # Error handlers (signal-based)
    "task_failure_handler",
    "task_success_handler",
    # Email
    "send_email_task",
    "send_bulk_email_task",
    # Reports
    "generate_report_task",
    # Notifications
    "send_notification_task",
    "send_push_notification_task",
    # Image processing (SP10 Task 59)
    "process_image_async",
    "process_bulk_images",
    "cleanup_temp_images",
    # Scheduled / periodic
    "daily_sales_report_task",
    "check_low_stock_task",
    "cleanup_old_sessions_task",
    "cleanup_expired_tokens_task",
    "database_backup_task",
]
