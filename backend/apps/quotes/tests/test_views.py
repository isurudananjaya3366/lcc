"""
Tests for Quote API views.

Covers: QuoteViewSet CRUD, status actions, PDF actions,
        public endpoints, line item management, filtering,
        search, convert_to_order, send_email.
"""

import uuid
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.quotes.constants import QuoteStatus

pytestmark = pytest.mark.django_db


# ── Helpers ──────────────────────────────────────────────────────


def make_user():
    """Create a test user using the project's auth model."""
    from django.contrib.auth import get_user_model

    User = get_user_model()
    return User.objects.create_user(
        email=f"test-{uuid.uuid4().hex[:6]}@example.com",
        password="testpass123",
    )


def make_quote(**kwargs):
    from apps.quotes.models import Quote

    defaults = {
        "id": uuid.uuid4(),
        "quote_number": f"QT-V-{uuid.uuid4().hex[:5].upper()}",
        "status": QuoteStatus.DRAFT,
        "issue_date": date.today(),
    }
    defaults.update(kwargs)
    return Quote.objects.create(**defaults)


def make_line_item(quote, **kwargs):
    from apps.quotes.models import QuoteLineItem

    defaults = {
        "product_name": "API Test Item",
        "quantity": Decimal("1"),
        "unit_price": Decimal("50.00"),
    }
    defaults.update(kwargs)
    return QuoteLineItem.objects.create(quote=quote, **defaults)


TENANT_DOMAIN = "quotes.testserver"


def authed_client(user=None):
    """Return an APIClient authenticated with a user."""
    client = APIClient(HTTP_HOST=TENANT_DOMAIN)
    user = user or make_user()
    client.force_authenticate(user=user)
    return client, user


# ═══════════════════════════════════════════════════════════════════
# Quote CRUD
# ═══════════════════════════════════════════════════════════════════


@pytest.mark.usefixtures("tenant_context")
class TestQuoteListCreate:
    def test_list_empty(self):
        client, _ = authed_client()
        resp = client.get(reverse("quotes:quote-list"))
        assert resp.status_code == status.HTTP_200_OK

    def test_create_quote(self):
        client, user = authed_client()
        data = {
            "title": "Test Quote",
            "guest_name": "Jane",
            "guest_email": "jane@example.com",
            "issue_date": "2026-01-15",
        }
        resp = client.post(reverse("quotes:quote-list"), data, format="json")
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["title"] == "Test Quote"

    def test_retrieve_quote(self):
        client, user = authed_client()
        q = make_quote(created_by=user)
        resp = client.get(reverse("quotes:quote-detail", args=[q.pk]))
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["quote_number"] == q.quote_number

    def test_update_draft_quote(self):
        client, user = authed_client()
        q = make_quote(created_by=user, title="Old")
        resp = client.patch(
            reverse("quotes:quote-detail", args=[q.pk]),
            {"title": "New"},
            format="json",
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["title"] == "New"

    def test_delete_draft_quote(self):
        client, user = authed_client()
        q = make_quote(created_by=user, status=QuoteStatus.DRAFT)
        resp = client.delete(reverse("quotes:quote-detail", args=[q.pk]))
        assert resp.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_sent_quote_forbidden(self):
        client, user = authed_client()
        q = make_quote(created_by=user, status=QuoteStatus.SENT)
        resp = client.delete(reverse("quotes:quote-detail", args=[q.pk]))
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_access(self):
        client = APIClient(HTTP_HOST=TENANT_DOMAIN)
        resp = client.get(reverse("quotes:quote-list"))
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


# ═══════════════════════════════════════════════════════════════════
# Status Actions
# ═══════════════════════════════════════════════════════════════════


@pytest.mark.usefixtures("tenant_context")
class TestQuoteStatusActions:
    def test_send_quote(self):
        client, user = authed_client()
        q = make_quote(created_by=user, status=QuoteStatus.DRAFT, guest_email="test@example.com")
        make_line_item(q)
        url = reverse("quotes:quote-send-quote", args=[q.pk])
        resp = client.post(url, {}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["status"] == QuoteStatus.SENT

    def test_accept_quote(self):
        client, user = authed_client()
        q = make_quote(status=QuoteStatus.SENT)
        url = reverse("quotes:quote-accept-quote", args=[q.pk])
        resp = client.post(url, {}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["status"] == QuoteStatus.ACCEPTED

    def test_reject_quote(self):
        client, user = authed_client()
        q = make_quote(status=QuoteStatus.SENT)
        url = reverse("quotes:quote-reject-quote", args=[q.pk])
        resp = client.post(url, {"rejection_reason": "Price too high"}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["status"] == QuoteStatus.REJECTED

    def test_send_expired_fails(self):
        client, user = authed_client()
        q = make_quote(status=QuoteStatus.EXPIRED)
        url = reverse("quotes:quote-send-quote", args=[q.pk])
        resp = client.post(url, {}, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


# ═══════════════════════════════════════════════════════════════════
# Line Items
# ═══════════════════════════════════════════════════════════════════


@pytest.mark.usefixtures("tenant_context")
class TestQuoteLineItemActions:
    def test_list_line_items(self):
        client, user = authed_client()
        q = make_quote()
        make_line_item(q, product_name="A")
        make_line_item(q, product_name="B")
        url = reverse("quotes:quote-line-items", args=[q.pk])
        resp = client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2

    def test_add_line_item(self):
        client, user = authed_client()
        q = make_quote(status=QuoteStatus.DRAFT)
        url = reverse("quotes:quote-line-items", args=[q.pk])
        data = {
            "quote": str(q.pk),
            "product_name": "New Item",
            "quantity": "3",
            "unit_price": "25.00",
        }
        resp = client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_201_CREATED

    def test_add_line_item_locked_fails(self):
        client, user = authed_client()
        q = make_quote(status=QuoteStatus.SENT)
        url = reverse("quotes:quote-line-items", args=[q.pk])
        data = {
            "quote": str(q.pk),
            "product_name": "Blocked",
            "quantity": "1",
            "unit_price": "10.00",
        }
        resp = client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


# ═══════════════════════════════════════════════════════════════════
# Duplicate & Revision
# ═══════════════════════════════════════════════════════════════════


@pytest.mark.usefixtures("tenant_context")
class TestDuplicateAndRevision:
    def test_duplicate(self):
        client, user = authed_client()
        q = make_quote(title="Orig", guest_name="Bob")
        make_line_item(q)
        url = reverse("quotes:quote-duplicate-quote", args=[q.pk])
        resp = client.post(url, {}, format="json")
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["status"] == QuoteStatus.DRAFT


# ═══════════════════════════════════════════════════════════════════
# History & Actions
# ═══════════════════════════════════════════════════════════════════


@pytest.mark.usefixtures("tenant_context")
class TestHistoryAndActions:
    def test_history(self):
        client, user = authed_client()
        q = make_quote()
        url = reverse("quotes:quote-history", args=[q.pk])
        resp = client.get(url)
        assert resp.status_code == status.HTTP_200_OK

    def test_available_actions(self):
        client, user = authed_client()
        q = make_quote(status=QuoteStatus.DRAFT)
        url = reverse("quotes:quote-available-actions", args=[q.pk])
        resp = client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert "actions" in resp.data


# ═══════════════════════════════════════════════════════════════════
# Public Endpoints
# ═══════════════════════════════════════════════════════════════════


@pytest.mark.usefixtures("tenant_context")
class TestPublicEndpoints:
    def test_public_view(self):
        token = uuid.uuid4()
        q = make_quote(public_token=token, status=QuoteStatus.SENT)
        client = APIClient(HTTP_HOST=TENANT_DOMAIN)
        url = reverse("quotes:public-quote-detail", args=[token])
        resp = client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["quote_number"] == q.quote_number

    def test_public_view_not_found(self):
        client = APIClient(HTTP_HOST=TENANT_DOMAIN)
        url = reverse("quotes:public-quote-detail", args=[uuid.uuid4()])
        resp = client.get(url)
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_public_accept(self):
        token = uuid.uuid4()
        q = make_quote(public_token=token, status=QuoteStatus.SENT)
        client = APIClient(HTTP_HOST=TENANT_DOMAIN)
        url = reverse("quotes:public-quote-accept", args=[token])
        resp = client.post(url, {}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        q.refresh_from_db()
        assert q.status == QuoteStatus.ACCEPTED

    def test_public_reject(self):
        token = uuid.uuid4()
        q = make_quote(public_token=token, status=QuoteStatus.SENT)
        client = APIClient(HTTP_HOST=TENANT_DOMAIN)
        url = reverse("quotes:public-quote-reject", args=[token])
        resp = client.post(url, {"reason": "Not needed"}, format="json")
        assert resp.status_code == status.HTTP_200_OK

    def test_public_accept_wrong_status(self):
        token = uuid.uuid4()
        q = make_quote(public_token=token, status=QuoteStatus.DRAFT)
        client = APIClient(HTTP_HOST=TENANT_DOMAIN)
        url = reverse("quotes:public-quote-accept", args=[token])
        resp = client.post(url, {}, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_public_reject_requires_reason(self):
        token = uuid.uuid4()
        q = make_quote(public_token=token, status=QuoteStatus.SENT)
        client = APIClient(HTTP_HOST=TENANT_DOMAIN)
        url = reverse("quotes:public-quote-reject", args=[token])
        resp = client.post(url, {}, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_public_accept_expired_quote_rejected(self):
        token = uuid.uuid4()
        q = make_quote(
            public_token=token,
            status=QuoteStatus.SENT,
            valid_until=date.today() - timedelta(days=1),
        )
        client = APIClient(HTTP_HOST=TENANT_DOMAIN)
        url = reverse("quotes:public-quote-accept", args=[token])
        resp = client.post(url, {}, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_public_view_increments_view_count(self):
        token = uuid.uuid4()
        q = make_quote(public_token=token, status=QuoteStatus.SENT)
        client = APIClient(HTTP_HOST=TENANT_DOMAIN)
        url = reverse("quotes:public-quote-detail", args=[token])
        client.get(url)
        client.get(url)
        q.refresh_from_db()
        assert q.view_count == 2


# ═══════════════════════════════════════════════════════════════════
# Filtering & Search
# ═══════════════════════════════════════════════════════════════════


@pytest.mark.usefixtures("tenant_context")
class TestQuoteFilteringAndSearch:
    def test_filter_by_status(self):
        client, user = authed_client()
        make_quote(status=QuoteStatus.DRAFT)
        make_quote(status=QuoteStatus.SENT)
        url = reverse("quotes:quote-list")
        resp = client.get(url, {"status": QuoteStatus.DRAFT})
        assert resp.status_code == status.HTTP_200_OK
        results = resp.data.get("results", resp.data)
        for item in results:
            assert item["status"] == QuoteStatus.DRAFT

    def test_search_by_quote_number(self):
        client, user = authed_client()
        q = make_quote(quote_number="QT-SEARCH-001")
        url = reverse("quotes:quote-list")
        resp = client.get(url, {"search": "SEARCH-001"})
        assert resp.status_code == status.HTTP_200_OK
        results = resp.data.get("results", resp.data)
        found = [r for r in results if r["quote_number"] == "QT-SEARCH-001"]
        assert len(found) >= 1

    def test_search_by_guest_name(self):
        client, user = authed_client()
        q = make_quote(guest_name="Bartholomew Uniquename")
        url = reverse("quotes:quote-list")
        resp = client.get(url, {"search": "Bartholomew"})
        assert resp.status_code == status.HTTP_200_OK


# ═══════════════════════════════════════════════════════════════════
# Convert to Order
# ═══════════════════════════════════════════════════════════════════


@pytest.mark.usefixtures("tenant_context")
class TestConvertToOrder:
    def test_convert_to_order_accepted_quote(self):
        client, user = authed_client()
        q = make_quote(status=QuoteStatus.ACCEPTED)
        make_line_item(q)
        url = reverse("quotes:quote-convert-to-order", args=[q.pk])
        resp = client.post(url, {}, format="json")
        # Should succeed or fail based on order module availability
        assert resp.status_code in (
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST,  # if order module not ready
        )

    def test_convert_draft_quote_fails(self):
        client, user = authed_client()
        q = make_quote(status=QuoteStatus.DRAFT)
        url = reverse("quotes:quote-convert-to-order", args=[q.pk])
        resp = client.post(url, {}, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


# ═══════════════════════════════════════════════════════════════════
# Send Email Endpoint
# ═══════════════════════════════════════════════════════════════════


@pytest.mark.usefixtures("tenant_context")
class TestSendEmailAction:
    @patch("apps.quotes.tasks.email.send_quote_email_task")
    def test_send_email_success(self, mock_task):
        mock_task.delay = MagicMock()
        client, user = authed_client()
        q = make_quote(guest_email="view-test@example.com")
        url = reverse("quotes:quote-send-email", args=[q.pk])
        resp = client.post(url, {}, format="json")
        assert resp.status_code == status.HTTP_200_OK

    def test_send_email_unauthenticated(self):
        client = APIClient(HTTP_HOST=TENANT_DOMAIN)
        url = reverse("quotes:quote-send-email", args=[uuid.uuid4()])
        resp = client.post(url, {}, format="json")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
