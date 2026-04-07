"""Credit & Loyalty test fixtures."""

import pytest
from decimal import Decimal

from django.db import connection
from django_tenants.utils import get_tenant_model, get_tenant_domain_model

TenantModel = get_tenant_model()
DomainModel = get_tenant_domain_model()

SCHEMA_NAME = "test_credit"
TENANT_DOMAIN = "credit.testserver"


@pytest.fixture(scope="session")
def setup_test_tenant(django_db_setup, django_db_blocker):
    """Create a test tenant schema once per session."""
    with django_db_blocker.unblock():
        if TenantModel.objects.filter(schema_name=SCHEMA_NAME).exists():
            t = TenantModel.objects.get(schema_name=SCHEMA_NAME)
            t.delete(force_drop=True)

        tenant = TenantModel(
            schema_name=SCHEMA_NAME,
            name="Credit Test Tenant",
            slug="credit-test",
        )
        tenant.save(verbosity=0)

        domain = DomainModel(
            tenant=tenant,
            domain=TENANT_DOMAIN,
            is_primary=True,
        )
        domain.save()

        yield tenant

        connection.set_schema_to_public()
        try:
            from django.db import connection as conn

            conn.set_schema_to_public()
            cursor = conn.cursor()
            cursor.execute(
                f'DROP SCHEMA IF EXISTS "{SCHEMA_NAME}" CASCADE'
            )
            cursor.execute(
                "DELETE FROM tenants_domain WHERE domain = %s",
                [TENANT_DOMAIN],
            )
            cursor.execute(
                "DELETE FROM tenants_tenant WHERE schema_name = %s",
                [SCHEMA_NAME],
            )
        except Exception:
            pass


@pytest.fixture
def tenant_context(setup_test_tenant, db):
    """Activate the test tenant schema for a test."""
    connection.set_tenant(setup_test_tenant)
    yield setup_test_tenant
    connection.set_schema_to_public()


@pytest.fixture
def user(tenant_context):
    """Create and return a regular user within the tenant schema."""
    from django.contrib.auth import get_user_model

    User = get_user_model()
    return User.objects.create_user(
        email="credituser@example.com",
        password="testpass123",
    )


@pytest.fixture
def staff_user(tenant_context):
    """Create and return a staff user within the tenant schema."""
    from django.contrib.auth import get_user_model

    User = get_user_model()
    return User.objects.create_user(
        email="creditstaff@example.com",
        password="staffpass123",
        is_staff=True,
    )


@pytest.fixture
def admin_user(tenant_context):
    """Create and return a superuser within the tenant schema."""
    from django.contrib.auth import get_user_model

    User = get_user_model()
    return User.objects.create_superuser(
        email="creditadmin@example.com",
        password="adminpass123",
    )


@pytest.fixture
def customer(tenant_context):
    """Create and return a test customer."""
    from apps.customers.models import Customer

    return Customer.objects.create(
        first_name="Test",
        last_name="Customer",
        business_name="Test Credit Customer Pvt Ltd",
        email="creditcustomer@example.com",
        phone="+94771234567",
    )


@pytest.fixture
def second_customer(tenant_context):
    """Create and return a second test customer."""
    from apps.customers.models import Customer

    return Customer.objects.create(
        first_name="Second",
        last_name="Customer",
        business_name="Second Customer Pvt Ltd",
        email="second@example.com",
        phone="+94771234568",
    )


@pytest.fixture
def credit_account(customer, staff_user):
    """Create a CustomerCredit account."""
    from apps.credit.models import CustomerCredit

    return CustomerCredit.objects.create(
        customer=customer,
        status="active",
        credit_limit=Decimal("100000.00"),
        available_credit=Decimal("100000.00"),
        outstanding_balance=Decimal("0.00"),
        payment_terms_days=30,
        interest_rate_annual=Decimal("12.00"),
        approved_by=staff_user,
    )


@pytest.fixture
def loyalty_program(tenant_context):
    """Create a LoyaltyProgram."""
    from apps.credit.models import LoyaltyProgram

    return LoyaltyProgram.objects.create(
        tenant_id=tenant_context.id,
        name="Test Rewards Program",
        description="Test loyalty program",
        points_per_currency=Decimal("1.00"),
        min_purchase_for_points=Decimal("100.00"),
        points_expiry_months=12,
        min_points_for_redemption=100,
        redemption_value_per_point=Decimal("0.50"),
        is_active=True,
    )


@pytest.fixture
def loyalty_tier(loyalty_program):
    """Create a base LoyaltyTier."""
    from apps.credit.models import LoyaltyTier

    return LoyaltyTier.objects.create(
        program=loyalty_program,
        name="Silver",
        level=1,
        min_points_required=0,
        min_spend_required=Decimal("0.00"),
        points_multiplier=Decimal("1.00"),
        discount_percentage=Decimal("5.00"),
        free_shipping=False,
        is_default=True,
    )


@pytest.fixture
def gold_tier(loyalty_program):
    """Create a gold-level LoyaltyTier."""
    from apps.credit.models import LoyaltyTier

    return LoyaltyTier.objects.create(
        program=loyalty_program,
        name="Gold",
        level=2,
        min_points_required=1000,
        min_spend_required=Decimal("50000.00"),
        points_multiplier=Decimal("1.50"),
        discount_percentage=Decimal("10.00"),
        free_shipping=True,
    )


@pytest.fixture
def customer_loyalty(customer, loyalty_program, loyalty_tier):
    """Create a CustomerLoyalty account."""
    from apps.credit.models import CustomerLoyalty

    return CustomerLoyalty.objects.create(
        customer=customer,
        program=loyalty_program,
        status="active",
        points_balance=500,
        lifetime_points_earned=500,
        current_tier=loyalty_tier,
    )


@pytest.fixture
def store_credit(customer, staff_user):
    """Create a StoreCredit account."""
    from apps.credit.models import StoreCredit

    return StoreCredit.objects.create(
        customer=customer,
        balance=Decimal("5000.00"),
        total_issued=Decimal("5000.00"),
        total_used=Decimal("0.00"),
        original_amount=Decimal("5000.00"),
        currency="LKR",
        created_from="gift",
        issued_by=staff_user,
        notes="Test store credit",
    )
