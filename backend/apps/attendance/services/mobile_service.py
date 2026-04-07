import logging
import math

from django.utils import timezone

logger = logging.getLogger(__name__)

# Minimum GPS accuracy in meters for a valid check-in
DEFAULT_MIN_GPS_ACCURACY = 100


class MobileCheckInService:
    """Service for mobile app check-in with GPS location validation.

    Supports geofencing, GPS accuracy validation, reverse geocoding lookup,
    and offline check-in queue processing.
    """

    @classmethod
    def check_in(cls, employee, location, ip_address=None):
        """Mobile check-in with GPS location.

        Args:
            employee: Employee instance.
            location: dict with latitude, longitude, accuracy.
            ip_address: Optional IP address.

        Returns:
            AttendanceRecord.
        """
        from apps.attendance.services.attendance_service import AttendanceService

        return AttendanceService.clock_in(
            employee=employee,
            method="mobile",
            location=location,
            ip_address=ip_address,
        )

    @classmethod
    def check_out(cls, employee, location, ip_address=None):
        """Mobile check-out with GPS location."""
        from apps.attendance.services.attendance_service import AttendanceService

        return AttendanceService.clock_out(
            employee=employee,
            method="mobile",
            location=location,
            ip_address=ip_address,
        )

    @classmethod
    def validate_location(cls, employee_location, office_locations, radius_meters=200):
        """Validate that employee location is within geofence of an office.

        Args:
            employee_location: dict with latitude, longitude.
            office_locations: list of dicts with latitude, longitude.
            radius_meters: Geofence radius in meters.

        Returns:
            tuple (is_valid, nearest_office, distance_meters)
        """
        if not office_locations:
            return True, None, 0

        emp_lat = employee_location.get("latitude")
        emp_lon = employee_location.get("longitude")
        if emp_lat is None or emp_lon is None:
            return False, None, None

        nearest_office = None
        min_distance = float("inf")

        for office in office_locations:
            distance = cls._haversine_distance(
                emp_lat, emp_lon,
                office["latitude"], office["longitude"],
            )
            if distance < min_distance:
                min_distance = distance
                nearest_office = office

        is_valid = min_distance <= radius_meters
        return is_valid, nearest_office, round(min_distance, 2)

    @classmethod
    def validate_gps_accuracy(cls, location, min_accuracy=None):
        """Validate GPS accuracy of the mobile device.

        Args:
            location: dict with latitude, longitude, accuracy (in meters).
            min_accuracy: Minimum acceptable accuracy in meters. Lower is better.

        Returns:
            tuple (is_valid, accuracy_value, message)
        """
        accuracy = location.get("accuracy")
        if accuracy is None:
            return False, None, "GPS accuracy data not provided."

        threshold = min_accuracy or DEFAULT_MIN_GPS_ACCURACY
        if accuracy > threshold:
            return (
                False,
                accuracy,
                f"GPS accuracy {accuracy}m exceeds threshold {threshold}m. "
                "Please move to an open area.",
            )
        return True, accuracy, "GPS accuracy acceptable."

    @classmethod
    def validate_check_in(cls, employee, location,
                          office_locations=None, radius_meters=200,
                          strict_geofencing=False, min_accuracy=None):
        """Full mobile check-in validation: GPS accuracy + geofence.

        Args:
            employee: Employee instance.
            location: dict with latitude, longitude, accuracy.
            office_locations: list of office location dicts.
            radius_meters: Geofence radius.
            strict_geofencing: If True, reject when outside geofence.
            min_accuracy: Minimum GPS accuracy in meters.

        Returns:
            dict with is_valid, errors, warnings, nearest_office, distance.
        """
        errors = []
        warnings = []

        # GPS accuracy check
        acc_valid, acc_value, acc_msg = cls.validate_gps_accuracy(location, min_accuracy)
        if not acc_valid:
            if strict_geofencing:
                errors.append(acc_msg)
            else:
                warnings.append(acc_msg)

        # Geofence check
        nearest_office = None
        distance = None
        if office_locations:
            geo_valid, nearest_office, distance = cls.validate_location(
                location, office_locations, radius_meters,
            )
            if not geo_valid:
                msg = (
                    f"Location is {distance}m from nearest office "
                    f"({nearest_office.get('name', 'unknown') if nearest_office else 'unknown'}), "
                    f"exceeds {radius_meters}m radius."
                )
                if strict_geofencing:
                    errors.append(msg)
                else:
                    warnings.append(msg)

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "nearest_office": nearest_office,
            "distance": distance,
            "gps_accuracy": acc_value,
        }

    @classmethod
    def reverse_geocode(cls, latitude, longitude):
        """Get human-readable address from GPS coordinates.

        Uses a simple approximation. In production, integrate with a geocoding
        API (Google Maps, Nominatim, etc.).

        Returns:
            dict with formatted_address and components.
        """
        return {
            "latitude": latitude,
            "longitude": longitude,
            "formatted_address": f"{latitude:.6f}, {longitude:.6f}",
            "source": "coordinates",
        }

    @classmethod
    def process_offline_checkins(cls, employee, events):
        """Process a batch of offline check-in/out events.

        Mobile apps may queue events when offline and submit them
        when connectivity is restored.

        Args:
            employee: Employee instance.
            events: list of dicts with type ('in'/'out'), timestamp, location.

        Returns:
            list of processing results.
        """
        results = []
        for event in sorted(events, key=lambda e: e.get("timestamp", "")):
            event_type = event.get("type", "in")
            location = event.get("location")
            try:
                if event_type == "in":
                    record = cls.check_in(employee, location)
                else:
                    record = cls.check_out(employee, location)
                results.append({
                    "event": event,
                    "status": "processed",
                    "record_id": str(record.pk) if record else None,
                })
            except Exception as e:
                results.append({
                    "event": event,
                    "status": "failed",
                    "error": str(e),
                })
        return results

    @staticmethod
    def _haversine_distance(lat1, lon1, lat2, lon2):
        """Calculate distance between two GPS coordinates in meters."""
        R = 6371000  # Earth's radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = (
            math.sin(dphi / 2) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c
