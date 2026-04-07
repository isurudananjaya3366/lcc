"""
Management command to clear application caches.

Usage::

    python manage.py clearcache                 # clear default cache
    python manage.py clearcache --alias sessions
    python manage.py clearcache --pattern "products:*"
    python manage.py clearcache --all
"""

from django.core.cache import caches
from django.core.management.base import BaseCommand

from apps.core.cache.invalidation import CacheInvalidator
from apps.core.cache.utils import clear_cache


class Command(BaseCommand):
    help = "Clear application cache (default, sessions, or all)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--alias",
            type=str,
            default="default",
            help="Cache alias to clear (default: 'default')",
        )
        parser.add_argument(
            "--pattern",
            type=str,
            default=None,
            help="Only delete keys matching this pattern (e.g. 'products:*')",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            dest="clear_all",
            help="Clear ALL cache aliases",
        )
        parser.add_argument(
            "--tenant",
            action="store_true",
            dest="tenant_only",
            help="Clear only the current tenant's cache",
        )
        parser.add_argument(
            "--model",
            type=str,
            default=None,
            help="Clear cache for a specific model (e.g. 'products.Product')",
        )

    def handle(self, *args, **options):
        if options["clear_all"]:
            for alias in caches:
                caches[alias].clear()
                self.stdout.write(self.style.SUCCESS(f"Cleared cache alias: {alias}"))
            return

        if options["tenant_only"]:
            CacheInvalidator.invalidate_tenant_cache()
            self.stdout.write(self.style.SUCCESS("Cleared current tenant cache"))
            return

        if options["model"]:
            from django.apps import apps as django_apps

            try:
                model_class = django_apps.get_model(options["model"])
                count = CacheInvalidator.invalidate_model(model_class)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Invalidated cache for {options['model']} ({count} keys)"
                    )
                )
            except LookupError:
                self.stderr.write(
                    self.style.ERROR(f"Model not found: {options['model']}")
                )
            return

        alias = options["alias"]
        pattern = options["pattern"]

        success = clear_cache(cache_alias=alias, pattern=pattern)
        if success:
            msg = f"Cache cleared (alias={alias}"
            if pattern:
                msg += f", pattern={pattern}"
            msg += ")"
            self.stdout.write(self.style.SUCCESS(msg))
        else:
            self.stderr.write(self.style.ERROR(f"Failed to clear cache alias: {alias}"))
