"""
Serializer for journal entries with nested line items.
"""

from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from apps.accounting.models import JournalEntry, JournalEntryLine
from apps.accounting.serializers.journal_line import JournalEntryLineSerializer
from apps.accounting.validators.entry_validators import (
    validate_entry,
    validate_line_amounts,
)


class JournalEntrySerializer(serializers.ModelSerializer):
    lines = JournalEntryLineSerializer(many=True)
    created_by_email = serializers.EmailField(
        source="created_by.email", read_only=True
    )
    posted_by_email = serializers.EmailField(
        source="posted_by.email", read_only=True
    )

    class Meta:
        model = JournalEntry
        fields = [
            "id",
            "entry_number",
            "entry_date",
            "entry_type",
            "entry_status",
            "entry_source",
            "reference",
            "description",
            "total_debit",
            "total_credit",
            "lines",
            "created_by",
            "created_by_email",
            "posted_by",
            "posted_by_email",
            "posted_at",
            "reversal_of",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "entry_number",
            "entry_status",
            "total_debit",
            "total_credit",
            "posted_by",
            "posted_at",
            "created_at",
            "updated_at",
        ]

    @transaction.atomic
    def create(self, validated_data):
        lines_data = validated_data.pop("lines")
        entry = JournalEntry.objects.create(**validated_data)

        for idx, line_data in enumerate(lines_data):
            line = JournalEntryLine(
                journal_entry=entry,
                sort_order=line_data.get("sort_order", idx),
                **{k: v for k, v in line_data.items() if k != "sort_order"},
            )
            validate_line_amounts(line)
            line.save()

        _update_cached_totals(entry)
        validate_entry(entry)
        return entry

    @transaction.atomic
    def update(self, instance, validated_data):
        if not instance.is_editable:
            raise serializers.ValidationError(
                f"Entry {instance.entry_number} is not editable."
            )

        lines_data = validated_data.pop("lines", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if lines_data is not None:
            instance.lines.all().delete()
            for idx, line_data in enumerate(lines_data):
                line = JournalEntryLine(
                    journal_entry=instance,
                    sort_order=line_data.get("sort_order", idx),
                    **{k: v for k, v in line_data.items() if k != "sort_order"},
                )
                validate_line_amounts(line)
                line.save()

            _update_cached_totals(instance)
            validate_entry(instance)

        return instance


def _update_cached_totals(entry):
    from django.db.models import Sum

    totals = entry.lines.aggregate(
        total_debit=Sum("debit_amount"),
        total_credit=Sum("credit_amount"),
    )
    entry.total_debit = totals["total_debit"] or Decimal("0")
    entry.total_credit = totals["total_credit"] or Decimal("0")
    entry.save(update_fields=["total_debit", "total_credit"])
