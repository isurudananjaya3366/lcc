"""
Django admin configuration for the accounting application.

Provides admin interfaces for Account (tree view via MPTT),
AccountTypeConfig, COATemplate, JournalEntry (with inline lines),
AccountingPeriod, JournalEntryTemplate, and RecurringEntry.
"""

from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from mptt.admin import MPTTModelAdmin

from apps.accounting.models import (
    Account,
    AccountingPeriod,
    AccountTypeConfig,
    BankAccount,
    BankStatement,
    COATemplate,
    JournalEntry,
    JournalEntryLine,
    JournalEntryTemplate,
    MatchingRule,
    Reconciliation,
    ReconciliationAdjustment,
    ReconciliationItem,
    RecurringEntry,
)
from apps.accounting.services.approval_service import ApprovalService
from apps.accounting.services.journal_service import JournalEntryService


@admin.register(Account)
class AccountAdmin(MPTTModelAdmin):
    """Admin with MPTT tree display for the chart of accounts."""

    list_display = (
        "code",
        "name",
        "account_type",
        "category",
        "is_header",
        "is_system",
        "current_balance",
        "status",
        "is_active",
    )
    list_filter = (
        "account_type",
        "category",
        "status",
        "is_header",
        "is_system",
        "is_active",
    )
    search_fields = ("code", "name")
    list_per_page = 100
    mptt_level_indent = 20
    readonly_fields = ("current_balance", "tree_id", "lft", "rght", "level")

    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_system:
            return False
        return super().has_delete_permission(request, obj)

    def get_readonly_fields(self, request, obj=None):
        ro = list(super().get_readonly_fields(request, obj))
        if obj and obj.is_system:
            ro.extend(["code", "account_type"])
        return ro


@admin.register(AccountTypeConfig)
class AccountTypeConfigAdmin(admin.ModelAdmin):
    list_display = (
        "type_name",
        "normal_balance",
        "code_start",
        "code_end",
        "display_order",
    )
    ordering = ("display_order",)


@admin.register(COATemplate)
class COATemplateAdmin(admin.ModelAdmin):
    list_display = (
        "template_name",
        "industry",
        "is_active",
        "account_count",
    )
    list_filter = ("industry", "is_active")
    search_fields = ("template_name",)

    @admin.display(description="Accounts")
    def account_count(self, obj):
        return obj.account_count


# ════════════════════════════════════════════════════════════════════════
# Journal Entry Admin (SP09)
# ════════════════════════════════════════════════════════════════════════


class JournalEntryLineInline(admin.TabularInline):
    model = JournalEntryLine
    extra = 2
    fields = ("account", "debit_amount", "credit_amount", "description", "sort_order")
    readonly_fields = ()

    def has_add_permission(self, request, obj=None):
        if obj and not obj.is_editable:
            return False
        return super().has_add_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if obj and not obj.is_editable:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and not obj.is_editable:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = (
        "entry_number",
        "entry_date",
        "entry_type",
        "entry_status",
        "entry_source",
        "total_debit",
        "total_credit",
        "is_balanced",
        "created_by",
    )
    list_filter = ("entry_status", "entry_type", "entry_source", "entry_date")
    search_fields = ("entry_number", "reference", "description")
    date_hierarchy = "entry_date"
    readonly_fields = (
        "entry_number",
        "total_debit",
        "total_credit",
        "posted_by",
        "posted_at",
        "created_at",
        "updated_at",
    )
    inlines = [JournalEntryLineInline]
    list_per_page = 50
    actions = ["post_selected", "approve_selected"]

    @admin.display(boolean=True, description="Balanced")
    def is_balanced(self, obj):
        return obj.is_balanced

    @admin.action(description="Post selected entries")
    def post_selected(self, request, queryset):
        posted = 0
        for entry in queryset:
            try:
                JournalEntryService.post_entry(entry, posted_by=request.user)
                posted += 1
            except Exception:
                pass
        self.message_user(request, f"{posted} entries posted.")

    @admin.action(description="Approve selected entries")
    def approve_selected(self, request, queryset):
        service = ApprovalService()
        approved = 0
        for entry in queryset:
            try:
                service.approve_entry(entry, approved_by=request.user)
                approved += 1
            except Exception:
                pass
        self.message_user(request, f"{approved} entries approved.")


@admin.register(AccountingPeriod)
class AccountingPeriodAdmin(admin.ModelAdmin):
    list_display = ("__str__", "start_date", "end_date", "status", "fiscal_year", "period_number")
    list_filter = ("status", "fiscal_year")
    ordering = ("-start_date",)


@admin.register(JournalEntryTemplate)
class JournalEntryTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "is_active", "created_at")
    list_filter = ("category", "is_active")
    search_fields = ("name",)


@admin.register(RecurringEntry)
class RecurringEntryAdmin(admin.ModelAdmin):
    list_display = ("template", "frequency", "is_active", "next_run_date", "last_run_date")
    list_filter = ("frequency", "is_active")
    ordering = ("next_run_date",)


# ════════════════════════════════════════════════════════════════════════
# Account Reconciliation Admin (SP10)
# ════════════════════════════════════════════════════════════════════════


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = (
        "account_name",
        "account_number",
        "bank_name",
        "account_type",
        "currency",
        "is_active",
        "last_reconciled_date",
    )
    list_filter = ("account_type", "currency", "is_active")
    search_fields = ("account_name", "account_number", "bank_name", "branch_name")
    readonly_fields = ("last_reconciled_date", "last_reconciled_balance")


@admin.register(BankStatement)
class BankStatementAdmin(admin.ModelAdmin):
    list_display = (
        "bank_account",
        "statement_format",
        "start_date",
        "end_date",
        "import_status",
        "import_line_count",
        "is_reconciled",
    )
    list_filter = ("statement_format", "import_status", "is_reconciled")
    search_fields = ("bank_account__account_name",)
    readonly_fields = ("imported_at", "imported_by")


@admin.register(MatchingRule)
class MatchingRuleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "bank_account",
        "priority",
        "amount_tolerance",
        "date_range_days",
        "match_reference",
        "is_active",
    )
    list_filter = ("is_active", "match_reference", "bank_account")
    search_fields = ("name",)
    ordering = ("priority", "name")


class ReconciliationItemInline(admin.TabularInline):
    model = ReconciliationItem
    extra = 0
    readonly_fields = ("statement_line", "journal_entry", "match_type", "matched_at", "matched_by")
    can_delete = False


class ReconciliationAdjustmentInline(admin.TabularInline):
    model = ReconciliationAdjustment
    extra = 0
    readonly_fields = ("journal_entry", "adjustment_type", "adjustment_amount", "created_by", "created_at")
    can_delete = False


@admin.register(Reconciliation)
class ReconciliationAdmin(admin.ModelAdmin):
    list_display = (
        "bank_account",
        "start_date",
        "end_date",
        "status",
        "statement_balance",
        "book_balance",
        "difference",
        "completed_by",
        "completed_at",
    )
    list_filter = ("status", "bank_account")
    search_fields = ("bank_account__account_name", "bank_account__account_number")
    readonly_fields = (
        "difference",
        "completed_at",
        "completed_by",
        "created_at",
        "updated_at",
    )
    inlines = [ReconciliationItemInline, ReconciliationAdjustmentInline]
    actions = ["mark_as_completed", "reopen_reconciliation"]

    @admin.display(description="Difference", ordering="difference")
    def difference_display(self, obj):
        if obj.difference == 0:
            return format_html('<span style="color: green;">0.00</span>')
        return format_html(
            '<span style="color: red;">{}</span>', obj.difference
        )

    @admin.action(description="Mark selected as completed")
    def mark_as_completed(self, request, queryset):
        from apps.accounting.models.enums import ReconciliationStatus

        updated = queryset.filter(
            status=ReconciliationStatus.IN_PROGRESS,
        ).update(
            status=ReconciliationStatus.COMPLETED,
            completed_at=timezone.now(),
            completed_by=request.user,
        )
        self.message_user(request, f"{updated} reconciliation(s) marked as completed.")

    @admin.action(description="Reopen selected reconciliations")
    def reopen_reconciliation(self, request, queryset):
        from apps.accounting.models.enums import ReconciliationStatus

        updated = queryset.filter(
            status=ReconciliationStatus.COMPLETED,
        ).update(
            status=ReconciliationStatus.IN_PROGRESS,
            completed_at=None,
            completed_by=None,
        )
        self.message_user(request, f"{updated} reconciliation(s) reopened.")


# ──────────────────────────────────────────────────────────────────
# Tax Reporting Admin
# ──────────────────────────────────────────────────────────────────

from apps.accounting.models import (
    EPFReturn,
    ETFReturn,
    PAYEReturn,
    TaxConfiguration,
    TaxPeriodRecord,
    TaxSubmission,
    VATReturn,
)


@admin.register(TaxConfiguration)
class TaxConfigurationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "vat_registration_no",
        "is_svat_registered",
        "epf_registration_no",
        "etf_registration_no",
        "is_active",
    )
    list_filter = ("is_active", "is_svat_registered")
    fieldsets = (
        ("VAT", {"fields": ("vat_registration_no", "is_svat_registered", "vat_filing_period")}),
        ("EPF / ETF", {"fields": ("epf_registration_no", "etf_registration_no")}),
        ("TIN", {"fields": ("tin_number",)}),
        ("Status", {"fields": ("is_active",)}),
    )


@admin.register(TaxPeriodRecord)
class TaxPeriodRecordAdmin(admin.ModelAdmin):
    list_display = (
        "tax_type",
        "year",
        "period_number",
        "start_date",
        "end_date",
        "due_date",
        "filing_status",
    )
    list_filter = ("tax_type", "filing_status", "year")
    search_fields = ("tax_type",)
    ordering = ("-year", "-period_number")


@admin.register(VATReturn)
class VATReturnAdmin(admin.ModelAdmin):
    list_display = (
        "reference_number",
        "output_vat",
        "input_vat",
        "net_vat_payable",
        "status",
        "created_at",
    )
    list_filter = ("status",)
    search_fields = ("reference_number",)
    readonly_fields = (
        "reference_number",
        "output_vat",
        "input_vat",
        "net_vat_payable",
        "line_items",
    )


@admin.register(PAYEReturn)
class PAYEReturnAdmin(admin.ModelAdmin):
    list_display = (
        "reference_number",
        "total_employees",
        "total_remuneration",
        "total_paye_deducted",
        "status",
        "created_at",
    )
    list_filter = ("status",)
    search_fields = ("reference_number",)
    readonly_fields = (
        "reference_number",
        "total_remuneration",
        "total_paye_deducted",
        "employee_details",
    )


@admin.register(EPFReturn)
class EPFReturnAdmin(admin.ModelAdmin):
    list_display = (
        "reference_number",
        "total_employees",
        "total_employee_contribution",
        "total_employer_contribution",
        "total_contribution",
        "status",
    )
    list_filter = ("status",)
    search_fields = ("reference_number",)
    readonly_fields = (
        "reference_number",
        "total_contribution",
        "employee_schedule",
    )


@admin.register(ETFReturn)
class ETFReturnAdmin(admin.ModelAdmin):
    list_display = (
        "reference_number",
        "total_employees",
        "total_contribution",
        "total_gross_salary",
        "status",
    )
    list_filter = ("status",)
    search_fields = ("reference_number",)
    readonly_fields = ("reference_number", "employee_schedule")


@admin.register(TaxSubmission)
class TaxSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "tax_period",
        "submission_reference",
        "submitted_at",
        "submitted_by",
        "status",
    )
    list_filter = ("status",)
    search_fields = ("submission_reference",)
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("tax_period", "submitted_by")
