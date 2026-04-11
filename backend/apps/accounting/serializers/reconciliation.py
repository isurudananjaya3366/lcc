"""
Serializers for bank reconciliation models.

Provides serialization for BankAccount, Reconciliation,
ReconciliationItem, and statement import operations.
"""

from rest_framework import serializers

from apps.accounting.models import (
    BankAccount,
    BankStatement,
    MatchingRule,
    Reconciliation,
    ReconciliationAdjustment,
    ReconciliationItem,
    StatementLine,
)


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = [
            "id",
            "account_name",
            "account_number",
            "bank_name",
            "branch_name",
            "branch_code",
            "account_type",
            "gl_account",
            "currency",
            "last_reconciled_date",
            "last_reconciled_balance",
            "is_active",
        ]
        read_only_fields = ["id", "last_reconciled_date", "last_reconciled_balance"]


class StatementLineSerializer(serializers.ModelSerializer):
    net_amount = serializers.SerializerMethodField()

    class Meta:
        model = StatementLine
        fields = [
            "id",
            "line_number",
            "transaction_date",
            "value_date",
            "description",
            "reference",
            "debit_amount",
            "credit_amount",
            "running_balance",
            "match_status",
            "matched_entry",
            "is_reconciled",
            "net_amount",
        ]
        read_only_fields = ["id"]

    def get_net_amount(self, obj):
        return str(obj.credit_amount - obj.debit_amount)


class BankStatementSerializer(serializers.ModelSerializer):
    line_count = serializers.SerializerMethodField()

    class Meta:
        model = BankStatement
        fields = [
            "id",
            "bank_account",
            "statement_format",
            "start_date",
            "end_date",
            "opening_balance",
            "closing_balance",
            "import_status",
            "import_line_count",
            "is_reconciled",
            "line_count",
        ]
        read_only_fields = ["id", "import_status", "import_line_count"]

    def get_line_count(self, obj):
        return obj.lines.count()


class ReconciliationItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReconciliationItem
        fields = [
            "id",
            "reconciliation",
            "statement_line",
            "journal_entry",
            "match_type",
            "matched_at",
            "matched_by",
            "notes",
        ]
        read_only_fields = ["id", "matched_at"]


class ReconciliationAdjustmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReconciliationAdjustment
        fields = [
            "id",
            "reconciliation",
            "journal_entry",
            "adjustment_type",
            "adjustment_amount",
            "adjustment_reason",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ReconciliationListSerializer(serializers.ModelSerializer):
    bank_account_name = serializers.CharField(
        source="bank_account.account_name", read_only=True,
    )
    matched_count = serializers.SerializerMethodField()
    period_description = serializers.CharField(read_only=True)

    class Meta:
        model = Reconciliation
        fields = [
            "id",
            "bank_account",
            "bank_account_name",
            "bank_statement",
            "start_date",
            "end_date",
            "period_description",
            "status",
            "statement_balance",
            "book_balance",
            "difference",
            "matched_count",
            "completed_at",
            "completed_by",
            "created_at",
        ]
        read_only_fields = [
            "id", "difference", "book_balance",
            "completed_at", "completed_by", "created_at",
        ]

    def get_matched_count(self, obj):
        return obj.items.count()


class ReconciliationDetailSerializer(ReconciliationListSerializer):
    items = ReconciliationItemSerializer(many=True, read_only=True)
    adjustments = ReconciliationAdjustmentSerializer(many=True, read_only=True)

    class Meta(ReconciliationListSerializer.Meta):
        fields = ReconciliationListSerializer.Meta.fields + [
            "items",
            "adjustments",
        ]

    def validate(self, data):
        if "start_date" in data and "end_date" in data:
            if data["end_date"] < data["start_date"]:
                raise serializers.ValidationError(
                    {"end_date": "End date must be >= start date."}
                )
        return data


class MatchingRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchingRule
        fields = [
            "id",
            "bank_account",
            "name",
            "priority",
            "amount_tolerance",
            "date_range_days",
            "match_reference",
            "description_pattern",
            "pattern_flags",
            "is_active",
        ]
        read_only_fields = ["id"]
