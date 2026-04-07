"""SalaryTemplate ViewSet."""

import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.payroll.filters import SalaryTemplateFilter
from apps.payroll.models import SalaryTemplate, TemplateComponent
from apps.payroll.serializers.template_serializer import (
    SalaryTemplateListSerializer,
    SalaryTemplateSerializer,
    TemplateComponentSerializer,
)

logger = logging.getLogger(__name__)


class SalaryTemplateViewSet(ModelViewSet):
    """ViewSet for SalaryTemplate CRUD with component management.

    Endpoints:
        GET    /templates/                          - List templates
        POST   /templates/                          - Create template
        GET    /templates/{id}/                     - Retrieve template
        PUT    /templates/{id}/                     - Update template
        DELETE /templates/{id}/                     - Delete template
        POST   /templates/{id}/add_component/       - Add component to template
        DELETE /templates/{id}/remove_component/    - Remove component
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SalaryTemplateFilter
    search_fields = ["name", "code"]
    ordering_fields = ["name", "code", "created_on"]
    ordering = ["name"]

    def get_queryset(self):
        return SalaryTemplate.objects.select_related("designation").prefetch_related(
            "components__component"
        )

    def get_serializer_class(self):
        if self.action == "list":
            return SalaryTemplateListSerializer
        return SalaryTemplateSerializer

    @action(detail=True, methods=["post"], url_path="add-component")
    def add_component(self, request, pk=None):
        """Add a component to this template."""
        template = self.get_object()
        component_id = request.data.get("component")
        default_value = request.data.get("default_value", 0)
        can_override = request.data.get("can_override", True)
        min_value = request.data.get("min_value")
        max_value = request.data.get("max_value")

        if not component_id:
            raise serializers.ValidationError({"component": "This field is required."})

        tc, created = TemplateComponent.objects.update_or_create(
            template=template,
            component_id=component_id,
            defaults={
                "default_value": default_value,
                "can_override": can_override,
                "min_value": min_value,
                "max_value": max_value,
            },
        )

        return Response(
            TemplateComponentSerializer(tc).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @action(detail=True, methods=["delete"], url_path="remove-component")
    def remove_component(self, request, pk=None):
        """Remove a component from this template."""
        template = self.get_object()
        component_id = request.data.get("component")

        if not component_id:
            raise serializers.ValidationError({"component": "This field is required."})

        deleted, _ = TemplateComponent.objects.filter(
            template=template, component_id=component_id
        ).delete()

        if not deleted:
            return Response(
                {"detail": "Component not found in template."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)
