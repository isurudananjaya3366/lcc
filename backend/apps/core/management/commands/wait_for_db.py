"""
Management command to wait for database availability.

Usage:
    python manage.py wait_for_db
    python manage.py wait_for_db --max-retries 60 --delay 2.0

Docker entrypoint usage:
    python manage.py wait_for_db && python manage.py migrate
"""

import time

from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    """Django management command to pause execution until database is available."""

    help = "Wait for the database to be available before proceeding."

    def add_arguments(self, parser):
        """Add configurable command arguments."""
        parser.add_argument(
            "--max-retries",
            type=int,
            default=30,
            help="Maximum number of retry attempts (default: 30).",
        )
        parser.add_argument(
            "--delay",
            type=float,
            default=1.0,
            help="Seconds to wait between retries (default: 1.0).",
        )

    def handle(self, *args, **options):
        """Wait for the database to become available."""
        max_retries = options["max_retries"]
        delay = options["delay"]

        self.stdout.write("Waiting for database...")

        for attempt in range(1, max_retries + 1):
            try:
                connection = connections["default"]
                connection.ensure_connection()
                self.stdout.write(self.style.SUCCESS("Database available!"))
                return
            except OperationalError:
                if attempt < max_retries:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Database unavailable, retrying in {delay} seconds... "
                            f"(attempt {attempt}/{max_retries})"
                        )
                    )
                    time.sleep(delay)
                else:
                    self.stderr.write(
                        self.style.ERROR(
                            f"Database not available after {max_retries} attempts"
                        )
                    )
                    raise SystemExit(1)
