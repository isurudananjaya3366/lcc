"""LeaveType serializers for the Leave Management module."""

import re

from rest_framework import serializers

from apps.leave.constants import GenderRestriction, LeaveTypeCategory
from apps.leave.models import LeaveType


class LeaveTypeListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for leave type list views."""

    category_display = serializers.CharField(source="get_category_display", read_only=True)

    class Meta:
        model = LeaveType
        fields = [
            "id",
            "name",
            "code",
            "category",
            "category_display",
            "color",
            "default_days_per_year",
            "is_paid",
            "allow_half_day",
            "is_active",
        ]
        read_only_fields = fields


class LeaveTypeSerializer(serializers.ModelSerializer):
    """Full serializer for LeaveType CRUD operations."""

    category_display = serializers.CharField(source="get_category_display", read_only=True)
    applicable_gender_display = serializers.CharField(
        source="get_applicable_gender_display", read_only=True,
    )
    is_active_display = serializers.SerializerMethodField()
    usage_count = serializers.SerializerMethodField()

    class Meta:
        model = LeaveType
        fields = [
            "id",
            "name",
            "code",
            "category",
            "category_display",
            "description",
            "color",
            "default_days_per_year",
            "max_consecutive_days",
            "max_days_per_request",
            "is_paid",
            "requires_document",
            "document_after_days",
            "is_active",
            "is_active_display",
            "allow_half_day",
            "applicable_gender",
            "applicable_gender_display",
            "min_service_months",
            "min_notice_days",
            "usage_count",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "created_on",
            "updated_on",
        ]

    def get_is_active_display(self, obj):
        return "Active" if obj.is_active else "Inactive"

    def get_usage_count(self, obj):
        return obj.leave_requests.filter(is_deleted=False).count()

    def validate_code(self, value):
        if value:
            value = value.upper()
            if not re.match(r"^[A-Z]{2,10}$", value):
                raise serializers.ValidationError(
                    "Code must be 2-10 uppercase letters."
                )
        return value

    def validate_color(self, value):
        if value and not re.match(r"^#[0-9A-Fa-f]{6}$", value):
            raise serializers.ValidationError(
                "Must be a valid hex color (#RRGGBB)."
            )
        return value

    def validate(self, attrs):
        category = attrs.get("category", getattr(self.instance, "category", None))
        gender = attrs.get(
            "applicable_gender",
            getattr(self.instance, "applicable_gender", GenderRestriction.ALL),
        )

        if category == LeaveTypeCategory.MATERNITY and gender != GenderRestriction.FEMALE:
            raise serializers.ValidationError(
                {"applicable_gender": "Maternity leave must be restricted to Female."}
            )
        if category == LeaveTypeCategory.PATERNITY and gender != GenderRestriction.MALE:
            raise serializers.ValidationError(
                {"applicable_gender": "Paternity leave must be restricted to Male."}
            )

        return attrs
