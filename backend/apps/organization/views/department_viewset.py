"""Department ViewSet with CRUD and hierarchy actions."""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.organization.filters import DepartmentFilter
from apps.organization.models import Department
from apps.organization.serializers import (
    DepartmentListSerializer,
    DepartmentSerializer,
)
from apps.organization.services.department_service import DepartmentService
from apps.organization.services.orgchart_service import OrgChartService


class DepartmentViewSet(ModelViewSet):
    """ViewSet for Department CRUD and hierarchy operations."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DepartmentFilter
    search_fields = ["name", "code", "description"]
    ordering_fields = ["name", "code", "created_on"]
    ordering = ["name"]

    def get_queryset(self):
        return (
            Department.objects.filter(is_deleted=False)
            .select_related("parent", "manager")
        )

    def get_serializer_class(self):
        if self.action == "list":
            return DepartmentListSerializer
        return DepartmentSerializer

    def perform_create(self, serializer):
        instance = DepartmentService.create(serializer.validated_data)
        serializer.instance = instance

    def perform_update(self, serializer):
        instance = DepartmentService.update(self.get_object(), serializer.validated_data)
        serializer.instance = instance

    # ── Custom Actions ──────────────────────────────────────────────

    @action(detail=False, methods=["get"])
    def tree(self, request):
        """Return the full department tree."""
        root_id = request.query_params.get("root_id")
        tree = OrgChartService.get_department_tree(root_id=root_id)
        return Response(tree)

    @action(detail=True, methods=["get"])
    def employees(self, request, pk=None):
        """List employees in this department."""
        department = self.get_object()
        from apps.employees.serializers import EmployeeListSerializer

        qs = department.employees.filter(is_deleted=False)
        serializer = EmployeeListSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def children(self, request, pk=None):
        """Return direct child departments."""
        department = self.get_object()
        qs = department.get_children().filter(is_deleted=False)
        serializer = DepartmentListSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def path(self, request, pk=None):
        """Return the path from this department to the root."""
        department = self.get_object()
        path_data = OrgChartService.get_path_to_root(department.pk)
        return Response(path_data)

    @action(detail=True, methods=["get"])
    def stats(self, request, pk=None):
        """Return statistics for this department."""
        department = self.get_object()
        stats = OrgChartService.get_department_stats(department.pk)
        return Response(stats)

    @action(detail=True, methods=["post"])
    def move(self, request, pk=None):
        """Move this department to a new parent."""
        department = self.get_object()
        new_parent_id = request.data.get("new_parent_id")

        new_parent = None
        if new_parent_id:
            try:
                new_parent = Department.objects.get(
                    pk=new_parent_id, is_deleted=False,
                )
            except Department.DoesNotExist:
                return Response(
                    {"detail": "Target parent department not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        try:
            DepartmentService.move(department, new_parent)
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        department.refresh_from_db()
        return Response(DepartmentSerializer(department).data)

    @action(detail=True, methods=["post"])
    def merge(self, request, pk=None):
        """Merge this department into target."""
        source = self.get_object()
        target_id = request.data.get("target_id")

        if not target_id:
            return Response(
                {"detail": "target_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            target = Department.objects.get(pk=target_id, is_deleted=False)
        except Department.DoesNotExist:
            return Response(
                {"detail": "Target department not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            result = DepartmentService.merge(source, target)
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(DepartmentSerializer(result).data)

    @action(detail=True, methods=["post"], url_path="archive")
    def archive_department(self, request, pk=None):
        """Archive this department."""
        department = self.get_object()
        department = DepartmentService.archive(department)
        serializer = self.get_serializer(department)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="activate")
    def activate_department(self, request, pk=None):
        """Re-activate this department."""
        department = self.get_object()
        department = DepartmentService.activate(department)
        serializer = self.get_serializer(department)
        return Response(serializer.data)
