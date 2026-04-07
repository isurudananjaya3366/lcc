"""
POS Terminal and Session ViewSets.

Provides CRUD for terminals and full session lifecycle (open, close,
suspend, current, summary).
"""

import logging
from decimal import Decimal

import django_filters
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.pos.constants import (
    SESSION_STATUS_CLOSED,
    SESSION_STATUS_OPEN,
    SESSION_STATUS_SUSPENDED,
    TERMINAL_STATUS_ACTIVE,
    TERMINAL_STATUS_INACTIVE,
    TERMINAL_STATUS_MAINTENANCE,
)
from apps.pos.terminal.models import POSSession, POSTerminal
from apps.pos.terminal.serializers import (
    POSSessionSerializer,
    POSTerminalSerializer,
    SessionCloseSerializer,
    SessionOpenSerializer,
)

logger = logging.getLogger(__name__)


# ── Filters ─────────────────────────────────────────────────────────────


class POSTerminalFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(lookup_expr="exact")
    location = django_filters.CharFilter(lookup_expr="icontains")
    code = django_filters.CharFilter(field_name="code", lookup_expr="iexact")
    has_open_session = django_filters.BooleanFilter(
        method="filter_has_open_session"
    )

    class Meta:
        model = POSTerminal
        fields = ["status", "location", "code", "is_active"]

    def filter_has_open_session(self, queryset, name, value):
        terminals_with_open = POSSession.objects.filter(
            status=SESSION_STATUS_OPEN
        ).values_list("terminal_id", flat=True)
        if value:
            return queryset.filter(pk__in=terminals_with_open)
        return queryset.exclude(pk__in=terminals_with_open)


class POSSessionFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(lookup_expr="exact")
    terminal = django_filters.UUIDFilter(field_name="terminal_id")
    operator = django_filters.UUIDFilter(field_name="user_id")
    opened_after = django_filters.DateTimeFilter(
        field_name="opened_at", lookup_expr="gte"
    )
    opened_before = django_filters.DateTimeFilter(
        field_name="opened_at", lookup_expr="lte"
    )

    class Meta:
        model = POSSession
        fields = ["status", "terminal", "operator"]


# ── POSTerminalViewSet ──────────────────────────────────────────────────


class POSTerminalViewSet(viewsets.ModelViewSet):
    """
    CRUD and custom actions for POS terminals.

    Endpoints:
      GET    /terminals/               List
      POST   /terminals/               Create
      GET    /terminals/{id}/          Detail
      PUT    /terminals/{id}/          Update
      PATCH  /terminals/{id}/          Partial update
      DELETE /terminals/{id}/          Soft-delete
      POST   /terminals/{id}/activate/
      POST   /terminals/{id}/deactivate/
      POST   /terminals/{id}/maintenance_mode/
      GET    /terminals/available/
    """

    queryset = POSTerminal.objects.select_related(
        "warehouse", "default_tax"
    ).all()
    serializer_class = POSTerminalSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = POSTerminalFilter
    search_fields = ["code", "name", "location"]
    ordering_fields = ["code", "name", "created_on"]
    ordering = ["code"]

    # ── custom actions ──────────────────────────────────────────────

    @action(detail=True, methods=["post"], url_path="activate")
    def activate(self, request, pk=None):
        terminal = self.get_object()
        if terminal.status == TERMINAL_STATUS_ACTIVE:
            return Response(
                {"detail": "Terminal is already active."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        terminal.status = TERMINAL_STATUS_ACTIVE
        terminal.save(update_fields=["status", "updated_on"])
        logger.info("Terminal %s activated by %s", terminal.code, request.user)
        return Response(POSTerminalSerializer(terminal).data)

    @action(detail=True, methods=["post"], url_path="deactivate")
    def deactivate(self, request, pk=None):
        terminal = self.get_object()
        has_open = POSSession.objects.filter(
            terminal=terminal, status=SESSION_STATUS_OPEN
        ).exists()
        if has_open:
            return Response(
                {"detail": "Cannot deactivate — terminal has an open session."},
                status=status.HTTP_409_CONFLICT,
            )
        terminal.status = TERMINAL_STATUS_INACTIVE
        terminal.save(update_fields=["status", "updated_on"])
        logger.info(
            "Terminal %s deactivated by %s", terminal.code, request.user
        )
        return Response(POSTerminalSerializer(terminal).data)

    @action(detail=True, methods=["post"], url_path="maintenance_mode")
    def maintenance_mode(self, request, pk=None):
        terminal = self.get_object()
        has_open = POSSession.objects.filter(
            terminal=terminal, status=SESSION_STATUS_OPEN
        ).exists()
        if has_open:
            return Response(
                {
                    "detail": "Cannot enter maintenance — terminal has an open session."
                },
                status=status.HTTP_409_CONFLICT,
            )
        terminal.status = TERMINAL_STATUS_MAINTENANCE
        terminal.save(update_fields=["status", "updated_on"])
        logger.info(
            "Terminal %s set to maintenance by %s",
            terminal.code,
            request.user,
        )
        return Response(POSTerminalSerializer(terminal).data)

    @action(detail=False, methods=["get"], url_path="available")
    def available_terminals(self, request):
        """List active terminals without an open session."""
        terminals_with_open = POSSession.objects.filter(
            status=SESSION_STATUS_OPEN
        ).values_list("terminal_id", flat=True)

        qs = self.get_queryset().filter(
            status=TERMINAL_STATUS_ACTIVE, is_active=True
        ).exclude(pk__in=terminals_with_open)

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(
            POSTerminalSerializer(qs, many=True).data
        )


# ── POSSessionViewSet ───────────────────────────────────────────────────


class POSSessionViewSet(viewsets.ModelViewSet):
    """
    CRUD and lifecycle actions for POS sessions.

    Endpoints:
      GET    /sessions/                      List (filtered)
      GET    /sessions/{id}/                 Detail with stats
      POST   /sessions/open_session/         Open new session
      POST   /sessions/{id}/close_session/   Close session
      GET    /sessions/current/              Current open session
      GET    /sessions/{id}/summary/         Detailed session summary
      GET    /sessions/my_sessions/          Current user's sessions
    """

    queryset = POSSession.objects.select_related(
        "terminal", "user"
    ).all()
    serializer_class = POSSessionSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = POSSessionFilter
    search_fields = ["session_number", "terminal__code"]
    ordering_fields = ["opened_at", "closed_at", "session_number"]
    ordering = ["-opened_at"]
    http_method_names = ["get", "post", "head", "options"]

    # ── open session ────────────────────────────────────────────────

    @action(detail=False, methods=["post"], url_path="open_session")
    def open_session(self, request):
        ser = SessionOpenSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        terminal = ser.validated_data["terminal"]
        opening_cash = ser.validated_data["opening_cash_amount"]

        with transaction.atomic():
            session = POSSession(
                terminal=terminal,
                user=request.user,
                opening_cash_amount=opening_cash,
            )
            session.open_session()  # validates & generates session_number

        logger.info(
            "Session %s opened on %s by %s",
            session.session_number,
            terminal.code,
            request.user,
        )
        return Response(
            POSSessionSerializer(session).data,
            status=status.HTTP_201_CREATED,
        )

    # ── close session ───────────────────────────────────────────────

    @action(detail=True, methods=["post"], url_path="close_session")
    def close_session(self, request, pk=None):
        session = self.get_object()

        if session.status != SESSION_STATUS_OPEN:
            return Response(
                {"detail": f"Session is {session.status}, not open."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ser = SessionCloseSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        actual_cash = ser.validated_data["actual_cash_amount"]

        with transaction.atomic():
            session.close_session(actual_cash_amount=actual_cash)

        logger.info(
            "Session %s closed by %s",
            session.session_number,
            request.user,
        )
        return Response(POSSessionSerializer(session).data)

    # ── current session ─────────────────────────────────────────────

    @action(detail=False, methods=["get"], url_path="current")
    def current(self, request):
        terminal_id = request.query_params.get("terminal")
        qs = POSSession.objects.filter(status=SESSION_STATUS_OPEN)
        if terminal_id:
            qs = qs.filter(terminal_id=terminal_id)
        else:
            qs = qs.filter(user=request.user)

        session = qs.select_related("terminal", "user").first()
        if not session:
            return Response(
                {"detail": "No open session found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(POSSessionSerializer(session).data)

    # ── summary ─────────────────────────────────────────────────────

    @action(detail=True, methods=["get"], url_path="summary")
    def session_summary(self, request, pk=None):
        session = self.get_object()
        from apps.pos.cart.models import POSCart
        from apps.pos.constants import CART_STATUS_COMPLETED
        from apps.pos.payment.models import POSPayment

        completed_carts = POSCart.objects.filter(
            session=session, status=CART_STATUS_COMPLETED
        )
        payments = POSPayment.objects.filter(
            cart__session=session,
            status="completed",
        )
        method_breakdown = (
            payments.values("method")
            .annotate(total=Sum("amount"))
            .order_by("method")
        )

        data = POSSessionSerializer(session).data
        data["payment_method_breakdown"] = list(method_breakdown)
        data["completed_transaction_count"] = completed_carts.count()
        return Response(data)

    # ── my sessions ─────────────────────────────────────────────────

    @action(detail=False, methods=["get"], url_path="my_sessions")
    def my_sessions(self, request):
        qs = self.get_queryset().filter(user=request.user)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(
            POSSessionSerializer(qs, many=True).data
        )
