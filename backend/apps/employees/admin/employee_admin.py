"""Admin configuration for Employee and related models."""

from django.contrib import admin

from apps.employees.models import (
    Employee,
    EmployeeAddress,
    EmployeeBankAccount,
    EmployeeDocument,
    EmployeeFamily,
    EmergencyContact,
    EmploymentHistory,
)


class EmploymentHistoryInline(admin.TabularInline):
    model = EmploymentHistory
    fk_name = "employee"
    extra = 0
    readonly_fields = ["effective_date", "change_type", "from_department", "to_department"]
    fields = ["effective_date", "change_type", "from_department", "to_department", "notes"]


class EmployeeAddressInline(admin.TabularInline):
    model = EmployeeAddress
    extra = 0
    fields = ["address_type", "line1", "city", "province", "is_primary"]


class EmergencyContactInline(admin.TabularInline):
    model = EmergencyContact
    extra = 0
    fields = ["name", "relationship", "phone", "priority"]


class EmployeeFamilyInline(admin.TabularInline):
    model = EmployeeFamily
    extra = 0
    fields = ["name", "relationship", "date_of_birth", "is_dependent"]


class EmployeeDocumentInline(admin.TabularInline):
    model = EmployeeDocument
    extra = 0
    fields = ["title", "document_type", "file", "issue_date", "expiry_date", "is_sensitive"]
    readonly_fields = ["file_size", "file_type"]


class EmployeeBankAccountInline(admin.TabularInline):
    model = EmployeeBankAccount
    extra = 0
    fields = ["bank_name", "branch_name", "account_number", "account_type", "is_primary", "is_verified"]


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Admin for Employee model."""

    list_display = [
        "employee_id",
        "first_name",
        "last_name",
        "email",
        "mobile",
        "employment_type",
        "status",
    ]
    list_filter = [
        "status",
        "employment_type",
        "gender",
        "marital_status",
    ]
    search_fields = [
        "employee_id",
        "first_name",
        "last_name",
        "nic_number",
        "email",
    ]
    readonly_fields = ["employee_id", "created_on", "updated_on"]
    inlines = [
        EmployeeAddressInline,
        EmergencyContactInline,
        EmployeeFamilyInline,
        EmployeeDocumentInline,
        EmployeeBankAccountInline,
        EmploymentHistoryInline,
    ]
    fieldsets = (
        (
            "Employee ID",
            {
                "fields": ("employee_id",),
            },
        ),
        (
            "Personal Information",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "middle_name",
                    "preferred_name",
                    "profile_photo",
                    "date_of_birth",
                    "gender",
                    "marital_status",
                    "nic_number",
                ),
            },
        ),
        (
            "Contact Information",
            {
                "fields": (
                    "email",
                    "personal_email",
                    "mobile",
                    "phone",
                    "work_phone",
                ),
            },
        ),
        (
            "Employment",
            {
                "fields": (
                    "employment_type",
                    "status",
                    "department",
                    "designation",
                    "manager",
                    "user",
                ),
            },
        ),
        (
            "Employment Dates",
            {
                "fields": (
                    "hire_date",
                    "probation_end_date",
                    "confirmation_date",
                ),
            },
        ),
        (
            "Work Location",
            {
                "fields": (
                    "work_location",
                    "work_from_home_eligible",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Termination / Resignation",
            {
                "fields": (
                    "termination_date",
                    "termination_reason",
                    "exit_interview_notes",
                    "resignation_date",
                    "resignation_reason",
                    "notice_period",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Notes",
            {
                "fields": ("notes",),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_on", "updated_on"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(EmployeeAddress)
class EmployeeAddressAdmin(admin.ModelAdmin):
    """Admin for EmployeeAddress model."""

    list_display = ["employee", "address_type", "city", "province", "is_primary"]
    list_filter = ["address_type", "province"]
    search_fields = ["employee__first_name", "employee__last_name", "city"]


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    """Admin for EmergencyContact model."""

    list_display = ["employee", "name", "relationship", "phone", "priority"]
    list_filter = ["relationship"]
    search_fields = ["name", "employee__first_name", "employee__last_name"]


@admin.register(EmployeeFamily)
class EmployeeFamilyAdmin(admin.ModelAdmin):
    """Admin for EmployeeFamily model."""

    list_display = ["employee", "name", "relationship", "is_dependent"]
    list_filter = ["relationship", "is_dependent"]
    search_fields = ["name", "employee__first_name", "employee__last_name"]


@admin.register(EmployeeDocument)
class EmployeeDocumentAdmin(admin.ModelAdmin):
    """Admin for EmployeeDocument model."""

    list_display = ["employee", "title", "document_type", "issue_date", "expiry_date", "is_sensitive"]
    list_filter = ["document_type", "is_sensitive", "visible_to_employee"]
    search_fields = ["title", "employee__first_name", "employee__last_name"]
    readonly_fields = ["file_size", "file_type", "original_filename", "created_on", "updated_on"]


@admin.register(EmployeeBankAccount)
class EmployeeBankAccountAdmin(admin.ModelAdmin):
    """Admin for EmployeeBankAccount model."""

    list_display = ["employee", "bank_name", "account_number", "account_type", "is_primary", "is_verified"]
    list_filter = ["account_type", "is_primary", "is_verified"]
    search_fields = ["bank_name", "account_number", "employee__first_name", "employee__last_name"]
