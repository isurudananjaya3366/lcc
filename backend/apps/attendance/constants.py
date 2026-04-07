# ──────────────────────────────────────────────────────────────
# Shift Type Choices
# ──────────────────────────────────────────────────────────────
SHIFT_TYPE_REGULAR = "regular"
SHIFT_TYPE_MORNING = "morning"
SHIFT_TYPE_EVENING = "evening"
SHIFT_TYPE_NIGHT = "night"
SHIFT_TYPE_FLEXIBLE = "flexible"

SHIFT_TYPE_CHOICES = [
    (SHIFT_TYPE_REGULAR, "Regular"),
    (SHIFT_TYPE_MORNING, "Morning"),
    (SHIFT_TYPE_EVENING, "Evening"),
    (SHIFT_TYPE_NIGHT, "Night"),
    (SHIFT_TYPE_FLEXIBLE, "Flexible"),
]

DEFAULT_SHIFT_TYPE = SHIFT_TYPE_REGULAR

# ──────────────────────────────────────────────────────────────
# Shift Status Choices
# ──────────────────────────────────────────────────────────────
SHIFT_STATUS_ACTIVE = "active"
SHIFT_STATUS_INACTIVE = "inactive"
SHIFT_STATUS_ARCHIVED = "archived"

SHIFT_STATUS_CHOICES = [
    (SHIFT_STATUS_ACTIVE, "Active"),
    (SHIFT_STATUS_INACTIVE, "Inactive"),
    (SHIFT_STATUS_ARCHIVED, "Archived"),
]

DEFAULT_SHIFT_STATUS = SHIFT_STATUS_ACTIVE

# ──────────────────────────────────────────────────────────────
# Attendance Status Choices
# ──────────────────────────────────────────────────────────────
ATTENDANCE_STATUS_PRESENT = "present"
ATTENDANCE_STATUS_ABSENT = "absent"
ATTENDANCE_STATUS_LATE = "late"
ATTENDANCE_STATUS_HALF_DAY = "half_day"
ATTENDANCE_STATUS_ON_LEAVE = "on_leave"
ATTENDANCE_STATUS_HOLIDAY = "holiday"
ATTENDANCE_STATUS_WEEKEND = "weekend"

ATTENDANCE_STATUS_CHOICES = [
    (ATTENDANCE_STATUS_PRESENT, "Present"),
    (ATTENDANCE_STATUS_ABSENT, "Absent"),
    (ATTENDANCE_STATUS_LATE, "Late"),
    (ATTENDANCE_STATUS_HALF_DAY, "Half Day"),
    (ATTENDANCE_STATUS_ON_LEAVE, "On Leave"),
    (ATTENDANCE_STATUS_HOLIDAY, "Holiday"),
    (ATTENDANCE_STATUS_WEEKEND, "Weekend"),
]

DEFAULT_ATTENDANCE_STATUS = ATTENDANCE_STATUS_PRESENT

# ──────────────────────────────────────────────────────────────
# Check-In Method Choices
# ──────────────────────────────────────────────────────────────
CHECKIN_METHOD_WEB = "web"
CHECKIN_METHOD_MOBILE = "mobile"
CHECKIN_METHOD_BIOMETRIC = "biometric"
CHECKIN_METHOD_MANUAL = "manual"
CHECKIN_METHOD_IMPORT = "import"

CHECKIN_METHOD_CHOICES = [
    (CHECKIN_METHOD_WEB, "Web"),
    (CHECKIN_METHOD_MOBILE, "Mobile"),
    (CHECKIN_METHOD_BIOMETRIC, "Biometric"),
    (CHECKIN_METHOD_MANUAL, "Manual"),
    (CHECKIN_METHOD_IMPORT, "Import"),
]

DEFAULT_CHECKIN_METHOD = CHECKIN_METHOD_WEB

# ──────────────────────────────────────────────────────────────
# Regularization Status Choices
# ──────────────────────────────────────────────────────────────
REGULARIZATION_STATUS_PENDING = "pending"
REGULARIZATION_STATUS_APPROVED = "approved"
REGULARIZATION_STATUS_REJECTED = "rejected"

REGULARIZATION_STATUS_CHOICES = [
    (REGULARIZATION_STATUS_PENDING, "Pending"),
    (REGULARIZATION_STATUS_APPROVED, "Approved"),
    (REGULARIZATION_STATUS_REJECTED, "Rejected"),
]

DEFAULT_REGULARIZATION_STATUS = REGULARIZATION_STATUS_PENDING

# ──────────────────────────────────────────────────────────────
# Overtime Request Status Choices
# ──────────────────────────────────────────────────────────────
OVERTIME_STATUS_PENDING = "pending"
OVERTIME_STATUS_APPROVED = "approved"
OVERTIME_STATUS_REJECTED = "rejected"

OVERTIME_STATUS_CHOICES = [
    (OVERTIME_STATUS_PENDING, "Pending"),
    (OVERTIME_STATUS_APPROVED, "Approved"),
    (OVERTIME_STATUS_REJECTED, "Rejected"),
]

DEFAULT_OVERTIME_STATUS = OVERTIME_STATUS_PENDING

# ──────────────────────────────────────────────────────────────
# Default Configuration Values
# ──────────────────────────────────────────────────────────────
DEFAULT_LATE_GRACE_MINUTES = 15
DEFAULT_EARLY_LEAVE_GRACE_MINUTES = 10
DEFAULT_OVERTIME_MULTIPLIER = 1.5
DEFAULT_MIN_HOURS_HALF_DAY = 4.0
DEFAULT_MIN_HOURS_FULL_DAY = 7.5
DEFAULT_OVERTIME_START_AFTER = 8.5
DEFAULT_MAX_OT_HOURS_PER_DAY = 4.0
DEFAULT_GEOFENCE_RADIUS_METERS = 200

# ──────────────────────────────────────────────────────────────
# Shift Code Prefix
# ──────────────────────────────────────────────────────────────
SHIFT_CODE_PREFIX = "SHF"
SHIFT_CODE_PADDING = 4  # SHF-0001
