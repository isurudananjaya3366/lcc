"""
Management command to clean up orphaned media files (SP10 Task 74).

Orphaned files are files that exist in storage but are no longer
referenced by any Django model.  This command wraps
:class:`apps.core.storage.cleanup.FileCleanup`.

Usage::

    # Preview orphaned files (dry-run, safe)
    python manage.py cleanmedia

    # Preview with custom age threshold
    python manage.py cleanmedia --min-age-days 30

    # Preview for a specific tenant
    python manage.py cleanmedia --tenant shop123

    # Actually delete orphaned files (requires confirmation)
    python manage.py cleanmedia --force

    # Delete files older than 30 days
    python manage.py cleanmedia --force --min-age-days 30

    # Clean specific storage path
    python manage.py cleanmedia --force --path tenant-shop123/products/
"""

from __future__ import annotations

import logging

from django.core.management.base import BaseCommand, CommandError

from apps.core.storage.cleanup import FileCleanup

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Find and optionally delete orphaned media files that are no "
        "longer referenced by any database record."
    )

    # ────────────────────────────────────────────────────────────────────
    # CLI arguments
    # ────────────────────────────────────────────────────────────────────

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=True,
            help="Preview files without deleting (default behaviour).",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            default=False,
            help="Actually delete orphaned files (disables dry-run).",
        )
        parser.add_argument(
            "--path",
            type=str,
            default="",
            help="Storage sub-path to scan (default: root).",
        )
        parser.add_argument(
            "--min-age-days",
            type=int,
            default=7,
            help="Minimum file age in days before considering orphaned "
                 "(default: 7).",
        )
        parser.add_argument(
            "--tenant",
            type=str,
            default="",
            help="Clean a specific tenant only (schema name).",
        )

    # ────────────────────────────────────────────────────────────────────
    # Command handler
    # ────────────────────────────────────────────────────────────────────

    def handle(self, *args, **options):
        dry_run: bool = not options["force"]
        path: str = options["path"]
        min_age_days: int = options["min_age_days"]
        tenant: str = options["tenant"]

        # Build tenant-scoped path when requested
        if tenant:
            path = f"tenant-{tenant}/"

        # ── Banner ──────────────────────────────────────────────────────
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "\n=== DRY RUN MODE ===\n"
                    "No files will be deleted. "
                    "Use --force to actually delete files.\n"
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    "\n=== LIVE MODE ===\n"
                    "Files will be PERMANENTLY DELETED!\n"
                )
            )

        self.stdout.write(f"Path:        {path or '(root)'}")
        self.stdout.write(f"Minimum age: {min_age_days} days")
        self.stdout.write("")

        # ── Confirmation for live mode ──────────────────────────────────
        if not dry_run:
            confirm = input(
                'Are you sure you want to delete files? '
                'Type "yes" to confirm: '
            )
            if confirm.strip().lower() != "yes":
                self.stdout.write(self.style.WARNING("Operation cancelled."))
                return

        # ── Run cleanup ─────────────────────────────────────────────────
        try:
            cleanup = FileCleanup(dry_run=dry_run)

            self.stdout.write("Scanning for orphaned files …")
            orphaned_files = cleanup.find_orphaned_files(path, min_age_days)

            if not orphaned_files:
                self.stdout.write(
                    self.style.SUCCESS("\nNo orphaned files found!")
                )
                return

            # Show preview (first 20 files)
            self.stdout.write(
                self.style.WARNING(
                    f"\nFound {len(orphaned_files)} orphaned file(s):"
                )
            )
            preview_limit = 20
            for fp in orphaned_files[:preview_limit]:
                try:
                    size = cleanup.storage.size(fp)
                    size_kb = size / 1024
                    self.stdout.write(f"  - {fp}  ({size_kb:.2f} KB)")
                except Exception:
                    self.stdout.write(f"  - {fp}")

            remaining = len(orphaned_files) - preview_limit
            if remaining > 0:
                self.stdout.write(f"  … and {remaining} more")

            self.stdout.write("")

            # ── Dry-run summary or live deletion ────────────────────────
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        "Dry run complete. Use --force to delete these files."
                    )
                )
            else:
                self.stdout.write("Deleting orphaned files …")
                result = cleanup.delete_orphaned_files(orphaned_files)

                freed_mb = result["total_size_freed"] / (1024 * 1024)
                self.stdout.write("")
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Cleanup complete!\n"
                        f"  Deleted:     {result['deleted']}\n"
                        f"  Skipped:     {result['skipped']}\n"
                        f"  Errors:      {result['errors']}\n"
                        f"  Space freed: {freed_mb:.2f} MB"
                    )
                )

        except Exception as exc:
            logger.error("Error during cleanup: %s", exc, exc_info=True)
            raise CommandError(f"Cleanup failed: {exc}") from exc
