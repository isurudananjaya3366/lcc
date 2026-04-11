"""
Django admin configuration for the accounting application.

Provides admin interfaces for Account (tree view via MPTT),
AccountTypeConfig, and COATemplate models.
"""

from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from apps.accounting.models import Account, AccountTypeConfig, COATemplate


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
