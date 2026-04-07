"""SalaryComponent serializers for the Payroll module."""

from rest_framework import serializers

from apps.payroll.models import SalaryComponent


class SalaryComponentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for component list views."""

    type_display = serializers.CharField(
        source="get_component_type_display", read_only=True
    )
    category_display = serializers.CharField(
        source="get_category_display", read_only=True
    )
    calculation_display = serializers.CharField(
        source="get_calculation_type_display", read_only=True
    )

    class Meta:
        model = SalaryComponent
        fields = [
            "id",
            "name",
            "code",
            "component_type",
            "type_display",
            "category",
            "category_display",
            "calculation_type",
            "calculation_display",
            "is_taxable",
            "is_epf_applicable",
            "is_active",
            "display_order",
        ]
        read_only_fields = fields


class SalaryComponentSerializer(serializers.ModelSerializer):
    """Full serializer for component detail/create/update."""

    type_display = serializers.CharField(
        source="get_component_type_display", read_only=True
    )
    category_display = serializers.CharField(
        source="get_category_display", read_only=True
    )

    class Meta:
        model = SalaryComponent
        fields = [
            "id",
            "name",
            "code",
            "component_type",
            "type_display",
            "category",
            "category_display",
            "calculation_type",
            "default_value",
            "percentage",
            "formula",
            "is_taxable",
            "is_epf_applicable",
            "is_fixed",
            "is_active",
            "display_order",
            "description",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "type_display", "category_display", "created_on", "updated_on"]
