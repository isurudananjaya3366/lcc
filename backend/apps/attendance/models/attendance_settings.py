import logging

from django.db import models

from apps.attendance.constants import (
    DEFAULT_EARLY_LEAVE_GRACE_MINUTES,
    DEFAULT_GEOFENCE_RADIUS_METERS,
    DEFAULT_LATE_GRACE_MINUTES,
    DEFAULT_MAX_OT_HOURS_PER_DAY,
    DEFAULT_OVERTIME_MULTIPLIER,
)
from apps.core.mixins import TimestampMixin, UUIDMixin

logger = logging.getLogger(__name__)


class AttendanceSettings(UUIDMixin, TimestampMixin, models.Model):
    """Tenant-level attendance configuration."""

    tenant = models.OneToOneField(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="attendance_settings",
    )

    # ── Grace Period Settings ────────────────────────────────
    default_late_grace_minutes = models.PositiveIntegerField(
        default=DEFAULT_LATE_GRACE_MINUTES,
        help_text="Default minutes of grace for late arrival.",
    )
    default_early_leave_grace_minutes = models.PositiveIntegerField(
        default=DEFAULT_EARLY_LEAVE_GRACE_MINUTES,
        help_text="Default minutes of grace for early departure.",
    )

    # ── Overtime Settings ────────────────────────────────────
    require_overtime_approval = models.BooleanField(
        default=True,
        help_text="Whether overtime requires prior approval.",
    )
    overtime_multiplier_normal = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=DEFAULT_OVERTIME_MULTIPLIER,
        help_text="Standard overtime multiplier (e.g. 1.5x).",
    )
    max_overtime_hours_per_day = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=DEFAULT_MAX_OT_HOURS_PER_DAY,
    )
    max_overtime_hours_per_month = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=60,
    )
    auto_approve_overtime_minutes = models.PositiveIntegerField(
        default=0,
        help_text="Auto-approve overtime under this many minutes (0 = disabled).",
    )
    weekend_overtime_multiplier = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=2.0,
    )
    holiday_overtime_multiplier = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=2.5,
    )

    # ── Geofencing Settings ──────────────────────────────────
    enable_geofencing = models.BooleanField(
        default=False,
        help_text="Whether GPS geofencing is enabled for check-in.",
    )
    strict_geofencing = models.BooleanField(
        default=False,
        help_text="Block check-in outside geofence (True) or just flag it (False).",
    )
    geofence_radius_meters = models.PositiveIntegerField(
        default=DEFAULT_GEOFENCE_RADIUS_METERS,
    )
    office_locations = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON list of office locations with lat/lng/radius.",
    )

    # ── Auto-Close Settings ──────────────────────────────────
    auto_clock_out_enabled = models.BooleanField(
        default=True,
        help_text="Whether auto clock-out is enabled.",
    )
    auto_clock_out_time = models.TimeField(
        null=True,
        blank=True,
        help_text="Auto clock-out time for forgotten punch-outs (e.g., 23:00).",
    )
    auto_absence_marking_enabled = models.BooleanField(
        default=True,
        help_text="Whether automatic absence marking is enabled.",
    )
    mark_absent_after_hours = models.PositiveIntegerField(
        default=4,
        help_text="Hours after shift start to mark absent if no clock-in.",
    )

    class Meta:
        verbose_name = "Attendance Settings"
        verbose_name_plural = "Attendance Settings"

    def __str__(self):
        return f"Attendance Settings (Tenant: {self.tenant_id})"

    @classmethod
    def get_for_tenant(cls, tenant):
        """Get or create settings for the given tenant."""
        tenant_pk = tenant.pk if hasattr(tenant, "pk") else tenant
        settings, _ = cls.objects.get_or_create(tenant_id=tenant_pk)
        return settings

    def get_overtime_multiplier(self, is_weekend=False, is_holiday=False):
        """Return the applicable overtime multiplier based on day type."""
        if is_holiday:
            return self.holiday_overtime_multiplier
        if is_weekend:
            return self.weekend_overtime_multiplier
        return self.overtime_multiplier_normal
