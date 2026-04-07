"""
LankaCommerce Cloud – Content & Tenant Validators (SP12 Tasks 44-46).

Validators for content integrity and multi-tenant uniqueness.

Validators:
    JSONValidator              — Validates that a string is well-formed JSON
    NoHTMLValidator            — Rejects strings containing HTML tags
    UniqueForTenantValidator   — Ensures a field value is unique within the
                                 current tenant scope (django-tenants)
"""

from __future__ import annotations

import json
import re
from typing import Any

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


# ════════════════════════════════════════════════════════════════════════
# JSON Validator
# ════════════════════════════════════════════════════════════════════════


@deconstructible
class JSONValidator:
    """
    Validate that a value is a well-formed JSON string.

    Accepts both plain JSON strings and already-parsed Python objects
    (``dict``, ``list``).  When the input is a ``str``, it is parsed
    with ``json.loads``; a ``json.JSONDecodeError`` triggers a
    ``ValidationError``.

    Use cases:
        * ``JSONField`` validation
        * API configuration payloads
        * Metadata / settings storage

    Usage::

        validator = JSONValidator()
        validator('{"key": "value"}')  # OK
        validator('{bad json}')        # raises ValidationError
    """

    message = _("Enter valid JSON.")
    code = "invalid_json"

    def __call__(self, value: Any) -> None:
        if value is None:
            raise ValidationError(self.message, code=self.code)

        # Already a parsed structure — accept.
        if isinstance(value, (dict, list)):
            return

        if not isinstance(value, str):
            raise ValidationError(self.message, code=self.code)

        if not value.strip():
            raise ValidationError(
                _("Empty string is not valid JSON."),
                code=self.code,
            )

        try:
            json.loads(value)
        except (json.JSONDecodeError, ValueError) as exc:
            raise ValidationError(
                _("Invalid JSON: %(error)s"),
                code=self.code,
                params={"error": str(exc)},
            )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, JSONValidator)


# ════════════════════════════════════════════════════════════════════════
# No-HTML Validator
# ════════════════════════════════════════════════════════════════════════

_HTML_TAG_RE = re.compile(r"<[a-zA-Z/!][^>]*>")


@deconstructible
class NoHTMLValidator:
    """
    Reject strings that contain HTML tags.

    Uses a regex to detect opening / closing / self-closing tags such as
    ``<div>``, ``</span>``, ``<br />``, and ``<script>`` (an important
    XSS vector).

    Security: prevents XSS injection in plain-text fields.

    Use cases:
        * Usernames
        * Product names
        * Short descriptions / comments

    Usage::

        validator = NoHTMLValidator()
        validator("Hello world")              # OK
        validator("<b>bold</b>")              # raises ValidationError
        validator("<script>alert(1)</script>") # raises ValidationError
    """

    message = _("HTML tags are not allowed in this field.")
    code = "html_not_allowed"

    def __call__(self, value: Any) -> None:
        if not isinstance(value, str):
            raise ValidationError(
                _("Expected a string value."),
                code=self.code,
            )

        if _HTML_TAG_RE.search(value):
            raise ValidationError(self.message, code=self.code)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, NoHTMLValidator)


# ════════════════════════════════════════════════════════════════════════
# Unique-for-Tenant Validator
# ════════════════════════════════════════════════════════════════════════


@deconstructible
class UniqueForTenantValidator:
    """
    Ensure a field value is unique **within** the current tenant's schema.

    Uses ``django.db.connection.tenant`` (provided by *django-tenants*)
    to resolve the active tenant at validation time.

    Parameters:
        model:        The Django model class to query
        field_name:   The field whose uniqueness should be checked
        message:      Optional custom error message

    For **updates**, pass the current model instance so that the validator
    can exclude it from the duplicate check::

        validator = UniqueForTenantValidator(Product, 'sku')
        validator('SKU-001')                            # create check
        validator('SKU-001', instance=existing_product)  # update check

    Use cases:
        * SKU numbers within a tenant
        * Customer email addresses within a tenant
        * Invoice numbers within a tenant
    """

    code = "unique_for_tenant"

    def __init__(
        self,
        model: type,
        field_name: str,
        message: str | None = None,
    ) -> None:
        self.model = model
        self.field_name = field_name
        self.message = message or _(
            "%(field)s must be unique within your organization."
        )

    def __call__(
        self,
        value: Any,
        instance: Any | None = None,
    ) -> None:
        from django.db import connection  # late import to pick up tenant context

        tenant = getattr(connection, "tenant", None)

        lookup = {self.field_name: value}
        queryset = self.model.objects.filter(**lookup)

        # When running inside a tenant schema (django-tenants sets the
        # search_path), the queryset is already scoped.  But if the model
        # has an explicit ``tenant`` FK, we add an extra filter for safety.
        if tenant is not None and hasattr(self.model, "tenant"):
            queryset = queryset.filter(tenant=tenant)

        # Exclude the current instance on update.
        if instance is not None and instance.pk:
            queryset = queryset.exclude(pk=instance.pk)

        if queryset.exists():
            raise ValidationError(
                self.message,
                code=self.code,
                params={"field": self.field_name},
            )

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, UniqueForTenantValidator)
            and self.model == other.model
            and self.field_name == other.field_name
        )
