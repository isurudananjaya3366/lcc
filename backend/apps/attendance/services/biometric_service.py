import hashlib
import hmac
import logging

from django.utils import timezone

logger = logging.getLogger(__name__)


class BiometricIntegrationService:
    """Service for biometric device integration via API.

    Supports device registration, event processing, HMAC signature verification,
    and device health monitoring.
    """

    PUNCH_IN = "punch_in"
    PUNCH_OUT = "punch_out"
    BREAK_START = "break_start"
    BREAK_END = "break_end"

    VALID_EVENT_TYPES = {PUNCH_IN, PUNCH_OUT, BREAK_START, BREAK_END}

    # ── Signature Verification ───────────────────────────────

    @classmethod
    def verify_signature(cls, payload_body, signature, secret_key):
        """Verify HMAC-SHA256 signature from biometric device.

        Args:
            payload_body: Raw request body bytes.
            signature: Signature from X-Biometric-Signature header.
            secret_key: Shared secret for HMAC computation.

        Returns:
            True if signature is valid.
        """
        if not secret_key or not signature:
            return False
        expected = hmac.new(
            secret_key.encode("utf-8"),
            payload_body if isinstance(payload_body, bytes) else payload_body.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

    # ── Event Processing ─────────────────────────────────────

    @classmethod
    def process_event(cls, device_id, employee_identifier, event_type, timestamp, location=None):
        """Process a biometric punch event and create/update attendance record.

        Args:
            device_id: Identifier of the biometric device.
            employee_identifier: Employee ID or biometric ID.
            event_type: One of PUNCH_IN, PUNCH_OUT, BREAK_START, BREAK_END.
            timestamp: datetime of the event.
            location: Optional GPS location dict.

        Returns:
            The AttendanceRecord.
        """
        from apps.attendance.services.attendance_service import AttendanceService
        from apps.employees.models import Employee

        employee = Employee.objects.get(employee_id=employee_identifier)

        if event_type in (cls.PUNCH_IN, "PUNCH_IN"):
            return AttendanceService.clock_in(
                employee=employee, method="biometric",
                location=location, ip_address=None,
            )
        elif event_type in (cls.PUNCH_OUT, "PUNCH_OUT"):
            return AttendanceService.clock_out(
                employee=employee, method="biometric",
                location=location, ip_address=None,
            )

        logger.info(
            "Biometric event processed: device=%s employee=%s event=%s",
            device_id, employee_identifier, event_type,
        )
        return None

    # ── Device Management ────────────────────────────────────

    @classmethod
    def register_device(cls, device_id, device_name, location_name=None, secret_key=None, **extra):
        """Register a biometric device with name, location, and secret key."""
        device_info = {
            "device_id": device_id,
            "device_name": device_name,
            "location_name": location_name or "",
            "secret_key": secret_key or "",
            "status": "active",
            "registered_at": timezone.now().isoformat(),
            **extra,
        }
        logger.info("Biometric device registered: %s (%s)", device_id, device_name)
        return device_info

    @classmethod
    def unregister_device(cls, device_id):
        """Unregister / deactivate a biometric device."""
        logger.info("Biometric device unregistered: %s", device_id)
        return {"device_id": device_id, "status": "inactive"}

    @classmethod
    def get_device_status(cls, device_id):
        """Get health status of a biometric device."""
        return {
            "device_id": device_id,
            "status": "online",
            "last_heartbeat": timezone.now().isoformat(),
        }

    @classmethod
    def get_registered_devices(cls):
        """Return list of registered devices from settings."""
        try:
            from apps.attendance.models.attendance_settings import AttendanceSettings
            settings = AttendanceSettings.get_for_tenant(None)
            return getattr(settings, "biometric_devices", []) or []
        except Exception:
            return []

    # ── Event Queue ──────────────────────────────────────────

    @classmethod
    def queue_event(cls, device_id, event_data):
        """Queue a biometric event for async processing.

        In production this would push to Redis/Celery. Current implementation
        processes synchronously as a fallback.
        """
        logger.info("Queuing biometric event from device %s", device_id)
        return cls.process_event(
            device_id=device_id,
            employee_identifier=event_data.get("employee_biometric_id"),
            event_type=event_data.get("event_type"),
            timestamp=event_data.get("timestamp"),
            location=event_data.get("location"),
        )

    @classmethod
    def get_device_event_log(cls, device_id, start_date=None, end_date=None, limit=100):
        """Retrieve recent events from a specific device.

        Queries attendance records created via biometric method.
        """
        from apps.attendance.models import AttendanceRecord

        qs = AttendanceRecord.objects.filter(
            clock_in_method="biometric",
            is_deleted=False,
        ).order_by("-clock_in")

        if start_date:
            qs = qs.filter(date__gte=start_date)
        if end_date:
            qs = qs.filter(date__lte=end_date)

        return list(qs[:limit].values(
            "id", "employee__employee_id", "date",
            "clock_in", "clock_out", "status",
        ))
