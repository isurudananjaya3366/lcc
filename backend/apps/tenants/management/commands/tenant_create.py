"""
Management command: tenant_create

Creates a new tenant with its primary domain in LankaCommerce Cloud.

Usage:
    python manage.py tenant_create --name "Acme Trading" --slug "acme-trading"
    python manage.py tenant_create --name "Best Shop" --slug "best-shop" --domain "best.localhost"

Required Arguments:
    --name      Human-readable business name
    --slug      URL-safe identifier (lowercase, digits, hyphens)

Optional Arguments:
    --domain    Primary domain (default: <slug>.localhost)
    --paid-until  Subscription expiry date (YYYY-MM-DD)
    --no-trial    Disable trial mode (default: on trial)
    --status      Tenant status: active, suspended, archived (default: active)

Validation Rules:
    - Slug must match: ^[a-z0-9](?:[a-z0-9]|-(?=[a-z0-9]))*$
    - Slug must not be a reserved schema name (public, pg_catalog, etc.)
    - Generated schema name must not exceed 63 characters
    - Slug must be unique across all tenants
"""

from datetime import datetime

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from apps.tenants.models import Domain, Tenant


class Command(BaseCommand):
    help = "Create a new tenant with its primary domain."

    def add_arguments(self, parser):
        parser.add_argument(
            "--name",
            required=True,
            help="Human-readable business name (e.g. 'Acme Trading Pvt Ltd').",
        )
        parser.add_argument(
            "--slug",
            required=True,
            help=(
                "URL-safe tenant identifier. Lowercase letters, digits, "
                "and hyphens only. Used for schema naming and subdomains."
            ),
        )
        parser.add_argument(
            "--domain",
            default=None,
            help=(
                "Primary domain for the tenant. "
                "Defaults to <slug>.localhost for development."
            ),
        )
        parser.add_argument(
            "--paid-until",
            default=None,
            help="Subscription expiry date in YYYY-MM-DD format.",
        )
        parser.add_argument(
            "--no-trial",
            action="store_true",
            default=False,
            help="Create tenant with trial mode disabled.",
        )
        parser.add_argument(
            "--status",
            default="active",
            choices=["active", "suspended", "archived"],
            help="Initial tenant status (default: active).",
        )

    def handle(self, *args, **options):
        name = options["name"]
        slug = options["slug"]
        domain_value = options["domain"] or f"{slug}.localhost"
        paid_until = options["paid_until"]
        on_trial = not options["no_trial"]
        status = options["status"]

        # Parse paid_until date if provided
        paid_until_date = None
        if paid_until:
            try:
                paid_until_date = datetime.strptime(paid_until, "%Y-%m-%d").date()
            except ValueError:
                raise CommandError(
                    f"Invalid date format: '{paid_until}'. Use YYYY-MM-DD."
                )

        # Check for duplicate slug
        if Tenant.objects.filter(slug=slug).exists():
            raise CommandError(f"A tenant with slug '{slug}' already exists.")

        # Check for duplicate domain
        if Domain.objects.filter(domain=domain_value).exists():
            raise CommandError(
                f"A domain '{domain_value}' is already assigned to another tenant."
            )

        self.stdout.write(f"Creating tenant '{name}' (slug: {slug})...")

        try:
            # Create tenant (auto_create_schema=True will create the
            # PostgreSQL schema and run TENANT_APPS migrations)
            tenant = Tenant(
                name=name,
                slug=slug,
                on_trial=on_trial,
                status=status,
                paid_until=paid_until_date,
                settings={
                    "currency": "LKR",
                    "timezone": "Asia/Colombo",
                    "date_format": "YYYY-MM-DD",
                    "language": "en",
                },
            )
            tenant.save()

        except ValidationError as e:
            raise CommandError(f"Validation error: {e}")

        self.stdout.write(
            self.style.SUCCESS(f"Tenant created successfully!")
        )
        self.stdout.write(f"  Name:        {tenant.name}")
        self.stdout.write(f"  Slug:        {tenant.slug}")
        self.stdout.write(f"  Schema:      {tenant.schema_name}")
        self.stdout.write(f"  Status:      {tenant.status}")
        self.stdout.write(f"  On Trial:    {tenant.on_trial}")
        self.stdout.write(f"  Paid Until:  {tenant.paid_until or 'N/A'}")

        # Create primary domain
        try:
            domain = Domain.objects.create(
                domain=domain_value,
                tenant=tenant,
                is_primary=True,
            )
        except Exception as e:
            raise CommandError(
                f"Tenant created but domain creation failed: {e}"
            )

        self.stdout.write(
            self.style.SUCCESS(f"Domain created successfully!")
        )
        self.stdout.write(f"  Domain:      {domain.domain}")
        self.stdout.write(f"  Is Primary:  {domain.is_primary}")

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Tenant '{name}' is ready at schema '{tenant.schema_name}'."
            )
        )
