"""Serializers for the Employees application."""

from rest_framework import serializers

from apps.employees.models import (
    Employee,
    EmployeeAddress,
    EmployeeBankAccount,
    EmployeeDocument,
    EmployeeFamily,
    EmergencyContact,
    EmploymentHistory,
)


# =====================================================================
# Nested / Related Serializers
# =====================================================================


class ManagerSummarySerializer(serializers.ModelSerializer):
    """Simplified serializer for manager references (avoids circular nesting)."""

    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Employee
        fields = ["id", "employee_id", "full_name", "email"]
        read_only_fields = fields


class EmployeeAddressSerializer(serializers.ModelSerializer):
    """Serializer for EmployeeAddress model."""

    class Meta:
        model = EmployeeAddress
        fields = [
            "id",
            "employee",
            "address_type",
            "line1",
            "line2",
            "city",
            "postal_code",
            "province",
            "district",
            "is_primary",
            "notes",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "employee", "created_on", "updated_on"]


class EmergencyContactSerializer(serializers.ModelSerializer):
    """Serializer for EmergencyContact model."""

    class Meta:
        model = EmergencyContact
        fields = [
            "id",
            "employee",
            "name",
            "relationship",
            "phone",
            "email",
            "priority",
            "notes",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "created_on", "updated_on"]


class EmployeeFamilySerializer(serializers.ModelSerializer):
    """Serializer for EmployeeFamily model."""

    class Meta:
        model = EmployeeFamily
        fields = [
            "id",
            "employee",
            "name",
            "relationship",
            "date_of_birth",
            "occupation",
            "is_dependent",
            "phone",
            "notes",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "created_on", "updated_on"]


class EmployeeDocumentSerializer(serializers.ModelSerializer):
    """Serializer for EmployeeDocument model."""

    is_expired = serializers.ReadOnlyField()

    class Meta:
        model = EmployeeDocument
        fields = [
            "id",
            "employee",
            "document_type",
            "title",
            "description",
            "file",
            "file_size",
            "file_type",
            "original_filename",
            "issue_date",
            "expiry_date",
            "is_sensitive",
            "visible_to_employee",
            "uploaded_by",
            "is_expired",
            "is_verified",
            "verified_by",
            "verified_at",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "file_size",
            "file_type",
            "original_filename",
            "is_expired",
            "is_verified",
            "verified_by",
            "verified_at",
            "created_on",
            "updated_on",
        ]


class EmployeeBankAccountSerializer(serializers.ModelSerializer):
    """Serializer for EmployeeBankAccount model."""

    account_number_masked = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeBankAccount
        fields = [
            "id",
            "employee",
            "bank_name",
            "bank_code",
            "branch_name",
            "account_number",
            "account_number_masked",
            "account_holder_name",
            "swift_code",
            "branch_code",
            "iban",
            "routing_number",
            "is_international",
            "currency",
            "account_type",
            "is_primary",
            "is_verified",
            "verified_by",
            "verified_at",
            "notes",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id", "account_number_masked", "is_verified",
            "verified_by", "verified_at", "created_on", "updated_on",
        ]

    def get_account_number_masked(self, obj):
        return obj.get_masked_account_number()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Mask account number in list views for security
        request = self.context.get("request")
        if request and request.method == "GET":
            data["account_number"] = instance.get_masked_account_number()
        return data


class EmploymentHistorySerializer(serializers.ModelSerializer):
    """Serializer for EmploymentHistory model."""

    salary_change_amount = serializers.ReadOnlyField()
    salary_change_percentage = serializers.ReadOnlyField()

    class Meta:
        model = EmploymentHistory
        fields = [
            "id",
            "employee",
            "effective_date",
            "change_type",
            "change_reason",
            "change_reason_detail",
            "from_department",
            "to_department",
            "from_designation",
            "to_designation",
            "from_manager",
            "to_manager",
            "previous_salary",
            "new_salary",
            "salary_change_amount",
            "salary_change_percentage",
            "notes",
            "changed_by",
            "created_on",
            "updated_on",
        ]
        read_only_fields = fields


# =====================================================================
# Employee Serializers (List / Detail / Create / Update)
# =====================================================================


class EmployeeListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for employee list views."""

    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Employee
        fields = [
            "id",
            "employee_id",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "mobile",
            "department",
            "designation",
            "employment_type",
            "status",
        ]
        read_only_fields = fields


class EmployeeDetailSerializer(serializers.ModelSerializer):
    """Full serializer for employee detail views with nested data."""

    full_name = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    is_active_employee = serializers.ReadOnlyField()
    has_system_access = serializers.ReadOnlyField()
    has_photo = serializers.ReadOnlyField()
    tenure_in_years = serializers.ReadOnlyField()
    is_on_probation = serializers.ReadOnlyField()
    is_confirmed = serializers.ReadOnlyField()
    has_spouse = serializers.ReadOnlyField()
    retirement_date = serializers.ReadOnlyField()
    manager_detail = ManagerSummarySerializer(source="manager", read_only=True)
    addresses = EmployeeAddressSerializer(many=True, read_only=True)
    emergency_contacts = EmergencyContactSerializer(many=True, read_only=True)
    family_members = EmployeeFamilySerializer(many=True, read_only=True)
    documents = EmployeeDocumentSerializer(many=True, read_only=True)
    bank_accounts = EmployeeBankAccountSerializer(many=True, read_only=True)
    employment_history = EmploymentHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Employee
        fields = [
            "id",
            "employee_id",
            "first_name",
            "last_name",
            "middle_name",
            "preferred_name",
            "full_name",
            "profile_photo",
            "nic_number",
            "date_of_birth",
            "age",
            "gender",
            "marital_status",
            "spouse_name",
            "marriage_date",
            "has_spouse",
            "email",
            "personal_email",
            "mobile",
            "phone",
            "work_phone",
            "phone_extension",
            "employment_type",
            "status",
            "is_active",
            "department",
            "designation",
            "manager",
            "manager_detail",
            "user",
            "has_system_access",
            "has_photo",
            "hire_date",
            "probation_end_date",
            "confirmation_date",
            "is_on_probation",
            "is_confirmed",
            "tenure_in_years",
            "retirement_date",
            "work_location",
            "work_location_type",
            "work_from_home_eligible",
            "termination_date",
            "termination_reason",
            "termination_notes",
            "exit_interview_date",
            "exit_interview_notes",
            "terminated_by",
            "final_settlement_amount",
            "final_settlement_paid",
            "resignation_date",
            "resignation_reason",
            "notice_period",
            "notice_period_waived",
            "last_working_date",
            "counter_offer_made",
            "counter_offer_accepted",
            "resignation_letter_received",
            "notes",
            "is_active_employee",
            "addresses",
            "emergency_contacts",
            "family_members",
            "documents",
            "bank_accounts",
            "employment_history",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "employee_id",
            "full_name",
            "age",
            "is_active_employee",
            "has_system_access",
            "has_photo",
            "tenure_in_years",
            "is_on_probation",
            "is_confirmed",
            "has_spouse",
            "retirement_date",
            "created_on",
            "updated_on",
        ]


class EmployeeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating employees."""

    class Meta:
        model = Employee
        fields = [
            "first_name",
            "last_name",
            "middle_name",
            "preferred_name",
            "profile_photo",
            "nic_number",
            "date_of_birth",
            "gender",
            "marital_status",
            "spouse_name",
            "marriage_date",
            "email",
            "personal_email",
            "mobile",
            "phone",
            "work_phone",
            "phone_extension",
            "employment_type",
            "status",
            "department",
            "designation",
            "manager",
            "hire_date",
            "probation_end_date",
            "work_location",
            "work_location_type",
            "work_from_home_eligible",
            "notes",
        ]

    def validate_nic_number(self, value):
        if value and Employee.objects.filter(nic_number=value).exists():
            raise serializers.ValidationError("An employee with this NIC number already exists.")
        return value

    def validate(self, attrs):
        """Cross-field validation."""
        from apps.employees.constants import MARITAL_STATUS_MARRIED

        # Spouse name required if married
        if attrs.get("marital_status") == MARITAL_STATUS_MARRIED and not attrs.get("spouse_name"):
            raise serializers.ValidationError({
                "spouse_name": "Spouse name is required when marital status is married."
            })

        # Probation end date must be after hire date
        hire = attrs.get("hire_date")
        probation = attrs.get("probation_end_date")
        if hire and probation and probation <= hire:
            raise serializers.ValidationError({
                "probation_end_date": "Probation end date must be after hire date."
            })

        return attrs


class EmployeeUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating employees."""

    class Meta:
        model = Employee
        fields = [
            "first_name",
            "last_name",
            "middle_name",
            "preferred_name",
            "profile_photo",
            "nic_number",
            "date_of_birth",
            "gender",
            "marital_status",
            "spouse_name",
            "marriage_date",
            "email",
            "personal_email",
            "mobile",
            "phone",
            "work_phone",
            "phone_extension",
            "employment_type",
            "department",
            "designation",
            "manager",
            "work_location",
            "work_location_type",
            "work_from_home_eligible",
            "notes",
        ]

    def validate_nic_number(self, value):
        if value and Employee.objects.filter(nic_number=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("An employee with this NIC number already exists.")
        return value
