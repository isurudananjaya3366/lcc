"""
Management command for non-interactive superuser creation.

Uses environment variables for credentials, making it safe for
Docker entrypoints and CI/CD pipelines.

Usage:
    python manage.py create_superuser
    python manage.py create_superuser --email admin@example.com --password secret

Environment Variables:
    DJANGO_SUPERUSER_EMAIL       - Superuser email (required)
    DJANGO_SUPERUSER_PASSWORD    - Superuser password (required)
    DJANGO_SUPERUSER_FIRST_NAME  - First name (default: 'Admin')
    DJANGO_SUPERUSER_LAST_NAME   - Last name (default: 'User')
"""

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Create a superuser non-interactively using environment variables."""

    help = (
        "Create a superuser non-interactively from environment variables "
        "or command-line arguments. Idempotent — skips if user already exists."
    )

    def add_arguments(self, parser):
        """Add command arguments for overriding environment variables."""
        parser.add_argument(
            "--email",
            type=str,
            help="Override DJANGO_SUPERUSER_EMAIL environment variable.",
        )
        parser.add_argument(
            "--password",
            type=str,
            help="Override DJANGO_SUPERUSER_PASSWORD environment variable.",
        )
        parser.add_argument(
            "--no-input",
            action="store_true",
            default=True,
            help="Skip interactive prompts (default behavior).",
        )

    def handle(self, *args, **options):
        """Create the superuser if one does not already exist."""
        User = get_user_model()  # noqa: N806

        # Get credentials from args or environment variables
        email = options.get("email") or os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = options.get("password") or os.environ.get(
            "DJANGO_SUPERUSER_PASSWORD"
        )
        first_name = os.environ.get("DJANGO_SUPERUSER_FIRST_NAME", "Admin")
        last_name = os.environ.get("DJANGO_SUPERUSER_LAST_NAME", "User")

        # Validate required fields
        if not email or not password:
            self.stderr.write(
                self.style.ERROR(
                    "Email and password required. Set DJANGO_SUPERUSER_EMAIL "
                    "and DJANGO_SUPERUSER_PASSWORD environment variables, "
                    "or use --email and --password arguments."
                )
            )
            raise SystemExit(1)

        # Check if user already exists (idempotent)
        try:
            if User.objects.filter(email=email).exists():
                self.stdout.write(
                    self.style.WARNING("Superuser already exists, skipping")
                )
                return
        except Exception:
            # Table may not exist yet if migrations haven't run
            # or the User model uses a different lookup field
            pass

        # Create the superuser
        # NOTE: When multi-tenancy is enabled, wrap with schema_context('public')
        # from django_tenants.utils import schema_context
        # with schema_context('public'):
        #     User.objects.create_superuser(...)
        try:
            User.objects.create_superuser(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
            self.stdout.write(
                self.style.SUCCESS("Superuser created successfully")
            )
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"Failed to create superuser: {e}")
            )
            raise SystemExit(1)
