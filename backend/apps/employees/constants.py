"""Constants for the Employees application."""

# ════════════════════════════════════════════════════════════════════════
# Employment Type Choices
# ════════════════════════════════════════════════════════════════════════

EMPLOYMENT_TYPE_FULL_TIME = "full_time"
EMPLOYMENT_TYPE_PART_TIME = "part_time"
EMPLOYMENT_TYPE_CONTRACT = "contract"
EMPLOYMENT_TYPE_INTERN = "intern"
EMPLOYMENT_TYPE_PROBATION = "probation"
EMPLOYMENT_TYPE_TEMPORARY = "temporary"
EMPLOYMENT_TYPE_CONSULTANT = "consultant"

EMPLOYMENT_TYPE_CHOICES = [
    (EMPLOYMENT_TYPE_FULL_TIME, "Full Time"),
    (EMPLOYMENT_TYPE_PART_TIME, "Part Time"),
    (EMPLOYMENT_TYPE_CONTRACT, "Contract"),
    (EMPLOYMENT_TYPE_INTERN, "Intern"),
    (EMPLOYMENT_TYPE_PROBATION, "Probation"),
    (EMPLOYMENT_TYPE_TEMPORARY, "Temporary"),
    (EMPLOYMENT_TYPE_CONSULTANT, "Consultant"),
]

DEFAULT_EMPLOYMENT_TYPE = EMPLOYMENT_TYPE_FULL_TIME

# ════════════════════════════════════════════════════════════════════════
# Employee Status Choices
# ════════════════════════════════════════════════════════════════════════

EMPLOYEE_STATUS_ACTIVE = "active"
EMPLOYEE_STATUS_INACTIVE = "inactive"
EMPLOYEE_STATUS_ON_LEAVE = "on_leave"
EMPLOYEE_STATUS_TERMINATED = "terminated"
EMPLOYEE_STATUS_RESIGNED = "resigned"

EMPLOYEE_STATUS_CHOICES = [
    (EMPLOYEE_STATUS_ACTIVE, "Active"),
    (EMPLOYEE_STATUS_INACTIVE, "Inactive"),
    (EMPLOYEE_STATUS_ON_LEAVE, "On Leave"),
    (EMPLOYEE_STATUS_TERMINATED, "Terminated"),
    (EMPLOYEE_STATUS_RESIGNED, "Resigned"),
]

DEFAULT_EMPLOYEE_STATUS = EMPLOYEE_STATUS_ACTIVE

# ════════════════════════════════════════════════════════════════════════
# Gender Choices
# ════════════════════════════════════════════════════════════════════════

GENDER_MALE = "male"
GENDER_FEMALE = "female"
GENDER_OTHER = "other"
GENDER_PREFER_NOT_TO_SAY = "prefer_not_to_say"

GENDER_CHOICES = [
    (GENDER_MALE, "Male"),
    (GENDER_FEMALE, "Female"),
    (GENDER_OTHER, "Other"),
    (GENDER_PREFER_NOT_TO_SAY, "Prefer Not to Say"),
]

# ════════════════════════════════════════════════════════════════════════
# Marital Status Choices
# ════════════════════════════════════════════════════════════════════════

MARITAL_STATUS_SINGLE = "single"
MARITAL_STATUS_MARRIED = "married"
MARITAL_STATUS_DIVORCED = "divorced"
MARITAL_STATUS_WIDOWED = "widowed"

MARITAL_STATUS_CHOICES = [
    (MARITAL_STATUS_SINGLE, "Single"),
    (MARITAL_STATUS_MARRIED, "Married"),
    (MARITAL_STATUS_DIVORCED, "Divorced"),
    (MARITAL_STATUS_WIDOWED, "Widowed"),
]

# ════════════════════════════════════════════════════════════════════════
# Address Type Choices
# ════════════════════════════════════════════════════════════════════════

ADDRESS_TYPE_PERMANENT = "permanent"
ADDRESS_TYPE_TEMPORARY = "temporary"
ADDRESS_TYPE_WORK = "work"

ADDRESS_TYPE_CHOICES = [
    (ADDRESS_TYPE_PERMANENT, "Permanent"),
    (ADDRESS_TYPE_TEMPORARY, "Temporary"),
    (ADDRESS_TYPE_WORK, "Work"),
]

# ════════════════════════════════════════════════════════════════════════
# Document Type Choices
# ════════════════════════════════════════════════════════════════════════

DOCUMENT_TYPE_CONTRACT = "contract"
DOCUMENT_TYPE_RESUME = "resume"
DOCUMENT_TYPE_NIC_COPY = "nic_copy"
DOCUMENT_TYPE_CERTIFICATE = "certificate"
DOCUMENT_TYPE_OTHER = "other"

DOCUMENT_TYPE_CHOICES = [
    (DOCUMENT_TYPE_CONTRACT, "Contract"),
    (DOCUMENT_TYPE_RESUME, "Resume"),
    (DOCUMENT_TYPE_NIC_COPY, "NIC Copy"),
    (DOCUMENT_TYPE_CERTIFICATE, "Certificate"),
    (DOCUMENT_TYPE_OTHER, "Other"),
]

# ════════════════════════════════════════════════════════════════════════
# Bank Account Type Choices
# ════════════════════════════════════════════════════════════════════════

ACCOUNT_TYPE_SAVINGS = "savings"
ACCOUNT_TYPE_CURRENT = "current"

ACCOUNT_TYPE_CHOICES = [
    (ACCOUNT_TYPE_SAVINGS, "Savings"),
    (ACCOUNT_TYPE_CURRENT, "Current"),
]

# ════════════════════════════════════════════════════════════════════════
# Employment History Change Type Choices
# ════════════════════════════════════════════════════════════════════════

CHANGE_TYPE_PROMOTION = "promotion"
CHANGE_TYPE_TRANSFER = "transfer"
CHANGE_TYPE_DEMOTION = "demotion"
CHANGE_TYPE_SALARY_CHANGE = "salary_change"
CHANGE_TYPE_ROLE_CHANGE = "role_change"
CHANGE_TYPE_HIRE = "hire"
CHANGE_TYPE_MANAGER_CHANGE = "manager_change"
CHANGE_TYPE_PROBATION_CONFIRMATION = "probation_confirmation"
CHANGE_TYPE_RESIGNATION = "resignation"
CHANGE_TYPE_TERMINATION = "termination"

CHANGE_TYPE_CHOICES = [
    (CHANGE_TYPE_PROMOTION, "Promotion"),
    (CHANGE_TYPE_TRANSFER, "Transfer"),
    (CHANGE_TYPE_DEMOTION, "Demotion"),
    (CHANGE_TYPE_SALARY_CHANGE, "Salary Change"),
    (CHANGE_TYPE_ROLE_CHANGE, "Role Change"),
    (CHANGE_TYPE_HIRE, "Hire"),
    (CHANGE_TYPE_MANAGER_CHANGE, "Manager Change"),
    (CHANGE_TYPE_PROBATION_CONFIRMATION, "Probation Confirmation"),
    (CHANGE_TYPE_RESIGNATION, "Resignation"),
    (CHANGE_TYPE_TERMINATION, "Termination"),
]

# ════════════════════════════════════════════════════════════════════════
# Relationship Choices (for emergency contacts & family)
# ════════════════════════════════════════════════════════════════════════

RELATIONSHIP_SPOUSE = "spouse"
RELATIONSHIP_PARENT = "parent"
RELATIONSHIP_CHILD = "child"
RELATIONSHIP_SIBLING = "sibling"
RELATIONSHIP_FRIEND = "friend"
RELATIONSHIP_RELATIVE = "relative"
RELATIONSHIP_OTHER = "other"

RELATIONSHIP_CHOICES = [
    (RELATIONSHIP_SPOUSE, "Spouse"),
    (RELATIONSHIP_PARENT, "Parent"),
    (RELATIONSHIP_CHILD, "Child"),
    (RELATIONSHIP_SIBLING, "Sibling"),
    (RELATIONSHIP_FRIEND, "Friend"),
    (RELATIONSHIP_RELATIVE, "Relative"),
    (RELATIONSHIP_OTHER, "Other"),
]

# ════════════════════════════════════════════════════════════════════════
# Sri Lanka Provinces
# ════════════════════════════════════════════════════════════════════════

PROVINCE_CHOICES = [
    ("western", "Western"),
    ("central", "Central"),
    ("southern", "Southern"),
    ("northern", "Northern"),
    ("eastern", "Eastern"),
    ("north_western", "North Western"),
    ("north_central", "North Central"),
    ("uva", "Uva"),
    ("sabaragamuwa", "Sabaragamuwa"),
]

# ════════════════════════════════════════════════════════════════════════
# Employee ID Prefix
# ════════════════════════════════════════════════════════════════════════

EMPLOYEE_ID_PREFIX = "EMP"
EMPLOYEE_ID_PADDING = 4  # EMP-0001

# ════════════════════════════════════════════════════════════════════════
# Termination Reason Choices
# ════════════════════════════════════════════════════════════════════════

TERMINATION_REASON_PERFORMANCE = "performance"
TERMINATION_REASON_MISCONDUCT = "misconduct"
TERMINATION_REASON_REDUNDANCY = "redundancy"
TERMINATION_REASON_MUTUAL = "mutual"
TERMINATION_REASON_CONTRACT_END = "contract_end"
TERMINATION_REASON_RESIGNATION = "resignation"
TERMINATION_REASON_OTHER = "other"

TERMINATION_REASON_CHOICES = [
    (TERMINATION_REASON_PERFORMANCE, "Performance"),
    (TERMINATION_REASON_MISCONDUCT, "Misconduct"),
    (TERMINATION_REASON_REDUNDANCY, "Redundancy"),
    (TERMINATION_REASON_MUTUAL, "Mutual Agreement"),
    (TERMINATION_REASON_CONTRACT_END, "Contract End"),
    (TERMINATION_REASON_RESIGNATION, "Resignation"),
    (TERMINATION_REASON_OTHER, "Other"),
]

# ════════════════════════════════════════════════════════════════════════
# Work Location Type Choices
# ════════════════════════════════════════════════════════════════════════

WORK_LOCATION_TYPE_OFFICE = "office"
WORK_LOCATION_TYPE_BRANCH = "branch"
WORK_LOCATION_TYPE_REMOTE = "remote"
WORK_LOCATION_TYPE_HYBRID = "hybrid"
WORK_LOCATION_TYPE_FIELD = "field"
WORK_LOCATION_TYPE_CLIENT_SITE = "client_site"

WORK_LOCATION_TYPE_CHOICES = [
    (WORK_LOCATION_TYPE_OFFICE, "Office"),
    (WORK_LOCATION_TYPE_BRANCH, "Branch"),
    (WORK_LOCATION_TYPE_REMOTE, "Remote"),
    (WORK_LOCATION_TYPE_HYBRID, "Hybrid"),
    (WORK_LOCATION_TYPE_FIELD, "Field"),
    (WORK_LOCATION_TYPE_CLIENT_SITE, "Client Site"),
]

# ════════════════════════════════════════════════════════════════════════
# Employment Change Reason Choices
# ════════════════════════════════════════════════════════════════════════

CHANGE_REASON_PERFORMANCE = "performance"
CHANGE_REASON_RESTRUCTURING = "restructuring"
CHANGE_REASON_BUSINESS_NEEDS = "business_needs"
CHANGE_REASON_SKILL_DEVELOPMENT = "skill_development"
CHANGE_REASON_EMPLOYEE_REQUEST = "employee_request"
CHANGE_REASON_RETENTION = "retention"
CHANGE_REASON_COST_OPTIMIZATION = "cost_optimization"
CHANGE_REASON_MARKET_ADJUSTMENT = "market_adjustment"
CHANGE_REASON_ANNUAL_REVIEW = "annual_review"
CHANGE_REASON_OTHER = "other"

CHANGE_REASON_CHOICES = [
    (CHANGE_REASON_PERFORMANCE, "Performance"),
    (CHANGE_REASON_RESTRUCTURING, "Restructuring"),
    (CHANGE_REASON_BUSINESS_NEEDS, "Business Needs"),
    (CHANGE_REASON_SKILL_DEVELOPMENT, "Skill Development"),
    (CHANGE_REASON_EMPLOYEE_REQUEST, "Employee Request"),
    (CHANGE_REASON_RETENTION, "Retention"),
    (CHANGE_REASON_COST_OPTIMIZATION, "Cost Optimization"),
    (CHANGE_REASON_MARKET_ADJUSTMENT, "Market Adjustment"),
    (CHANGE_REASON_ANNUAL_REVIEW, "Annual Review"),
    (CHANGE_REASON_OTHER, "Other"),
]

# ════════════════════════════════════════════════════════════════════════
# Sri Lankan Banks
# ════════════════════════════════════════════════════════════════════════

SRI_LANKAN_BANKS = [
    {"code": "7010", "name": "Bank of Ceylon", "short": "BOC"},
    {"code": "7038", "name": "Cargills Bank Limited", "short": "CARGILLS"},
    {"code": "7047", "name": "Citibank N.A.", "short": "CITI"},
    {"code": "7056", "name": "Commercial Bank of Ceylon PLC", "short": "COMBANK"},
    {"code": "7074", "name": "Deutsche Bank AG", "short": "DEUTSCHE"},
    {"code": "7083", "name": "DFCC Bank PLC", "short": "DFCC"},
    {"code": "7092", "name": "Habib Bank Limited", "short": "HBL"},
    {"code": "7108", "name": "Hatton National Bank PLC", "short": "HNB"},
    {"code": "7117", "name": "Hongkong & Shanghai Banking Corp", "short": "HSBC"},
    {"code": "7135", "name": "Indian Bank", "short": "INDIAN"},
    {"code": "7144", "name": "Indian Overseas Bank", "short": "IOB"},
    {"code": "7162", "name": "MCB Bank Limited", "short": "MCB"},
    {"code": "7175", "name": "National Development Bank PLC", "short": "NDB"},
    {"code": "7194", "name": "Nations Trust Bank PLC", "short": "NTB"},
    {"code": "7205", "name": "Pan Asia Banking Corporation PLC", "short": "PABC"},
    {"code": "7214", "name": "People's Bank", "short": "PEOPLES"},
    {"code": "7269", "name": "Sampath Bank PLC", "short": "SAMPATH"},
    {"code": "7278", "name": "Seylan Bank PLC", "short": "SEYLAN"},
    {"code": "7287", "name": "Standard Chartered Bank", "short": "SCB"},
    {"code": "7296", "name": "State Bank of India", "short": "SBI"},
    {"code": "7302", "name": "Union Bank of Colombo PLC", "short": "UBC"},
    {"code": "7384", "name": "Amana Bank PLC", "short": "AMANA"},
    {"code": "7454", "name": "Sanasa Development Bank PLC", "short": "SDB"},
    {"code": "7719", "name": "National Savings Bank", "short": "NSB"},
    {"code": "7728", "name": "Regional Development Bank", "short": "RDB"},
    {"code": "7737", "name": "Housing Development Finance Corp Bank", "short": "HDFC"},
    {"code": "7746", "name": "State Mortgage & Investment Bank", "short": "SMIB"},
    {"code": "7755", "name": "Lanka Puthra Development Bank", "short": "LPDB"},
    {"code": "7764", "name": "Pradeshiya Sanwardhana Bank", "short": "PSB"},
]

SRI_LANKAN_BANK_CHOICES = [
    (bank["code"], bank["name"]) for bank in SRI_LANKAN_BANKS
]

# ════════════════════════════════════════════════════════════════════════
# Valid Status Transitions
# ════════════════════════════════════════════════════════════════════════

VALID_STATUS_TRANSITIONS = {
    EMPLOYEE_STATUS_ACTIVE: [
        EMPLOYEE_STATUS_INACTIVE,
        EMPLOYEE_STATUS_ON_LEAVE,
        EMPLOYEE_STATUS_TERMINATED,
        EMPLOYEE_STATUS_RESIGNED,
    ],
    EMPLOYEE_STATUS_INACTIVE: [
        EMPLOYEE_STATUS_ACTIVE,
        EMPLOYEE_STATUS_TERMINATED,
    ],
    EMPLOYEE_STATUS_ON_LEAVE: [
        EMPLOYEE_STATUS_ACTIVE,
        EMPLOYEE_STATUS_TERMINATED,
        EMPLOYEE_STATUS_RESIGNED,
    ],
    EMPLOYEE_STATUS_TERMINATED: [],  # Terminal state
    EMPLOYEE_STATUS_RESIGNED: [],  # Terminal state
}

# ════════════════════════════════════════════════════════════════════════
# Retirement Age (Sri Lanka)
# ════════════════════════════════════════════════════════════════════════

RETIREMENT_AGE = 60
