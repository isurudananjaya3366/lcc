"""
TenantAuditLog model for the accounting application.

Defines the TenantAuditLog model which tracks significant
activities within a tenant schema. Each log entry records
the action performed, the actor who performed it, the
timestamp, and additional details as JSON.
"""

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.mixins import UUIDMixin


class TenantAuditLog(UUIDMixin, models.Model):
    """
    Tenant-level audit log entry.

    Records significant actions performed within the tenant
    for compliance, debugging, and activity tracking. Each
    entry captures what happened, who did it, when, and any
    relevant context as structured JSON data.

    Fields:
        action: Short description of the action performed.
        actor: FK to the user who performed the action.
        actor_name: Cached display name of the actor (for when
            the user account is deleted).
        timestamp: When the action occurred.
        model_name: The model/entity type affected (optional).
        object_id: The ID of the affected object (optional).
        details: Additional context as JSON (IP address,
            old/new values, request metadata, etc.).
        ip_address: IP address of the request (optional).
    """

    # ── Action ──────────────────────────────────────────────────────
    action = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name="Action",
        help_text=(
            "Short description of the action performed "
            "(e.g. 'created_order', 'updated_product', 'login')."
        ),
    )

    # ── Actor ───────────────────────────────────────────────────────
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tenant_audit_logs",
        verbose_name="Actor",
        help_text="The user who performed this action.",
    )
    actor_name = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Actor Name",
        help_text=(
            "Cached display name of the actor. Preserved even "
            "if the user account is later deleted."
        ),
    )

    # ── Timestamp ───────────────────────────────────────────────────
    timestamp = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Timestamp",
        help_text="When the action occurred.",
    )

    # ── Target Entity ───────────────────────────────────────────────
    model_name = models.CharField(
        max_length=100,
        blank=True,
        default="",
        db_index=True,
        verbose_name="Model Name",
        help_text="The model/entity type affected (e.g. 'Order', 'Product').",
    )
    object_id = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Object ID",
        help_text="The ID of the affected object.",
    )

    # ── Details (JSON) ──────────────────────────────────────────────
    details = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Details",
        help_text=(
            "Additional context as JSON: IP address, old/new values, "
            "request metadata, etc."
        ),
    )

    # ── IP Address ──────────────────────────────────────────────────
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP Address",
        help_text="IP address of the request, if available.",
    )

    class Meta:
        db_table = "accounting_tenantauditlog"
        verbose_name = "Tenant Audit Log"
        verbose_name_plural = "Tenant Audit Logs"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(
                fields=["-timestamp"],
                name="idx_audit_timestamp_desc",
            ),
            models.Index(
                fields=["action", "timestamp"],
                name="idx_audit_action_time",
            ),
            models.Index(
                fields=["actor", "timestamp"],
                name="idx_audit_actor_time",
            ),
            models.Index(
                fields=["model_name", "object_id"],
                name="idx_audit_model_object",
            ),
        ]

    def __str__(self):
        actor_display = self.actor_name or "System"
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {actor_display}: {self.action}"

    @property
    def has_actor(self):
        """Return True if the action has an identified actor."""
        return self.actor_id is not None or bool(self.actor_name)

    @property
    def target(self):
        """Return the target entity string (model_name:object_id)."""
        if self.model_name and self.object_id:
            return f"{self.model_name}:{self.object_id}"
        return self.model_name or ""
