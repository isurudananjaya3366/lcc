"""Designation serializers."""

from rest_framework import serializers

from apps.organization.constants import DESIGNATION_LEVEL_ORDER
from apps.organization.models import Designation


class DesignationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for designation list views."""

    level_display = serializers.CharField(source="get_level_display", read_only=True)
    employee_count = serializers.SerializerMethodField()

    class Meta:
        model = Designation
        fields = [
            "id",
            "title",
            "code",
            "status",
            "level",
            "level_display",
            "department",
            "is_manager",
            "employee_count",
        ]
        read_only_fields = fields

    def get_employee_count(self, obj):
        return obj.employees.filter(is_deleted=False).count()


class DesignationSerializer(serializers.ModelSerializer):
    """Full designation serializer with computed fields."""

    level_display = serializers.CharField(source="get_level_display", read_only=True)
    salary_range_display = serializers.SerializerMethodField()
    employee_count = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    reports_to_title = serializers.SerializerMethodField()
    level_rank = serializers.SerializerMethodField()

    class Meta:
        model = Designation
        fields = [
            "id",
            "title",
            "code",
            "status",
            "level",
            "level_display",
            "level_rank",
            "description",
            "responsibilities",
            "department",
            "department_name",
            "min_salary",
            "max_salary",
            "currency",
            "salary_range_display",
            "qualifications",
            "experience_years",
            "reports_to",
            "reports_to_title",
            "is_manager",
            "employee_count",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "level_display",
            "level_rank",
            "salary_range_display",
            "employee_count",
            "department_name",
            "reports_to_title",
            "created_on",
            "updated_on",
        ]

    def get_salary_range_display(self, obj):
        if obj.min_salary is not None and obj.max_salary is not None:
            return f"{obj.currency} {obj.min_salary:,.2f} – {obj.max_salary:,.2f}"
        if obj.min_salary is not None:
            return f"{obj.currency} {obj.min_salary:,.2f}+"
        if obj.max_salary is not None:
            return f"Up to {obj.currency} {obj.max_salary:,.2f}"
        return None

    def get_employee_count(self, obj):
        return obj.employees.filter(is_deleted=False).count()

    def get_department_name(self, obj):
        return obj.department.name if obj.department else None

    def get_reports_to_title(self, obj):
        return obj.reports_to.title if obj.reports_to else None

    def get_level_rank(self, obj):
        return DESIGNATION_LEVEL_ORDER.get(obj.level, 0)
