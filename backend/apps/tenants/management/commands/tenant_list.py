"""
Management command: tenant_list

Lists all tenants in LankaCommerce Cloud with their details.

Usage:
    python manage.py tenant_list
    python manage.py tenant_list --status active
    python manage.py tenant_list --verbose

Output Fields:
    ID          - Database primary key
    Schema      - PostgreSQL schema name
    Name        - Human-readable business name
    Slug        - URL-safe identifier
    Status      - Lifecycle state (active/suspended/archived)
    Domains     - Associated domain names
    Created     - Creation timestamp

Optional Arguments:
    --status    Filter by tenant status (active, suspended, archived)
    --verbose   Show additional details (trial status, paid_until, settings)
"""

from django.core.management.base import BaseCommand

from apps.tenants.models import Domain, Tenant


class Command(BaseCommand):
    help = "List all tenants with their details and domains."

    def add_arguments(self, parser):
        parser.add_argument(
            "--status",
            default=None,
            choices=["active", "suspended", "archived"],
            help="Filter tenants by status.",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            default=False,
            help="Show additional tenant details.",
        )

    def handle(self, *args, **options):
        status_filter = options["status"]
        verbose = options["verbose"]

        queryset = Tenant.objects.all().order_by("id")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        tenant_count = queryset.count()

        if tenant_count == 0:
            self.stdout.write(self.style.WARNING("No tenants found."))
            return

        # Header
        self.stdout.write("")
        self.stdout.write("=" * 80)
        self.stdout.write(f"  LankaCommerce Cloud — Tenant List ({tenant_count} tenants)")
        self.stdout.write("=" * 80)

        for tenant in queryset:
            domains = Domain.objects.filter(tenant=tenant).order_by("-is_primary")
            domain_list = ", ".join(
                f"{d.domain}{'*' if d.is_primary else ''}" for d in domains
            )

            self.stdout.write("")
            self.stdout.write(f"  [{tenant.pk}] {tenant.name}")
            self.stdout.write(f"      Schema:   {tenant.schema_name}")
            self.stdout.write(f"      Slug:     {tenant.slug}")
            self.stdout.write(f"      Status:   {tenant.status}")
            self.stdout.write(f"      Domains:  {domain_list or '(none)'}")
            self.stdout.write(f"      Created:  {tenant.created_on:%Y-%m-%d %H:%M UTC}")

            if verbose:
                self.stdout.write(f"      On Trial: {tenant.on_trial}")
                self.stdout.write(f"      Paid Until: {tenant.paid_until or 'N/A'}")
                self.stdout.write(f"      Public:   {tenant.is_public}")
                if tenant.settings:
                    settings_str = ", ".join(
                        f"{k}={v}" for k, v in tenant.settings.items()
                    )
                    self.stdout.write(f"      Settings: {settings_str}")

        self.stdout.write("")
        self.stdout.write("-" * 80)
        self.stdout.write(f"  Total: {tenant_count} tenant(s)")
        if status_filter:
            self.stdout.write(f"  Filter: status={status_filter}")
        self.stdout.write(f"  (* = primary domain)")
        self.stdout.write("-" * 80)
        self.stdout.write("")
