"""DRF serializers for the attributes app models."""

from rest_framework import serializers

from .constants import SELECT, MULTISELECT
from .models import Attribute, AttributeGroup, AttributeOption


class AttributeGroupSerializer(serializers.ModelSerializer):
    """Serializer for AttributeGroup with attribute count."""

    attribute_count = serializers.SerializerMethodField()

    class Meta:
        model = AttributeGroup
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "display_order",
            "is_active",
            "attribute_count",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "slug", "created_on", "updated_on"]

    def get_attribute_count(self, obj):
        return obj.attributes.count()


class AttributeOptionSerializer(serializers.ModelSerializer):
    """Serializer for AttributeOption with visual field support."""

    attribute_name = serializers.CharField(
        source="attribute.name", read_only=True
    )

    class Meta:
        model = AttributeOption
        fields = [
            "id",
            "attribute",
            "attribute_name",
            "value",
            "label",
            "color_code",
            "image",
            "display_order",
            "is_default",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "created_on", "updated_on"]


class AttributeListSerializer(serializers.ModelSerializer):
    """Optimized serializer for attribute list views with minimal data."""

    group_name = serializers.CharField(
        source="group.name", read_only=True, default=None
    )
    type_display = serializers.CharField(
        source="get_attribute_type_display", read_only=True
    )
    option_count = serializers.SerializerMethodField()

    class Meta:
        model = Attribute
        fields = [
            "id",
            "name",
            "slug",
            "attribute_type",
            "type_display",
            "group",
            "group_name",
            "is_required",
            "is_filterable",
            "is_searchable",
            "display_order",
            "option_count",
        ]
        read_only_fields = ["id", "slug"]

    def get_option_count(self, obj):
        if obj.attribute_type in (SELECT, MULTISELECT):
            return obj.options.count()
        return None


class AttributeSerializer(serializers.ModelSerializer):
    """Standard serializer for Attribute create/update operations."""

    group_name = serializers.CharField(
        source="group.name", read_only=True, default=None
    )
    type_display = serializers.CharField(
        source="get_attribute_type_display", read_only=True
    )

    class Meta:
        model = Attribute
        fields = [
            "id",
            "name",
            "slug",
            "group",
            "group_name",
            "attribute_type",
            "type_display",
            "unit",
            "is_required",
            "is_filterable",
            "is_searchable",
            "is_comparable",
            "is_visible_on_product",
            "display_order",
            "validation_regex",
            "min_value",
            "max_value",
            "categories",
            "is_active",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "slug", "created_on", "updated_on"]

    def validate(self, data):
        attr_type = data.get(
            "attribute_type",
            getattr(self.instance, "attribute_type", None),
        )
        min_val = data.get(
            "min_value",
            getattr(self.instance, "min_value", None),
        )
        max_val = data.get(
            "max_value",
            getattr(self.instance, "max_value", None),
        )
        if attr_type == "number" and not data.get(
            "unit", getattr(self.instance, "unit", "")
        ):
            raise serializers.ValidationError(
                "Unit is required for NUMBER type attributes."
            )
        if (
            min_val is not None
            and max_val is not None
            and min_val > max_val
        ):
            raise serializers.ValidationError(
                "Minimum value cannot be greater than maximum value."
            )
        return data


class AttributeDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer with nested group and options."""

    group = AttributeGroupSerializer(read_only=True)
    group_id = serializers.PrimaryKeyRelatedField(
        queryset=AttributeGroup.objects.all(),
        source="group",
        write_only=True,
        required=False,
        allow_null=True,
    )
    type_display = serializers.CharField(
        source="get_attribute_type_display", read_only=True
    )
    options = AttributeOptionSerializer(many=True, read_only=True)
    option_count = serializers.SerializerMethodField()

    class Meta:
        model = Attribute
        fields = [
            "id",
            "name",
            "slug",
            "group",
            "group_id",
            "attribute_type",
            "type_display",
            "unit",
            "is_required",
            "is_filterable",
            "is_searchable",
            "is_comparable",
            "is_visible_on_product",
            "display_order",
            "validation_regex",
            "min_value",
            "max_value",
            "categories",
            "options",
            "option_count",
            "is_active",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "slug", "created_on", "updated_on"]

    def get_option_count(self, obj):
        return obj.options.count()
