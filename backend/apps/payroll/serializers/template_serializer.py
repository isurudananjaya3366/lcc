"""SalaryTemplate serializers for the Payroll module."""

from rest_framework import serializers

from apps.payroll.models import SalaryTemplate, TemplateComponent
from apps.payroll.serializers.component_serializer import SalaryComponentListSerializer


class TemplateComponentSerializer(serializers.ModelSerializer):
    """Serializer for template-component relationships."""

    component_detail = SalaryComponentListSerializer(
        source="component", read_only=True
    )

    class Meta:
        model = TemplateComponent
        fields = [
            "id",
            "component",
            "component_detail",
            "default_value",
            "can_override",
            "min_value",
            "max_value",
        ]
        read_only_fields = ["id", "component_detail"]


class SalaryTemplateListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for template list views."""

    component_count = serializers.SerializerMethodField()
    designation_name = serializers.SerializerMethodField()

    class Meta:
        model = SalaryTemplate
        fields = [
            "id",
            "name",
            "code",
            "designation",
            "designation_name",
            "is_active",
            "component_count",
        ]
        read_only_fields = fields

    def get_component_count(self, obj):
        return obj.components.count()

    def get_designation_name(self, obj):
        return obj.designation.name if obj.designation else None


class SalaryTemplateSerializer(serializers.ModelSerializer):
    """Full serializer with nested components."""

    components = TemplateComponentSerializer(many=True, read_only=True)
    designation_name = serializers.SerializerMethodField()

    class Meta:
        model = SalaryTemplate
        fields = [
            "id",
            "name",
            "code",
            "description",
            "designation",
            "designation_name",
            "is_active",
            "components",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id", "designation_name", "components", "created_on", "updated_on"
        ]

    def get_designation_name(self, obj):
        return obj.designation.name if obj.designation else None
