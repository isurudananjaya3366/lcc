"""
LankaCommerce Cloud – Orphaned-File Cleanup Utilities (SP10 Task 73).

Identifies and removes files in storage that are no longer referenced by
any Django model (``FileField`` / ``ImageField``).

Orphaned files typically arise from:
- Users deleting records without the application removing the file
- Failed uploads that leave partial files behind
- Image replacements where the old file was not cleaned up

Usage::

    from apps.core.storage.cleanup import FileCleanup

    # Dry-run preview (no deletions)
    cleanup = FileCleanup(dry_run=True)
    orphans = cleanup.find_orphaned_files(min_age_days=7)

    # Live deletion
    cleanup = FileCleanup(dry_run=False)
    result  = cleanup.cleanup(min_age_days=30)
    print(result)  # {'deleted': 12, 'skipped': 0, 'errors': 1, ...}

    # Convenience function
    from apps.core.storage.cleanup import cleanup_old_files
    result = cleanup_old_files(days_old=30, dry_run=False)
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from django.apps import apps
from django.core.files.storage import default_storage
from django.db import models
from django.utils import timezone

if TYPE_CHECKING:
    from django.core.files.storage import Storage

logger = logging.getLogger(__name__)


class FileCleanup:
    """
    Utility for cleaning up orphaned files in storage.

    Orphaned files are files that exist in storage but are no longer
    referenced by any database record.  These accumulate over time from
    failed uploads, deleted records, or application errors.

    Attributes:
        storage: Storage backend to scan/delete from.
        dry_run: When ``True`` (default) **no files are deleted**.
        orphaned_files: Populated after :meth:`find_orphaned_files`.
        deleted_count, skipped_count, error_count: Counters.
    """

    def __init__(
        self,
        storage: Storage | None = None,
        dry_run: bool = True,
    ):
        self.storage: Storage = storage or default_storage
        self.dry_run = dry_run
        self.orphaned_files: list[str] = []
        self.deleted_count: int = 0
        self.skipped_count: int = 0
        self.error_count: int = 0

    # ────────────────────────────────────────────────────────────────────
    # Find orphaned files
    # ────────────────────────────────────────────────────────────────────

    def find_orphaned_files(
        self,
        path: str = "",
        min_age_days: int = 7,
    ) -> list[str]:
        """
        Scan *path* for files not referenced in the database.

        Args:
            path: Sub-path inside the storage root to scan
                  (empty string = root directory).
            min_age_days: Ignore files younger than this many days.

        Returns:
            Sorted list of orphaned file paths.
        """
        logger.info("Scanning for orphaned files in: %s", path or "(root)")

        storage_files = self._collect_storage_files(path, min_age_days)
        referenced_files = self.get_referenced_files()

        orphaned = storage_files - referenced_files

        logger.info(
            "Found %d files in storage, %d referenced, %d orphaned",
            len(storage_files),
            len(referenced_files),
            len(orphaned),
        )

        self.orphaned_files = sorted(orphaned)
        return self.orphaned_files

    # ────────────────────────────────────────────────────────────────────

    def _collect_storage_files(
        self,
        path: str,
        min_age_days: int,
    ) -> set[str]:
        """Recursively list files in *path*, filtering by age."""
        result: set[str] = set()
        cutoff = timezone.now() - timedelta(days=min_age_days)

        try:
            dirs, files = self.storage.listdir(path)
        except Exception:
            logger.exception("Error listing directory: %s", path)
            return result

        for file_name in files:
            file_path = os.path.join(path, file_name) if path else file_name

            try:
                modified = self.storage.get_modified_time(file_path)
                # Ensure timezone-aware comparison
                if timezone.is_naive(modified):
                    modified = timezone.make_aware(modified)
                if modified > cutoff:
                    logger.debug("Skipping recent file: %s", file_path)
                    continue
            except Exception:
                logger.debug(
                    "Could not determine age of %s — including it", file_path
                )

            result.add(file_path)

        for dir_name in dirs:
            sub = os.path.join(path, dir_name) if path else dir_name
            result.update(self._collect_storage_files(sub, min_age_days))

        return result

    # ────────────────────────────────────────────────────────────────────

    def get_referenced_files(self) -> set[str]:
        """
        Return all file paths currently referenced by ``FileField`` or
        ``ImageField`` columns across every installed Django model.
        """
        referenced: set[str] = set()

        for model in apps.get_models():
            file_fields = [
                f
                for f in model._meta.get_fields()
                if isinstance(f, (models.FileField, models.ImageField))
            ]
            if not file_fields:
                continue

            try:
                qs = model.objects.using("default").all()
                for instance in qs.iterator(chunk_size=500):
                    for field in file_fields:
                        value = getattr(instance, field.name, None)
                        if value and value.name:
                            referenced.add(value.name)
            except Exception:
                logger.debug(
                    "Skipping model %s.%s — error reading rows",
                    model._meta.app_label,
                    model._meta.model_name,
                    exc_info=True,
                )

        return referenced

    # ────────────────────────────────────────────────────────────────────
    # Delete orphaned files
    # ────────────────────────────────────────────────────────────────────

    def delete_orphaned_files(
        self,
        orphaned_files: list[str] | None = None,
    ) -> dict[str, int]:
        """
        Delete the given (or previously found) orphaned files.

        Args:
            orphaned_files: Explicit list; defaults to :attr:`orphaned_files`.

        Returns:
            Dict with keys ``deleted``, ``skipped``, ``errors``,
            ``total_size_freed``.
        """
        files = orphaned_files if orphaned_files is not None else self.orphaned_files

        if not files:
            logger.info("No orphaned files to delete")
            return self._stats(total_size=0)

        total_size = 0

        for file_path in files:
            try:
                try:
                    file_size = self.storage.size(file_path)
                except Exception:
                    file_size = 0

                total_size += file_size

                if self.dry_run:
                    logger.info(
                        "[DRY RUN] Would delete: %s (%d bytes)",
                        file_path,
                        file_size,
                    )
                    self.skipped_count += 1
                else:
                    self.storage.delete(file_path)
                    logger.info("Deleted: %s (%d bytes)", file_path, file_size)
                    self.deleted_count += 1

            except Exception:
                logger.exception("Error deleting %s", file_path)
                self.error_count += 1

        stats = self._stats(total_size=total_size)
        logger.info(
            "Cleanup complete: %(deleted)d deleted, %(skipped)d skipped, "
            "%(errors)d errors, %(total_size_freed)d bytes freed",
            stats,
        )
        return stats

    # ────────────────────────────────────────────────────────────────────

    def _stats(self, *, total_size: int) -> dict[str, int]:
        return {
            "deleted": self.deleted_count,
            "skipped": self.skipped_count,
            "errors": self.error_count,
            "total_size_freed": total_size,
        }

    # ────────────────────────────────────────────────────────────────────
    # High-level convenience
    # ────────────────────────────────────────────────────────────────────

    def cleanup(
        self,
        path: str = "",
        min_age_days: int = 7,
    ) -> dict[str, int]:
        """
        Find **and** delete orphaned files in a single call.

        Args:
            path: Storage sub-path to scan (empty = root).
            min_age_days: Minimum age in days before a file is eligible.

        Returns:
            Deletion statistics dict.
        """
        self.find_orphaned_files(path, min_age_days)
        return self.delete_orphaned_files()


# ════════════════════════════════════════════════════════════════════════════
# Module-level convenience function
# ════════════════════════════════════════════════════════════════════════════


def cleanup_old_files(
    days_old: int = 30,
    dry_run: bool = True,
) -> dict[str, int]:
    """
    Clean up files older than *days_old*.

    Args:
        days_old: Delete files older than this many days.
        dry_run: When ``True`` no files are actually removed.

    Returns:
        Deletion statistics dict.
    """
    cleaner = FileCleanup(dry_run=dry_run)
    return cleaner.cleanup(min_age_days=days_old)
