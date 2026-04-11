"""
Django admin configuration for the accounting application.

Provides admin interfaces for Account (tree view via MPTT),
AccountTypeConfig, COATemplate, JournalEntry (with inline lines),
AccountingPeriod, JournalEntryTemplate, and RecurringEntry.
"""

from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from apps.accounting.models import (
    Account,
    AccountingPeriod,
    AccountTypeConfig,
    COATemplate,
    JournalEntry,
    JournalEntryLine,
    JournalEntryTemplate,
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
