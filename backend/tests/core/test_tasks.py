"""
LankaCommerce Cloud - Celery Task Tests (SP08 Tasks 82-86).

Covers:
    - BaseTask lifecycle hooks (on_success, on_failure, on_retry)
    - TenantAwareTask tenant-context switching
    - Email tasks (mock send_mail / send_mass_mail)
    - Report task (stub result)
    - Notification tasks (stub result)
    - Scheduled tasks (mock Tenant iteration)
    - Error handler signals
    - Task base-class assertions

All tests run without Redis or a Celery worker by using
CELERY_TASK_ALWAYS_EAGER = True (set in test_pg.py).
"""

import logging
from smtplib import SMTPException
from unittest.mock import MagicMock, patch

import pytest


# ════════════════════════════════════════════════════════════════════════
# BaseTask lifecycle hooks
# ════════════════════════════════════════════════════════════════════════


class TestBaseTaskLifecycle:
    """Verify BaseTask on_success / on_failure / on_retry hooks."""

    def test_on_success_logs_info(self, caplog):
        from apps.core.tasks.base import BaseTask

        task = BaseTask()
        task.name = "test_task"
        task._start_time = 0  # fake start so elapsed is large but finite

        with caplog.at_level(logging.INFO):
            task.on_success(retval={"ok": True}, task_id="abc-123", args=(), kwargs={})

        assert "succeeded" in caplog.text
        assert "abc-123" in caplog.text

    def test_on_failure_logs_error(self, caplog):
        from apps.core.tasks.base import BaseTask

        task = BaseTask()
        task.name = "test_task"

        with caplog.at_level(logging.ERROR):
            task.on_failure(
                exc=RuntimeError("boom"),
                task_id="abc-456",
                args=(),
                kwargs={},
                einfo="traceback…",
            )

        assert "failed" in caplog.text
        assert "abc-456" in caplog.text

    def test_on_retry_logs_warning(self, caplog):
        from apps.core.tasks.base import BaseTask

        task = BaseTask()
        task.name = "test_task"

        with caplog.at_level(logging.WARNING):
            task.on_retry(
                exc=RuntimeError("flaky"),
                task_id="abc-789",
                args=(),
                kwargs={},
                einfo="traceback…",
            )

        assert "retrying" in caplog.text.lower()
        assert "abc-789" in caplog.text

    def test_before_start_records_time(self):
        from apps.core.tasks.base import BaseTask

        task = BaseTask()
        task.before_start("id-1", args=(), kwargs={})
        assert hasattr(task, "_start_time")
        assert task._start_time > 0

    def test_get_elapsed_returns_zero_without_start(self):
        from apps.core.tasks.base import BaseTask

        task = BaseTask()
        assert task._get_elapsed("id-1") == 0.0


# ════════════════════════════════════════════════════════════════════════
# TenantAwareTask
# ════════════════════════════════════════════════════════════════════════


class TestTenantAwareTask:
    """Verify TenantAwareTask sets tenant context."""

    @patch("apps.core.tasks.base.connection")
    @patch("apps.tenants.models.Tenant.objects")
    def test_call_sets_tenant(self, mock_qs, mock_conn):
        from apps.core.tasks.base import TenantAwareTask

        tenant = MagicMock(pk=1, schema_name="acme")
        mock_qs.get.return_value = tenant

        # Create a concrete subclass because TenantAwareTask is abstract.
        # Patch celery.Task.__call__ to avoid needing a running app.
        class ConcreteTask(TenantAwareTask):
            abstract = False
            name = "test.concrete_task"

            def run(self, *args, **kwargs):
                return "ok"

        task = ConcreteTask()

        with patch.object(
            TenantAwareTask.__mro__[2],  # celery.Task
            "__call__",
            return_value="ok",
        ):
            result = task(tenant_id=1)

        mock_qs.get.assert_called_once_with(pk=1)
        mock_conn.set_tenant.assert_called_once_with(tenant)
        assert result == "ok"

    def test_call_without_tenant_id_raises(self):
        from apps.core.tasks.base import TenantAwareTask

        class ConcreteTask(TenantAwareTask):
            abstract = False
            name = "test.no_tenant"

            def run(self, *args, **kwargs):
                return "ok"

        task = ConcreteTask()
        with pytest.raises(ValueError, match="requires 'tenant_id'"):
            task()

    @patch("apps.core.tasks.base.connection")
    @patch("apps.tenants.models.Tenant.objects")
    def test_call_nonexistent_tenant_raises(self, mock_qs, mock_conn):
        from apps.core.tasks.base import TenantAwareTask

        # Import the actual exception from the tenant model's module
        from django.core.exceptions import ObjectDoesNotExist

        mock_qs.get.side_effect = ObjectDoesNotExist("not found")

        class ConcreteTask(TenantAwareTask):
            abstract = False
            name = "test.bad_tenant"

            def run(self, *args, **kwargs):
                return "ok"

        task = ConcreteTask()
        with pytest.raises(ObjectDoesNotExist):
            task(tenant_id=999)


# ════════════════════════════════════════════════════════════════════════
# Email Tasks
# ════════════════════════════════════════════════════════════════════════


class TestEmailTasks:
    """Test email tasks with mocked SMTP."""

    @patch("apps.core.tasks.base.connection")
    @patch("apps.tenants.models.Tenant.objects")
    @patch("apps.core.tasks.email_tasks.send_mail")
    def test_send_email_task_calls_send_mail(
        self, mock_send, mock_tenant_qs, mock_conn
    ):
        from apps.core.tasks.email_tasks import send_email_task

        tenant = MagicMock(pk=1, schema_name="acme")
        mock_tenant_qs.get.return_value = tenant

        send_email_task(
            tenant_id=1,
            subject="Hello",
            message="World",
            recipient_list=["user@example.com"],
        )

        mock_send.assert_called_once()
        call_kwargs = mock_send.call_args
        assert call_kwargs[1]["subject"] == "Hello"
        assert call_kwargs[1]["recipient_list"] == ["user@example.com"]

    @patch("apps.core.tasks.base.connection")
    @patch("apps.tenants.models.Tenant.objects")
    @patch("apps.core.tasks.email_tasks.send_mail", side_effect=SMTPException("fail"))
    def test_send_email_task_retries_on_smtp_error(
        self, mock_send, mock_tenant_qs, mock_conn
    ):
        from apps.core.tasks.email_tasks import send_email_task

        tenant = MagicMock(pk=1, schema_name="acme")
        mock_tenant_qs.get.return_value = tenant

        # In eager mode, retry raises the exception.  We expect the
        # SMTPException to eventually propagate after max retries.
        with pytest.raises((SMTPException, Exception)):
            send_email_task(
                tenant_id=1,
                subject="Hello",
                message="World",
                recipient_list=["user@example.com"],
            )

    @patch("apps.core.tasks.base.connection")
    @patch("apps.tenants.models.Tenant.objects")
    @patch("apps.core.tasks.email_tasks.send_mass_mail")
    def test_send_bulk_email_task(self, mock_mass, mock_tenant_qs, mock_conn):
        from apps.core.tasks.email_tasks import send_bulk_email_task

        tenant = MagicMock(pk=1, schema_name="acme")
        mock_tenant_qs.get.return_value = tenant

        messages = [
            ("Sub1", "Msg1", "from@ex.com", ["to1@ex.com"]),
            ("Sub2", "Msg2", "from@ex.com", ["to2@ex.com"]),
        ]
        send_bulk_email_task(tenant_id=1, messages=messages)

        mock_mass.assert_called_once()


# ════════════════════════════════════════════════════════════════════════
# Report Task
# ════════════════════════════════════════════════════════════════════════


class TestReportTask:
    """Test report generation stub."""

    @patch("apps.core.tasks.base.connection")
    @patch("apps.tenants.models.Tenant.objects")
    def test_generate_report_returns_stub(self, mock_tenant_qs, mock_conn):
        from apps.core.tasks.report_tasks import generate_report_task

        tenant = MagicMock(pk=1, schema_name="acme")
        mock_tenant_qs.get.return_value = tenant

        result = generate_report_task(
            tenant_id=1,
            report_type="daily_sales",
            params={"date": "2026-03-10"},
        )

        assert result["status"] == "generated"
        assert result["report_type"] == "daily_sales"
        assert result["tenant_id"] == 1


# ════════════════════════════════════════════════════════════════════════
# Notification Tasks
# ════════════════════════════════════════════════════════════════════════


class TestNotificationTasks:
    """Test notification task stubs."""

    @patch("apps.core.tasks.base.connection")
    @patch("apps.tenants.models.Tenant.objects")
    def test_send_notification_returns_sent(self, mock_tenant_qs, mock_conn):
        from apps.core.tasks.notification_tasks import send_notification_task

        tenant = MagicMock(pk=1, schema_name="acme")
        mock_tenant_qs.get.return_value = tenant

        result = send_notification_task(
            tenant_id=1,
            user_id=42,
            title="Alert",
            message="Low stock",
        )

        assert result["status"] == "sent"
        assert result["user_id"] == 42
        assert result["title"] == "Alert"

    @patch("apps.core.tasks.base.connection")
    @patch("apps.tenants.models.Tenant.objects")
    def test_send_push_notification_returns_sent(self, mock_tenant_qs, mock_conn):
        from apps.core.tasks.notification_tasks import send_push_notification_task

        tenant = MagicMock(pk=1, schema_name="acme")
        mock_tenant_qs.get.return_value = tenant

        result = send_push_notification_task(
            tenant_id=1,
            user_id=7,
            title="New Order",
            body="You have a new order #123",
        )

        assert result["status"] == "sent"
        assert result["user_id"] == 7


# ════════════════════════════════════════════════════════════════════════
# Scheduled Tasks
# ════════════════════════════════════════════════════════════════════════


class TestScheduledTasks:
    """Test scheduled (periodic) tasks with mocked tenant iteration."""

    @patch("apps.core.tasks.report_tasks.generate_report_task")
    @patch("apps.tenants.models.Tenant.objects")
    def test_daily_sales_report_dispatches_per_tenant(
        self, mock_tenant_qs, mock_report
    ):
        from apps.core.tasks.scheduled_tasks import daily_sales_report_task

        t1 = MagicMock(pk=1, schema_name="tenant_a")
        t2 = MagicMock(pk=2, schema_name="tenant_b")

        # Build a queryset mock that supports .filter().exclude().iterator()
        qs = MagicMock()
        qs.iterator.return_value = iter([t1, t2])
        mock_tenant_qs.filter.return_value.exclude.return_value = qs

        result = daily_sales_report_task()

        assert result["dispatched"] == 2
        assert mock_report.apply_async.call_count == 2

    @patch("apps.core.tasks.scheduled_tasks.connection")
    @patch("apps.tenants.models.Tenant.objects")
    def test_check_low_stock_iterates_tenants(self, mock_tenant_qs, mock_conn):
        from apps.core.tasks.scheduled_tasks import check_low_stock_task

        t1 = MagicMock(pk=1, schema_name="tenant_a")
        qs = MagicMock()
        qs.iterator.return_value = iter([t1])
        mock_tenant_qs.filter.return_value.exclude.return_value = qs

        result = check_low_stock_task()

        assert result["tenants_checked"] == 1
        mock_conn.set_tenant.assert_called_once_with(t1)

    @patch("apps.core.tasks.scheduled_tasks.Session")
    def test_cleanup_old_sessions(self, mock_session_cls):
        from apps.core.tasks.scheduled_tasks import cleanup_old_sessions_task

        qs = MagicMock()
        qs.count.return_value = 5
        mock_session_cls.objects.filter.return_value = qs

        result = cleanup_old_sessions_task()

        assert result["deleted_sessions"] == 5
        qs.delete.assert_called_once()

    def test_cleanup_expired_tokens_stub(self):
        from apps.core.tasks.scheduled_tasks import cleanup_expired_tokens_task

        result = cleanup_expired_tokens_task()
        assert result["status"] == "stub"

    def test_database_backup_stub(self):
        from apps.core.tasks.scheduled_tasks import database_backup_task

        result = database_backup_task()
        assert result["status"] == "stub"


# ════════════════════════════════════════════════════════════════════════
# Error Handler Signals
# ════════════════════════════════════════════════════════════════════════


class TestErrorHandlers:
    """Verify signal-based error/success handlers log correctly."""

    def test_task_failure_handler_logs_error(self, caplog):
        from apps.core.tasks.error_handlers import task_failure_handler

        sender = MagicMock(name="apps.core.tasks.email_tasks.send_email_task")
        sender.name = "apps.core.tasks.email_tasks.send_email_task"

        with caplog.at_level(logging.ERROR):
            task_failure_handler(
                task_id="fail-001",
                exception=RuntimeError("boom"),
                args=(),
                kwargs={"tenant_id": 1},
                traceback=None,
                einfo=None,
                sender=sender,
            )

        assert "TASK FAILURE" in caplog.text
        assert "fail-001" in caplog.text
        assert "RuntimeError" in caplog.text

    def test_task_success_handler_logs_debug(self, caplog):
        from apps.core.tasks.error_handlers import task_success_handler

        sender = MagicMock()
        sender.name = "apps.core.tasks.report_tasks.generate_report_task"

        with caplog.at_level(logging.DEBUG):
            task_success_handler(sender=sender, result={"ok": True})

        assert "TASK SUCCESS" in caplog.text


# ════════════════════════════════════════════════════════════════════════
# Task Base-Class Assertions
# ════════════════════════════════════════════════════════════════════════


def _unwrap_task(proxy_task):
    """Unwrap a Celery Proxy to get the real task class MRO names."""
    real = proxy_task._get_current_object()
    return [cls.__name__ for cls in type(real).__mro__]


class TestTaskBaseClasses:
    """Ensure tasks use the correct base classes."""

    def test_email_tasks_use_tenant_aware_base(self):
        from apps.core.tasks.email_tasks import (
            send_bulk_email_task,
            send_email_task,
        )

        for task in (send_email_task, send_bulk_email_task):
            bases = _unwrap_task(task)
            assert "TenantAwareTask" in bases, f"{task.name} MRO: {bases}"

    def test_report_task_uses_tenant_aware_base(self):
        from apps.core.tasks.report_tasks import generate_report_task

        bases = _unwrap_task(generate_report_task)
        assert "TenantAwareTask" in bases

    def test_notification_tasks_use_tenant_aware_base(self):
        from apps.core.tasks.notification_tasks import (
            send_notification_task,
            send_push_notification_task,
        )

        for task in (send_notification_task, send_push_notification_task):
            bases = _unwrap_task(task)
            assert "TenantAwareTask" in bases

    def test_scheduled_tasks_use_base_task(self):
        from apps.core.tasks.scheduled_tasks import (
            check_low_stock_task,
            cleanup_old_sessions_task,
            daily_sales_report_task,
        )

        for task in (
            daily_sales_report_task,
            check_low_stock_task,
            cleanup_old_sessions_task,
        ):
            bases = _unwrap_task(task)
            assert "BaseTask" in bases
