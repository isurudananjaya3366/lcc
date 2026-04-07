"""
Management command: ``validate_schema``

Generates the OpenAPI schema and validates it can be serialised to
JSON and YAML.  Intended for CI pipelines to catch schema regressions.

Usage::

    python manage.py validate_schema
    python manage.py validate_schema --format json
    python manage.py validate_schema --format yaml
    python manage.py validate_schema --strict
"""

from __future__ import annotations

import json
import sys
from typing import Any

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Generate and validate the OpenAPI schema (CI/CD gate)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--format",
            type=str,
            choices=["json", "yaml", "both"],
            default="both",
            help="Output format(s) to validate (default: both)",
        )
        parser.add_argument(
            "--strict",
            action="store_true",
            default=False,
            help="Treat warnings as errors",
        )
        parser.add_argument(
            "--output",
            type=str,
            default=None,
            help="Write generated schema to this file path",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        fmt: str = options["format"]
        strict: bool = options["strict"]
        output_path: str | None = options["output"]

        warnings: list[str] = []
        errors: list[str] = []

        # ── 1. Generate schema ────────────────────────────────────────
        self.stdout.write("Generating OpenAPI schema …")
        try:
            from drf_spectacular.generators import SchemaGenerator

            generator = SchemaGenerator()
            schema = generator.get_schema(request=None, public=True)
        except Exception as exc:
            errors.append(f"Schema generation failed: {exc}")
            self._report(errors, warnings, strict)
            sys.exit(1)

        if schema is None:
            errors.append("Schema generation returned None")
            self._report(errors, warnings, strict)
            sys.exit(1)

        self.stdout.write(self.style.SUCCESS("  ✔ Schema generated"))

        # ── 2. Validate structure ─────────────────────────────────────
        self.stdout.write("Validating schema structure …")
        for key in ("openapi", "info", "paths"):
            if key not in schema:
                errors.append(f"Missing top-level key: {key}")

        info = schema.get("info", {})
        if not info.get("title"):
            warnings.append("Schema info.title is empty")
        if not info.get("version"):
            warnings.append("Schema info.version is empty")

        paths = schema.get("paths", {})
        if len(paths) == 0:
            warnings.append("Schema contains no paths")

        if not errors:
            self.stdout.write(self.style.SUCCESS("  ✔ Structure valid"))

        # ── 3. JSON serialisation ─────────────────────────────────────
        json_str: str | None = None
        if fmt in ("json", "both"):
            self.stdout.write("Validating JSON serialisation …")
            try:
                json_str = json.dumps(schema, indent=2, default=str)
                # Verify round-trip
                json.loads(json_str)
                self.stdout.write(self.style.SUCCESS("  ✔ JSON valid"))
            except (TypeError, ValueError) as exc:
                errors.append(f"JSON serialisation failed: {exc}")

        # ── 4. YAML serialisation ─────────────────────────────────────
        yaml_str: str | None = None
        if fmt in ("yaml", "both"):
            self.stdout.write("Validating YAML serialisation …")
            try:
                import yaml

                yaml_str = yaml.dump(
                    json.loads(json.dumps(schema, default=str)),
                    default_flow_style=False,
                    allow_unicode=True,
                )
                self.stdout.write(self.style.SUCCESS("  ✔ YAML valid"))
            except ImportError:
                warnings.append(
                    "PyYAML not installed — skipping YAML validation"
                )
            except Exception as exc:
                errors.append(f"YAML serialisation failed: {exc}")

        # ── 5. Optionally write output ────────────────────────────────
        if output_path and not errors:
            self.stdout.write(f"Writing schema to {output_path} …")
            try:
                content = json_str or json.dumps(schema, indent=2, default=str)
                with open(output_path, "w", encoding="utf-8") as fh:
                    fh.write(content)
                self.stdout.write(
                    self.style.SUCCESS(f"  ✔ Schema written to {output_path}")
                )
            except OSError as exc:
                errors.append(f"Failed to write output file: {exc}")

        # ── 6. Summary ────────────────────────────────────────────────
        self._report(errors, warnings, strict)

        if errors or (strict and warnings):
            sys.exit(1)

    # ── helpers ───────────────────────────────────────────────────────

    def _report(
        self,
        errors: list[str],
        warnings: list[str],
        strict: bool,
    ) -> None:
        """Print a summary of errors and warnings."""
        self.stdout.write("")
        if errors:
            self.stdout.write(self.style.ERROR("ERRORS:"))
            for msg in errors:
                self.stdout.write(self.style.ERROR(f"  ✘ {msg}"))

        if warnings:
            style = self.style.ERROR if strict else self.style.WARNING
            self.stdout.write(style("WARNINGS:"))
            for msg in warnings:
                self.stdout.write(style(f"  ⚠ {msg}"))

        if not errors and not (strict and warnings):
            self.stdout.write(
                self.style.SUCCESS(
                    "\n✔ Schema validation passed — no issues found."
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f"\n✘ Validation failed — {len(errors)} error(s), "
                    f"{len(warnings)} warning(s)."
                )
            )
