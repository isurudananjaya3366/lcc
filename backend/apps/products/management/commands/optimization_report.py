"""
Management command to generate an image optimization report.

Usage::

    python manage.py optimization_report
    python manage.py optimization_report --format json --output report.json
    python manage.py optimization_report --detailed --product <uuid>
"""

from __future__ import annotations

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Generate an image optimization report for product media."

    def add_arguments(self, parser):
        parser.add_argument(
            "--format",
            type=str,
            choices=["text", "json"],
            default="text",
            dest="output_format",
            help="Output format (default: text).",
        )
        parser.add_argument(
            "--output",
            type=str,
            default=None,
            help="Write report to file instead of stdout.",
        )
        parser.add_argument(
            "--detailed",
            action="store_true",
            default=False,
            help="Generate a detailed per-image report.",
        )
        parser.add_argument(
            "--product",
            type=str,
            default=None,
            help="Filter by product UUID (detailed mode only).",
        )

    def handle(self, **options):
        from apps.products.media.optimization_report import OptimizationReport

        report = OptimizationReport()
        fmt = options["output_format"]

        if options["detailed"]:
            result = report.generate_detailed_report(
                product=options["product"],
                output_format=fmt,
            )
        else:
            result = report.generate_summary_report(output_format=fmt)

        if options["output"]:
            with open(options["output"], "w", encoding="utf-8") as fh:
                fh.write(result if isinstance(result, str) else str(result))
            self.stdout.write(
                self.style.SUCCESS(f"Report written to {options['output']}")
            )
        else:
            self.stdout.write(result if isinstance(result, str) else str(result))
