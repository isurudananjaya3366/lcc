"""Tests for Group E — Admin config and DRF serializers."""

from decimal import Decimal

import pytest
from rest_framework.exceptions import ValidationError as DRFValidationError

from apps.accounting.models import Account, AccountTypeConfig, COATemplate, IndustryType
from apps.accounting.serializers import (
    AccountChildrenSerializer,
    AccountSerializer,
    AccountTreeSerializer,
    AccountTypeConfigSerializer,
    COATemplateSerializer,
)


# ═══════════════════════════════════════════════════════════════════
# Admin registration (smoke test)
# ═══════════════════════════════════════════════════════════════════
class TestAdminRegistration:
    def test_account_admin_registered(self):
        from django.contrib import admin

        assert admin.site.is_registered(Account)

    def test_account_type_config_admin_registered(self):
        from django.contrib import admin

        assert admin.site.is_registered(AccountTypeConfig)

    def test_coa_template_admin_registered(self):
        from django.contrib import admin

        assert admin.site.is_registered(COATemplate)


# ═══════════════════════════════════════════════════════════════════
# AccountSerializer
# ═══════════════════════════════════════════════════════════════════
@pytest.mark.django_db
class TestAccountSerializer:
    def test_serialize_account(self, tenant_context):
        acc = Account.objects.create(
            code="1100",
            name="Cash",
            account_type="asset",
        )
        data = AccountSerializer(acc).data
        assert data["code"] == "1100"
        assert data["name"] == "Cash"
        assert data["account_type"] == "asset"
        assert "children_count" in data
        assert data["children_count"] == 0

    def test_read_only_fields(self, tenant_context):
        acc = Account.objects.create(
            code="1101",
            name="Cash on Hand",
            account_type="asset",
        )
        data = AccountSerializer(acc).data
        assert "current_balance" in data
        assert "level" in data

    def test_validate_code_format(self, tenant_context):
        serializer = AccountSerializer(data={
            "code": "AB",
            "name": "Bad",
            "account_type": "asset",
        })
        assert serializer.is_valid() is False

    def test_validate_code_range(self, tenant_context):
        serializer = AccountSerializer(data={
            "code": "5000",
            "name": "Wrong Range",
            "account_type": "asset",
        })
        assert serializer.is_valid() is False

    def test_validate_code_unique(self, tenant_context):
        Account.objects.create(
            code="1200",
            name="AR",
            account_type="asset",
        )
        serializer = AccountSerializer(data={
            "code": "1200",
            "name": "Duplicate",
            "account_type": "asset",
        })
        assert serializer.is_valid() is False

    def test_create_valid(self, tenant_context):
        serializer = AccountSerializer(data={
            "code": "1300",
            "name": "Inventory",
            "account_type": "asset",
        })
        assert serializer.is_valid(), serializer.errors
        acc = serializer.save()
        assert acc.pk is not None

    def test_update_system_blocks_code(self, tenant_context):
        acc = Account.objects.create(
            code="1400",
            name="System Acc",
            account_type="asset",
            is_system=True,
        )
        serializer = AccountSerializer(acc, data={"code": "1401"}, partial=True)
        # Validation should pass (code format/range ok, unique ok)
        # but update should block because is_system
        if serializer.is_valid():
            with pytest.raises(DRFValidationError):
                serializer.save()


# ═══════════════════════════════════════════════════════════════════
# AccountChildrenSerializer
# ═══════════════════════════════════════════════════════════════════
@pytest.mark.django_db
class TestAccountChildrenSerializer:
    def test_includes_children(self, tenant_context):
        parent = Account.objects.create(
            code="1100",
            name="Cash",
            account_type="asset",
            is_header=True,
        )
        Account.objects.create(
            code="1101",
            name="Cash on Hand",
            account_type="asset",
            parent=parent,
        )
        Account.objects.rebuild()
        data = AccountChildrenSerializer(parent).data
        assert len(data["children"]) == 1
        assert data["children"][0]["code"] == "1101"


# ═══════════════════════════════════════════════════════════════════
# AccountTreeSerializer
# ═══════════════════════════════════════════════════════════════════
@pytest.mark.django_db
class TestAccountTreeSerializer:
    def test_recursive_tree(self, tenant_context):
        root = Account.objects.create(
            code="1000",
            name="Assets",
            account_type="asset",
            is_header=True,
        )
        child = Account.objects.create(
            code="1100",
            name="Cash",
            account_type="asset",
            is_header=True,
            parent=root,
        )
        Account.objects.create(
            code="1101",
            name="Cash on Hand",
            account_type="asset",
            parent=child,
        )
        Account.objects.rebuild()
        data = AccountTreeSerializer(root).data
        assert data["code"] == "1000"
        assert len(data["children"]) == 1
        assert data["children"][0]["code"] == "1100"
        assert len(data["children"][0]["children"]) == 1


# ═══════════════════════════════════════════════════════════════════
# AccountTypeConfigSerializer
# ═══════════════════════════════════════════════════════════════════
@pytest.mark.django_db
class TestAccountTypeConfigSerializer:
    def test_serialize(self, account_type_config):
        data = AccountTypeConfigSerializer(account_type_config).data
        assert data["type_name"] == "ASSET"
        assert data["code_range_display"] == "1000-1999"

    def test_all_fields_present(self, account_type_config):
        data = AccountTypeConfigSerializer(account_type_config).data
        expected = {
            "id", "type_name", "normal_balance", "code_start",
            "code_end", "display_order", "description",
            "code_range_display",
        }
        assert expected.issubset(set(data.keys()))


# ═══════════════════════════════════════════════════════════════════
# COATemplateSerializer
# ═══════════════════════════════════════════════════════════════════
@pytest.mark.django_db
class TestCOATemplateSerializer:
    def test_serialize(self, tenant_context):
        tpl = COATemplate.objects.create(
            template_name="Retail",
            industry=IndustryType.RETAIL,
            template_accounts=[{"code": "1000"}],
        )
        data = COATemplateSerializer(tpl).data
        assert data["template_name"] == "Retail"
        assert data["account_count"] == 1

    def test_create_via_serializer(self, tenant_context):
        serializer = COATemplateSerializer(data={
            "template_name": "New Template",
            "industry": "SERVICE",
            "template_accounts": [],
        })
        assert serializer.is_valid(), serializer.errors
        tpl = serializer.save()
        assert tpl.pk is not None
