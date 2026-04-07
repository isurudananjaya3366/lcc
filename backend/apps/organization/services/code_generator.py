import re

from django.db import models


class DepartmentCodeGenerator:
    """Generate unique department codes from department names."""

    PREFIX = "DEPT"

    @classmethod
    def generate_code(cls, name: str, exclude_id=None) -> str:
        """Generate a unique department code from the given name.

        Args:
            name: Department name to derive the code from.
            exclude_id: Department ID to exclude from uniqueness check
                        (useful when updating an existing department).

        Returns:
            A unique code in the format ``DEPT-XX`` (e.g. ``DEPT-HR``).
        """
        from apps.organization.models.department import Department

        base = cls._format_code(name)
        candidate = f"{cls.PREFIX}-{base}"

        qs = Department.objects.all()
        if exclude_id:
            qs = qs.exclude(id=exclude_id)

        if not qs.filter(code=candidate).exists():
            return candidate

        # Resolve collision with numeric suffix
        for i in range(2, 100):
            suffixed = f"{candidate}-{i}"
            if not qs.filter(code=suffixed).exists():
                return suffixed

        raise RuntimeError(
            f"Unable to generate unique department code for '{name}'."
        )

    @classmethod
    def validate_code(cls, code: str, exclude_id=None) -> bool:
        """Check if a code is valid and unique."""
        from apps.organization.models.department import Department

        pattern = r"^[A-Z][A-Z0-9\-]{1,19}$"
        if not re.match(pattern, code):
            return False

        qs = Department.objects.filter(code=code)
        if exclude_id:
            qs = qs.exclude(id=exclude_id)

        return not qs.exists()

    @classmethod
    def _format_code(cls, name: str) -> str:
        """Extract an abbreviation from a department name."""
        stop_words = {"department", "division", "section", "unit", "team", "and", "of", "the"}
        words = [
            w for w in name.split()
            if w.lower() not in stop_words
        ]
        if not words:
            words = name.split()

        if len(words) == 1:
            return words[0][:3].upper()

        return "".join(w[0] for w in words).upper()


class DesignationCodeGenerator:
    """Generate unique designation codes from designation titles."""

    @classmethod
    def generate_code(cls, title: str, exclude_id=None) -> str:
        """Generate a unique designation code from the given title.

        Args:
            title: Designation title to derive the code from.
            exclude_id: Designation ID to exclude from uniqueness check.

        Returns:
            A unique code (e.g. ``SE``, ``HRM``).
        """
        from apps.organization.models.designation import Designation

        base = cls._format_code(title)
        candidate = base

        qs = Designation.objects.all()
        if exclude_id:
            qs = qs.exclude(id=exclude_id)

        if not qs.filter(code=candidate).exists():
            return candidate

        for i in range(2, 100):
            suffixed = f"{candidate}{i}"
            if not qs.filter(code=suffixed).exists():
                return suffixed

        raise RuntimeError(
            f"Unable to generate unique designation code for '{title}'."
        )

    @classmethod
    def validate_code(cls, code: str, exclude_id=None) -> bool:
        """Check if a code is valid and unique."""
        from apps.organization.models.designation import Designation

        pattern = r"^[A-Z][A-Z0-9]{0,19}$"
        if not re.match(pattern, code):
            return False

        qs = Designation.objects.filter(code=code)
        if exclude_id:
            qs = qs.exclude(id=exclude_id)

        return not qs.exists()

    @classmethod
    def _format_code(cls, title: str) -> str:
        """Extract an abbreviation from a designation title."""
        stop_words = {"the", "and", "of", "a", "an"}
        words = [
            w for w in title.split()
            if w.lower() not in stop_words
        ]
        if not words:
            words = title.split()

        if len(words) == 1:
            return words[0][:3].upper()

        return "".join(w[0] for w in words).upper()
