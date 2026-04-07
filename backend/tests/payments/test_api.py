"""Payment API tests."""

import pytest
from decimal import Decimal

from apps.payments.constants import PaymentMethod, PaymentStatus

pytestmark = pytest.mark.django_db


TENANT_DOMAIN = "payments.testserver"


class TestPaymentAPI:
    """Tests for Payment API endpoints."""

    def test_list_payments(self, api_client, user, payment):
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/v1/payments/")
        assert response.status_code == 200
        assert len(response.data["results"]) >= 1

    def test_retrieve_payment(self, api_client, user, payment):
        api_client.force_authenticate(user=user)
        response = api_client.get(f"/api/v1/payments/{payment.id}/")
        assert response.status_code == 200
        assert response.data["payment_number"] == payment.payment_number

    def test_create_payment(self, api_client, user, customer):
        api_client.force_authenticate(user=user)
        data = {
            "method": PaymentMethod.CASH,
            "amount": "5000.00",
            "customer_id": str(customer.id),
        }
        response = api_client.post("/api/v1/payments/", data=data, format="json")
        assert response.status_code == 201
        assert response.data["payment_number"].startswith("PAY-")

    def test_create_payment_unauthenticated(self, api_client, customer):
        data = {
            "method": PaymentMethod.CASH,
            "amount": "1000.00",
            "customer_id": str(customer.id),
        }
        response = api_client.post("/api/v1/payments/", data=data, format="json")
        assert response.status_code == 401

    def test_create_payment_invalid_amount(self, api_client, user, customer):
        api_client.force_authenticate(user=user)
        data = {
            "method": PaymentMethod.CASH,
            "amount": "-100.00",
            "customer_id": str(customer.id),
        }
        response = api_client.post("/api/v1/payments/", data=data, format="json")
        assert response.status_code == 400

    def test_complete_action(self, api_client, user, payment):
        api_client.force_authenticate(user=user)
        response = api_client.post(f"/api/v1/payments/{payment.id}/complete/")
        assert response.status_code == 200
        assert response.data["status"] == PaymentStatus.COMPLETED

    def test_cancel_action(self, api_client, user, payment):
        api_client.force_authenticate(user=user)
        response = api_client.post(
            f"/api/v1/payments/{payment.id}/cancel/",
            data={"reason": "Changed mind"},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["status"] == PaymentStatus.CANCELLED

    def test_filter_by_status(self, api_client, user, payment):
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/v1/payments/?status=PENDING")
        assert response.status_code == 200

    def test_filter_by_method(self, api_client, user, payment):
        api_client.force_authenticate(user=user)
        response = api_client.get(f"/api/v1/payments/?method={PaymentMethod.CASH}")
        assert response.status_code == 200

    def test_search_by_number(self, api_client, user, payment):
        api_client.force_authenticate(user=user)
        response = api_client.get(
            f"/api/v1/payments/?search={payment.payment_number}"
        )
        assert response.status_code == 200
        assert len(response.data["results"]) >= 1

    def test_soft_delete(self, api_client, user, payment):
        api_client.force_authenticate(user=user)
        response = api_client.delete(f"/api/v1/payments/{payment.id}/")
        assert response.status_code == 204


class TestRefundAPI:
    """Tests for Refund API endpoints."""

    def test_list_refunds(self, api_client, user):
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/v1/refunds/")
        assert response.status_code == 200

    def test_create_refund(self, api_client, user, completed_payment):
        api_client.force_authenticate(user=user)
        data = {
            "payment_id": str(completed_payment.id),
            "amount": "1000.00",
            "reason": "RETURN",
        }
        response = api_client.post("/api/v1/refunds/", data=data, format="json")
        assert response.status_code == 201
        assert response.data["status"] == "PENDING"

    def test_approve_refund(self, api_client, user, completed_payment):
        from apps.payments.services.refund_service import RefundService

        api_client.force_authenticate(user=user)
        refund = RefundService.request_refund(
            original_payment=completed_payment,
            amount=Decimal("500.00"),
            reason="OVERCHARGE",
            user=user,
        )
        response = api_client.post(f"/api/v1/refunds/{refund.id}/approve/", format="json")
        assert response.status_code == 200
        assert response.data["status"] == "APPROVED"

    def test_reject_refund(self, api_client, user, completed_payment):
        from apps.payments.services.refund_service import RefundService

        api_client.force_authenticate(user=user)
        refund = RefundService.request_refund(
            original_payment=completed_payment,
            amount=Decimal("500.00"),
            reason="OVERCHARGE",
            user=user,
        )
        response = api_client.post(
            f"/api/v1/refunds/{refund.id}/reject/",
            data={"notes": "Not eligible"},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["status"] == "REJECTED"

    def test_process_refund(self, api_client, user, completed_payment):
        from apps.payments.services.refund_service import RefundService

        api_client.force_authenticate(user=user)
        refund = RefundService.request_refund(
            original_payment=completed_payment,
            amount=Decimal("500.00"),
            reason="RETURN",
            user=user,
        )
        RefundService.approve_refund(refund, user=user)
        response = api_client.post(f"/api/v1/refunds/{refund.id}/process/", format="json")
        assert response.status_code == 200
        assert response.data["status"] == "PROCESSED"
