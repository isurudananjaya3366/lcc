"""
Account ViewSet.

Provides CRUD operations for the Account model plus custom actions
for tree view, account types listing, and COA initialization.
"""

import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.accounting.models import Account, AccountTypeConfig
from apps.accounting.serializers import (
    AccountSerializer,
    AccountTreeSerializer,
    AccountTypeConfigSerializer,
)
from apps.accounting.services import AccountValidator, COAInitializerService
from apps.accounting.services.coa_initializer import (
    COAInitializerError,
    InvalidTemplateException,
    TenantAlreadyInitializedException,
)

logger = logging.getLogger(__name__)


class AccountViewSet(ModelViewSet):
    """
    ViewSet for Account CRUD and chart-of-accounts management.

    list:   GET    /api/v1/accounting/accounts/
    create: POST   /api/v1/accounting/accounts/
    read:   GET    /api/v1/accounting/accounts/{id}/
    update: PUT    /api/v1/accounting/accounts/{id}/
    patch:  PATCH  /api/v1/accounting/accounts/{id}/
    delete: DELETE /api/v1/accounting/accounts/{id}/

    Custom endpoints:
        GET  /api/v1/accounting/accounts/tree/       — full tree view
        GET  /api/v1/accounting/accounts/types/      — account type configs
        POST /api/v1/accounting/accounts/initialize/  — seed default COA
    """

    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"

    # ── Filtering / Search / Ordering ───────────────────────────────
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {
        "account_type": ["exact"],
        "category": ["exact"],
        "status": ["exact"],
        "parent": ["exact", "isnull"],
        "is_active": ["exact"],
        "is_header": ["exact"],
        "is_system": ["exact"],
    }
    search_fields = ["code", "name", "description"]
    ordering_fields = ["code", "name", "account_type", "created_on"]
    ordering = ["code"]

    def get_queryset(self):
        return (
            Account.objects.select_related("parent", "account_type_config")
            .all()
        )

    def get_serializer_class(self):
        if self.action == "tree":
            return AccountTreeSerializer
        return AccountSerializer

    # ── Destroy → archive instead of hard delete ────────────────────

    def perform_destroy(self, instance):
        """Archive instead of hard-deleting an account."""
        AccountValidator.archive_account(instance.pk, archive_children=False)

    # ── Custom Actions ──────────────────────────────────────────────

    @action(detail=False, methods=["get"], url_path="tree")
    def tree(self, request):
        """Return the full chart of accounts as a nested tree."""
        root_nodes = self.get_queryset().filter(parent__isnull=True)
        serializer = AccountTreeSerializer(root_nodes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="types")
    def types(self, request):
        """Return all account type configurations."""
        configs = AccountTypeConfig.objects.all().order_by("display_order")
        serializer = AccountTypeConfigSerializer(configs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="initialize")
    def initialize(self, request):
        """
        Initialize the chart of accounts for the current tenant.

        Body (optional):
            template_id: UUID — use a specific COA template.
            force: bool — replace existing accounts (default: false).
        """
        template_id = request.data.get("template_id")
        force = request.data.get("force", False)

        svc = COAInitializerService()

        try:
            if template_id:
                result = svc.create_from_template(template_id, force=force)
            else:
                result = svc.create_default(force=force)
        except TenantAlreadyInitializedException as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_409_CONFLICT,
            )
        except InvalidTemplateException as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except COAInitializerError as exc:
            logger.exception("COA initialization failed")
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(result, status=status.HTTP_201_CREATED)
