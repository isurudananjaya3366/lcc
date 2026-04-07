"""SalaryComponent ViewSet."""

import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.payroll.filters import SalaryComponentFilter
from apps.payroll.models import SalaryComponent
from apps.payroll.serializers.component_serializer import (
    SalaryComponentListSerializer,
    SalaryComponentSerializer,
)

logger = logging.getLogger(__name__)


class SalaryComponentViewSet(ModelViewSet):
    """ViewSet for SalaryComponent CRUD.

    Endpoints:
        GET    /components/           - List components
        POST   /components/           - Create component
        GET    /components/{id}/      - Retrieve component
        PUT    /components/{id}/      - Update component
        DELETE /components/{id}/      - Soft delete component
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SalaryComponentFilter
    search_fields = ["name", "code"]
    ordering_fields = ["display_order", "name", "code", "created_on"]
    ordering = ["display_order", "name"]

    def get_queryset(self):
        return SalaryComponent.objects.filter(is_deleted=False)

    def get_serializer_class(self):
        if self.action == "list":
            return SalaryComponentListSerializer
        return SalaryComponentSerializer

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.is_active = False
        instance.save(update_fields=["is_deleted", "is_active"])
