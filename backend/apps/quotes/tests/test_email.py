"""
Tests for Quote email service and Celery tasks.

Task 87: Covers QuoteEmailService.send_quote_email,
         send_expiry_reminder, Celery tasks, and send_email endpoint.
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
    from django.contrib.auth import get_user_model

    User = get_user_model()
    return User.objects.create_user(
        email=f"email-{uuid.uuid4().hex[:6]}@example.com",
        password="testpass123",
    )


def make_quote(**kwargs):
    from apps.quotes.models import Quote

    defaults = {
        "id": uuid.uuid4(),
        "quote_number": f"QT-EM-{uuid.uuid4().hex[:5].upper()}",
        "status": QuoteStatus.SENT,
        "issue_date": date.today(),
        "guest_email": "customer@example.com",
        "public_token": uuid.uuid4(),
        "valid_until": date.today() + timedelta(days=30),
    }
    defaults.update(kwargs)
    return Quote.objects.create(**defaults)


def make_line_item(quote, **kwargs):
    from apps.quotes.models import QuoteLineItem

    defaults = {
        "product_name": "Email Test Item",
        "quantity": Decimal("1"),
        "unit_price": Decimal("100.00"),
    }
    defaults.update(kwargs)
    return QuoteLineItem.objects.create(quote=quote, **defaults)


TENANT_DOMAIN = "quotes.testserver"


def authed_client(user=None):
    client = APIClient(HTTP_HOST=TENANT_DOMAIN)
    user = user or make_user()
    client.force_authenticate(user=user)
    return client, user


# ═══════════════════════════════════════════════════════════════════
# QuoteEmailService.send_quote_email
# ═══════════════════════════════════════════════════════════════════


@pytest.mark.usefixtures("tenant_context")
class TestSendQuoteEmail:
    @patch("apps.quotes.services.email_service.EmailMultiAlternatives")
    @patch("apps.quotes.services.email_service.render_to_string", return_value="body")
    def test_send_email_success(self, mock_render, MockEmail):
        from apps.quotes.services import QuoteEmailService

        mock_email_inst = MagicMock()
        MockEmail.return_value = mock_email_inst

        q = make_quote()
        QuoteEmailService.send_quote_email(q, to_email="test@example.com")
        mock_email_inst.send.assert_called_once_with(fail_silently=False)

    @patch("apps.quotes.services.email_service.EmailMultiAlternatives")
    @patch("apps.quotes.services.email_service.render_to_string", return_value="body")
    def test_send_email_updates_tracking(self, mock_render, MockEmail):
        from apps.quotes.services import QuoteEmailService

        mock_email_inst = MagicMock()
        MockEmail.return_value = mock_email_inst

        q = make_quote()
        QuoteEmailService.send_quote_email(q, to_email="test@example.com")
        q.refresh_from_db()
        assert q.email_sent_to == "test@example.com"
        assert q.email_sent_count == 1

    def test_send_email_no_recipient_raises(self):
        from apps.quotes.services import QuoteEmailService

        q = make_quote(guest_email="")
        with pytest.raises(ValueError, match="No email"):
            QuoteEmailService.send_quote_email(q)

    @patch("apps.quotes.services.email_service.EmailMultiAlternatives")
    @patch("apps.quotes.services.email_service.render_to_string", return_value="body")
    def test_send_email_with_custom_subject(self, mock_render, MockEmail):
        from apps.quotes.services import QuoteEmailService

        mock_email_inst = MagicMock()
        MockEmail.return_value = mock_email_inst

        q = make_quote()
        QuoteEmailService.send_quote_email(
            q, to_email="test@example.com", subject="Custom Subject"
        )
        call_kwargs = MockEmail.call_args[1]
        assert call_kwargs["subject"] == "Custom Subject"

    @patch("apps.quotes.services.email_service.EmailMultiAlternatives")
    @patch("apps.quotes.services.email_service.render_to_string", return_value="body")
    def test_send_email_with_cc(self, mock_render, MockEmail):
        from apps.quotes.services import QuoteEmailService

        mock_email_inst = MagicMock()
        MockEmail.return_value = mock_email_inst

        q = make_quote()
        QuoteEmailService.send_quote_email(
            q, to_email="test@example.com", cc=["boss@example.com"]
        )
        call_kwargs = MockEmail.call_args[1]
        assert "boss@example.com" in call_kwargs["cc"]


# ═══════════════════════════════════════════════════════════════════
# QuoteEmailService.send_expiry_reminder
# ═══════════════════════════════════════════════════════════════════


@pytest.mark.usefixtures("tenant_context")
class TestSendExpiryReminder:
    @patch("apps.quotes.services.email_service.EmailMultiAlternatives")
    @patch("apps.quotes.services.email_service.render_to_string", return_value="body")
    def test_send_expiry_reminder_success(self, mock_render, MockEmail):
        from apps.quotes.services import QuoteEmailService

        mock_email_inst = MagicMock()
        MockEmail.return_value = mock_email_inst

        q = make_quote(valid_until=date.today() + timedelta(days=2))
        result = QuoteEmailService.send_expiry_reminder(q, to_email="cust@example.com")
        assert result is True
        mock_email_inst.send.assert_called_once()

    def test_send_expiry_reminder_no_recipient_raises(self):
        from apps.quotes.services import QuoteEmailService

        q = make_quote(guest_email="")
        with pytest.raises(ValueError, match="No email"):
            QuoteEmailService.send_expiry_reminder(q)


# ═══════════════════════════════════════════════════════════════════
# Celery Tasks
# ═══════════════════════════════════════════════════════════════════


@pytest.mark.usefixtures("tenant_context")
class TestEmailCeleryTasks:
    @patch("apps.quotes.services.email_service.EmailMultiAlternatives")
    @patch("apps.quotes.services.email_service.render_to_string", return_value="body")
    def test_send_quote_email_task(self, mock_render, MockEmail):
        from apps.quotes.tasks.email import send_quote_email_task

        mock_email_inst = MagicMock()
        MockEmail.return_value = mock_email_inst

        q = make_quote()
        send_quote_email_task(str(q.pk), to_email="task@example.com")
        mock_email_inst.send.assert_called_once()

    @patch("apps.quotes.services.email_service.EmailMultiAlternatives")
    @patch("apps.quotes.services.email_service.render_to_string", return_value="body")
    def test_send_expiry_reminder_task(self, mock_render, MockEmail):
        from apps.quotes.tasks.email import send_expiry_reminder_task

        mock_email_inst = MagicMock()
        MockEmail.return_value = mock_email_inst

        q = make_quote(valid_until=date.today() + timedelta(days=2))
        send_expiry_reminder_task(str(q.pk), to_email="reminder@example.com")
        mock_email_inst.send.assert_called_once()

    def test_send_quote_email_task_has_retry_backoff(self):
        from apps.quotes.tasks.email import send_quote_email_task

        assert send_quote_email_task.retry_backoff is True
        assert send_quote_email_task.max_retries == 3

    def test_send_expiry_reminder_task_has_retry_backoff(self):
        from apps.quotes.tasks.email import send_expiry_reminder_task

        assert send_expiry_reminder_task.retry_backoff is True
        assert send_expiry_reminder_task.max_retries == 3

    @patch("apps.quotes.tasks.email.send_expiry_reminder_task.delay")
    def test_send_expiry_reminders_task_finds_quotes(self, mock_delay):
        from apps.quotes.tasks.email import send_expiry_reminders_task

        # Create a quote expiring in 2 days (within default 3-day threshold)
        make_quote(valid_until=date.today() + timedelta(days=2))
        # Create a quote expiring in 10 days (outside threshold)
        make_quote(valid_until=date.today() + timedelta(days=10))

        count = send_expiry_reminders_task(days_before=3)
        assert count == 1
        assert mock_delay.called


# ═══════════════════════════════════════════════════════════════════
# Send Email API Endpoint
# ═══════════════════════════════════════════════════════════════════


@pytest.mark.usefixtures("tenant_context")
class TestSendEmailEndpoint:
    @patch("apps.quotes.tasks.email.send_quote_email_task")
    def test_send_email_action(self, mock_task):
        mock_task.delay = MagicMock()
        client, user = authed_client()
        q = make_quote(created_by=user, guest_email="api@example.com")
        url = reverse("quotes:quote-send-email", args=[q.pk])
        resp = client.post(url, {}, format="json")
        assert resp.status_code == status.HTTP_200_OK

    @patch("apps.quotes.tasks.email.send_quote_email_task")
    def test_send_email_with_custom_recipient(self, mock_task):
        mock_task.delay = MagicMock()
        client, user = authed_client()
        q = make_quote(created_by=user, guest_email="default@example.com")
        url = reverse("quotes:quote-send-email", args=[q.pk])
        resp = client.post(url, {"to_email": "override@example.com"}, format="json")
        assert resp.status_code == status.HTTP_200_OK
