"""
Order API endpoint tests (Task 91).
"""

import pytest
from decimal import Decimal

from rest_framework import status as http_status
from rest_framework.test import APIClient

from apps.orders.constants import OrderStatus

pytestmark = pytest.mark.django_db

TENANT_HOST = "orders.testserver"


@pytest.fixture
def api_client(setup_test_tenant):
    """APIClient that sends requests to the tenant domain."""
    return APIClient(SERVER_NAME=TENANT_HOST)


class TestOrderAPI:
    """Tests for the Order ViewSet API endpoints."""

    def test_list_orders(self, api_client, user, create_order):
        create_order()
        create_order()
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/v1/orders/")
        assert response.status_code == http_status.HTTP_200_OK
        assert len(response.data["results"]) >= 2

    def test_retrieve_order(self, api_client, user, create_order):
        order = create_order()
        api_client.force_authenticate(user=user)
        response = api_client.get(f"/api/v1/orders/{order.pk}/")
        assert response.status_code == http_status.HTTP_200_OK
        assert response.data["order_number"] == order.order_number

    def test_create_order_via_api(self, api_client, user):
        api_client.force_authenticate(user=user)
        data = {
            "customer_name": "API Customer",
            "customer_email": "api@example.com",
            "source": "manual",
            "currency": "LKR",
        }
        response = api_client.post("/api/v1/orders/", data, format="json")
        assert response.status_code in (
            http_status.HTTP_201_CREATED,
            http_status.HTTP_200_OK,
        ), f"Expected 201/200 but got {response.status_code}: {response.content[:2000]}"

    def test_delete_draft_order(self, api_client, user, create_order):
        order = create_order(is_draft=True)
        api_client.force_authenticate(user=user)
        response = api_client.delete(f"/api/v1/orders/{order.pk}/")
        assert response.status_code == http_status.HTTP_204_NO_CONTENT

    def test_delete_non_draft_order_forbidden(self, api_client, user, create_order):
        order = create_order(is_draft=False)
        api_client.force_authenticate(user=user)
        response = api_client.delete(f"/api/v1/orders/{order.pk}/")
        assert response.status_code == http_status.HTTP_403_FORBIDDEN

    def test_confirm_order_action(self, api_client, user, create_order):
        order = create_order(status=OrderStatus.PENDING)
        api_client.force_authenticate(user=user)
        response = api_client.post(
            f"/api/v1/orders/{order.pk}/confirm/", {}, format="json"
        )
        assert response.status_code == http_status.HTTP_200_OK
        assert response.data["status"] == "confirmed"

    def test_cancel_order_action(self, api_client, user, create_order):
        order = create_order(status=OrderStatus.PENDING)
        api_client.force_authenticate(user=user)
        response = api_client.post(
            f"/api/v1/orders/{order.pk}/cancel/",
            {"reason": "Changed mind"},
            format="json",
        )
        assert response.status_code == http_status.HTTP_200_OK
        assert response.data["status"] == "cancelled"

    def test_available_actions(self, api_client, user, create_order):
        order = create_order(status=OrderStatus.PENDING)
        api_client.force_authenticate(user=user)
        response = api_client.get(
            f"/api/v1/orders/{order.pk}/available_actions/"
        )
        assert response.status_code == http_status.HTTP_200_OK
        assert "actions" in response.data

    def test_order_history(self, api_client, user, create_order):
        order = create_order()
        api_client.force_authenticate(user=user)
        response = api_client.get(f"/api/v1/orders/{order.pk}/history/")
        if response.status_code >= 400:
            print(f"HISTORY RESPONSE ({response.status_code}): {response.content[:2000]}")
        assert response.status_code == http_status.HTTP_200_OK

    def test_unauthenticated_access(self, api_client, create_order):
        create_order()
        response = api_client.get("/api/v1/orders/")
        assert response.status_code == http_status.HTTP_401_UNAUTHORIZED

    def test_filter_by_status(self, api_client, user, create_order):
        create_order(status=OrderStatus.PENDING)
        create_order(status=OrderStatus.CONFIRMED)
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/v1/orders/?status=pending")
        assert response.status_code == http_status.HTTP_200_OK

    def test_search_by_order_number(self, api_client, user, create_order):
        order = create_order(order_number="ORD-SEARCH-001")
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/v1/orders/?search=SEARCH-001")
        assert response.status_code == http_status.HTTP_200_OK


class TestFulfillmentAPI:
    """Tests for the Fulfillment ViewSet API endpoints."""

    def test_list_fulfillments(self, api_client, user):
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/v1/fulfillments/")
        assert response.status_code == http_status.HTTP_200_OK

    def test_retrieve_fulfillment(self, api_client, user, create_order):
        from apps.orders.models.fulfillment import Fulfillment

        order = create_order()
        ful = Fulfillment.objects.create(
            order=order, fulfillment_number="FUL-API-01"
        )
        api_client.force_authenticate(user=user)
        response = api_client.get(f"/api/v1/fulfillments/{ful.pk}/")
        assert response.status_code == http_status.HTTP_200_OK


class TestReturnAPI:
    """Tests for the Return ViewSet API endpoints."""

    def test_list_returns(self, api_client, user):
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/v1/returns/")
        assert response.status_code == http_status.HTTP_200_OK

    def test_retrieve_return(self, api_client, user, create_order):
        from apps.orders.models.order_return import OrderReturn

        order = create_order()
        ret = OrderReturn.objects.create(
            order=order, return_number="RET-API-001"
        )
        api_client.force_authenticate(user=user)
        response = api_client.get(f"/api/v1/returns/{ret.pk}/")
        assert response.status_code == http_status.HTTP_200_OK
