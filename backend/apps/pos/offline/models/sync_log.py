"""
Sync Log model.

Records every synchronisation operation between POS terminals and the
server, including timing, entity counts, errors, network metrics, and
conflict details.
"""

import json

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import BaseModel
from apps.pos.offline.constants import (
    SYNC_DIRECTION_CHOICES,
    SYNC_DIRECTION_PUSH,
    SYNC_STATUS_CHOICES,
    SYNC_STATUS_COMPLETED,
    SYNC_STATUS_FAILED,
    SYNC_STATUS_PENDING,
    SYNC_TYPE_CHOICES,
    SYNC_TYPE_AUTO,
)


class SyncLog(BaseModel):
    """
    Immutable log of a single sync operation.

    Tracks which terminal initiated the sync, timing, per-entity counts,
    errors, network quality metrics, and conflict details. Used for
    monitoring, debugging, and analytics.
    """

    # ── Relationships ─────────────────────────────────────────────────────
    terminal = models.ForeignKey(
        "pos.POSTerminal",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sync_logs",
        help_text="Terminal that initiated this sync.",
    )
    config = models.ForeignKey(
        "pos.OfflineSyncConfig",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sync_logs",
        help_text="Sync configuration used for this operation.",
    )
    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="initiated_sync_logs",
        help_text="User who initiated the sync.",
    )

    # ── Sync Type / Status ────────────────────────────────────────────────
    sync_type = models.CharField(
        max_length=20,
        choices=SYNC_TYPE_CHOICES,
        default=SYNC_TYPE_AUTO,
        help_text="Type of sync operation.",
    )
    status = models.CharField(
        max_length=20,
        choices=SYNC_STATUS_CHOICES,
        default=SYNC_STATUS_PENDING,
        help_text="Current status of the sync operation.",
    )
    sync_direction = models.CharField(
        max_length=20,
        choices=SYNC_DIRECTION_CHOICES,
        default=SYNC_DIRECTION_PUSH,
        help_text="Direction of data flow.",
    )

    # ── Timing ────────────────────────────────────────────────────────────
    initiated_at = models.DateTimeField(
        default=timezone.now,
        help_text="When the sync was initiated.",
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the sync actually started processing.",
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the sync completed (success or failure).",
    )
    duration_ms = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Total duration of sync in milliseconds.",
    )

    # ── Entity Counts ─────────────────────────────────────────────────────
    entities_synced = models.JSONField(
        default=dict,
        blank=True,
        help_text="Per-entity breakdown of synced records.",
    )
    total_records_processed = models.PositiveIntegerField(
        default=0,
        help_text="Total number of records processed.",
    )
    records_successful = models.PositiveIntegerField(
        default=0,
        help_text="Number of records synced successfully.",
    )
    records_failed = models.PositiveIntegerField(
        default=0,
        help_text="Number of records that failed to sync.",
    )
    conflicts_detected = models.PositiveIntegerField(
        default=0,
        help_text="Number of conflicts detected during sync.",
    )

    # ── Error / Warning Tracking ──────────────────────────────────────────
    errors = models.JSONField(
        default=dict,
        blank=True,
        help_text="Structured error information.",
    )
    warnings = models.JSONField(
        default=list,
        blank=True,
        help_text="Non-fatal warnings encountered.",
    )

    # ── Data Transfer Metrics ─────────────────────────────────────────────
    bytes_uploaded = models.BigIntegerField(
        default=0,
        help_text="Total bytes uploaded to server.",
    )
    bytes_downloaded = models.BigIntegerField(
        default=0,
        help_text="Total bytes downloaded from server.",
    )
    network_latency_ms = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Average network latency in milliseconds.",
    )

    # ── Retry Information ─────────────────────────────────────────────────
    retry_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of retry attempts for this sync.",
    )
    retry_reason = models.TextField(
        blank=True,
        default="",
        help_text="Reason the sync was retried.",
    )

    # ── Conflict Details ──────────────────────────────────────────────────
    conflict_details = models.JSONField(
        default=dict,
        blank=True,
        help_text="Detailed conflict information for resolution.",
    )

    class Meta(BaseModel.Meta):
        db_table = "pos_sync_log"
        verbose_name = "Sync Log"
        verbose_name_plural = "Sync Logs"
        indexes = [
            models.Index(
                fields=["status"],
                name="idx_synclog_status",
            ),
            models.Index(
                fields=["initiated_at"],
                name="idx_synclog_initiated",
            ),
            models.Index(
                fields=["status", "initiated_at"],
                name="idx_synclog_status_init",
            ),
        ]

    def __str__(self):
        return (
            f"SyncLog {self.pk} [{self.sync_type}/{self.status}] "
            f"at {self.initiated_at:%Y-%m-%d %H:%M}"
        )

    # ── Properties ────────────────────────────────────────────────────────

    @property
    def success_rate(self):
        """Return percentage of successfully synced records."""
        if self.total_records_processed == 0:
            return 0.0
        return (self.records_successful / self.total_records_processed) * 100

    @property
    def is_successful(self):
        """Return True if the sync completed successfully."""
        return self.status == SYNC_STATUS_COMPLETED

    # ── Helper Methods ────────────────────────────────────────────────────

    def calculate_duration(self):
        """Calculate and store duration from started_at to completed_at."""
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            self.duration_ms = int(delta.total_seconds() * 1000)

    def mark_completed(self):
        """Mark the sync as completed and calculate summary metrics."""
        now = timezone.now()
        self.status = SYNC_STATUS_COMPLETED
        self.completed_at = now
        self.calculate_duration()
        # Derive totals from entities_synced if populated
        if self.entities_synced:
            total = 0
            successful = 0
            failed = 0
            for entity_data in self.entities_synced.values():
                if isinstance(entity_data, dict):
                    total += entity_data.get("total", 0)
                    successful += entity_data.get("successful", 0)
                    failed += entity_data.get("failed", 0)
            self.total_records_processed = total
            self.records_successful = successful
            self.records_failed = failed
        self.save()

    def mark_failed(self, error_message=""):
        """Mark the sync as failed and record the error."""
        self.status = SYNC_STATUS_FAILED
        self.completed_at = timezone.now()
        self.calculate_duration()
        if error_message:
            self.add_error("sync", "sync_operation", error_message)
        self.save()

    def add_error(self, entity_type, entity_id, error_message):
        """Append an error entry to the errors JSON field."""
        errors_list = self.errors.get("errors", []) if isinstance(self.errors, dict) else []
        errors_list.append({
            "entity_type": entity_type,
            "entity_id": str(entity_id),
            "error_message": error_message,
            "timestamp": timezone.now().isoformat(),
        })
        self.errors = {"errors": errors_list}
        self.records_failed += 1
        self.save()

    def add_warning(self, entity_type, entity_id, warning_message):
        """Append a warning entry to the warnings JSON field."""
        warnings_list = self.warnings if isinstance(self.warnings, list) else []
        warnings_list.append({
            "entity_type": entity_type,
            "entity_id": str(entity_id),
            "warning_message": warning_message,
            "timestamp": timezone.now().isoformat(),
        })
        self.warnings = warnings_list
        self.save()

    def calculate_metrics(self):
        """Return a dictionary of calculated performance metrics."""
        metrics = {
            "success_rate": self.success_rate,
            "error_rate": (
                (self.records_failed / self.total_records_processed) * 100
                if self.total_records_processed
                else 0.0
            ),
            "conflict_rate": (
                (self.conflicts_detected / self.total_records_processed) * 100
                if self.total_records_processed
                else 0.0
            ),
        }
        if self.duration_ms and self.total_records_processed:
            metrics["records_per_second"] = round(
                self.total_records_processed / (self.duration_ms / 1000), 2
            )
        if self.bytes_downloaded and self.total_records_processed:
            metrics["bytes_per_record"] = round(
                self.bytes_downloaded / self.total_records_processed, 2
            )
        return metrics
