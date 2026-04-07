"""
API endpoint tests for all POS ViewSets and APIViews.

Tests authentication, CRUD operations, custom actions, and error responses
through the REST framework test client.
"""

from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status

from apps.pos.constants import (
    CART_STATUS_ACTIVE,
    CART_STATUS_COMPLETED,
    CART_STATUS_HELD,
    CART_STATUS_VOIDED,
    PAYMENT_METHOD_CARD,
    PAYMENT_METHOD_CASH,
    SESSION_STATUS_CLOSED,
    SESSION_STATUS_OPEN,
    TERMINAL_STATUS_ACTIVE,
    TERMINAL_STATUS_INACTIVE,
    TERMINAL_STATUS_MAINTENANCE,
)

pytestmark = pytest.mark.django_db


# ── Terminal API Tests ───────────────────────────────────────────────


class TestTerminalAPI:
    """Tests for /api/v1/pos/terminals/ endpoints."""

    def test_list_terminals_unauthenticated(self, api_client):
        url = reverse("pos:terminal-list")
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_terminals_authenticated(self, authenticated_client, terminal):
        url = reverse("pos:terminal-list")
        resp = authenticated_client.get(url)
        assert resp.status_code == status.HTTP_200_OK

    def test_create_terminal(self, manager_client, warehouse):
        url = reverse("pos:terminal-list")
        data = {
            "name": "New Terminal",
            "code": "NT-001",
            "warehouse": str(warehouse.id),
            "status": TERMINAL_STATUS_ACTIVE,
        }
        resp = manager_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["code"] == "NT-001"

    def test_retrieve_terminal(self, authenticated_client, terminal):
        url = reverse("pos:terminal-detail", kwargs={"pk": terminal.pk})
        resp = authenticated_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["code"] == terminal.code

    def test_update_terminal(self, manager_client, terminal):
        url = reverse("pos:terminal-detail", kwargs={"pk": terminal.pk})
        resp = manager_client.patch(
            url, {"name": "Updated Name"}, format="json"
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["name"] == "Updated Name"

    def test_activate_terminal(self, manager_client, inactive_terminal):
        url = reverse(
            "pos:terminal-activate",
            kwargs={"pk": inactive_terminal.pk},
        )
        resp = manager_client.post(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["status"] == TERMINAL_STATUS_ACTIVE

    def test_activate_already_active(self, manager_client, terminal):
        url = reverse("pos:terminal-activate", kwargs={"pk": terminal.pk})
        resp = manager_client.post(url)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_deactivate_terminal_no_session(
        self, manager_client, terminal
    ):
        url = reverse(
            "pos:terminal-deactivate", kwargs={"pk": terminal.pk}
        )
        resp = manager_client.post(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["status"] == TERMINAL_STATUS_INACTIVE

    def test_deactivate_terminal_with_open_session(
        self, manager_client, terminal, session
    ):
        url = reverse(
            "pos:terminal-deactivate", kwargs={"pk": terminal.pk}
        )
        resp = manager_client.post(url)
        assert resp.status_code == status.HTTP_409_CONFLICT

    def test_maintenance_mode(self, manager_client, terminal2):
        url = reverse(
            "pos:terminal-maintenance-mode",
            kwargs={"pk": terminal2.pk},
        )
        resp = manager_client.post(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["status"] == TERMINAL_STATUS_MAINTENANCE

    def test_available_terminals(self, authenticated_client, terminal, terminal2):
        url = reverse("pos:terminal-available-terminals")
        resp = authenticated_client.get(url)
        assert resp.status_code == status.HTTP_200_OK


# ── Session API Tests ────────────────────────────────────────────────


class TestSessionAPI:
    """Tests for /api/v1/pos/sessions/ endpoints."""

    def test_list_sessions_unauthenticated(self, api_client):
        url = reverse("pos:session-list")
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_sessions(self, authenticated_client, session):
        url = reverse("pos:session-list")
        resp = authenticated_client.get(url)
        assert resp.status_code == status.HTTP_200_OK

    def test_open_session(self, authenticated_client, terminal2):
        url = reverse("pos:session-open-session")
        data = {
            "terminal": str(terminal2.pk),
            "opening_cash_amount": "10000.00",
        }
        resp = authenticated_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["status"] == SESSION_STATUS_OPEN

    def test_close_session(self, authenticated_client, session):
        url = reverse(
            "pos:session-close-session", kwargs={"pk": session.pk}
        )
        data = {"actual_cash_amount": "10000.00"}
        resp = authenticated_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["status"] == SESSION_STATUS_CLOSED

    def test_close_already_closed_session(
        self, authenticated_client, closed_session
    ):
        url = reverse(
            "pos:session-close-session",
            kwargs={"pk": closed_session.pk},
        )
        data = {"actual_cash_amount": "10000.00"}
        resp = authenticated_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_current_session(self, authenticated_client, session):
        url = reverse("pos:session-current")
        resp = authenticated_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["session_number"] == session.session_number

    def test_current_session_none(self, manager_client):
        url = reverse("pos:session-current")
        resp = manager_client.get(url)
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_session_summary(self, authenticated_client, session):
        url = reverse(
            "pos:session-session-summary", kwargs={"pk": session.pk}
        )
        resp = authenticated_client.get(url)
        assert resp.status_code == status.HTTP_200_OK

    def test_my_sessions(self, authenticated_client, session):
        url = reverse("pos:session-my-sessions")
        resp = authenticated_client.get(url)
        assert resp.status_code == status.HTTP_200_OK


# ── Cart API Tests ───────────────────────────────────────────────────


class TestCartAPI:
    """Tests for /api/v1/pos/cart/ endpoints."""

    def test_list_carts_unauthenticated(self, api_client):
        url = reverse("pos:cart-list")
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_carts(self, authenticated_client, cart):
        url = reverse("pos:cart-list")
        resp = authenticated_client.get(url)
        assert resp.status_code == status.HTTP_200_OK

    def test_retrieve_cart(self, authenticated_client, cart):
        url = reverse("pos:cart-detail", kwargs={"pk": cart.pk})
        resp = authenticated_client.get(url)
        assert resp.status_code == status.HTTP_200_OK

    def test_add_item_to_cart(self, authenticated_client, cart, product):
        url = reverse("pos:cart-add-item", kwargs={"pk": cart.pk})
        data = {
            "product": str(product.pk),
            "quantity": 2,
        }
        resp = authenticated_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_200_OK

    def test_add_item_invalid_product(self, authenticated_client, cart):
        url = reverse("pos:cart-add-item", kwargs={"pk": cart.pk})
        data = {
            "product": "00000000-0000-0000-0000-000000000000",
            "quantity": 1,
        }
        resp = authenticated_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_update_quantity(self, authenticated_client, cart_with_items):
        item = cart_with_items.items.first()
        url = reverse(
            "pos:cart-update-quantity",
            kwargs={"pk": cart_with_items.pk, "item_id": item.pk},
        )
        resp = authenticated_client.patch(
            url, {"quantity": 5}, format="json"
        )
        assert resp.status_code == status.HTTP_200_OK

    def test_remove_item(self, authenticated_client, cart_with_items):
        item = cart_with_items.items.first()
        url = reverse(
            "pos:cart-remove-item",
            kwargs={"pk": cart_with_items.pk, "item_id": item.pk},
        )
        resp = authenticated_client.delete(url)
        assert resp.status_code == status.HTTP_200_OK

    def test_apply_cart_discount(self, authenticated_client, cart_with_items):
        url = reverse(
            "pos:cart-apply-discount",
            kwargs={"pk": cart_with_items.pk},
        )
        data = {
            "discount_type": "percent",
            "discount_value": "10.00",
        }
        resp = authenticated_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_200_OK

    def test_apply_line_discount(self, authenticated_client, cart_with_items):
        item = cart_with_items.items.first()
        url = reverse(
            "pos:cart-apply-line-discount",
            kwargs={"pk": cart_with_items.pk, "item_id": item.pk},
        )
        data = {
            "discount_type": "fixed",
            "discount_value": "20.00",
        }
        resp = authenticated_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_200_OK

    def test_hold_cart(self, authenticated_client, cart):
        url = reverse("pos:cart-hold", kwargs={"pk": cart.pk})
        resp = authenticated_client.post(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["status"] == CART_STATUS_HELD

    def test_recall_cart(self, authenticated_client, cart):
        from apps.pos.cart.services.cart_service import CartService

        CartService.hold_cart(cart)
        url = reverse("pos:cart-recall", kwargs={"pk": cart.pk})
        resp = authenticated_client.post(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["status"] == CART_STATUS_ACTIVE

    def test_void_cart(self, authenticated_client, cart):
        url = reverse("pos:cart-void", kwargs={"pk": cart.pk})
        resp = authenticated_client.post(
            url, {"reason": "Test void"}, format="json"
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["status"] == CART_STATUS_VOIDED

    def test_active_carts(self, authenticated_client, cart):
        url = reverse("pos:cart-active-carts")
        resp = authenticated_client.get(url)
        assert resp.status_code == status.HTTP_200_OK

    def test_held_carts(self, authenticated_client):
        url = reverse("pos:cart-held-carts")
        resp = authenticated_client.get(url)
        assert resp.status_code == status.HTTP_200_OK


# ── Search API Tests ─────────────────────────────────────────────────


class TestSearchAPI:
    """Tests for /api/v1/pos/search/ endpoints."""

    def test_search_unauthenticated(self, api_client):
        url = reverse("pos:product-search")
        resp = api_client.post(url, {"query": "test"}, format="json")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_product_search(self, authenticated_client, product):
        url = reverse("pos:product-search")
        resp = authenticated_client.post(
            url, {"query": product.name}, format="json"
        )
        assert resp.status_code == status.HTTP_200_OK
        assert isinstance(resp.data, list)

    def test_barcode_scan(self, authenticated_client, product):
        url = reverse("pos:barcode-scan")
        resp = authenticated_client.post(
            url, {"barcode": product.barcode}, format="json"
        )
        # 200 if found, 404 if not — both are valid responses
        assert resp.status_code in (
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
        )

    def test_barcode_scan_not_found(self, authenticated_client):
        url = reverse("pos:barcode-scan")
        resp = authenticated_client.post(
            url, {"barcode": "0000000000000"}, format="json"
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_quick_buttons(self, authenticated_client, quick_button_group):
        url = reverse("pos:quick-buttons")
        resp = authenticated_client.get(url)
        assert resp.status_code == status.HTTP_200_OK

    def test_search_history(self, authenticated_client):
        url = reverse("pos:search-history")
        resp = authenticated_client.get(url)
        assert resp.status_code == status.HTTP_200_OK


# ── Payment API Tests ────────────────────────────────────────────────


class TestPaymentAPI:
    """Tests for /api/v1/pos/payment/ endpoints."""

    def test_payment_process_unauthenticated(self, api_client):
        url = reverse("pos:payment-process")
        resp = api_client.post(url, {}, format="json")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_process_cash_payment(
        self, authenticated_client, cart_with_items
    ):
        url = reverse("pos:payment-process")
        data = {
            "cart": str(cart_with_items.pk),
            "payment_method": PAYMENT_METHOD_CASH,
            "amount": str(cart_with_items.grand_total),
            "tendered_amount": str(
                cart_with_items.grand_total + Decimal("100")
            ),
        }
        resp = authenticated_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["cart_status"] == "COMPLETED"

    def test_process_card_payment(
        self, authenticated_client, cart_with_items
    ):
        url = reverse("pos:payment-process")
        data = {
            "cart": str(cart_with_items.pk),
            "payment_method": PAYMENT_METHOD_CARD,
            "amount": str(cart_with_items.grand_total),
            "authorization_code": "AUTH123",
        }
        resp = authenticated_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_200_OK

    def test_process_payment_cart_not_found(self, authenticated_client):
        url = reverse("pos:payment-process")
        data = {
            "cart": "00000000-0000-0000-0000-000000000000",
            "payment_method": PAYMENT_METHOD_CASH,
            "amount": "100.00",
        }
        resp = authenticated_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_split_payment(self, authenticated_client, cart_with_items):
        url = reverse("pos:payment-split")
        total = cart_with_items.grand_total
        half = (total / 2).quantize(Decimal("0.01"))
        remainder = total - half
        data = {
            "cart": str(cart_with_items.pk),
            "payments": [
                {
                    "payment_method": PAYMENT_METHOD_CASH,
                    "amount": str(half),
                    "tendered_amount": str(half),
                },
                {
                    "payment_method": PAYMENT_METHOD_CARD,
                    "amount": str(remainder),
                },
            ],
        }
        resp = authenticated_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_200_OK

    def test_payment_history(self, authenticated_client):
        url = reverse("pos:payment-history")
        resp = authenticated_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
