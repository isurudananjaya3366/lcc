"""
Root conftest.py — shared pytest fixtures for LankaCommerce Cloud.

Provides common fixtures for database access, API clients,
and user instances used across all test modules.
"""

import pytest
from django.test import Client
from rest_framework.test import APIClient


# ── API / HTTP Client Fixtures ────────────────────────────────────


@pytest.fixture
def client():
    """Return a Django test client."""
    return Client()


@pytest.fixture
def api_client():
    """Return a Django REST Framework API test client."""
    return APIClient()


# ── User Fixtures ─────────────────────────────────────────────────
# NOTE: These fixtures use `get_user_model()` so they work regardless
# of whether the custom User model has been created yet.  They will
# become functional once `AUTH_USER_MODEL` is set and the User model
# exists (Phase 3).


@pytest.fixture
def user(db):
    """Create and return a regular user.

    Requires the User model to be available (Phase 3+).
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()  # noqa: N806
    return User.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="testpass123",  # noqa: S106
    )


@pytest.fixture
def staff_user(db):
    """Create and return a staff user.

    Requires the User model to be available (Phase 3+).
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()  # noqa: N806
    return User.objects.create_user(
        username="staffuser",
        email="staff@example.com",
        password="staffpass123",  # noqa: S106
        is_staff=True,
    )


@pytest.fixture
def superuser(db):
    """Create and return a superuser.

    Requires the User model to be available (Phase 3+).
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()  # noqa: N806
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpass123",  # noqa: S106
    )


@pytest.fixture
def api_client_auth(api_client, user):
    """Return an authenticated DRF API client.

    Requires the User model to be available (Phase 3+).
    """
    api_client.force_authenticate(user=user)
    return api_client


# ── Tenant Fixtures (Placeholders) ────────────────────────────────
# These will be implemented when multi-tenancy is configured (Phase 2).


# @pytest.fixture
# def tenant(db):
#     """Create and return a test tenant."""
#     pass


# @pytest.fixture
# def tenant_context(tenant):
#     """Activate tenant schema context for the test."""
#     pass


# ── Mock Fixtures (Placeholders) ──────────────────────────────────


# @pytest.fixture
# def mock_redis(mocker):
#     """Mock Redis connection for tests that don't need real Redis."""
#     pass


# @pytest.fixture
# def mock_celery(mocker):
#     """Mock Celery for tests that don't need a real task queue."""
#     pass
