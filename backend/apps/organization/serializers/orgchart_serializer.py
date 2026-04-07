"""Org-chart serializer (non-model based)."""

from rest_framework import serializers


class OrgChartNodeSerializer(serializers.Serializer):
    """Recursive serializer for org-chart tree nodes."""

    id = serializers.CharField()
    name = serializers.CharField()
    children = serializers.ListField(child=serializers.DictField(), default=[])


class OrgChartSerializer(serializers.Serializer):
    """Top-level org-chart response serializer."""

    type = serializers.CharField()
    generated_at = serializers.CharField()
    tree = OrgChartNodeSerializer(many=True)
