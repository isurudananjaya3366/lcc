#!/usr/bin/env python3
"""
LankaCommerce Cloud — Backend Environment Variable Validator

Standalone script to validate that all required, important, and optional
environment variables are present and correctly formatted before starting
the application.

Usage:
    python scripts/validate_env.py
    python scripts/validate_env.py --env-file .env.docker
    python scripts/validate_env.py --env-file backend/.env --strict
    python scripts/validate_env.py --strict   # production-level validation

Exit codes:
    0  All checks passed (or only warnings in non-strict mode)
    1  One or more required/important checks failed

Requires only Python standard library — no Django or django-environ needed.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

# ════════════════════════════════════════════════════════════════════════════════
# ANSI Colour Helpers
# ════════════════════════════════════════════════════════════════════════════════

# Respect NO_COLOR (https://no-color.org/) and dumb terminals.
_NO_COLOR = os.environ.get("NO_COLOR") is not None or os.environ.get("TERM") == "dumb"

# On Windows, enable ANSI escape sequences for the console.
if sys.platform == "win32" and not _NO_COLOR:
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
        # Enable ENABLE_VIRTUAL_TERMINAL_PROCESSING (0x0004) on stdout.
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass


def _c(code: str, text: str) -> str:
    """Wrap *text* in an ANSI colour code, unless colours are disabled."""
    if _NO_COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"


def green(text: str) -> str:
    return _c("32", text)


def red(text: str) -> str:
    return _c("31", text)


def yellow(text: str) -> str:
    return _c("33", text)


def bold(text: str) -> str:
    return _c("1", text)


def dim(text: str) -> str:
    return _c("2", text)


# ════════════════════════════════════════════════════════════════════════════════
# .env File Parser
# ════════════════════════════════════════════════════════════════════════════════

def parse_env_file(filepath: Path) -> dict[str, str]:
    """
    Parse a .env file into a dictionary.

    Supports:
      - KEY=VALUE
      - KEY="VALUE" / KEY='VALUE' (quoted values — quotes are stripped)
      - # comments and blank lines
      - Inline comments after unquoted values

    Does NOT expand ${VAR} references — keeps raw values for validation.
    """
    env_vars: dict[str, str] = {}
    if not filepath.is_file():
        return env_vars

    with filepath.open("r", encoding="utf-8") as fh:
        for raw_line in fh:
            line = raw_line.strip()

            # Skip blanks and comments.
            if not line or line.startswith("#"):
                continue

            # Must contain '=' to be a valid assignment.
            if "=" not in line:
                continue

            key, _, value = line.partition("=")
            key = key.strip()

            # Skip lines where the key is empty or looks invalid.
            if not key or not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", key):
                continue

            value = value.strip()

            # Handle quoted values (double or single quotes).
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            else:
                # Strip inline comments for unquoted values.
                comment_match = re.match(r"^([^#]*?)(\s+#.*)$", value)
                if comment_match:
                    value = comment_match.group(1).strip()

            env_vars[key] = value

    return env_vars


# ════════════════════════════════════════════════════════════════════════════════
# Validation Helpers
# ════════════════════════════════════════════════════════════════════════════════

# Insecure default that ships with env.py — must never be used in production.
_INSECURE_SECRET_KEY = "django-insecure-CHANGE-ME-IN-ENVIRONMENT-SETTINGS"

_POSTGRES_URL_RE = re.compile(
    r"^postgres(ql)?://"   # scheme
    r"[^:]+:[^@]+@"        # user:password@
    r"[^:/]+"              # host
    r"(:\d+)?"             # optional :port
    r"/\w+"                # /dbname
    r"(\?.*)?$"            # optional query string
)

_REDIS_URL_RE = re.compile(
    r"^rediss?://"         # scheme (redis:// or rediss://)
    r"([^:]+:[^@]+@)?"     # optional user:password@
    r"[^:/]+"              # host
    r"(:\d+)?"             # optional :port
    r"(/\d+)?"             # optional /db-number
    r"(\?.*)?$"            # optional query string
)

_SETTINGS_MODULE_RE = re.compile(
    r"^[a-zA-Z_][a-zA-Z0-9_]*"          # first segment
    r"(\.[a-zA-Z_][a-zA-Z0-9_]*)+$"     # at least one more dotted segment
)

_EMAIL_RE = re.compile(
    r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
)

_URL_RE = re.compile(
    r"^https?://.+"
)


# ════════════════════════════════════════════════════════════════════════════════
# Result Tracking
# ════════════════════════════════════════════════════════════════════════════════

class ValidationResult:
    """Accumulates pass / fail / warning counts and messages."""

    def __init__(self) -> None:
        self.passed: list[str] = []
        self.failed: list[str] = []
        self.warnings: list[str] = []

    # ── Recording helpers ───────────────────────────────────────────────

    def ok(self, var: str, detail: str = "") -> None:
        msg = f"  {green('✔')} {var}"
        if detail:
            msg += f"  {dim(detail)}"
        self.passed.append(msg)

    def fail(self, var: str, reason: str) -> None:
        msg = f"  {red('✘')} {var}  — {reason}"
        self.failed.append(msg)

    def warn(self, var: str, reason: str) -> None:
        msg = f"  {yellow('⚠')} {var}  — {reason}"
        self.warnings.append(msg)

    # ── Output ──────────────────────────────────────────────────────────

    def print_all(self) -> None:
        for line in self.passed + self.warnings + self.failed:
            print(line)

    def print_summary(self) -> None:
        parts = [
            green(f"{len(self.passed)} passed"),
            red(f"{len(self.failed)} failed"),
            yellow(f"{len(self.warnings)} warnings"),
        ]
        print(f"\n{'─' * 60}")
        print(f"  Summary: {', '.join(parts)}")
        print(f"{'─' * 60}")

    @property
    def success(self) -> bool:
        return len(self.failed) == 0


# ════════════════════════════════════════════════════════════════════════════════
# Core Validation Logic
# ════════════════════════════════════════════════════════════════════════════════

def _get(env: dict[str, str], key: str) -> str | None:
    """Return the value for *key* or ``None`` if missing/empty."""
    val = env.get(key)
    if val is None or val.strip() == "":
        return None
    return val.strip()


def validate_required(env: dict[str, str], strict: bool, result: ValidationResult) -> None:
    """Validate variables that **must** be set (especially in production)."""

    print(f"\n{bold('Required Variables')}")
    print(f"{'─' * 60}")

    # ── DJANGO_SECRET_KEY ───────────────────────────────────────────────
    key = "DJANGO_SECRET_KEY"
    val = _get(env, key)
    if val is None:
        result.fail(key, "not set — a secret key is required")
    elif strict and val == _INSECURE_SECRET_KEY:
        result.fail(key, "still using the insecure default value")
    elif val == _INSECURE_SECRET_KEY:
        result.warn(key, "using the insecure default — change before production")
    elif strict and len(val) < 32:
        result.fail(key, f"too short ({len(val)} chars) — use ≥ 32 characters")
    else:
        result.ok(key)

    # ── DATABASE_URL ────────────────────────────────────────────────────
    key = "DATABASE_URL"
    val = _get(env, key)
    if val is None:
        result.fail(key, "not set — a PostgreSQL database URL is required")
    elif not _POSTGRES_URL_RE.match(val):
        result.fail(key, f"invalid format — expected postgres://user:pass@host/dbname, got: {val[:60]}")
    else:
        result.ok(key)

    # ── DJANGO_SETTINGS_MODULE ──────────────────────────────────────────
    key = "DJANGO_SETTINGS_MODULE"
    val = _get(env, key)
    if val is None:
        if strict:
            result.fail(key, "not set — must be a dotted Python settings path")
        else:
            result.warn(key, "not set — will default to config.settings.local")
    elif not _SETTINGS_MODULE_RE.match(val):
        result.fail(key, f"invalid settings path: {val}")
    else:
        result.ok(key, f"({val})")


def validate_important(env: dict[str, str], strict: bool, result: ValidationResult) -> None:
    """Validate variables that should be set but may fall back to defaults."""

    print(f"\n{bold('Important Variables')}")
    print(f"{'─' * 60}")

    # ── DEBUG ───────────────────────────────────────────────────────────
    key = "DEBUG"
    val = _get(env, key)
    allowed_bools = {"true", "false", "1", "0", "yes", "no", "on", "off"}
    if val is None:
        result.warn(key, "not set — defaults to False")
    elif val.lower() not in allowed_bools:
        result.fail(key, f"invalid boolean value: {val}")
    else:
        if strict and val.lower() in ("true", "1", "yes", "on"):
            result.fail(key, "DEBUG is True — must be False in production (--strict mode)")
        else:
            result.ok(key, f"({val})")

    # ── ALLOWED_HOSTS ───────────────────────────────────────────────────
    key = "ALLOWED_HOSTS"
    # Check both ALLOWED_HOSTS and DJANGO_ALLOWED_HOSTS (used in .env.docker)
    val = _get(env, key) or _get(env, "DJANGO_ALLOWED_HOSTS")
    if val is None:
        if strict:
            result.fail(key, "not set — must specify allowed hosts in production")
        else:
            result.warn(key, "not set — defaults to empty list (Django will reject all requests)")
    elif strict and "*" in val:
        result.fail(key, "wildcard '*' is not allowed in production (--strict mode)")
    else:
        hosts = [h.strip() for h in val.split(",") if h.strip()]
        result.ok(key, f"({len(hosts)} host(s))")

    # ── REDIS_URL ───────────────────────────────────────────────────────
    key = "REDIS_URL"
    val = _get(env, key)
    if val is None:
        result.warn(key, "not set — defaults to redis://localhost:6379/0")
    elif not _REDIS_URL_RE.match(val):
        result.fail(key, f"invalid Redis URL format: {val[:60]}")
    else:
        result.ok(key)

    # ── CELERY_BROKER_URL ───────────────────────────────────────────────
    key = "CELERY_BROKER_URL"
    val = _get(env, key)
    if val is None:
        result.warn(key, "not set — defaults to redis://localhost:6379/0")
    elif not _REDIS_URL_RE.match(val):
        result.fail(key, f"invalid Redis URL format: {val[:60]}")
    else:
        result.ok(key)

    # ── CELERY_RESULT_BACKEND ───────────────────────────────────────────
    key = "CELERY_RESULT_BACKEND"
    val = _get(env, key)
    if val is None:
        result.warn(key, "not set — defaults to redis://localhost:6379/0")
    elif not _REDIS_URL_RE.match(val):
        result.fail(key, f"invalid Redis URL format: {val[:60]}")
    else:
        result.ok(key)


def validate_optional(env: dict[str, str], _strict: bool, result: ValidationResult) -> None:
    """Validate optional variables — only checked when present."""

    print(f"\n{bold('Optional Variables')}")
    print(f"{'─' * 60}")

    # ── EMAIL_HOST_USER ─────────────────────────────────────────────────
    key = "EMAIL_HOST_USER"
    val = _get(env, key)
    if val is None:
        result.ok(key, "(not set — skipped)")
    elif not _EMAIL_RE.match(val):
        result.warn(key, f"does not look like a valid email: {val}")
    else:
        result.ok(key)

    # ── EMAIL_PORT ──────────────────────────────────────────────────────
    key = "EMAIL_PORT"
    val = _get(env, key)
    if val is None:
        result.ok(key, "(not set — defaults to 587)")
    else:
        try:
            port = int(val)
            if not 1 <= port <= 65535:
                raise ValueError
            result.ok(key, f"({port})")
        except ValueError:
            result.fail(key, f"must be an integer 1–65535, got: {val}")

    # ── SENTRY_DSN ──────────────────────────────────────────────────────
    key = "SENTRY_DSN"
    val = _get(env, key)
    if val is None:
        result.ok(key, "(not set — Sentry disabled)")
    elif not _URL_RE.match(val):
        result.fail(key, f"must be a valid URL, got: {val[:60]}")
    else:
        result.ok(key)

    # ── JWT_ACCESS_TOKEN_LIFETIME_MINUTES ───────────────────────────────
    key = "JWT_ACCESS_TOKEN_LIFETIME_MINUTES"
    val = _get(env, key)
    if val is None:
        result.ok(key, "(not set — defaults to 30)")
    else:
        try:
            minutes = int(val)
            if minutes <= 0:
                raise ValueError
            result.ok(key, f"({minutes} min)")
        except ValueError:
            result.fail(key, f"must be a positive integer, got: {val}")

    # ── JWT_REFRESH_TOKEN_LIFETIME_DAYS ─────────────────────────────────
    key = "JWT_REFRESH_TOKEN_LIFETIME_DAYS"
    val = _get(env, key)
    if val is None:
        result.ok(key, "(not set — defaults to 7)")
    else:
        try:
            days = int(val)
            if days <= 0:
                raise ValueError
            result.ok(key, f"({days} day(s))")
        except ValueError:
            result.fail(key, f"must be a positive integer, got: {val}")

    # ── SENTRY_TRACES_SAMPLE_RATE ───────────────────────────────────────
    key = "SENTRY_TRACES_SAMPLE_RATE"
    val = _get(env, key)
    if val is None:
        result.ok(key, "(not set — defaults to 0.1)")
    else:
        try:
            rate = float(val)
            if not 0.0 <= rate <= 1.0:
                raise ValueError
            result.ok(key, f"({rate})")
        except ValueError:
            result.fail(key, f"must be a float between 0.0 and 1.0, got: {val}")

    # ── STRIPE_SECRET_KEY ───────────────────────────────────────────────
    key = "STRIPE_SECRET_KEY"
    val = _get(env, key)
    if val is None:
        result.ok(key, "(not set — Stripe disabled)")
    elif not val.startswith("sk_"):
        result.fail(key, f"must start with 'sk_', got: {val[:10]}...")
    else:
        result.ok(key, f"({val[:7]}...)")

    # ── STRIPE_PUBLISHABLE_KEY ──────────────────────────────────────────
    key = "STRIPE_PUBLISHABLE_KEY"
    val = _get(env, key)
    if val is None:
        result.ok(key, "(not set — Stripe disabled)")
    elif not val.startswith("pk_"):
        result.fail(key, f"must start with 'pk_', got: {val[:10]}...")
    else:
        result.ok(key, f"({val[:7]}...)")


# ════════════════════════════════════════════════════════════════════════════════
# CLI & Entry Point
# ════════════════════════════════════════════════════════════════════════════════

def resolve_env_files(custom_path: str | None) -> list[Path]:
    """
    Determine which .env files to load, in priority order (later wins).

    Default search order (when no custom path is given):
        1. <project_root>/.env.docker
        2. <project_root>/backend/.env
    """
    project_root = Path(__file__).resolve().parent.parent

    if custom_path:
        p = Path(custom_path)
        # Resolve relative paths against the project root.
        if not p.is_absolute():
            p = project_root / p
        return [p]

    # Default search order — later file values override earlier ones.
    candidates = [
        project_root / ".env.docker",
        project_root / "backend" / ".env",
    ]
    return [c for c in candidates if c.is_file()]


def load_env(files: list[Path]) -> dict[str, str]:
    """
    Merge environment variables from multiple .env files.

    Values from later files override earlier ones, matching the behaviour
    of docker-compose and django-environ.
    """
    merged: dict[str, str] = {}
    for f in files:
        merged.update(parse_env_file(f))
    return merged


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate backend environment variables for LankaCommerce Cloud.",
    )
    parser.add_argument(
        "--env-file",
        dest="env_file",
        default=None,
        help="Path to a specific .env file to validate (default: auto-detect).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Enable production-level strict validation.",
    )
    args = parser.parse_args(argv)

    # ── Header ──────────────────────────────────────────────────────────
    print()
    print(bold("╔══════════════════════════════════════════════════════════╗"))
    print(bold("║   LankaCommerce Cloud — Environment Validator           ║"))
    print(bold("╚══════════════════════════════════════════════════════════╝"))

    mode = "STRICT (production)" if args.strict else "standard (development)"
    print(f"\n  Mode: {bold(mode)}")

    # ── Load .env files ─────────────────────────────────────────────────
    env_files = resolve_env_files(args.env_file)

    if not env_files:
        print(red("\n  ✘ No .env files found to validate."))
        print(dim("    Searched: .env.docker (project root), backend/.env"))
        print(dim("    Use --env-file PATH to specify a custom file.\n"))
        return 1

    for ef in env_files:
        print(f"  Loading: {dim(str(ef))}")

    env = load_env(env_files)

    if not env:
        print(red("\n  ✘ Env file(s) found but no variables were parsed."))
        return 1

    print(f"  Variables loaded: {bold(str(len(env)))}")

    # ── Run validations ─────────────────────────────────────────────────
    result = ValidationResult()

    validate_required(env, args.strict, result)
    validate_important(env, args.strict, result)
    validate_optional(env, args.strict, result)

    # ── Print collected messages & summary ──────────────────────────────
    result.print_all()
    result.print_summary()

    if result.success:
        print(f"\n  {green('✔ All checks passed!')}\n")
    else:
        print(f"\n  {red('✘ Validation failed — fix the errors above.')}\n")

    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
