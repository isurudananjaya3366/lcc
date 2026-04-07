"""
HR constants module.

Defines choices, status values, and other constants used across
the HR application models (employees, departments, attendance).
"""

# ════════════════════════════════════════════════════════════════════════
# Employee Role Choices
# ════════════════════════════════════════════════════════════════════════

EMPLOYEE_ROLE_ADMIN = "admin"
EMPLOYEE_ROLE_MANAGER = "manager"
EMPLOYEE_ROLE_CASHIER = "cashier"
EMPLOYEE_ROLE_WAREHOUSE = "warehouse"
EMPLOYEE_ROLE_ACCOUNTANT = "accountant"

EMPLOYEE_ROLE_CHOICES = [
    (EMPLOYEE_ROLE_ADMIN, "Admin"),
    (EMPLOYEE_ROLE_MANAGER, "Manager"),
    (EMPLOYEE_ROLE_CASHIER, "Cashier"),
    (EMPLOYEE_ROLE_WAREHOUSE, "Warehouse"),
    (EMPLOYEE_ROLE_ACCOUNTANT, "Accountant"),
]

# Default employee role
DEFAULT_EMPLOYEE_ROLE = EMPLOYEE_ROLE_CASHIER


# ════════════════════════════════════════════════════════════════════════
# Employee Status Choices
# ════════════════════════════════════════════════════════════════════════

EMPLOYEE_STATUS_ACTIVE = "active"
EMPLOYEE_STATUS_INACTIVE = "inactive"
EMPLOYEE_STATUS_SUSPENDED = "suspended"

EMPLOYEE_STATUS_CHOICES = [
    (EMPLOYEE_STATUS_ACTIVE, "Active"),
    (EMPLOYEE_STATUS_INACTIVE, "Inactive"),
    (EMPLOYEE_STATUS_SUSPENDED, "Suspended"),
]

# Default employee status
DEFAULT_EMPLOYEE_STATUS = EMPLOYEE_STATUS_ACTIVE
