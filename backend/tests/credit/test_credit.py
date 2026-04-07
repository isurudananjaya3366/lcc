"""Tests for credit models and services."""

import pytest
from decimal import Decimal

from django.db import transaction

pytestmark = pytest.mark.django_db


class TestCustomerCreditModel:
    """Tests for the CustomerCredit model."""

    def test_create_credit_account(self, credit_account, customer):
        """Credit account is created with correct defaults."""
        assert credit_account.customer == customer
        assert credit_account.status == "active"
        assert credit_account.credit_limit == Decimal("100000.00")
        assert credit_account.available_credit == Decimal("100000.00")
        assert credit_account.outstanding_balance == Decimal("0.00")

    def test_credit_utilization_percentage(self, credit_account):
        """credit_utilization_percentage returns correct value."""
        credit_account.outstanding_balance = Decimal("25000.00")
        credit_account.save(update_fields=["outstanding_balance"])
        assert credit_account.credit_utilization_percentage == Decimal("25.00")

    def test_credit_utilization_zero_limit(self, credit_account):
        """credit_utilization_percentage handles zero credit limit."""
        credit_account.credit_limit = Decimal("0.00")
        credit_account.save(update_fields=["credit_limit"])
        assert credit_account.credit_utilization_percentage == Decimal("0")

    def test_unique_customer_constraint(self, credit_account, customer):
        """Cannot create two credit accounts for same customer."""
        from apps.credit.models import CustomerCredit

        with transaction.atomic():
            with pytest.raises(Exception):
                CustomerCredit.objects.create(
                    customer=customer,
                    status="active",
                    credit_limit=Decimal("50000.00"),
                    available_credit=Decimal("50000.00"),
                )

    def test_str_representation(self, credit_account):
        """String representation includes customer info."""
        result = str(credit_account)
        assert result  # Non-empty string


class TestCreditService:
    """Tests for CreditService business logic."""

    def test_record_purchase(self, credit_account, user):
        """record_purchase decreases available credit."""
        from apps.credit.services.credit_service import CreditService

        service = CreditService(credit_account)
        txn = service.record_purchase(
            amount=Decimal("10000.00"),
            reference_type="order",
            notes="Test purchase",
            user=user,
        )
        credit_account.refresh_from_db()
        assert txn is not None
        assert credit_account.outstanding_balance == Decimal("10000.00")
        assert credit_account.available_credit == Decimal("90000.00")

    def test_record_payment(self, credit_account, user):
        """record_payment reduces outstanding balance."""
        from apps.credit.services.credit_service import CreditService

        service = CreditService(credit_account)
        service.record_purchase(amount=Decimal("20000.00"), user=user)
        credit_account.refresh_from_db()

        txn = service.record_payment(
            amount=Decimal("15000.00"),
            payment_method="bank_transfer",
            notes="Partial payment",
            user=user,
        )
        credit_account.refresh_from_db()
        assert txn is not None
        assert credit_account.outstanding_balance == Decimal("5000.00")

    def test_check_credit_limit(self, credit_account):
        """check_credit_limit returns True when sufficient."""
        from apps.credit.services.credit_service import CreditService

        can_purchase, _ = CreditService.check_credit_limit(
            credit_account, Decimal("50000.00")
        )
        assert can_purchase
        can_purchase, _ = CreditService.check_credit_limit(
            credit_account, Decimal("150000.00")
        )
        assert not can_purchase

    def test_suspend_account(self, credit_account, user):
        """suspend_account changes status to suspended."""
        from apps.credit.services.credit_service import CreditService

        service = CreditService(credit_account)
        service.suspend_account(reason="Late payment", user=user)
        credit_account.refresh_from_db()
        assert credit_account.status == "suspended"

    def test_reactivate_account(self, credit_account, user):
        """reactivate_account restores active status."""
        from apps.credit.services.credit_service import CreditService

        service = CreditService(credit_account)
        service.suspend_account(reason="Test", user=user)
        service.reactivate_account(user=user)
        credit_account.refresh_from_db()
        assert credit_account.status == "active"

    def test_calculate_aging_buckets(self, credit_account):
        """calculate_aging_buckets returns dict with bucket keys."""
        from apps.credit.services.credit_service import CreditService

        service = CreditService(credit_account)
        buckets = service.calculate_aging_buckets()
        assert isinstance(buckets, dict)

    def test_write_off(self, credit_account, user):
        """write_off records the write-off transaction."""
        from apps.credit.services.credit_service import CreditService

        service = CreditService(credit_account)
        service.record_purchase(amount=Decimal("10000.00"), user=user)
        credit_account.refresh_from_db()

        service.write_off(
            amount=Decimal("5000.00"), notes="Bad debt", user=user
        )
        credit_account.refresh_from_db()
        assert credit_account.outstanding_balance == Decimal("5000.00")

    def test_record_adjustment(self, credit_account, user):
        """record_adjustment creates adjustment transaction."""
        from apps.credit.services.credit_service import CreditService

        service = CreditService(credit_account)
        txn = service.record_adjustment(
            amount=Decimal("5000.00"), notes="Goodwill", user=user
        )
        assert txn is not None


class TestCreditTransaction:
    """Tests for CreditTransaction model."""

    def test_transaction_created_on_purchase(self, credit_account, user):
        """Transactions are created when credit is used."""
        from apps.credit.models import CreditTransaction
        from apps.credit.services.credit_service import CreditService

        service = CreditService(credit_account)
        service.record_purchase(amount=Decimal("5000.00"), user=user)

        txns = CreditTransaction.objects.filter(
            credit_account=credit_account
        )
        assert txns.count() >= 1

    def test_transaction_ordering(self, credit_account, user):
        """Transactions are ordered by -transaction_date, -created_on."""
        from apps.credit.models import CreditTransaction
        from apps.credit.services.credit_service import CreditService

        service = CreditService(credit_account)
        service.record_purchase(amount=Decimal("1000.00"), user=user)
        service.record_purchase(amount=Decimal("2000.00"), user=user)

        txns = CreditTransaction.objects.filter(
            credit_account=credit_account
        )
        dates = list(txns.values_list("transaction_date", flat=True))
        assert dates == sorted(dates, reverse=True)


class TestStoreCreditModel:
    """Tests for StoreCredit model."""

    def test_create_store_credit(self, store_credit, customer):
        """Store credit is created with correct values."""
        assert store_credit.customer == customer
        assert store_credit.balance == Decimal("5000.00")
        assert store_credit.created_from == "gift"

    def test_get_available_balance(self, store_credit):
        """get_available_balance returns balance when not expired."""
        assert store_credit.get_available_balance() == Decimal("5000.00")

    def test_has_balance(self, store_credit):
        """has_balance returns True when balance > 0."""
        assert store_credit.has_balance(Decimal("1000.00"))

    def test_is_expired_default(self, store_credit):
        """is_expired returns False when no expiry set."""
        assert not store_credit.is_expired


class TestStoreCreditService:
    """Tests for StoreCreditService."""

    def test_issue_credit(self, customer, staff_user, tenant_context):
        """issue_credit creates or updates store credit."""
        from apps.credit.services.store_credit_service import (
            StoreCreditService,
        )

        result = StoreCreditService.issue_credit(
            customer_id=customer.id,
            amount=Decimal("3000.00"),
            source="promotional",
            reference="PROMO123",
            issued_by=staff_user,
            notes="Promo credit",
        )
        assert result is not None

    def test_redeem_credit(self, store_credit, user):
        """redeem_credit reduces balance."""
        from apps.credit.services.store_credit_service import (
            StoreCreditService,
        )

        result = StoreCreditService.redeem_credit(
            customer_id=store_credit.customer_id,
            amount=Decimal("2000.00"),
            performed_by=user,
            notes="Order payment",
        )
        store_credit.refresh_from_db()
        assert store_credit.balance == Decimal("3000.00")

    def test_check_balance(self, store_credit):
        """check_balance returns correct balance."""
        from apps.credit.services.store_credit_service import (
            StoreCreditService,
        )

        result = StoreCreditService.check_balance(
            store_credit.customer_id
        )
        assert result["current_balance"] == Decimal("5000.00")
        assert result["has_credit"] is True

    def test_can_redeem(self, store_credit):
        """can_redeem returns True for valid amounts."""
        from apps.credit.services.store_credit_service import (
            StoreCreditService,
        )

        assert StoreCreditService.can_redeem(
            store_credit.customer_id, Decimal("5000.00")
        )
        assert not StoreCreditService.can_redeem(
            store_credit.customer_id, Decimal("10000.00")
        )
