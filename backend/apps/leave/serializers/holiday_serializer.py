"""Holiday serializers for the Leave Management module."""

from django.utils import timezone
from rest_framework import serializers

from apps.leave.models import Holiday


class HolidayCalendarSerializer(serializers.ModelSerializer):
    """Lightweight serializer for calendar views."""

    class Meta:
        model = Holiday
        fields = ["id", "name", "date", "holiday_type", "applies_to"]
        read_only_fields = fields


class HolidayListSerializer(serializers.ModelSerializer):
    """Serializer for holiday list views."""

    holiday_type_display = serializers.CharField(
        source="get_holiday_type_display", read_only=True,
    )
    days_until = serializers.SerializerMethodField()
    is_upcoming = serializers.SerializerMethodField()
    is_past = serializers.SerializerMethodField()

    class Meta:
        model = Holiday
        fields = [
            "id",
            "name",
            "date",
            "holiday_type",
            "holiday_type_display",
            "applies_to",
            "is_active",
            "days_until",
            "is_upcoming",
            "is_past",
        ]
        read_only_fields = fields

    def get_days_until(self, obj):
        if obj.date:
            return (obj.date - timezone.now().date()).days
        return None

    def get_is_upcoming(self, obj):
        if obj.date:
            days = (obj.date - timezone.now().date()).days
            return 0 <= days <= 30
        return False

    def get_is_past(self, obj):
        if obj.date:
            return obj.date < timezone.now().date()
        return False


class HolidaySerializer(serializers.ModelSerializer):
    """Full serializer for Holiday CRUD operations."""

    holiday_type_display = serializers.CharField(
        source="get_holiday_type_display", read_only=True,
    )
    applies_to_display = serializers.CharField(
        source="get_applies_to_display", read_only=True,
    )
    department_name = serializers.SerializerMethodField()
    days_until = serializers.SerializerMethodField()
    is_upcoming = serializers.SerializerMethodField()
    is_past = serializers.SerializerMethodField()

    class Meta:
        model = Holiday
        fields = [
            "id",
            "name",
            "date",
            "holiday_type",
            "holiday_type_display",
            "description",
            "is_active",
            "applies_to",
            "applies_to_display",
            "department",
            "department_name",
            "location",
            "is_recurring",
            "recurrence_rule",
            "year",
            "days_until",
            "is_upcoming",
            "is_past",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "created_on",
            "updated_on",
        ]

    def get_department_name(self, obj):
        return obj.department.name if obj.department else None

    def get_days_until(self, obj):
        if obj.date:
            return (obj.date - timezone.now().date()).days
        return None

    def get_is_upcoming(self, obj):
        if obj.date:
            days = (obj.date - timezone.now().date()).days
            return 0 <= days <= 30
        return False

    def get_is_past(self, obj):
        if obj.date:
            return obj.date < timezone.now().date()
        return False

    def validate(self, attrs):
        applies_to = attrs.get(
            "applies_to", getattr(self.instance, "applies_to", None),
        )
        department = attrs.get(
            "department", getattr(self.instance, "department", None),
        )
        location = attrs.get(
            "location", getattr(self.instance, "location", None),
        )

        from apps.leave.constants import HolidayScope

        if applies_to == HolidayScope.ALL:
            if department:
                raise serializers.ValidationError(
                    {"department": "Department must be empty when applies_to is ALL."}
                )
            if location:
                raise serializers.ValidationError(
                    {"location": "Location must be empty when applies_to is ALL."}
                )
        elif applies_to == HolidayScope.DEPARTMENT:
            if not department:
                raise serializers.ValidationError(
                    {"department": "Department is required when applies_to is DEPARTMENT."}
                )
        elif applies_to == HolidayScope.LOCATION:
            if not location:
                raise serializers.ValidationError(
                    {"location": "Location is required when applies_to is LOCATION."}
                )

        return attrs
