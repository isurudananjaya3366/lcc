"""Fixtures for accounting module tests."""

import pytest
from django.contrib.auth import get_user_model
from django.db import connection
from django_tenants.utils import get_tenant_domain_model, get_tenant_model

TenantModel = get_tenant_model()
DomainModel = get_tenant_domain_model()

SCHEMA_NAME = "test_accounting"
TENANT_DOMAIN = "accounting.testserver"


@pytest.fixture(scope="session")
def setup_test_tenant(django_db_setup, django_db_blocker):
    """Create a test tenant for accounting tests, reusing if it exists."""
    with django_db_blocker.unblock():
        # Check if tenant schema already exists (for --reuse-db)
        with connection.cursor() as cur:
            cur.execute(
                "SELECT nspname FROM pg_catalog.pg_namespace "
                "WHERE nspname = %s",
                [SCHEMA_NAME],
            )
            schema_exists = cur.fetchone() is not None

        if schema_exists:
            # Reuse existing tenant
            try:
                tenant = TenantModel.objects.get(schema_name=SCHEMA_NAME)
                connection.set_tenant(tenant)
                yield tenant
                connection.set_schema_to_public()
                return
            except TenantModel.DoesNotExist:
                # Schema exists but tenant record gone, clean up
                with connection.cursor() as cur:
                    cur.execute(
                        "DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA_NAME
                    )

        # Clean up any stale records
        with connection.cursor() as cur:
            cur.execute(
                "DELETE FROM %s WHERE tenant_id IN "
                "(SELECT id FROM %s WHERE schema_name = %%s)"
                % (DomainModel._meta.db_table, TenantModel._meta.db_table),
                [SCHEMA_NAME],
            )
            cur.execute(
                "DELETE FROM tenants_tenantsettings WHERE tenant_id IN "
                "(SELECT id FROM %s WHERE schema_name = %%s)"
                % TenantModel._meta.db_table,
                [SCHEMA_NAME],
            )
            cur.execute(
                "DELETE FROM %s WHERE schema_name = %%s"
                % TenantModel._meta.db_table,
                [SCHEMA_NAME],
            )

        tenant = TenantModel(
            schema_name=SCHEMA_NAME,
            name="Accounting Test Tenant",
            slug="test-accounting",
        )
        tenant.save(verbosity=0)

        domain = DomainModel(
            tenant=tenant,
            domain=TENANT_DOMAIN,
            is_primary=True,
        )
        domain.save()

        yield tenant

        # Don't destroy tenant schema when using --reuse-db
        connection.set_schema_to_public()


@pytest.fixture
def tenant_context(setup_test_tenant, db):
    """Activate tenant schema for a test."""
    connection.set_tenant(setup_test_tenant)
    yield setup_test_tenant
    connection.set_schema_to_public()


@pytest.fixture
def user(tenant_context):
    """Create a test user within tenant context."""
    User = get_user_model()
    return User.objects.create_user(
        email="accountingtest@example.com",
        password="testpass123",
    )


@pytest.fixture
def staff_user(tenant_context):
    """Create a staff user."""
    User = get_user_model()
    return User.objects.create_user(
        email="accstaff@example.com",
        password="testpass123",
        is_staff=True,
    )


@pytest.fixture
def account_type_config(tenant_context):
    """Create a basic AccountTypeConfig."""
    from apps.accounting.models import AccountTypeConfig

    return AccountTypeConfig.objects.create(
        type_name="ASSET",
        normal_balance="DEBIT",
        code_start=1000,
        code_end=1999,
        display_order=1,
        description="Asset accounts.",
    )


@pytest.fixture
def all_account_type_configs(tenant_context):
    """Create all five AccountTypeConfig records."""
    from apps.accounting.models import AccountTypeConfig

    configs = []
    data = [
        ("ASSET", "DEBIT", 1000, 1999, 1),
        ("LIABILITY", "CREDIT", 2000, 2999, 2),
        ("EQUITY", "CREDIT", 3000, 3999, 3),
        ("REVENUE", "CREDIT", 4000, 4999, 4),
        ("EXPENSE", "DEBIT", 5000, 5999, 5),
    ]
    for type_name, balance, start, end, order in data:
        configs.append(
            AccountTypeConfig.objects.create(
                type_name=type_name,
                normal_balance=balance,
                code_start=start,
                code_end=end,
                display_order=order,
            )
        )
    return configs


@pytest.fixture
def account(tenant_context):
    """Create a basic Account."""
    from apps.accounting.models import Account

    return Account.objects.create(
        code="1000",
        name="Cash on Hand",
        account_type="asset",
        description="Primary cash account.",
    )


# ════════════════════════════════════════════════════════════════════════
# Journal Entry Fixtures (SP09)
# ════════════════════════════════════════════════════════════════════════


@pytest.fixture
def debit_account(tenant_context):
    """Create a debit (expense) account for journal entry tests."""
    from apps.accounting.models import Account

    return Account.objects.create(
        code="5300",
        name="Rent Expense",
        account_type="expense",
        description="Office rent.",
    )


@pytest.fixture
def credit_account(tenant_context):
    """Create a credit (asset) account for journal entry tests."""
    from apps.accounting.models import Account

    return Account.objects.create(
        code="1100",
        name="Bank Account",
        account_type="asset",
        description="Main bank account.",
    )


@pytest.fixture
def journal_entry(tenant_context, debit_account, credit_account, user):
    """Create a balanced draft journal entry with two lines."""
    import datetime
    from decimal import Decimal

    from apps.accounting.models import JournalEntry, JournalEntryLine

    entry = JournalEntry.objects.create(
        entry_date=datetime.date(2026, 1, 15),
        description="Test journal entry",
        created_by=user,
    )
    JournalEntryLine.objects.create(
        journal_entry=entry,
        account=debit_account,
        debit_amount=Decimal("10000.00"),
        credit_amount=Decimal("0"),
        description="Debit line",
        sort_order=0,
    )
    JournalEntryLine.objects.create(
        journal_entry=entry,
        account=credit_account,
        debit_amount=Decimal("0"),
        credit_amount=Decimal("10000.00"),
        description="Credit line",
        sort_order=1,
    )
    # Update cached totals
    entry.total_debit = Decimal("10000.00")
    entry.total_credit = Decimal("10000.00")
    entry.save(update_fields=["total_debit", "total_credit"])
    return entry


@pytest.fixture
def second_user(tenant_context):
    """Create a second user for approval segregation tests."""
    User = get_user_model()
    return User.objects.create_user(
        email="approver@example.com",
        password="testpass123",
    )
