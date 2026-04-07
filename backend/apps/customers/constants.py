"""
Customers constants module.

Defines choices, status values, and other constants used across
the customers application models.
"""

from django.db import models

# ════════════════════════════════════════════════════════════════════════
# Customer Type Choices
# ════════════════════════════════════════════════════════════════════════

CUSTOMER_TYPE_INDIVIDUAL = "individual"
CUSTOMER_TYPE_BUSINESS = "business"
CUSTOMER_TYPE_WHOLESALE = "wholesale"
CUSTOMER_TYPE_VIP = "vip"
CUSTOMER_TYPE_GOVERNMENT = "government"
CUSTOMER_TYPE_NONPROFIT = "nonprofit"

CUSTOMER_TYPE_CHOICES = [
    (CUSTOMER_TYPE_INDIVIDUAL, "Individual"),
    (CUSTOMER_TYPE_BUSINESS, "Business"),
    (CUSTOMER_TYPE_WHOLESALE, "Wholesale Buyer"),
    (CUSTOMER_TYPE_VIP, "VIP Customer"),
    (CUSTOMER_TYPE_GOVERNMENT, "Government"),
    (CUSTOMER_TYPE_NONPROFIT, "Non-Profit"),
]

# Default customer type for new customers
DEFAULT_CUSTOMER_TYPE = CUSTOMER_TYPE_INDIVIDUAL

# Default credit limit (in LKR)
DEFAULT_CREDIT_LIMIT = 0


# ════════════════════════════════════════════════════════════════════════
# Customer Status Choices
# ════════════════════════════════════════════════════════════════════════

CUSTOMER_STATUS_ACTIVE = "active"
CUSTOMER_STATUS_INACTIVE = "inactive"
CUSTOMER_STATUS_BLOCKED = "blocked"
CUSTOMER_STATUS_ARCHIVED = "archived"

CUSTOMER_STATUS_CHOICES = [
    (CUSTOMER_STATUS_ACTIVE, "Active"),
    (CUSTOMER_STATUS_INACTIVE, "Inactive"),
    (CUSTOMER_STATUS_BLOCKED, "Blocked"),
    (CUSTOMER_STATUS_ARCHIVED, "Archived"),
]

DEFAULT_CUSTOMER_STATUS = CUSTOMER_STATUS_ACTIVE


# ════════════════════════════════════════════════════════════════════════
# Customer Source Choices
# ════════════════════════════════════════════════════════════════════════

CUSTOMER_SOURCE_MANUAL = "manual"
CUSTOMER_SOURCE_POS = "pos"
CUSTOMER_SOURCE_WEBSTORE = "webstore"
CUSTOMER_SOURCE_IMPORT = "import"

CUSTOMER_SOURCE_CHOICES = [
    (CUSTOMER_SOURCE_MANUAL, "Manual Entry"),
    (CUSTOMER_SOURCE_POS, "POS"),
    (CUSTOMER_SOURCE_WEBSTORE, "Webstore"),
    (CUSTOMER_SOURCE_IMPORT, "Import"),
]

DEFAULT_CUSTOMER_SOURCE = CUSTOMER_SOURCE_MANUAL


# ════════════════════════════════════════════════════════════════════════
# Customer Code Configuration
# ════════════════════════════════════════════════════════════════════════

CUSTOMER_CODE_PREFIX = "CUST"
CUSTOMER_CODE_SEPARATOR = "-"
CUSTOMER_CODE_SEQUENCE_LENGTH = 5

# ════════════════════════════════════════════════════════════════════════
# Profile Image Configuration
# ════════════════════════════════════════════════════════════════════════

PROFILE_IMAGE_MAX_SIZE_MB = 2
PROFILE_IMAGE_MIN_DIMENSION = 100
PROFILE_IMAGE_MAX_DIMENSION = 1000


# ════════════════════════════════════════════════════════════════════════
# Address Type Choices
# ════════════════════════════════════════════════════════════════════════

ADDRESS_TYPE_BILLING = "billing"
ADDRESS_TYPE_SHIPPING = "shipping"
ADDRESS_TYPE_HOME = "home"
ADDRESS_TYPE_WORK = "work"
ADDRESS_TYPE_OTHER = "other"

ADDRESS_TYPE_CHOICES = [
    (ADDRESS_TYPE_BILLING, "Billing Address"),
    (ADDRESS_TYPE_SHIPPING, "Shipping Address"),
    (ADDRESS_TYPE_HOME, "Home Address"),
    (ADDRESS_TYPE_WORK, "Work Address"),
    (ADDRESS_TYPE_OTHER, "Other"),
]


# ════════════════════════════════════════════════════════════════════════
# Phone Type Choices
# ════════════════════════════════════════════════════════════════════════

PHONE_TYPE_MOBILE = "mobile"
PHONE_TYPE_LANDLINE = "landline"
PHONE_TYPE_WHATSAPP = "whatsapp"
PHONE_TYPE_WORK = "work"
PHONE_TYPE_OTHER = "other"

PHONE_TYPE_CHOICES = [
    (PHONE_TYPE_MOBILE, "Mobile"),
    (PHONE_TYPE_LANDLINE, "Landline"),
    (PHONE_TYPE_WHATSAPP, "WhatsApp"),
    (PHONE_TYPE_WORK, "Work"),
    (PHONE_TYPE_OTHER, "Other"),
]


# ════════════════════════════════════════════════════════════════════════
# Communication Type Choices
# ════════════════════════════════════════════════════════════════════════

COMMUNICATION_TYPE_EMAIL = "email"
COMMUNICATION_TYPE_PHONE_CALL = "phone_call"
COMMUNICATION_TYPE_SMS = "sms"
COMMUNICATION_TYPE_VISIT = "visit"
COMMUNICATION_TYPE_NOTE = "note"
COMMUNICATION_TYPE_OTHER = "other"

COMMUNICATION_TYPE_CHOICES = [
    (COMMUNICATION_TYPE_EMAIL, "Email"),
    (COMMUNICATION_TYPE_PHONE_CALL, "Phone Call"),
    (COMMUNICATION_TYPE_SMS, "SMS"),
    (COMMUNICATION_TYPE_VISIT, "Visit"),
    (COMMUNICATION_TYPE_NOTE, "Note"),
    (COMMUNICATION_TYPE_OTHER, "Other"),
]
