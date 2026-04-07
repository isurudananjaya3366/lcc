"""
Management command to create a platform admin user.

Creates a new PlatformUser with the platform_admin role and staff
access to the Django admin interface. This command provides an
interactive way to bootstrap platform admin accounts without
requiring superuser-level create_superuser.

Usage:
    python manage.py create_platform_admin

Required inputs:
    - Email address (unique, used as login identifier)
    - Password (minimum 8 characters, validated against all
      configured password validators)
    - First name (optional)
    - Last name (optional)
    - Role (defaults to platform_admin, can be set to support
      or viewer)

The command validates all inputs before creating the user and
provides clear error messages for invalid data. It sets is_staff
to True so the created user can access the Django admin interface.

Schema: public (shared)
Model: PlatformUser (AUTH_USER_MODEL)
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from apps.platform.models.user import (
    PLATFORM_ROLE_CHOICES,
    ROLE_PLATFORM_ADMIN,
    ROLE_SUPER_ADMIN,
)

UserModel = get_user_model()

# Roles that can be created with this command (excludes super_admin)
ALLOWED_ROLES = [
    choice for choice in PLATFORM_ROLE_CHOICES
    if choice[0] != ROLE_SUPER_ADMIN
]
ALLOWED_ROLE_VALUES = [choice[0] for choice in ALLOWED_ROLES]


class Command(BaseCommand):
    """
    Create a platform admin user with email-based authentication.

    This command creates a new PlatformUser with staff access and
    an assigned platform role. It is designed for creating admin
    accounts that do not need superuser privileges.

    For creating superusers, use Django's built-in createsuperuser
    management command instead, which automatically assigns the
    super_admin role.
    """

    help = (
        "Create a platform admin user with staff access and an "
        "assigned role (platform_admin, support, or viewer)."
    )

    def add_arguments(self, parser):
        """Add command-line arguments for non-interactive usage."""
        parser.add_argument(
            "--email",
            type=str,
            help="Email address for the new platform admin.",
        )
        parser.add_argument(
            "--role",
            type=str,
            choices=ALLOWED_ROLE_VALUES,
            default=ROLE_PLATFORM_ADMIN,
            help=(
                "Platform role to assign. Defaults to platform_admin. "
                "Options: platform_admin, support, viewer."
            ),
        )
        parser.add_argument(
            "--first-name",
            type=str,
            default="",
            help="First name of the user (optional).",
        )
        parser.add_argument(
            "--last-name",
            type=str,
            default="",
            help="Last name of the user (optional).",
        )
        parser.add_argument(
            "--noinput",
            "--no-input",
            action="store_false",
            dest="interactive",
            help="Run in non-interactive mode (requires --email).",
        )

    def handle(self, *args, **options):
        """Execute the command to create a platform admin user."""
        email = options.get("email")
        role = options.get("role") or ROLE_PLATFORM_ADMIN
        first_name = options.get("first_name") or ""
        last_name = options.get("last_name") or ""
        interactive = options.get("interactive", True)

        if interactive:
            email, role, first_name, last_name = self._get_interactive_input(
                email, role, first_name, last_name,
            )

        if not email:
            raise CommandError("Email address is required.")

        # Validate email uniqueness
        email = UserModel.objects.normalize_email(email)
        if UserModel.objects.filter(email__iexact=email).exists():
            raise CommandError(
                f"A user with email '{email}' already exists."
            )

        # Validate role
        if role not in ALLOWED_ROLE_VALUES:
            raise CommandError(
                f"Invalid role '{role}'. Allowed: "
                f"{', '.join(ALLOWED_ROLE_VALUES)}"
            )

        # Get password
        if interactive:
            password = self._get_password()
        else:
            raise CommandError(
                "Non-interactive mode requires using createsuperuser "
                "or setting password after creation."
            )

        # Create the user
        try:
            user = UserModel.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role,
                is_staff=True,
            )
        except Exception as e:
            raise CommandError(f"Failed to create user: {e}")

        role_display = dict(PLATFORM_ROLE_CHOICES).get(role, role)
        self.stdout.write(
            self.style.SUCCESS(
                f"\nPlatform admin created successfully:\n"
                f"  Email: {user.email}\n"
                f"  Role:  {role_display}\n"
                f"  Name:  {user.full_name or '(not set)'}\n"
                f"  Staff: True\n"
                f"  ID:    {user.id}\n"
            )
        )

    def _get_interactive_input(self, email, role, first_name, last_name):
        """Prompt user for input in interactive mode."""
        self.stdout.write(
            self.style.NOTICE("\n=== Create Platform Admin ===\n")
        )

        if not email:
            while True:
                email = input("Email address: ").strip()
                if email:
                    break
                self.stderr.write(
                    self.style.ERROR("Email address is required.")
                )

        # Role selection
        self.stdout.write("\nAvailable roles:")
        for value, label in ALLOWED_ROLES:
            marker = " (default)" if value == ROLE_PLATFORM_ADMIN else ""
            self.stdout.write(f"  - {value}: {label}{marker}")

        role_input = input(
            f"\nRole [{ROLE_PLATFORM_ADMIN}]: "
        ).strip()
        if role_input:
            role = role_input

        if not first_name:
            first_name = input("First name (optional): ").strip()

        if not last_name:
            last_name = input("Last name (optional): ").strip()

        return email, role, first_name, last_name

    def _get_password(self):
        """Prompt for password with validation and confirmation."""
        import getpass

        while True:
            password = getpass.getpass("Password: ")
            password_confirm = getpass.getpass("Password (again): ")

            if password != password_confirm:
                self.stderr.write(
                    self.style.ERROR("Passwords do not match. Try again.")
                )
                continue

            try:
                validate_password(password)
            except ValidationError as e:
                self.stderr.write(
                    self.style.ERROR("Password validation failed:")
                )
                for message in e.messages:
                    self.stderr.write(f"  - {message}")
                continue

            return password
