"""
Vendors constants module.

Defines choices, status values, and other constants used across
the vendors application models.
"""

# ════════════════════════════════════════════════════════════════════════
# Vendor Status
# ════════════════════════════════════════════════════════════════════════

VENDOR_STATUS_ACTIVE = "active"
VENDOR_STATUS_INACTIVE = "inactive"
VENDOR_STATUS_BLOCKED = "blocked"
VENDOR_STATUS_PENDING_APPROVAL = "pending_approval"

VENDOR_STATUS_CHOICES = [
    (VENDOR_STATUS_ACTIVE, "Active"),
    (VENDOR_STATUS_INACTIVE, "Inactive"),
    (VENDOR_STATUS_BLOCKED, "Blocked"),
    (VENDOR_STATUS_PENDING_APPROVAL, "Pending Approval"),
]

DEFAULT_VENDOR_STATUS = VENDOR_STATUS_PENDING_APPROVAL

# ════════════════════════════════════════════════════════════════════════
# Vendor Type
# ════════════════════════════════════════════════════════════════════════

VENDOR_TYPE_MANUFACTURER = "manufacturer"
VENDOR_TYPE_DISTRIBUTOR = "distributor"
VENDOR_TYPE_WHOLESALER = "wholesaler"
VENDOR_TYPE_IMPORTER = "importer"
VENDOR_TYPE_SERVICE = "service"

VENDOR_TYPE_CHOICES = [
    (VENDOR_TYPE_MANUFACTURER, "Manufacturer"),
    (VENDOR_TYPE_DISTRIBUTOR, "Distributor"),
    (VENDOR_TYPE_WHOLESALER, "Wholesaler"),
    (VENDOR_TYPE_IMPORTER, "Importer"),
    (VENDOR_TYPE_SERVICE, "Service Provider"),
]

DEFAULT_VENDOR_TYPE = VENDOR_TYPE_MANUFACTURER

# ════════════════════════════════════════════════════════════════════════
# Payment Terms Choices
# ════════════════════════════════════════════════════════════════════════

PAYMENT_TERM_IMMEDIATE = "immediate"
PAYMENT_TERM_NET_15 = "net_15"
PAYMENT_TERM_NET_30 = "net_30"
PAYMENT_TERM_NET_60 = "net_60"
PAYMENT_TERM_COD = "cod"

PAYMENT_TERMS_CHOICES = [
    (PAYMENT_TERM_IMMEDIATE, "Immediate"),
    (PAYMENT_TERM_NET_15, "Net 15 Days"),
    (PAYMENT_TERM_NET_30, "Net 30 Days"),
    (PAYMENT_TERM_NET_60, "Net 60 Days"),
    (PAYMENT_TERM_COD, "Cash on Delivery"),
]

DEFAULT_PAYMENT_TERMS = PAYMENT_TERM_NET_30

# ════════════════════════════════════════════════════════════════════════
# Contact Role Choices
# ════════════════════════════════════════════════════════════════════════

CONTACT_ROLE_SALES = "sales"
CONTACT_ROLE_ACCOUNTS = "accounts"
CONTACT_ROLE_LOGISTICS = "logistics"
CONTACT_ROLE_MANAGER = "manager"
CONTACT_ROLE_SUPPORT = "support"
CONTACT_ROLE_OTHER = "other"

CONTACT_ROLE_CHOICES = [
    (CONTACT_ROLE_SALES, "Sales Representative"),
    (CONTACT_ROLE_ACCOUNTS, "Accounts Manager"),
    (CONTACT_ROLE_LOGISTICS, "Logistics Coordinator"),
    (CONTACT_ROLE_MANAGER, "Manager"),
    (CONTACT_ROLE_SUPPORT, "Technical Support"),
    (CONTACT_ROLE_OTHER, "Other"),
]

# ════════════════════════════════════════════════════════════════════════
# Address Type Choices
# ════════════════════════════════════════════════════════════════════════

ADDRESS_TYPE_MAIN = "main"
ADDRESS_TYPE_WAREHOUSE = "warehouse"
ADDRESS_TYPE_BILLING = "billing"
ADDRESS_TYPE_SHIPPING = "shipping"

ADDRESS_TYPE_CHOICES = [
    (ADDRESS_TYPE_MAIN, "Main Office"),
    (ADDRESS_TYPE_WAREHOUSE, "Warehouse"),
    (ADDRESS_TYPE_BILLING, "Billing Address"),
    (ADDRESS_TYPE_SHIPPING, "Shipping Address"),
]

# ════════════════════════════════════════════════════════════════════════
# Bank Verification Status
# ════════════════════════════════════════════════════════════════════════

BANK_VERIFICATION_PENDING = "pending"
BANK_VERIFICATION_VERIFIED = "verified"
BANK_VERIFICATION_FAILED = "failed"

BANK_VERIFICATION_CHOICES = [
    (BANK_VERIFICATION_PENDING, "Pending"),
    (BANK_VERIFICATION_VERIFIED, "Verified"),
    (BANK_VERIFICATION_FAILED, "Failed"),
]

# ════════════════════════════════════════════════════════════════════════
# Communication Type
# ════════════════════════════════════════════════════════════════════════

COMMUNICATION_TYPE_EMAIL = "email"
COMMUNICATION_TYPE_PHONE = "phone"
COMMUNICATION_TYPE_MEETING = "meeting"
COMMUNICATION_TYPE_SITE_VISIT = "site_visit"
COMMUNICATION_TYPE_OTHER = "other"

COMMUNICATION_TYPE_CHOICES = [
    (COMMUNICATION_TYPE_EMAIL, "Email"),
    (COMMUNICATION_TYPE_PHONE, "Phone Call"),
    (COMMUNICATION_TYPE_MEETING, "Meeting"),
    (COMMUNICATION_TYPE_SITE_VISIT, "Site Visit"),
    (COMMUNICATION_TYPE_OTHER, "Other"),
]

# ════════════════════════════════════════════════════════════════════════
# Document Type
# ════════════════════════════════════════════════════════════════════════

DOCUMENT_TYPE_CONTRACT = "contract"
DOCUMENT_TYPE_CERTIFICATE = "certificate"
DOCUMENT_TYPE_PRICE_LIST = "price_list"
DOCUMENT_TYPE_LICENSE = "license"
DOCUMENT_TYPE_OTHER = "other"

DOCUMENT_TYPE_CHOICES = [
    (DOCUMENT_TYPE_CONTRACT, "Contract"),
    (DOCUMENT_TYPE_CERTIFICATE, "Certificate"),
    (DOCUMENT_TYPE_PRICE_LIST, "Price List"),
    (DOCUMENT_TYPE_LICENSE, "License"),
    (DOCUMENT_TYPE_OTHER, "Other"),
]

# ════════════════════════════════════════════════════════════════════════
# History Change Type
# ════════════════════════════════════════════════════════════════════════

CHANGE_TYPE_CREATE = "create"
CHANGE_TYPE_UPDATE = "update"
CHANGE_TYPE_DELETE = "delete"

CHANGE_TYPE_CHOICES = [
    (CHANGE_TYPE_CREATE, "Created"),
    (CHANGE_TYPE_UPDATE, "Updated"),
    (CHANGE_TYPE_DELETE, "Deleted"),
]
