"""
ViewSets for bank reconciliation.

Provides CRUD operations and custom workflow actions for bank
accounts, reconciliations, matching rules, and statement import.
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounting.models import (
    BankAccount,
    MatchingRule,
    Reconciliation,
    StatementLine,
)
from apps.accounting.serializers.reconciliation import (
    BankAccountSerializer,
    MatchingRuleSerializer,
    ReconciliationDetailSerializer,
    ReconciliationListSerializer,
    StatementLineSerializer,
)
from apps.accounting.services.reconciliation_service import (
    ReconciliationError,
    ReconciliationService,
)


class BankAccountViewSet(viewsets.ModelViewSet):
    """CRUD for bank accounts."""

    serializer_class = BankAccountSerializer
    permission_classes = [IsAuthenticated]
    queryset = BankAccount.objects.all()
    filterset_fields = ["account_type", "is_active", "currency"]
    search_fields = ["account_name", "account_number", "bank_name"]
    ordering_fields = ["account_name", "bank_name"]
    ordering = ["account_name"]


class ReconciliationViewSet(viewsets.ModelViewSet):
    """CRUD + workflow actions for reconciliation sessions."""

    permission_classes = [IsAuthenticated]
    filterset_fields = ["bank_account", "status"]
    search_fields = ["bank_account__account_name", "bank_account__account_number"]
    ordering_fields = ["start_date", "end_date", "status"]
    ordering = ["-end_date"]

    def get_queryset(self):
        return (
            Reconciliation.objects.select_related("bank_account", "bank_statement")
            .prefetch_related("items", "adjustments")
            .all()
        )

    def get_serializer_class(self):
        if self.action == "list":
            return ReconciliationListSerializer
        return ReconciliationDetailSerializer

    # ── Custom workflow actions ────────────────────────────────────

    @action(detail=True, methods=["post"], url_path="start")
    def start_reconciliation(self, request, pk=None):
        """Start a new reconciliation from a bank account."""
        bank_account = BankAccount.objects.get(pk=pk)
        svc = ReconciliationService()
        statement_id = request.data.get("statement_id")
        statement = None
        if statement_id:
            from apps.accounting.models import BankStatement

            statement = BankStatement.objects.get(pk=statement_id)

        recon = svc.start_reconciliation(
            bank_account=bank_account,
            user=request.user,
            statement=statement,
        )
        serializer = ReconciliationDetailSerializer(recon)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="auto-match")
    def auto_match(self, request, pk=None):
        """Run automatic matching on a reconciliation."""
        recon = self.get_object()
        svc = ReconciliationService()
        try:
            stats = svc.run_auto_matching(recon)
            return Response(stats)
        except ReconciliationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="match")
    def match_items(self, request, pk=None):
        """Manually match a statement line to a journal entry."""
        recon = self.get_object()
        svc = ReconciliationService()
        statement_line_id = request.data.get("statement_line_id")
        journal_entry_id = request.data.get("journal_entry_id")
        notes = request.data.get("notes", "")

        from apps.accounting.models import JournalEntry

        try:
            line = StatementLine.objects.get(pk=statement_line_id)
            entry = JournalEntry.objects.get(pk=journal_entry_id)
            item = svc.match_transactions(
                recon, line, entry, request.user, notes=notes,
            )
            from apps.accounting.serializers.reconciliation import (
                ReconciliationItemSerializer,
            )

            return Response(
                ReconciliationItemSerializer(item).data,
                status=status.HTTP_201_CREATED,
            )
        except ReconciliationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="unmatch")
    def unmatch_items(self, request, pk=None):
        """Remove a match."""
        recon = self.get_object()
        item_id = request.data.get("item_id")
        svc = ReconciliationService()
        try:
            from apps.accounting.models import ReconciliationItem

            item = ReconciliationItem.objects.get(
                pk=item_id, reconciliation=recon,
            )
            svc.unmatch_transaction(item)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ReconciliationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="complete")
    def complete_reconciliation(self, request, pk=None):
        """Finalise reconciliation."""
        recon = self.get_object()
        svc = ReconciliationService()
        force = request.data.get("force", False)
        try:
            recon = svc.complete_reconciliation(recon, request.user, force_complete=force)
            serializer = ReconciliationDetailSerializer(recon)
            return Response(serializer.data)
        except ReconciliationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel_reconciliation(self, request, pk=None):
        """Cancel reconciliation."""
        recon = self.get_object()
        svc = ReconciliationService()
        try:
            recon = svc.cancel_reconciliation(recon, request.user)
            serializer = ReconciliationDetailSerializer(recon)
            return Response(serializer.data)
        except ReconciliationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="reopen")
    def reopen_reconciliation(self, request, pk=None):
        """Reopen a completed reconciliation."""
        recon = self.get_object()
        from apps.accounting.models.enums import ReconciliationStatus

        if recon.status != ReconciliationStatus.COMPLETED:
            return Response(
                {"error": "Only completed reconciliations can be reopened."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        recon.status = ReconciliationStatus.IN_PROGRESS
        recon.completed_at = None
        recon.completed_by = None
        recon.save(update_fields=["status", "completed_at", "completed_by", "updated_at"])
        serializer = ReconciliationDetailSerializer(recon)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="suggestions")
    def get_suggestions(self, request, pk=None):
        """Get match suggestions for a statement line."""
        recon = self.get_object()
        line_id = request.query_params.get("line_id")
        if not line_id:
            return Response(
                {"error": "line_id query parameter required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        from apps.accounting.services.matching_engine import MatchingEngine

        line = StatementLine.objects.get(pk=line_id)
        engine = MatchingEngine(recon.bank_account)
        suggestions = engine.suggest_matches(line)
        # Serialize suggestions (replace ORM objects with IDs)
        result = []
        for s in suggestions:
            entry = s.pop("journal_entry")
            s["journal_entry_id"] = str(entry.pk)
            s["journal_entry_number"] = entry.entry_number
            s["journal_entry_description"] = entry.description or ""
            result.append(s)
        return Response(result)

    @action(
        detail=True,
        methods=["post"],
        url_path="import",
        parser_classes=[MultiPartParser, FormParser],
    )
    def import_statement(self, request, pk=None):
        """Import a bank statement file (CSV/OFX)."""
        recon = self.get_object()
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response(
                {"error": "No file uploaded."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from apps.accounting.models import BankStatement
        from apps.accounting.services.importers.factory import StatementParserFactory

        fmt = request.data.get("format", "CSV").upper()
        try:
            parser = StatementParserFactory.get_parser(fmt)
            content = file_obj.read().decode("utf-8", errors="replace")
            result = parser.parse(content)

            if not result.success:
                return Response(
                    {"error": result.error, "warnings": result.warnings},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Create BankStatement
            stmt = BankStatement.objects.create(
                bank_account=recon.bank_account,
                statement_format=fmt,
                start_date=result.start_date,
                end_date=result.end_date,
                opening_balance=result.opening_balance or 0,
                closing_balance=result.closing_balance or 0,
                file=file_obj,
                import_status="IMPORTED",
                import_line_count=len(result.lines),
                imported_by=request.user,
            )

            # Create StatementLines
            for i, line in enumerate(result.lines, start=1):
                StatementLine.objects.create(
                    statement=stmt,
                    line_number=i,
                    transaction_date=line.date,
                    description=line.description,
                    reference=line.reference or "",
                    debit_amount=line.debit_amount,
                    credit_amount=line.credit_amount,
                    running_balance=line.balance,
                )

            # Link to reconciliation
            recon.bank_statement = stmt
            recon.start_date = result.start_date
            recon.end_date = result.end_date
            recon.statement_balance = result.closing_balance or 0
            recon.save(update_fields=[
                "bank_statement", "start_date", "end_date",
                "statement_balance", "updated_at",
            ])

            return Response({
                "imported_count": len(result.lines),
                "statement_id": str(stmt.pk),
                "start_date": str(result.start_date),
                "end_date": str(result.end_date),
                "opening_balance": str(result.opening_balance or 0),
                "closing_balance": str(result.closing_balance or 0),
                "warnings": result.warnings,
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["get"], url_path="summary")
    def summary(self, request, pk=None):
        """Get reconciliation summary report."""
        recon = self.get_object()
        svc = ReconciliationService()
        return Response(svc.get_reconciliation_summary(recon))

    @action(detail=True, methods=["get"], url_path="report")
    def report(self, request, pk=None):
        """Get full reconciliation report as JSON."""
        recon = self.get_object()
        from apps.accounting.services.reconciliation_report import (
            ReconciliationReportService,
        )

        svc = ReconciliationReportService(recon)
        return Response(svc.generate_report())


class MatchingRuleViewSet(viewsets.ModelViewSet):
    """CRUD for matching rules."""

    serializer_class = MatchingRuleSerializer
    permission_classes = [IsAuthenticated]
    queryset = MatchingRule.objects.all()
    filterset_fields = ["bank_account", "is_active", "match_reference"]
    search_fields = ["name"]
    ordering = ["priority", "name"]
