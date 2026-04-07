"""Department serializers."""

from rest_framework import serializers

from apps.organization.models import Department


class DepartmentParentSerializer(serializers.ModelSerializer):
    """Minimal representation for the parent department reference."""

    class Meta:
        model = Department
        fields = ["id", "name", "code"]
        read_only_fields = fields


class DepartmentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for department list views."""

    employee_count = serializers.SerializerMethodField()
    children_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = [
            "id",
            "name",
            "code",
            "status",
            "parent",
            "level",
            "employee_count",
            "children_count",
        ]
        read_only_fields = fields

    def get_employee_count(self, obj):
        return obj.employees.filter(is_deleted=False).count()

    def get_children_count(self, obj):
        return obj.get_children().filter(is_deleted=False).count()


class DepartmentSerializer(serializers.ModelSerializer):
    """Full department serializer with nested parent and computed fields."""

    parent_detail = DepartmentParentSerializer(source="parent", read_only=True)
    employee_count = serializers.SerializerMethodField()
    children_count = serializers.SerializerMethodField()
    level = serializers.IntegerField(read_only=True)
    path = serializers.SerializerMethodField()
    manager_name = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = [
            "id",
            "name",
            "code",
            "status",
            "description",
            "mission_statement",
            "parent",
            "parent_detail",
            "manager",
            "manager_name",
            "location",
            "building",
            "floor",
            "email",
            "phone",
            "extension",
            "cost_center",
            "annual_budget",
            "currency",
            "level",
            "employee_count",
            "children_count",
            "path",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "level",
            "employee_count",
            "children_count",
            "path",
            "created_on",
            "updated_on",
        ]

    def get_employee_count(self, obj):
        return obj.employees.filter(is_deleted=False).count()

    def get_children_count(self, obj):
        return obj.get_children().filter(is_deleted=False).count()

    def get_path(self, obj):
        return " → ".join(
            a.name
            for a in obj.get_ancestors(include_self=True)
        )

    def get_manager_name(self, obj):
        return obj.manager.full_name if obj.manager else None
