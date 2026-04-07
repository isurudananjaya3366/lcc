"""Employee ViewSet with CRUD operations and lifecycle actions."""

from datetime import date

from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.employees.filters import EmployeeFilter
from apps.employees.models import (
    Employee,
    EmployeeAddress,
    EmployeeBankAccount,
    EmployeeDocument,
    EmployeeFamily,
    EmergencyContact,
    EmploymentHistory,
)
from apps.employees.serializers import (
    EmployeeAddressSerializer,
    EmployeeBankAccountSerializer,
    EmployeeCreateSerializer,
    EmployeeDetailSerializer,
    EmployeeDocumentSerializer,
    EmployeeFamilySerializer,
    EmployeeListSerializer,
    EmployeeUpdateSerializer,
    EmploymentHistorySerializer,
    EmergencyContactSerializer,
)
from apps.employees.services.employee_service import EmployeeService


class EmployeePagination(PageNumberPagination):
    """Default pagination for employee list."""

    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100


class EmployeeViewSet(ModelViewSet):
    """ViewSet for Employee CRUD and lifecycle management."""

    permission_classes = [IsAuthenticated]
    pagination_class = EmployeePagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = EmployeeFilter
    search_fields = [
        "employee_id", "first_name", "last_name",
        "nic_number", "email", "mobile",
    ]
    ordering_fields = [
        "employee_id", "first_name", "last_name",
        "hire_date", "department", "created_on",
    ]
    ordering = ["-created_on"]

    def get_queryset(self):
        return (
            Employee.objects.filter(is_deleted=False)
            .select_related("manager", "user")
            .prefetch_related(
                "addresses", "emergency_contacts", "documents",
            )
        )

    def get_serializer_class(self):
        if self.action == "list":
            return EmployeeListSerializer
        if self.action == "create":
            return EmployeeCreateSerializer
        if self.action in ("update", "partial_update"):
            return EmployeeUpdateSerializer
        return EmployeeDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employee = serializer.save()
        return Response(
            EmployeeDetailSerializer(employee).data,
            status=status.HTTP_201_CREATED,
        )

    def perform_destroy(self, instance):
        """Soft delete — mark as deleted instead of permanent removal."""
        instance.is_deleted = True
        instance.deleted_on = timezone.now()
        instance.save(update_fields=["is_deleted", "deleted_on"])

    # ------------------------------------------------------------------
    # Custom lifecycle actions
    # ------------------------------------------------------------------

    @action(detail=True, methods=["post"], url_path="activate")
    def activate(self, request, pk=None):
        """Activate an employee."""
        employee = self.get_object()
        EmployeeService._validate_status_transition(employee.status, "active")
        employee.status = "active"
        employee.is_active = True
        employee.save(update_fields=["status", "is_active", "updated_on"])
        return Response(EmployeeDetailSerializer(employee).data)

    @action(detail=True, methods=["post"], url_path="deactivate")
    def deactivate(self, request, pk=None):
        """Deactivate an employee."""
        employee = self.get_object()
        EmployeeService._validate_status_transition(employee.status, "inactive")
        employee.status = "inactive"
        employee.is_active = False
        employee.save(update_fields=["status", "is_active", "updated_on"])
        return Response(EmployeeDetailSerializer(employee).data)

    @action(detail=True, methods=["post"], url_path="terminate")
    def terminate(self, request, pk=None):
        """Terminate an employee."""
        employee = self.get_object()
        EmployeeService._validate_status_transition(employee.status, "terminated")
        employee.status = "terminated"
        employee.is_active = False
        term_date = request.data.get("termination_date")
        employee.termination_date = (
            date.fromisoformat(term_date) if term_date else timezone.now().date()
        )
        employee.termination_reason = request.data.get("reason", "")
        employee.save(update_fields=[
            "status", "is_active", "termination_date", "termination_reason", "updated_on",
        ])
        return Response(EmployeeDetailSerializer(employee).data)

    @action(detail=True, methods=["post"], url_path="resign")
    def resign(self, request, pk=None):
        """Process an employee resignation."""
        employee = self.get_object()
        EmployeeService._validate_status_transition(employee.status, "resigned")
        employee.status = "resigned"
        employee.is_active = False
        resign_date = request.data.get("resignation_date")
        employee.resignation_date = (
            date.fromisoformat(resign_date) if resign_date else timezone.now().date()
        )
        employee.resignation_reason = request.data.get("reason", "")
        notice_period = request.data.get("notice_period")
        if notice_period is not None:
            employee.notice_period = notice_period
        employee.save(update_fields=[
            "status", "is_active", "resignation_date", "resignation_reason",
            "notice_period", "updated_on",
        ])
        return Response(EmployeeDetailSerializer(employee).data)

    @action(detail=True, methods=["post"], url_path="link-user")
    def link_user(self, request, pk=None):
        """Link a platform user account to this employee."""
        from django.contrib.auth import get_user_model

        User = get_user_model()
        email = request.data.get("email")
        if not email:
            return Response(
                {"detail": "email is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user_account = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "User with this email not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        employee = self.get_object()
        employee.user = user_account
        employee.save(update_fields=["user", "updated_on"])
        return Response(EmployeeDetailSerializer(employee).data)

    # ------------------------------------------------------------------
    # Nested resource actions
    # ------------------------------------------------------------------

    @action(detail=True, methods=["get", "post"], url_path="addresses")
    def addresses(self, request, pk=None):
        """List or create addresses for this employee."""
        employee = self.get_object()
        if request.method == "GET":
            qs = EmployeeAddress.objects.filter(employee=employee)
            serializer = EmployeeAddressSerializer(qs, many=True)
            return Response(serializer.data)
        serializer = EmployeeAddressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(employee=employee)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get", "post"], url_path="emergency-contacts")
    def emergency_contacts(self, request, pk=None):
        """List or create emergency contacts for this employee."""
        employee = self.get_object()
        if request.method == "GET":
            qs = EmergencyContact.objects.filter(employee=employee)
            serializer = EmergencyContactSerializer(qs, many=True)
            return Response(serializer.data)
        serializer = EmergencyContactSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(employee=employee)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get", "post"], url_path="family-members")
    def family_members(self, request, pk=None):
        """List or create family members for this employee."""
        employee = self.get_object()
        if request.method == "GET":
            qs = EmployeeFamily.objects.filter(employee=employee)
            serializer = EmployeeFamilySerializer(qs, many=True)
            return Response(serializer.data)
        serializer = EmployeeFamilySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(employee=employee)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get", "post"], url_path="documents")
    def documents(self, request, pk=None):
        """List or upload documents for this employee."""
        employee = self.get_object()
        if request.method == "GET":
            qs = EmployeeDocument.objects.filter(employee=employee, is_deleted=False)
            serializer = EmployeeDocumentSerializer(qs, many=True)
            return Response(serializer.data)
        serializer = EmployeeDocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(employee=employee, uploaded_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get", "post"], url_path="bank-accounts")
    def bank_accounts(self, request, pk=None):
        """List or add bank accounts for this employee."""
        employee = self.get_object()
        if request.method == "GET":
            qs = EmployeeBankAccount.objects.filter(employee=employee)
            serializer = EmployeeBankAccountSerializer(qs, many=True)
            return Response(serializer.data)
        serializer = EmployeeBankAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(employee=employee)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="history")
    def history(self, request, pk=None):
        """Return employment history for this employee."""
        employee = self.get_object()
        qs = EmploymentHistory.objects.filter(employee=employee).order_by("-effective_date")
        serializer = EmploymentHistorySerializer(qs, many=True)
        return Response(serializer.data)
