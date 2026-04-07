#!/usr/bin/env python
"""
SP12 Core Utilities & Helpers Verification Script.

Verifies all components of SubPhase-12 are properly implemented.
Run: python scripts/verify_sp12.py
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")

import django  # noqa: E402

django.setup()


class SP12Verifier:
    """Verifier for SP12 Core Utilities & Helpers."""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def check(self, name, condition, error_msg=""):
        if condition:
            self.passed += 1
            print(f"  \u2705 {name}")
        else:
            self.failed += 1
            self.errors.append(f"{name}: {error_msg}")
            print(f"  \u274c {name}: {error_msg}")

    def _try_import(self, module_path, symbol):
        """Return the symbol from module_path, or None on failure."""
        try:
            mod = __import__(module_path, fromlist=[symbol])
            return getattr(mod, symbol, None)
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Group A: Pagination
    # ------------------------------------------------------------------

    def verify_pagination(self):
        print("\n\U0001f4c4 Group A: Pagination")

        # Imports
        SP = self._try_import("apps.core.pagination", "StandardPagination")
        self.check("Import StandardPagination", SP is not None, "import failed")

        CP = self._try_import("apps.core.pagination", "LCCCursorPagination")
        self.check("Import LCCCursorPagination", CP is not None, "import failed")

        LO = self._try_import("apps.core.pagination", "LCCLimitOffsetPagination")
        self.check(
            "Import LCCLimitOffsetPagination", LO is not None, "import failed"
        )

        NP = self._try_import("apps.core.pagination", "NoPagination")
        self.check("Import NoPagination", NP is not None, "import failed")

        # Attributes
        if SP:
            self.check(
                "StandardPagination.page_size == 20",
                SP.page_size == 20,
                f"got {getattr(SP, 'page_size', 'N/A')}",
            )
            self.check(
                "StandardPagination.max_page_size == 100",
                SP.max_page_size == 100,
                f"got {getattr(SP, 'max_page_size', 'N/A')}",
            )
            self.check(
                "StandardPagination.page_size_query_param == 'page_size'",
                SP.page_size_query_param == "page_size",
                f"got {getattr(SP, 'page_size_query_param', 'N/A')}",
            )

        if CP:
            self.check(
                "CursorPagination.ordering == '-created_on'",
                CP.ordering == "-created_on",
                f"got {getattr(CP, 'ordering', 'N/A')}",
            )
            self.check(
                "CursorPagination.page_size == 20",
                CP.page_size == 20,
                f"got {getattr(CP, 'page_size', 'N/A')}",
            )

        if LO:
            self.check(
                "LimitOffsetPagination.default_limit == 20",
                LO.default_limit == 20,
                f"got {getattr(LO, 'default_limit', 'N/A')}",
            )
            self.check(
                "LimitOffsetPagination.max_limit == 100",
                LO.max_limit == 100,
                f"got {getattr(LO, 'max_limit', 'N/A')}",
            )

        if NP:
            self.check(
                "NoPagination has paginate_queryset method",
                hasattr(NP, "paginate_queryset"),
                "missing paginate_queryset",
            )

        # Version
        import apps.core.pagination as pmod

        self.check(
            "pagination.__version__ == '1.0.0'",
            getattr(pmod, "__version__", None) == "1.0.0",
            f"got {getattr(pmod, '__version__', 'N/A')}",
        )

        # __all__ completeness
        expected = {
            "StandardPagination",
            "LCCCursorPagination",
            "LCCLimitOffsetPagination",
            "NoPagination",
        }
        actual = set(getattr(pmod, "__all__", []))
        self.check(
            "pagination.__all__ complete",
            expected.issubset(actual),
            f"missing {expected - actual}",
        )

        # Settings check
        from django.conf import settings

        default_class = getattr(settings, "REST_FRAMEWORK", {}).get(
            "DEFAULT_PAGINATION_CLASS", ""
        )
        self.check(
            "DEFAULT_PAGINATION_CLASS in settings",
            "StandardPagination" in default_class,
            f"got {default_class}",
        )

    # ------------------------------------------------------------------
    # Group B: Filters
    # ------------------------------------------------------------------

    def verify_filters(self):
        print("\n\U0001f50d Group B: Filters")

        backend_names = [
            "TenantFilterBackend",
            "DateRangeFilterBackend",
            "LCCSearchFilter",
            "LCCOrderingFilter",
            "IsActiveFilterBackend",
            "CreatedByFilterBackend",
            "ModifiedAtFilterBackend",
        ]

        for name in backend_names:
            cls = self._try_import("apps.core.filters", name)
            self.check(f"Import {name}", cls is not None, "import failed")

        BFS = self._try_import("apps.core.filters", "BaseFilterSet")
        self.check("Import BaseFilterSet", BFS is not None, "import failed")

        import apps.core.filters as fmod

        self.check(
            "filters.__version__ == '1.0.0'",
            getattr(fmod, "__version__", None) == "1.0.0",
            f"got {getattr(fmod, '__version__', 'N/A')}",
        )

        expected = set(backend_names) | {"BaseFilterSet"}
        actual = set(getattr(fmod, "__all__", []))
        self.check(
            "filters.__all__ complete",
            expected.issubset(actual),
            f"missing {expected - actual}",
        )

    # ------------------------------------------------------------------
    # Group C: Validators
    # ------------------------------------------------------------------

    def verify_validators(self):
        print("\n\u2705 Group C: Validators")

        validator_names = [
            "LCCEmailValidator",
            "LCCURLValidator",
            "LCCSlugValidator",
            "PositiveNumberValidator",
            "DecimalValidator",
            "PercentageValidator",
            "FileSizeValidator",
            "ImageDimensionValidator",
            "FileExtensionValidator",
            "JSONValidator",
            "NoHTMLValidator",
            "UniqueForTenantValidator",
        ]

        for name in validator_names:
            cls = self._try_import("apps.core.validators", name)
            self.check(f"Import {name}", cls is not None, "import failed")

        # Functional: PositiveNumberValidator
        try:
            from apps.core.validators import PositiveNumberValidator

            v = PositiveNumberValidator()
            v(10)
            self.check("PositiveNumberValidator(10) passes", True)
        except Exception as e:
            self.check("PositiveNumberValidator(10) passes", False, str(e))

        # Functional: PercentageValidator
        try:
            from apps.core.validators import PercentageValidator

            v = PercentageValidator()
            v(50)
            self.check("PercentageValidator(50) passes", True)
        except Exception as e:
            self.check("PercentageValidator(50) passes", False, str(e))

        # Functional: LCCSlugValidator
        try:
            from apps.core.validators import LCCSlugValidator

            v = LCCSlugValidator()
            v("valid-slug")
            self.check("LCCSlugValidator('valid-slug') passes", True)
        except Exception as e:
            self.check("LCCSlugValidator('valid-slug') passes", False, str(e))

        # Functional: JSONValidator
        try:
            from apps.core.validators import JSONValidator

            v = JSONValidator()
            v('{"key": "value"}')
            self.check("JSONValidator('{...}') passes", True)
        except Exception as e:
            self.check("JSONValidator('{...}') passes", False, str(e))

        import apps.core.validators as vmod

        self.check(
            "validators.__version__ == '1.0.0'",
            getattr(vmod, "__version__", None) == "1.0.0",
            f"got {getattr(vmod, '__version__', 'N/A')}",
        )

        expected = set(validator_names)
        actual = set(getattr(vmod, "__all__", []))
        self.check(
            "validators.__all__ complete",
            expected.issubset(actual),
            f"missing {expected - actual}",
        )

    # ------------------------------------------------------------------
    # Group D: DateTime Helpers
    # ------------------------------------------------------------------

    def verify_datetime(self):
        print("\n\U0001f550 Group D: DateTime Helpers")

        fn_names = [
            "SL_TIMEZONE",
            "get_local_now",
            "convert_to_utc",
            "convert_to_local",
            "get_date_range",
            "get_month_range",
            "get_year_range",
            "format_date",
            "format_datetime",
        ]

        for name in fn_names:
            obj = self._try_import("apps.core.datetime", name)
            self.check(f"Import {name}", obj is not None, "import failed")

        # SL_TIMEZONE
        from apps.core.datetime import SL_TIMEZONE

        self.check(
            "SL_TIMEZONE == Asia/Colombo",
            str(SL_TIMEZONE) == "Asia/Colombo",
            f"got {SL_TIMEZONE}",
        )

        # format_date
        from datetime import date as _date
        from apps.core.datetime import format_date

        result = format_date(_date(2026, 1, 23))
        self.check(
            "format_date(2026-01-23) == '23/01/2026'",
            result == "23/01/2026",
            f"got {result}",
        )

        # format_datetime
        from datetime import datetime as _datetime
        from apps.core.datetime import format_datetime

        result = format_datetime(_datetime(2026, 1, 23, 14, 30))
        self.check(
            "format_datetime(2026-01-23 14:30) == '23/01/2026 14:30'",
            result == "23/01/2026 14:30",
            f"got {result}",
        )

        # get_month_range
        from apps.core.datetime import get_month_range

        start, end = get_month_range(2026, 1)
        self.check(
            "get_month_range(2026, 1) start day == 1",
            start.day == 1,
            f"got {start.day}",
        )
        self.check(
            "get_month_range(2026, 1) end day == 31",
            end.day == 31,
            f"got {end.day}",
        )

        # get_year_range fiscal
        from apps.core.datetime import get_year_range

        start, end = get_year_range(2025, fiscal=True)
        self.check(
            "Fiscal year starts April",
            start.month == 4 and start.day == 1,
            f"got month={start.month} day={start.day}",
        )
        self.check(
            "Fiscal year ends March 31",
            end.month == 3 and end.day == 31,
            f"got month={end.month} day={end.day}",
        )

        import apps.core.datetime as dtmod

        self.check(
            "datetime.__version__ == '1.0.0'",
            getattr(dtmod, "__version__", None) == "1.0.0",
            f"got {getattr(dtmod, '__version__', 'N/A')}",
        )

        expected = set(fn_names)
        actual = set(getattr(dtmod, "__all__", []))
        self.check(
            "datetime.__all__ complete",
            expected.issubset(actual),
            f"missing {expected - actual}",
        )

    # ------------------------------------------------------------------
    # Group E: Sri Lanka Utilities
    # ------------------------------------------------------------------

    def verify_srilanka(self):
        print("\n\U0001f1f1\U0001f1f0 Group E: Sri Lanka Utilities")

        # Currency imports
        from apps.core.srilanka import format_lkr, parse_lkr, convert_currency

        self.check("Import format_lkr", format_lkr is not None)
        self.check("Import parse_lkr", parse_lkr is not None)
        self.check("Import convert_currency", convert_currency is not None)

        # Currency functional
        from decimal import Decimal

        result = format_lkr(1500)
        self.check(
            "format_lkr(1500) == 'Rs. 1,500.00'",
            result == "Rs. 1,500.00",
            f"got {result}",
        )

        result = format_lkr(1500, show_symbol=False)
        self.check(
            "format_lkr(1500, False) == '1,500.00'",
            result == "1,500.00",
            f"got {result}",
        )

        result = parse_lkr("Rs. 1,500.00")
        self.check(
            "parse_lkr('Rs. 1,500.00') == Decimal('1500.00')",
            result == Decimal("1500.00"),
            f"got {result}",
        )

        result = convert_currency(300, "LKR", "USD", exchange_rate=Decimal("0.0033"))
        self.check(
            "convert_currency(300, ..., 0.0033) == Decimal('0.9900')",
            result == Decimal("0.9900"),
            f"got {result}",
        )

        # Phone imports
        from apps.core.srilanka import (
            validate_sl_phone,
            format_sl_phone,
            normalize_sl_phone,
        )

        self.check("Import validate_sl_phone", validate_sl_phone is not None)
        self.check("Import format_sl_phone", format_sl_phone is not None)
        self.check("Import normalize_sl_phone", normalize_sl_phone is not None)

        # Phone functional
        self.check(
            "validate_sl_phone('0712345678') is True",
            validate_sl_phone("0712345678") is True,
        )
        self.check(
            "validate_sl_phone('invalid') is False",
            validate_sl_phone("invalid") is False,
        )

        result = format_sl_phone("0712345678")
        self.check(
            "format_sl_phone('0712345678') == '+94 71 234 5678'",
            result == "+94 71 234 5678",
            f"got {result}",
        )

        result = normalize_sl_phone("0712345678")
        self.check(
            "normalize_sl_phone('0712345678') == '+94712345678'",
            result == "+94712345678",
            f"got {result}",
        )

        # NIC imports
        from apps.core.srilanka import validate_nic, parse_nic_dob

        self.check("Import validate_nic", validate_nic is not None)
        self.check("Import parse_nic_dob", parse_nic_dob is not None)

        # NIC functional
        self.check(
            "validate_nic('881234567V') is True",
            validate_nic("881234567V") is True,
        )
        self.check(
            "validate_nic('198812345678') is True",
            validate_nic("198812345678") is True,
        )
        self.check(
            "validate_nic('invalid') is False",
            validate_nic("invalid") is False,
        )

        dob, gender = parse_nic_dob("881234567V")
        self.check(
            "parse_nic_dob returns date",
            hasattr(dob, "year"),
            f"got type {type(dob)}",
        )
        self.check(
            "parse_nic_dob returns M or F",
            gender in ("M", "F"),
            f"got {gender}",
        )

        # Provinces & Districts
        from apps.core.srilanka import (
            PROVINCES,
            DISTRICTS,
            get_province_by_code,
            get_province_choices,
            get_districts_by_province,
            get_district_by_code,
            get_district_choices,
        )

        self.check(
            "PROVINCES count == 9",
            len(PROVINCES) == 9,
            f"got {len(PROVINCES)}",
        )
        self.check(
            "DISTRICTS count == 25",
            len(DISTRICTS) == 25,
            f"got {len(DISTRICTS)}",
        )

        wp = get_province_by_code("WP")
        self.check(
            "get_province_by_code('WP') returns Western Province",
            wp is not None and wp["name"] == "Western Province",
            f"got {wp}",
        )

        choices = get_province_choices()
        self.check(
            "get_province_choices() returns 9 tuples",
            len(choices) == 9,
            f"got {len(choices)}",
        )

        wp_districts = get_districts_by_province("WP")
        self.check(
            "WP has 3 districts",
            len(wp_districts) == 3,
            f"got {len(wp_districts)}",
        )

        co = get_district_by_code("CO")
        self.check(
            "get_district_by_code('CO') returns Colombo",
            co is not None and co["name"] == "Colombo",
            f"got {co}",
        )

        all_choices = get_district_choices()
        self.check(
            "get_district_choices() returns 25 tuples",
            len(all_choices) == 25,
            f"got {len(all_choices)}",
        )

        import apps.core.srilanka as slmod

        self.check(
            "srilanka.__version__ == '1.0.0'",
            getattr(slmod, "__version__", None) == "1.0.0",
            f"got {getattr(slmod, '__version__', 'N/A')}",
        )

        expected = {
            "format_lkr",
            "parse_lkr",
            "convert_currency",
            "validate_sl_phone",
            "format_sl_phone",
            "normalize_sl_phone",
            "validate_nic",
            "parse_nic_dob",
            "PROVINCES",
            "DISTRICTS",
            "get_province_by_code",
            "get_province_choices",
            "get_districts_by_province",
            "get_district_by_code",
            "get_district_choices",
        }
        actual = set(getattr(slmod, "__all__", []))
        self.check(
            "srilanka.__all__ complete",
            expected.issubset(actual),
            f"missing {expected - actual}",
        )

    # ------------------------------------------------------------------
    # Group F: Documentation
    # ------------------------------------------------------------------

    def verify_documentation(self):
        print("\n\U0001f4d6 Group F: Documentation")

        backend_root = os.path.dirname(os.path.abspath(__file__)) + "/.."

        readme_path = os.path.join(backend_root, "apps", "core", "README.md")
        self.check(
            "apps/core/README.md exists",
            os.path.isfile(readme_path),
            "file not found",
        )

        if os.path.isfile(readme_path):
            size = os.path.getsize(readme_path)
            self.check(
                "README.md size > 5 KB",
                size > 5000,
                f"got {size} bytes",
            )

        docs_path = os.path.join(
            backend_root, "..", "docs", "backend", "utilities.md"
        )
        docs_exists = os.path.isfile(os.path.normpath(docs_path))
        if not docs_exists:
            # Docker mounts only backend/ as /app - docs/ is at project root
            # outside the container. Skip gracefully in Docker.
            in_docker = os.path.isfile("/.dockerenv")
            if in_docker:
                print("  ⏭️  docs/backend/utilities.md (skipped in Docker)")
            else:
                self.check(
                    "docs/backend/utilities.md exists",
                    False,
                    "file not found",
                )
        else:
            self.check(
                "docs/backend/utilities.md exists",
                True,
            )

    # ------------------------------------------------------------------
    # Tests
    # ------------------------------------------------------------------

    def verify_tests(self):
        print("\n\U0001f9ea Test Files")

        tests_root = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "tests", "core"
        )

        test_files = [
            ("test_pagination.py", "Pagination tests"),
            ("test_filters.py", "Filter tests"),
            ("test_validators.py", "Validator tests"),
            ("test_datetime.py", "DateTime tests"),
            ("test_srilanka.py", "Sri Lanka tests"),
            ("test_integration.py", "Integration tests"),
        ]

        for filename, label in test_files:
            filepath = os.path.join(tests_root, filename)
            self.check(
                f"{label} ({filename}) exists",
                os.path.isfile(os.path.normpath(filepath)),
                "file not found",
            )

        # Verify script itself
        verify_path = os.path.abspath(__file__)
        self.check(
            "Verification script exists",
            os.path.isfile(verify_path),
            "file not found",
        )

    # ------------------------------------------------------------------
    # Module file structure
    # ------------------------------------------------------------------

    def verify_module_files(self):
        print("\n\U0001f4c1 Module File Structure")

        backend_root = os.path.normpath(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
        )

        module_files = [
            ("apps/core/pagination/__init__.py", "Pagination __init__"),
            ("apps/core/pagination/standard.py", "StandardPagination"),
            ("apps/core/pagination/cursor.py", "CursorPagination"),
            ("apps/core/pagination/limit_offset.py", "LimitOffsetPagination"),
            ("apps/core/pagination/none.py", "NoPagination"),
            ("apps/core/filters/__init__.py", "Filters __init__"),
            ("apps/core/filters/backends.py", "Filter backends"),
            ("apps/core/filters/filtersets.py", "BaseFilterSet"),
            ("apps/core/validators/__init__.py", "Validators __init__"),
            ("apps/core/validators/common.py", "Common validators"),
            ("apps/core/validators/file_validators.py", "File validators"),
            ("apps/core/validators/content.py", "Content validators"),
            ("apps/core/datetime/__init__.py", "DateTime __init__"),
            ("apps/core/datetime/timezone.py", "Timezone utils"),
            ("apps/core/datetime/date_utils.py", "Date utils"),
            ("apps/core/srilanka/__init__.py", "Sri Lanka __init__"),
            ("apps/core/srilanka/currency.py", "Currency utils"),
            ("apps/core/srilanka/phone.py", "Phone utils"),
            ("apps/core/srilanka/nic.py", "NIC utils"),
            ("apps/core/srilanka/provinces.py", "Provinces & districts"),
        ]

        for rel_path, label in module_files:
            full_path = os.path.join(backend_root, rel_path.replace("/", os.sep))
            self.check(
                f"{label} ({rel_path})",
                os.path.isfile(full_path),
                "file not found",
            )

    # ------------------------------------------------------------------
    # Run all
    # ------------------------------------------------------------------

    def run(self):
        print("=" * 60)
        print("SP12 Core Utilities & Helpers Verification")
        print("=" * 60)

        self.verify_pagination()
        self.verify_filters()
        self.verify_validators()
        self.verify_datetime()
        self.verify_srilanka()
        self.verify_documentation()
        self.verify_tests()
        self.verify_module_files()

        print("\n" + "=" * 60)
        total = self.passed + self.failed
        print(f"Results: {self.passed}/{total} checks passed")
        if self.errors:
            print(f"\nFailures ({self.failed}):")
            for e in self.errors:
                print(f"  - {e}")
        else:
            print("\nAll checks passed! SP12 is fully verified.")
        print("=" * 60)

        return self.failed == 0


if __name__ == "__main__":
    verifier = SP12Verifier()
    success = verifier.run()
    sys.exit(0 if success else 1)
