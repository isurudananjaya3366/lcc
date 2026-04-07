#!/usr/bin/env python
"""
SP11 – API Documentation Integration Verification Script (Task 82).

Runs a series of automated checks to confirm that every SP11 component
is correctly installed, configured, and wired together.

Usage (inside Docker):
    python scripts/verify_api_docs.py

Exit codes:
    0  — all checks pass
    1  — one or more checks failed
"""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

# ── Django bootstrap (run from backend/ directory) ────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test_pg")

import django  # noqa: E402

django.setup()


# ── Helpers ───────────────────────────────────────────────────────────
_passed: list[str] = []
_failed: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    """Record a check result."""
    if condition:
        _passed.append(label)
        print(f"  ✅  {label}")
    else:
        msg = f"{label}: {detail}" if detail else label
        _failed.append(msg)
        print(f"  ❌  {msg}")


# ── 1. Package imports ────────────────────────────────────────────────
print("\n🔍  1. Package imports")

try:
    import apps.core.api_docs as api_docs  # noqa: F811

    check("api_docs package importable", True)
except ImportError as exc:
    check("api_docs package importable", False, str(exc))

for sub in ("extensions", "schemas", "examples", "urls"):
    try:
        importlib.import_module(f"apps.core.api_docs.{sub}")
        check(f"  api_docs.{sub} importable", True)
    except ImportError as exc:
        check(f"  api_docs.{sub} importable", False, str(exc))


# ── 2. SPECTACULAR_SETTINGS ──────────────────────────────────────────
print("\n🔍  2. SPECTACULAR_SETTINGS configuration")

from django.conf import settings as django_settings  # noqa: E402

ss = getattr(django_settings, "SPECTACULAR_SETTINGS", None)
check("SPECTACULAR_SETTINGS exists", ss is not None)
if ss:
    check("  TITLE set", bool(ss.get("TITLE")))
    check("  VERSION set", bool(ss.get("VERSION")))
    check("  DESCRIPTION non-empty", len(ss.get("DESCRIPTION", "")) > 100)
    check("  CONTACT configured", "name" in ss.get("CONTACT", {}))
    check("  LICENSE configured", "name" in ss.get("LICENSE", {}))
    check("  SERVERS non-empty", len(ss.get("SERVERS", [])) >= 1)
    check("  TAGS non-empty", len(ss.get("TAGS", [])) >= 5)
    check("  SECURITY configured", len(ss.get("SECURITY", [])) >= 1)
    check(
        "  COMPONENT_SECURITY_SCHEMES has Bearer",
        "Bearer" in ss.get("COMPONENT_SECURITY_SCHEMES", {}),
    )
    check("  SERVE_INCLUDE_SCHEMA is False", ss.get("SERVE_INCLUDE_SCHEMA") is False)
    check("  SWAGGER_UI_SETTINGS present", isinstance(ss.get("SWAGGER_UI_SETTINGS"), dict))
    check("  REDOC_UI_SETTINGS present", isinstance(ss.get("REDOC_UI_SETTINGS"), dict))
    check(
        "  PREPROCESSING_HOOKS configured",
        len(ss.get("PREPROCESSING_HOOKS", [])) >= 1,
    )
    check(
        "  EXTENSIONS_INFO x-logo",
        "x-logo" in ss.get("EXTENSIONS_INFO", {}),
    )


# ── 3. INSTALLED_APPS ────────────────────────────────────────────────
print("\n🔍  3. INSTALLED_APPS")

installed = django_settings.INSTALLED_APPS
check("drf_spectacular in INSTALLED_APPS", "drf_spectacular" in installed)
check("drf_spectacular_sidecar in INSTALLED_APPS", "drf_spectacular_sidecar" in installed)


# ── 4. REST_FRAMEWORK schema class ───────────────────────────────────
print("\n🔍  4. REST_FRAMEWORK")

rf = getattr(django_settings, "REST_FRAMEWORK", {})
check(
    "DEFAULT_SCHEMA_CLASS is AutoSchema",
    rf.get("DEFAULT_SCHEMA_CLASS") == "drf_spectacular.openapi.AutoSchema",
)


# ── 5. URL patterns ──────────────────────────────────────────────────
print("\n🔍  5. URL configuration")

try:
    from apps.core.api_docs.urls import urlpatterns, app_name

    check("urlpatterns has 3 entries", len(urlpatterns) == 3)
    check("app_name == 'api_docs'", app_name == "api_docs")

    names = {p.name for p in urlpatterns}
    check("  'schema' URL present", "schema" in names)
    check("  'swagger-ui' URL present", "swagger-ui" in names)
    check("  'redoc' URL present", "redoc" in names)
except Exception as exc:
    check("URL configuration", False, str(exc))


# ── 6. Schema generation ─────────────────────────────────────────────
print("\n🔍  6. Schema generation")

try:
    from drf_spectacular.generators import SchemaGenerator

    generator = SchemaGenerator()
    schema = generator.get_schema(request=None, public=True)
    check("Schema generates without error", schema is not None)
    check("  has 'openapi' key", "openapi" in schema)
    check("  has 'info' key", "info" in schema)
    check("  has 'paths' key", "paths" in schema)

    json_str = json.dumps(schema, default=str)
    check("  serialises to JSON", len(json_str) > 0)
except Exception as exc:
    check("Schema generation", False, str(exc))


# ── 7. Extensions / schemas / examples ───────────────────────────────
print("\n🔍  7. Extensions, schemas, and examples")

from apps.core.api_docs.extensions import (  # noqa: E402
    AUTHENTICATION_DESCRIPTION,
    DESCRIPTION_SUPPLEMENT,
    TENANT_HEADER_PARAMETER,
    custom_preprocessing_hook,
)

check("custom_preprocessing_hook callable", callable(custom_preprocessing_hook))
check("TENANT_HEADER_PARAMETER defined", TENANT_HEADER_PARAMETER is not None)
check("AUTHENTICATION_DESCRIPTION non-empty", len(AUTHENTICATION_DESCRIPTION) > 50)
check("DESCRIPTION_SUPPLEMENT non-empty", len(DESCRIPTION_SUPPLEMENT) > 200)

from apps.core.api_docs.schemas import (  # noqa: E402
    ErrorResponseSerializer,
    PaginatedResponseSerializer,
    TokenResponseSerializer,
)

check("ErrorResponseSerializer exists", ErrorResponseSerializer is not None)
check("TokenResponseSerializer exists", TokenResponseSerializer is not None)
check("PaginatedResponseSerializer exists", PaginatedResponseSerializer is not None)

from apps.core.api_docs.examples import (  # noqa: E402
    LOGIN_REQUEST_EXAMPLE,
    LOGIN_RESPONSE_EXAMPLE,
    PRODUCT_RESPONSE_EXAMPLE,
)

check("LOGIN_REQUEST_EXAMPLE exists", LOGIN_REQUEST_EXAMPLE is not None)
check("LOGIN_RESPONSE_EXAMPLE exists", LOGIN_RESPONSE_EXAMPLE is not None)
check("PRODUCT_RESPONSE_EXAMPLE exists", PRODUCT_RESPONSE_EXAMPLE is not None)


# ── 8. Static assets ─────────────────────────────────────────────────
print("\n🔍  8. Static assets")

for name in ("custom.css", "logo.png", "logo.svg"):
    path = BASE_DIR / "static" / "api_docs" / name
    check(f"  {name} exists", path.exists())


# ── 9. Management command ─────────────────────────────────────────────
print("\n🔍  9. Management command")

try:
    importlib.import_module("apps.core.management.commands.validate_schema")
    check("validate_schema command importable", True)
except ImportError as exc:
    check("validate_schema command importable", False, str(exc))


# ── 10. Documentation files ──────────────────────────────────────────
print("\n🔍  10. Documentation files")

doc_checks = {
    "api_docs/README.md": BASE_DIR / "apps" / "core" / "api_docs" / "README.md",
    "docs/api_docs/decorators.md": BASE_DIR / "docs" / "api_docs" / "decorators.md",
    "docs/api_docs/extensions.md": BASE_DIR / "docs" / "api_docs" / "extensions.md",
}
for label, path in doc_checks.items():
    check(f"  {label}", path.exists())


# ── Summary ───────────────────────────────────────────────────────────
total = len(_passed) + len(_failed)
print(f"\n{'═' * 60}")
print(f"  Total checks:  {total}")
print(f"  Passed:        {len(_passed)}")
print(f"  Failed:        {len(_failed)}")
print(f"{'═' * 60}")

if _failed:
    print("\n⚠️  FAILED checks:")
    for f in _failed:
        print(f"    • {f}")
    sys.exit(1)
else:
    print("\n🎉  All SP11 API Documentation checks PASSED!")
    sys.exit(0)
