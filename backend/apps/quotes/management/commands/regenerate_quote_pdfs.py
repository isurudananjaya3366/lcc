"""
Management command to regenerate PDF files for existing quotes.

Task 67: Bulk PDF regeneration management command.

Usage:
    python manage.py regenerate_quote_pdfs              # all that need it
    python manage.py regenerate_quote_pdfs --force       # regenerate all
    python manage.py regenerate_quote_pdfs --quote QT-2026-00001  # single
    python manage.py regenerate_quote_pdfs --status sent  # by status
"""

import logging

from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Regenerate PDF files for quotes"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Regenerate all PDFs, even if they are up to date",
        )
        parser.add_argument(
            "--quote",
            type=str,
            help="Regenerate PDF for a specific quote number",
        )
        parser.add_argument(
            "--status",
            type=str,
            help="Regenerate PDFs for quotes with this status",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be regenerated without doing it",
        )

    def handle(self, *args, **options):
        from apps.quotes.models import Quote
        from apps.quotes.services.pdf_generator import QuotePDFGenerator

        qs = Quote.objects.all()

        if options["quote"]:
            qs = qs.filter(quote_number=options["quote"])
        if options["status"]:
            qs = qs.filter(status=options["status"])

        total = qs.count()
        self.stdout.write(f"Found {total} quote(s) to process.")

        if options["dry_run"]:
            for q in qs.iterator():
                needs = q.needs_regeneration or options["force"]
                tag = "REGENERATE" if needs else "SKIP"
                self.stdout.write(f"  [{tag}] {q.quote_number}")
            return

        success = 0
        errors = 0

        for quote in qs.iterator():
            if not options["force"] and not quote.needs_regeneration:
                self.stdout.write(f"  [SKIP] {quote.quote_number} — up to date")
                continue

            try:
                generator = QuotePDFGenerator(quote)
                path = generator.generate_and_save()
                success += 1
                self.stdout.write(
                    self.style.SUCCESS(f"  [OK] {quote.quote_number} → {path}")
                )
            except Exception as exc:
                errors += 1
                self.stderr.write(
                    self.style.ERROR(f"  [ERR] {quote.quote_number} — {exc}")
                )
                logger.exception("PDF regeneration failed for %s", quote.quote_number)

        self.stdout.write(
            self.style.SUCCESS(f"\nDone: {success} succeeded, {errors} failed out of {total}.")
        )
