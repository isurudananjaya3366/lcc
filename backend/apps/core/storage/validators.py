"""
LankaCommerce Cloud – File Upload Validators (SP10 Tasks 61-66).

Comprehensive file validation and security scanning for uploads.

This module provides:
- **Extension Validation:** Verify allowed file types
- **Size Validation:** Enforce upload limits with human-readable errors
- **MIME Type Validation:** Verify actual file content matches extension
- **Malware Scanning:** Detect malicious files (ClamAV / VirusTotal)
- **Security Logging:** Track all validation attempts and failures

Security note:
    This is security-critical code.  Every uploaded file MUST pass through
    ``FileValidator`` before being persisted.  Extension checks alone are
    insufficient — always combine with MIME-type verification.

Usage::

    from apps.core.storage.validators import FileValidator

    validator = FileValidator(
        allowed_extensions={'.jpg', '.png', '.pdf'},
        max_size=5 * 1024 * 1024,  # 5 MB
    )

    # As a Django field validator (calls __call__)
    validator(uploaded_file)

    # Full validation including MIME type
    validator.validate_all(uploaded_file)
"""

from __future__ import annotations

import logging
import mimetypes
import os
from typing import TYPE_CHECKING

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from django.core.files.uploadedfile import UploadedFile

logger = logging.getLogger(__name__)


class FileValidator:
    """
    Comprehensive file validator for uploads.

    Validates uploaded files against:
    - Allowed file extensions
    - Maximum file size limits
    - MIME type verification (requires ``python-magic``)
    - Malware scanning (requires ClamAV or VirusTotal)

    Usage::

        validator = FileValidator(
            allowed_extensions={'.jpg', '.png', '.pdf'},
            max_size=5 * 1024 * 1024,  # 5 MB
        )

        # Quick validation (extension + size only) — use as Django validator
        validator(uploaded_file)

        # Full validation (extension + size + MIME + optional malware scan)
        validator.validate_all(uploaded_file)
    """

    # ────────────────────────────────────────────────────────────────────
    # MIME Type Mapping (extension → list of valid MIME types)
    # ────────────────────────────────────────────────────────────────────

    MIME_TYPE_MAP: dict[str, list[str]] = {
        # Images
        "jpg": ["image/jpeg"],
        "jpeg": ["image/jpeg"],
        "png": ["image/png"],
        "gif": ["image/gif"],
        "webp": ["image/webp"],
        "bmp": ["image/bmp", "image/x-ms-bmp"],
        "svg": ["image/svg+xml"],
        "ico": ["image/x-icon", "image/vnd.microsoft.icon"],
        # Documents
        "pdf": ["application/pdf"],
        "doc": ["application/msword"],
        "docx": [
            "application/vnd.openxmlformats-officedocument"
            ".wordprocessingml.document",
        ],
        "xls": ["application/vnd.ms-excel"],
        "xlsx": [
            "application/vnd.openxmlformats-officedocument"
            ".spreadsheetml.sheet",
        ],
        "txt": ["text/plain"],
        "csv": ["text/csv", "text/plain", "application/csv"],
        "rtf": ["application/rtf", "text/rtf"],
        "odt": ["application/vnd.oasis.opendocument.text"],
        "ods": ["application/vnd.oasis.opendocument.spreadsheet"],
        # Archives
        "zip": ["application/zip", "application/x-zip-compressed"],
        "tar": ["application/x-tar"],
        "gz": ["application/gzip", "application/x-gzip"],
        "rar": ["application/vnd.rar", "application/x-rar-compressed"],
    }

    # ────────────────────────────────────────────────────────────────────
    # Initialisation
    # ────────────────────────────────────────────────────────────────────

    def __init__(
        self,
        max_size: int | None = None,
        allowed_extensions: set[str] | None = None,
    ):
        """
        Initialise FileValidator.

        Args:
            max_size: Maximum file size in bytes.  ``None`` disables the check.
            allowed_extensions: Set of allowed extensions **with leading dot**
                (e.g. ``{'.jpg', '.png'}``).  ``None`` falls back to
                ``settings.ALL_ALLOWED_EXTENSIONS``.
        """
        self.max_size = max_size
        self.allowed_extensions: set[str] = allowed_extensions or getattr(
            settings, "ALL_ALLOWED_EXTENSIONS", set()
        )
        self.errors: list[str] = []

    # ────────────────────────────────────────────────────────────────────
    # Callable interface (for Django field validators)
    # ────────────────────────────────────────────────────────────────────

    def __call__(self, file: UploadedFile) -> None:
        """Run extension + size validation (Django field-validator API)."""
        self.validate_extension(file)
        self.validate_size(file)

    # ────────────────────────────────────────────────────────────────────
    # Full validation pipeline
    # ────────────────────────────────────────────────────────────────────

    def validate_all(self, uploaded_file: UploadedFile) -> bool:
        """
        Run **all** validations on *uploaded_file*.

        Checks run in order: extension → size → MIME type.
        Malware scanning is intentionally excluded from the default
        pipeline (it is expensive); call :meth:`scan_for_malware`
        explicitly when needed.

        Args:
            uploaded_file: Django ``UploadedFile`` object.

        Raises:
            ValidationError: If any validation fails.

        Returns:
            ``True`` when every check passes.
        """
        self.errors = []

        try:
            self.validate_extension(uploaded_file)
            self.validate_size(uploaded_file)
            self.validate_mime_type(uploaded_file)
        except ValidationError as exc:
            self.errors.append(str(exc.message if hasattr(exc, "message") else exc))
            logger.warning(
                "File validation failed: %s – errors: %s",
                uploaded_file.name,
                self.errors,
            )
            raise

        logger.info("File validation passed: %s", uploaded_file.name)
        return True

    # ────────────────────────────────────────────────────────────────────
    # Helpers
    # ────────────────────────────────────────────────────────────────────

    @staticmethod
    def get_file_extension(filename: str) -> str:
        """
        Extract the lowercase extension **without** the leading dot.

        Args:
            filename: Original file name.

        Returns:
            Extension string (e.g. ``'pdf'``).  Empty string when no
            extension is present.
        """
        ext = os.path.splitext(filename)[1].lower()
        return ext.lstrip(".")

    @staticmethod
    def format_file_size(size_bytes: int | float) -> str:
        """
        Format *size_bytes* as a human-readable string.

        Examples::

            format_file_size(512)           # '512 bytes'
            format_file_size(1536)          # '1.50 KB'
            format_file_size(5_242_880)     # '5.00 MB'
            format_file_size(1_073_741_824) # '1.00 GB'
        """
        if size_bytes < 1024:
            return f"{int(size_bytes)} bytes"
        if size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        if size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

    # ────────────────────────────────────────────────────────────────────
    # Extension validation (Task 63)
    # ────────────────────────────────────────────────────────────────────

    def validate_extension(self, file: UploadedFile) -> None:
        """
        Validate that the file extension is in the allowed set.

        Performs **case-insensitive** matching.  Rejects files without an
        extension when an allowed-extensions list is configured.

        Args:
            file: Django ``UploadedFile`` object.

        Raises:
            ValidationError: If the extension is missing or disallowed.
        """
        if not self.allowed_extensions:
            return  # No restrictions configured

        ext = os.path.splitext(file.name)[1].lower()

        if not ext:
            raise ValidationError(
                _("File has no extension. Please upload a valid file.")
            )

        # Build a normalised set (lowercase, with leading dot)
        allowed_lower = {e.lower() for e in self.allowed_extensions}

        if ext not in allowed_lower:
            raise ValidationError(
                _(
                    "File type '%(ext)s' is not allowed. "
                    "Allowed types: %(allowed)s"
                )
                % {
                    "ext": ext,
                    "allowed": ", ".join(sorted(allowed_lower)),
                }
            )

        logger.debug("Extension validation passed: %s", ext)

    # ────────────────────────────────────────────────────────────────────
    # Size validation (Task 64)
    # ────────────────────────────────────────────────────────────────────

    def validate_size(self, file: UploadedFile) -> None:
        """
        Validate the file size against the configured maximum.

        Also rejects zero-byte (empty) files.

        Args:
            file: Django ``UploadedFile`` object.

        Raises:
            ValidationError: If the file is empty or exceeds *max_size*.
        """
        if not hasattr(file, "size"):
            return  # Cannot determine size — skip

        file_size: int = file.size

        # Reject empty files
        if file_size == 0:
            raise ValidationError(
                _("File is empty. Please upload a valid file.")
            )

        if self.max_size is None:
            return  # No size restriction configured

        if file_size > self.max_size:
            raise ValidationError(
                _(
                    "File size (%(actual)s) exceeds the maximum allowed "
                    "size (%(limit)s)."
                )
                % {
                    "actual": self.format_file_size(file_size),
                    "limit": self.format_file_size(self.max_size),
                }
            )

        logger.debug(
            "Size validation passed: %d bytes (max: %s bytes)",
            file_size,
            self.max_size,
        )

    # ────────────────────────────────────────────────────────────────────
    # MIME-type validation (Task 65)
    # ────────────────────────────────────────────────────────────────────

    def validate_mime_type(
        self,
        uploaded_file: UploadedFile,
        *,
        strict: bool = False,
    ) -> None:
        """
        Verify the actual MIME type of *uploaded_file* matches its extension.

        Prevents users from uploading malicious files disguised with a
        safe-looking extension (e.g. ``malware.exe`` renamed to ``doc.pdf``).

        When ``strict=True`` the detected MIME must exactly match one of the
        expected types.  In lenient mode (default) a *category* match
        (e.g. ``image/*``) is accepted as well.

        Requires the ``python-magic`` library.  If unavailable the check is
        skipped with a logged warning.

        Args:
            uploaded_file: Django ``UploadedFile`` object.
            strict: Require an exact MIME-type match.

        Raises:
            ValidationError: On MIME mismatch or corrupted content.
        """
        try:
            import magic  # python-magic
        except ImportError:
            logger.warning(
                "python-magic is not installed — skipping MIME-type "
                "validation for %s",
                uploaded_file.name,
            )
            return

        extension = self.get_file_extension(uploaded_file.name)
        expected_mimes = self.MIME_TYPE_MAP.get(extension, [])

        if not expected_mimes:
            # No mapping for this extension — fall back to mimetypes stdlib
            guessed, _encoding = mimetypes.guess_type(uploaded_file.name)
            if guessed:
                expected_mimes = [guessed]
            else:
                logger.debug(
                    "No MIME mapping for extension '%s' — skipping check",
                    extension,
                )
                return

        # Read the first 8 KB for magic-byte detection
        uploaded_file.seek(0)
        header = uploaded_file.read(8192)
        uploaded_file.seek(0)

        try:
            actual_mime: str = magic.from_buffer(header, mime=True)
        except Exception:
            logger.exception("MIME detection failed for %s", uploaded_file.name)
            raise ValidationError(
                _("Unable to determine file type. The file may be corrupted.")
            )

        if strict:
            if actual_mime not in expected_mimes:
                raise ValidationError(
                    _(
                        "File type mismatch. Expected %(expected)s, "
                        "but detected %(actual)s. "
                        "The file may be corrupted or mislabelled."
                    )
                    % {
                        "expected": ", ".join(expected_mimes),
                        "actual": actual_mime,
                    }
                )
        else:
            expected_categories = {m.split("/")[0] for m in expected_mimes}
            actual_category = actual_mime.split("/")[0]
            if (
                actual_category not in expected_categories
                and actual_mime not in expected_mimes
            ):
                raise ValidationError(
                    _(
                        "File type mismatch. Expected %(expected)s, "
                        "but detected %(actual)s."
                    )
                    % {
                        "expected": ", ".join(expected_mimes),
                        "actual": actual_mime,
                    }
                )

        logger.debug("MIME validation passed: %s", actual_mime)

    # ────────────────────────────────────────────────────────────────────
    # Malware scanning (Task 66)
    # ────────────────────────────────────────────────────────────────────

    def scan_for_malware(
        self,
        uploaded_file: UploadedFile,
        scanner: str = "clamav",
    ) -> bool:
        """
        Scan *uploaded_file* for malware and viruses.

        Requires ``ENABLE_MALWARE_SCANNING = True`` in Django settings.
        Supported scanners:

        * ``clamav``  – Local ClamAV daemon via ``pyclamd``
        * ``virustotal`` – VirusTotal cloud API (needs ``VIRUSTOTAL_API_KEY``)
        * ``none`` – Skip scanning

        The method is **fail-safe**: when the scanner is unavailable or
        misconfigured the file is allowed through (with a logged error).

        Args:
            uploaded_file: Django ``UploadedFile`` object.
            scanner: Scanner backend to use.

        Raises:
            ValidationError: If malware is detected.

        Returns:
            ``True`` if the file is clean (or scanning is unavailable).
        """
        if not getattr(settings, "ENABLE_MALWARE_SCANNING", False):
            logger.debug("Malware scanning is disabled — skipping")
            return True

        if scanner == "none":
            return True

        if scanner == "clamav":
            return self._scan_with_clamav(uploaded_file)
        if scanner == "virustotal":
            return self._scan_with_virustotal(uploaded_file)

        logger.warning("Unknown malware scanner '%s' — skipping", scanner)
        return True

    # -- ClamAV integration --------------------------------------------------

    def _scan_with_clamav(self, uploaded_file: UploadedFile) -> bool:
        """Scan with local ClamAV daemon via ``pyclamd``."""
        try:
            import pyclamd
        except ImportError:
            logger.error(
                "pyclamd is not installed — cannot scan for malware"
            )
            return True  # fail-safe

        try:
            cd = pyclamd.ClamdUnixSocket()
            if not cd.ping():
                logger.error("ClamAV daemon is not responding")
                return True  # fail-safe

            uploaded_file.seek(0)
            content = uploaded_file.read()
            uploaded_file.seek(0)

            result = cd.scan_stream(content)
            if result:
                virus_name = result.get("stream", ("UNKNOWN", "UNKNOWN"))[1]
                logger.error(
                    "MALWARE DETECTED in %s — virus: %s",
                    uploaded_file.name,
                    virus_name,
                )
                raise ValidationError(
                    _(
                        "Security Alert: This file appears to contain "
                        "malicious content and cannot be uploaded. "
                        "If you believe this is an error, please contact support."
                    )
                )

            logger.info("ClamAV scan passed: %s", uploaded_file.name)
            return True

        except ValidationError:
            raise
        except Exception:
            logger.exception("ClamAV scan error for %s", uploaded_file.name)
            return True  # fail-safe

    # -- VirusTotal integration -----------------------------------------------

    def _scan_with_virustotal(self, uploaded_file: UploadedFile) -> bool:
        """Scan with VirusTotal cloud API."""
        import requests

        api_key = getattr(settings, "VIRUSTOTAL_API_KEY", None)
        if not api_key:
            logger.warning("VirusTotal API key is not configured — skipping")
            return True

        try:
            url = "https://www.virustotal.com/vtapi/v2/file/scan"

            uploaded_file.seek(0)
            files = {"file": (uploaded_file.name, uploaded_file.read())}
            uploaded_file.seek(0)

            response = requests.post(
                url, files=files, params={"apikey": api_key}, timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                positives = data.get("positives", 0)
                if positives > 0:
                    logger.error(
                        "MALWARE DETECTED by VirusTotal: %s — detections: %d",
                        uploaded_file.name,
                        positives,
                    )
                    raise ValidationError(
                        _(
                            "Security Alert: This file has been flagged as "
                            "potentially malicious and cannot be uploaded."
                        )
                    )
                logger.info("VirusTotal scan passed: %s", uploaded_file.name)
                return True

            logger.error("VirusTotal API error: HTTP %d", response.status_code)
            return True  # fail-safe

        except ValidationError:
            raise
        except Exception:
            logger.exception(
                "VirusTotal scan error for %s", uploaded_file.name
            )
            return True  # fail-safe


# ════════════════════════════════════════════════════════════════════════════
# Pre-built validators (convenience instances)
# ════════════════════════════════════════════════════════════════════════════


def _lazy_validator(
    max_size_attr: str,
    extensions_attr: str,
) -> FileValidator:
    """
    Build a :class:`FileValidator` whose limits come from Django settings.

    Values are resolved at call time so that settings overrides (e.g.
    in tests) are respected.
    """
    return FileValidator(
        max_size=getattr(settings, max_size_attr, None),
        allowed_extensions=getattr(settings, extensions_attr, set()),
    )


def get_image_validator() -> FileValidator:
    """Return a validator configured for image uploads."""
    return _lazy_validator("MAX_IMAGE_SIZE", "IMAGE_EXTENSIONS")


def get_document_validator() -> FileValidator:
    """Return a validator configured for document uploads."""
    return _lazy_validator("MAX_DOCUMENT_SIZE", "DOCUMENT_EXTENSIONS")


def get_avatar_validator() -> FileValidator:
    """Return a validator configured for avatar uploads."""
    return _lazy_validator("MAX_AVATAR_SIZE", "IMAGE_EXTENSIONS")


def get_invoice_validator() -> FileValidator:
    """Return a validator configured for invoice uploads."""
    return _lazy_validator("MAX_INVOICE_SIZE", "DOCUMENT_EXTENSIONS")
