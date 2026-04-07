"""EmployeeSalary ViewSet."""

import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.payroll.filters import EmployeeSalaryFilter
from apps.payroll.models import EmployeeSalary, SalaryTemplate
from apps.payroll.serializers.employee_salary_serializer import (
    EmployeeSalaryListSerializer,
    EmployeeSalarySerializer,
)
from apps.payroll.services.salary_service import SalaryService

logger = logging.getLogger(__name__)


class EmployeeSalaryViewSet(ModelViewSet):
    """ViewSet for EmployeeSalary CRUD with assignment and revision actions.

    Endpoints:
        GET    /salaries/                   - List salaries
        POST   /salaries/                   - Create salary
        GET    /salaries/{id}/              - Retrieve salary
        PUT    /salaries/{id}/              - Update salary
        POST   /salaries/assign/            - Assign template to employee
        POST   /salaries/revise/            - Revise employee salary
        GET    /salaries/{id}/compare/      - Compare with previous salary
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = EmployeeSalaryFilter
    search_fields = [
        "employee__first_name",
        "employee__last_name",
        "employee__employee_id",
    ]
    ordering_fields = ["basic_salary", "gross_salary", "effective_from", "created_on"]
    ordering = ["-effective_from"]

    def get_queryset(self):
        return EmployeeSalary.objects.select_related(
            "employee", "template"
        ).prefetch_related("salary_components__component")

    def get_serializer_class(self):
        if self.action == "list":
            return EmployeeSalaryListSerializer
        return EmployeeSalarySerializer

    @action(detail=False, methods=["post"], url_path="assign")
    def assign(self, request):
        """Assign a salary template to an employee."""
        from apps.employees.models import Employee

        employee_id = request.data.get("employee")
        template_id = request.data.get("template")
        basic_salary = request.data.get("basic_salary")
        effective_from = request.data.get("effective_from")

        if not all([employee_id, template_id, basic_salary]):
            raise serializers.ValidationError(
                "employee, template, and basic_salary are required."
            )

        try:
            employee = Employee.objects.get(id=employee_id)
            template = SalaryTemplate.objects.get(id=template_id)
        except (Employee.DoesNotExist, SalaryTemplate.DoesNotExist) as e:
            raise serializers.ValidationError(str(e))

        from decimal import Decimal
        from datetime import date

        salary = SalaryService.assign_template(
            employee=employee,
            template=template,
            basic_salary=Decimal(str(basic_salary)),
            effective_from=date.fromisoformat(effective_from) if effective_from else None,
        )

        return Response(
            EmployeeSalarySerializer(salary).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], url_path="revise")
    def revise(self, request):
        """Revise an employee's salary."""
        from apps.employees.models import Employee

        employee_id = request.data.get("employee")
        new_basic = request.data.get("basic_salary")
        effective_from = request.data.get("effective_from")
        change_reason = request.data.get("change_reason", "OTHER")
        remarks = request.data.get("remarks", "")

        if not all([employee_id, new_basic, effective_from]):
            raise serializers.ValidationError(
                "employee, basic_salary, and effective_from are required."
            )

        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist as e:
            raise serializers.ValidationError(str(e))

        from decimal import Decimal
        from datetime import date

        salary = SalaryService.revise_salary(
            employee=employee,
            new_basic=Decimal(str(new_basic)),
            effective_from=date.fromisoformat(effective_from),
            change_reason=change_reason,
            remarks=remarks,
        )

        return Response(
            EmployeeSalarySerializer(salary).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"], url_path="compare")
    def compare(self, request, pk=None):
        """Compare this salary with the previous one."""
        current_salary = self.get_object()

        previous = EmployeeSalary.objects.filter(
            employee=current_salary.employee,
            effective_from__lt=current_salary.effective_from,
        ).order_by("-effective_from").first()

        if not previous:
            return Response(
                {"detail": "No previous salary found for comparison."},
                status=status.HTTP_404_NOT_FOUND,
            )

        result = SalaryService.compare_salaries(previous, current_salary)
        return Response(result)

    @action(detail=True, methods=["post"], url_path="override-component")
    def override_component(self, request, pk=None):
        """Override a specific component in this salary."""
        from apps.payroll.models import SalaryComponent
        from decimal import Decimal

        salary = self.get_object()
        component_id = request.data.get("component")
        amount = request.data.get("amount")

        if not all([component_id, amount]):
            raise serializers.ValidationError(
                "component and amount are required."
            )

        try:
            component = SalaryComponent.objects.get(id=component_id)
        except SalaryComponent.DoesNotExist as e:
            raise serializers.ValidationError(str(e))

        SalaryService.override_component(
            employee_salary=salary,
            component=component,
            amount=Decimal(str(amount)),
        )

        salary.refresh_from_db()
        return Response(EmployeeSalarySerializer(salary).data)

    @action(detail=False, methods=["get"], url_path="current")
    def current_salaries(self, request):
        """List only current (active) salaries."""
        qs = self.get_queryset().filter(is_current=True)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = EmployeeSalaryListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = EmployeeSalaryListSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="export")
    def export_salaries(self, request):
        """Export current salaries to CSV."""
        from django.http import HttpResponse
        from apps.payroll.services.export_service import SalaryExportService

        csv_content = SalaryExportService.export_current_salaries()
        response = HttpResponse(csv_content, content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="salaries_export.csv"'
        return response
