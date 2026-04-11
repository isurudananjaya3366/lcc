"""
Account serializers.

AccountSerializer — flat representation.
AccountChildrenSerializer — includes nested direct children.
AccountTreeSerializer — recursive full-depth tree.
"""

from rest_framework import serializers

from apps.accounting.models import Account
from apps.accounting.services.validators import AccountValidator


class AccountSerializer(serializers.ModelSerializer):
    """Flat account representation for list / detail views."""

    children_count = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = [
            "id",
            "code",
            "name",
            "account_type",
            "account_type_config",
            "category",
            "status",
            "parent",
            "is_header",
            "is_system",
            "is_active",
            "currency",
            "opening_balance",
            "current_balance",
            "description",
            "level",
            "children_count",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "current_balance",
            "is_system",
            "level",
            "children_count",
            "created_on",
            "updated_on",
        ]

    def get_children_count(self, obj) -> int:
        return obj.get_children().count()

    # ── Create / Update validation ──────────────────────────────────

    def validate_code(self, value):
        AccountValidator.validate_code_format(value)
        return value

    def validate(self, attrs):
        code = attrs.get("code", getattr(self.instance, "code", None))
        account_type = attrs.get(
            "account_type",
            getattr(self.instance, "account_type", None),
        )
        if code and account_type:
            AccountValidator.validate_code_range(code, account_type)

        # Uniqueness on create (or code change)
        if code:
            exclude_id = self.instance.pk if self.instance else None
            AccountValidator.validate_code_unique(code, exclude_id)

        return attrs

    def update(self, instance, validated_data):
        if instance.is_system:
            protected = {"code", "account_type"}
            changed = protected & set(validated_data.keys())
            if changed:
                raise serializers.ValidationError(
                    f"Cannot modify {', '.join(changed)} on a system account."
                )
        return super().update(instance, validated_data)


# ── Nested children ─────────────────────────────────────────────────

class AccountChildrenSerializer(AccountSerializer):
    """Account with one level of nested children."""

    children = AccountSerializer(many=True, read_only=True)

    class Meta(AccountSerializer.Meta):
        fields = AccountSerializer.Meta.fields + ["children"]


# ── Recursive tree ──────────────────────────────────────────────────

class AccountTreeSerializer(serializers.ModelSerializer):
    """Full recursive tree for rendering the chart of accounts."""

    children = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = [
            "id",
            "code",
            "name",
            "account_type",
            "category",
            "status",
            "is_header",
            "is_system",
            "current_balance",
            "level",
            "children",
        ]

    def get_children(self, obj):
        children_qs = obj.get_children()
        return AccountTreeSerializer(children_qs, many=True).data
