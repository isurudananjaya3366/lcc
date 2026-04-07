"""
Monitoring log model for tracking stock monitoring task executions.
"""

from django.db import models
from django.utils import timezone

from apps.core.mixins import UUIDMixin


class MonitoringLogManager(models.Manager):
    """Custom manager for MonitoringLog."""

    def get_recent(self, limit=10):
        """Return most recent monitoring logs."""
        return self.get_queryset().order_by("-run_started_at")[:limit]

    def get_monitoring_statistics(self, days=7):
        """Get monitoring execution statistics over a period."""
        from datetime import timedelta

        from django.db.models import Avg, Sum

        cutoff = timezone.now() - timedelta(days=days)
        logs = self.get_queryset().filter(run_started_at__gte=cutoff)

        total_runs = logs.count()
        successful_runs = logs.filter(status="completed").count()
        failed_runs = logs.filter(status="failed").count()

        aggregates = logs.aggregate(
            avg_execution_time=Avg("execution_time"),
            total_products_checked=Sum("products_checked"),
            total_alerts_created=Sum("alerts_created"),
        )

        last_run = logs.order_by("-run_started_at").first()

        return {
            "total_runs": total_runs,
            "success_rate": (
                round(successful_runs / total_runs * 100, 1) if total_runs > 0 else 0
            ),
            "failed_runs": failed_runs,
            "avg_execution_time": aggregates["avg_execution_time"],
            "total_products_checked": aggregates["total_products_checked"] or 0,
            "total_alerts_created": aggregates["total_alerts_created"] or 0,
            "last_run": last_run,
        }

    def cleanup_old_logs(self, retention_days=30):
        """Delete logs older than retention period."""
        from datetime import timedelta

        cutoff = timezone.now() - timedelta(days=retention_days)
        deleted, _ = self.get_queryset().filter(run_started_at__lt=cutoff).delete()
        return deleted


class MonitoringLog(UUIDMixin, models.Model):
    """
    Log of stock monitoring task executions.

    Tracks each monitoring run with statistics and results
    for debugging and performance monitoring.
    """

    STATUS_RUNNING = "running"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_RUNNING, "Running"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_FAILED, "Failed"),
    ]

    objects = MonitoringLogManager()

    run_started_at = models.DateTimeField(auto_now_add=True)
    run_completed_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_RUNNING,
    )

    # ── Statistics ──────────────────────────────────────────────
    products_checked = models.PositiveIntegerField(default=0)
    alerts_created = models.PositiveIntegerField(default=0)
    alerts_updated = models.PositiveIntegerField(default=0)
    alerts_resolved = models.PositiveIntegerField(default=0)
    errors_encountered = models.PositiveIntegerField(default=0)

    execution_time = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Execution time in seconds.",
    )

    # ── Error Details ───────────────────────────────────────────
    error_message = models.TextField(blank=True, default="")
    traceback = models.TextField(blank=True, default="")

    # ── Detailed Statistics ─────────────────────────────────────
    statistics = models.JSONField(
        default=dict,
        blank=True,
        help_text="Detailed statistics from the monitoring run.",
    )

    class Meta:
        verbose_name = "Monitoring Log"
        verbose_name_plural = "Monitoring Logs"
        db_table = "inventory_monitoring_log"
        ordering = ["-run_started_at"]
        indexes = [
            models.Index(fields=["-run_started_at"], name="idx_mlog_started"),
            models.Index(fields=["status"], name="idx_mlog_status"),
        ]

    def __str__(self):
        return f"Monitoring Run - {self.run_started_at:%Y-%m-%d %H:%M}"

    def mark_completed(self, stats):
        """Mark monitoring run as completed with statistics."""
        self.run_completed_at = timezone.now()
        self.status = self.STATUS_COMPLETED
        self.products_checked = stats.get("products_checked", 0)
        self.alerts_created = stats.get("alerts_created", 0)
        self.alerts_updated = stats.get("alerts_updated", 0)
        self.alerts_resolved = stats.get("alerts_resolved", 0)
        self.errors_encountered = stats.get("errors", 0)
        self.execution_time = stats.get("execution_time", 0)
        self.statistics = stats
        self.save()

    def mark_failed(self, error_message, tb=""):
        """Mark monitoring run as failed."""
        self.run_completed_at = timezone.now()
        self.status = self.STATUS_FAILED
        self.error_message = str(error_message)
        self.traceback = tb
        self.save()

    @property
    def duration(self):
        """Return duration of the monitoring run."""
        if self.run_completed_at and self.run_started_at:
            return self.run_completed_at - self.run_started_at
        return None
