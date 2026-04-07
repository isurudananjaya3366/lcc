"""
DNS verification and SSL tracking utilities for LankaCommerce Cloud custom domains.

Provides DNS TXT record verification for custom domain ownership,
verification token generation, domain verification status management,
and SSL certificate status tracking.

Verification workflow:
    1. Tenant requests custom domain (e.g. shop.mybusiness.lk).
    2. Platform generates a unique verification token (UUID4).
    3. Token is stored in Domain.metadata["verification_token"].
    4. Tenant adds a TXT record to their DNS:
       _lcc-verification.shop.mybusiness.lk  TXT  "lcc-verify=<token>"
    5. Platform checks the DNS TXT record via dnspython.
    6. If the TXT record matches, Domain.is_verified is set to True
       and Domain.verified_at is set to the current timestamp.

DNS lookup:
    Uses the dnspython library (dns.resolver) for TXT record resolution.
    Falls back gracefully when dnspython is not installed (logs a warning
    and returns False for all verification attempts).

Verification token format:
    lcc-verify=<uuid4>
    Example: lcc-verify=a1b2c3d4-e5f6-7890-abcd-ef1234567890

TXT record name:
    _lcc-verification.{domain}
    Example: _lcc-verification.shop.mybusiness.lk

Verification states (Task 35):
    - pending:  Token generated, waiting for DNS propagation.
    - verified: DNS check passed, domain ownership confirmed.
    - failed:   DNS check failed (wrong or missing TXT record).

SSL certificate status tracking (Task 36):
    The Domain model tracks TLS certificate lifecycle via ssl_status:
    - none:    No SSL certificate configured.
    - pending: Certificate provisioning in progress (e.g. Let's Encrypt).
    - active:  Valid certificate installed and serving traffic.
    - expired: Certificate has expired; renewal needed.
    - failed:  Certificate provisioning or renewal failed.

    SSL status transitions are managed by update_ssl_status() and
    expiry is tracked via Domain.ssl_expires_at.

Task coverage:
    - Task 32: DNS TXT verification logic (verify_domain_dns)
    - Task 33: Verification token generation (generate_verification_token)
    - Task 34: Verification check workflow (check_domain_verification)
    - Task 35: Verification status storage (update_verification_status)
    - Task 36: SSL certificate status tracking (update_ssl_status)
"""

from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING

from django.utils import timezone

if TYPE_CHECKING:
    from apps.tenants.models import Domain

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Prefix for the DNS TXT record name
DNS_VERIFICATION_PREFIX = "_lcc-verification"

# Prefix for the TXT record value
TXT_RECORD_VALUE_PREFIX = "lcc-verify="

# Verification status constants (stored in Domain.metadata)
VERIFICATION_STATUS_PENDING = "pending"
VERIFICATION_STATUS_VERIFIED = "verified"
VERIFICATION_STATUS_FAILED = "failed"

# Metadata keys used in Domain.metadata
META_KEY_VERIFICATION_TOKEN = "verification_token"
META_KEY_VERIFICATION_STATUS = "verification_status"
META_KEY_VERIFICATION_INITIATED_AT = "verification_initiated_at"
META_KEY_VERIFICATION_LAST_CHECKED_AT = "verification_last_checked_at"
META_KEY_VERIFICATION_FAILURE_REASON = "verification_failure_reason"


# ---------------------------------------------------------------------------
# Task 33: Generate Verification Token
# ---------------------------------------------------------------------------

def generate_verification_token() -> str:
    """
    Generate a unique verification token for DNS ownership verification.

    Uses UUID4 (random) to produce a universally unique token that is
    stored in Domain.metadata and must be added as a DNS TXT record
    by the domain owner.

    Returns:
        str: A UUID4 string, e.g. "a1b2c3d4-e5f6-7890-abcd-ef1234567890".
    """
    return str(uuid.uuid4())


def get_expected_txt_value(token: str) -> str:
    """
    Build the expected TXT record value from a verification token.

    The domain owner must create a TXT record with this exact value
    at the _lcc-verification subdomain of their custom domain.

    Args:
        token: The verification token (UUID4 string).

    Returns:
        str: The expected TXT record value,
            e.g. "lcc-verify=a1b2c3d4-e5f6-7890-abcd-ef1234567890".
    """
    return f"{TXT_RECORD_VALUE_PREFIX}{token}"


def get_verification_record_name(domain: str) -> str:
    """
    Build the DNS TXT record name for verification.

    Args:
        domain: The custom domain string, e.g. "shop.mybusiness.lk".

    Returns:
        str: The TXT record name,
            e.g. "_lcc-verification.shop.mybusiness.lk".
    """
    return f"{DNS_VERIFICATION_PREFIX}.{domain}"


# ---------------------------------------------------------------------------
# Task 32: DNS Verification Logic
# ---------------------------------------------------------------------------

def verify_domain_dns(domain_str: str, expected_token: str) -> bool:
    """
    Verify that the DNS TXT record for a domain matches the expected token.

    Queries the DNS TXT records at _lcc-verification.{domain} and checks
    if any record matches the expected value "lcc-verify={token}".

    Uses the dnspython library for DNS resolution. If dnspython is not
    installed, logs a warning and returns False.

    Args:
        domain_str: The custom domain to verify, e.g. "shop.mybusiness.lk".
        expected_token: The verification token to match against.

    Returns:
        bool: True if a matching TXT record was found, False otherwise.
    """
    record_name = get_verification_record_name(domain_str)
    expected_value = get_expected_txt_value(expected_token)

    try:
        import dns.resolver
    except ImportError:
        logger.warning(
            "dnspython is not installed. DNS verification is unavailable. "
            "Install with: pip install dnspython"
        )
        return False

    try:
        answers = dns.resolver.resolve(record_name, "TXT")
    except dns.resolver.NXDOMAIN:
        logger.debug(
            "verify_domain_dns: NXDOMAIN for '%s' - no DNS record found",
            record_name,
        )
        return False
    except dns.resolver.NoAnswer:
        logger.debug(
            "verify_domain_dns: NoAnswer for '%s' - no TXT records",
            record_name,
        )
        return False
    except dns.resolver.NoNameservers:
        logger.warning(
            "verify_domain_dns: NoNameservers for '%s' - DNS resolution failed",
            record_name,
        )
        return False
    except Exception as exc:
        logger.warning(
            "verify_domain_dns: unexpected error resolving '%s': %s",
            record_name,
            exc,
        )
        return False

    # Check each TXT record for a match
    for rdata in answers:
        # TXT records can have multiple strings concatenated
        txt_value = b"".join(rdata.strings).decode("utf-8", errors="ignore").strip()
        if txt_value == expected_value:
            logger.info(
                "verify_domain_dns: TXT record match for '%s'",
                domain_str,
            )
            return True

    logger.debug(
        "verify_domain_dns: no matching TXT record for '%s' "
        "(expected '%s' at '%s')",
        domain_str,
        expected_value,
        record_name,
    )
    return False


# ---------------------------------------------------------------------------
# Task 34: Verification Workflow (Initiate + Check)
# ---------------------------------------------------------------------------

def initiate_domain_verification(domain: "Domain") -> str:
    """
    Start the DNS verification process for a custom domain.

    Generates a new verification token, stores it in Domain.metadata,
    sets the verification status to 'pending', and saves the domain.

    The domain owner must then create a DNS TXT record:
        Name:  _lcc-verification.{domain.domain}
        Value: lcc-verify={token}

    Args:
        domain: The Domain model instance to verify. Must have
            domain_type='custom'.

    Returns:
        str: The generated verification token.

    Raises:
        ValueError: If the domain is not a custom domain.
    """
    if domain.is_platform_domain:
        raise ValueError(
            f"Cannot initiate verification for platform domain '{domain.domain}'. "
            "Only custom domains require DNS verification."
        )

    token = generate_verification_token()

    # Ensure metadata is a dict
    if not isinstance(domain.metadata, dict):
        domain.metadata = {}

    domain.metadata[META_KEY_VERIFICATION_TOKEN] = token
    domain.metadata[META_KEY_VERIFICATION_STATUS] = VERIFICATION_STATUS_PENDING
    domain.metadata[META_KEY_VERIFICATION_INITIATED_AT] = (
        timezone.now().isoformat()
    )
    # Clear any previous failure reason
    domain.metadata.pop(META_KEY_VERIFICATION_FAILURE_REASON, None)

    domain.is_verified = False
    domain.verified_at = None
    domain.save(update_fields=["metadata", "is_verified", "verified_at", "updated_on"])

    logger.info(
        "initiate_domain_verification: token generated for domain='%s' "
        "tenant='%s' - TXT record: %s.%s -> %s",
        domain.domain,
        getattr(domain.tenant, "name", "?"),
        DNS_VERIFICATION_PREFIX,
        domain.domain,
        get_expected_txt_value(token),
    )

    return token


def check_domain_verification(domain: "Domain") -> bool:
    """
    Check DNS and update the domain's verification status.

    Reads the verification token from Domain.metadata, performs a DNS
    TXT lookup, and updates the domain's verification status accordingly.

    On success (Task 35):
        - domain.is_verified = True
        - domain.verified_at = now
        - domain.metadata["verification_status"] = "verified"

    On failure:
        - domain.metadata["verification_status"] = "failed"
        - domain.metadata["verification_failure_reason"] = reason
        - domain.metadata["verification_last_checked_at"] = now

    Args:
        domain: The Domain model instance to check. Must have a
            verification token in metadata.

    Returns:
        bool: True if verification succeeded, False otherwise.

    Raises:
        ValueError: If no verification token is found in metadata.
    """
    if not isinstance(domain.metadata, dict):
        raise ValueError(
            f"Domain '{domain.domain}' has no metadata. "
            "Call initiate_domain_verification() first."
        )

    token = domain.metadata.get(META_KEY_VERIFICATION_TOKEN)
    if not token:
        raise ValueError(
            f"Domain '{domain.domain}' has no verification token. "
            "Call initiate_domain_verification() first."
        )

    now = timezone.now()
    domain.metadata[META_KEY_VERIFICATION_LAST_CHECKED_AT] = now.isoformat()

    # Perform DNS lookup
    is_valid = verify_domain_dns(domain.domain, token)

    if is_valid:
        # Task 35: Store verification status and timestamp
        update_verification_status(domain, VERIFICATION_STATUS_VERIFIED)
        logger.info(
            "check_domain_verification: domain='%s' verified successfully",
            domain.domain,
        )
        return True
    else:
        domain.metadata[META_KEY_VERIFICATION_STATUS] = VERIFICATION_STATUS_FAILED
        domain.metadata[META_KEY_VERIFICATION_FAILURE_REASON] = (
            "DNS TXT record not found or does not match expected value"
        )
        domain.save(update_fields=["metadata", "updated_on"])
        logger.warning(
            "check_domain_verification: domain='%s' verification failed",
            domain.domain,
        )
        return False


# ---------------------------------------------------------------------------
# Task 35: Store Verification Status
# ---------------------------------------------------------------------------

def update_verification_status(
    domain: "Domain",
    status: str,
) -> None:
    """
    Update the verification status of a domain.

    Handles the state transitions for domain verification:
        - pending:  Waiting for DNS propagation.
        - verified: DNS check passed, domain ownership confirmed.
        - failed:   DNS check failed.

    When status is 'verified':
        - domain.is_verified = True
        - domain.verified_at = current timestamp
        - domain.metadata["verification_status"] = "verified"

    When status is 'pending' or 'failed':
        - domain.is_verified = False
        - domain.verified_at = None (cleared)
        - domain.metadata["verification_status"] = status

    Args:
        domain: The Domain model instance to update.
        status: One of VERIFICATION_STATUS_PENDING, VERIFICATION_STATUS_VERIFIED,
            or VERIFICATION_STATUS_FAILED.

    Raises:
        ValueError: If the status is not a valid verification status.
    """
    valid_statuses = {
        VERIFICATION_STATUS_PENDING,
        VERIFICATION_STATUS_VERIFIED,
        VERIFICATION_STATUS_FAILED,
    }
    if status not in valid_statuses:
        raise ValueError(
            f"Invalid verification status '{status}'. "
            f"Must be one of: {', '.join(sorted(valid_statuses))}"
        )

    if not isinstance(domain.metadata, dict):
        domain.metadata = {}

    domain.metadata[META_KEY_VERIFICATION_STATUS] = status

    if status == VERIFICATION_STATUS_VERIFIED:
        domain.is_verified = True
        domain.verified_at = timezone.now()
        # Clear failure reason on success
        domain.metadata.pop(META_KEY_VERIFICATION_FAILURE_REASON, None)
        domain.save(
            update_fields=[
                "is_verified",
                "verified_at",
                "metadata",
                "updated_on",
            ]
        )
    else:
        domain.is_verified = False
        domain.verified_at = None
        domain.save(
            update_fields=[
                "is_verified",
                "verified_at",
                "metadata",
                "updated_on",
            ]
        )

    logger.info(
        "update_verification_status: domain='%s' status='%s' "
        "is_verified=%s verified_at=%s",
        domain.domain,
        status,
        domain.is_verified,
        domain.verified_at,
    )


# ---------------------------------------------------------------------------
# Task 36: SSL Certificate Status Tracking
# ---------------------------------------------------------------------------

# SSL status constants (mirror Domain model choices)
SSL_STATUS_NONE = "none"
SSL_STATUS_PENDING = "pending"
SSL_STATUS_ACTIVE = "active"
SSL_STATUS_EXPIRED = "expired"
SSL_STATUS_FAILED = "failed"

_VALID_SSL_STATUSES = frozenset({
    SSL_STATUS_NONE,
    SSL_STATUS_PENDING,
    SSL_STATUS_ACTIVE,
    SSL_STATUS_EXPIRED,
    SSL_STATUS_FAILED,
})


def update_ssl_status(
    domain: "Domain",
    status: str,
    ssl_expires_at=None,
) -> None:
    """
    Update the SSL certificate status for a domain.

    Manages the TLS certificate lifecycle state transitions:
        - none:    No certificate configured (initial state).
        - pending: Certificate provisioning initiated (e.g. ACME/Let's Encrypt).
        - active:  Valid certificate installed and serving traffic.
        - expired: Certificate has expired; renewal needed.
        - failed:  Certificate provisioning or renewal failed.

    When status is 'active' and ssl_expires_at is provided, the expiry
    date is recorded for monitoring and automated renewal.

    When status transitions to 'none' or 'failed', ssl_expires_at is
    cleared.

    Args:
        domain: The Domain model instance to update.
        status: One of SSL_STATUS_NONE, SSL_STATUS_PENDING,
            SSL_STATUS_ACTIVE, SSL_STATUS_EXPIRED, SSL_STATUS_FAILED.
        ssl_expires_at: Optional datetime for certificate expiry.
            Only relevant when status is 'active'.

    Raises:
        ValueError: If the status is not a valid SSL status.
    """
    if status not in _VALID_SSL_STATUSES:
        raise ValueError(
            f"Invalid SSL status '{status}'. "
            f"Must be one of: {', '.join(sorted(_VALID_SSL_STATUSES))}"
        )

    domain.ssl_status = status

    if status == SSL_STATUS_ACTIVE and ssl_expires_at is not None:
        domain.ssl_expires_at = ssl_expires_at
    elif status in (SSL_STATUS_NONE, SSL_STATUS_FAILED):
        domain.ssl_expires_at = None

    update_fields = ["ssl_status", "ssl_expires_at", "updated_on"]
    domain.save(update_fields=update_fields)

    logger.info(
        "update_ssl_status: domain='%s' ssl_status='%s' "
        "ssl_expires_at=%s",
        domain.domain,
        status,
        domain.ssl_expires_at,
    )


def check_ssl_expiry(domain: "Domain") -> bool:
    """
    Check if a domain's SSL certificate has expired.

    Compares Domain.ssl_expires_at against the current time. If the
    certificate has expired, updates ssl_status to 'expired'.

    Args:
        domain: The Domain model instance to check.

    Returns:
        bool: True if the certificate is still valid (not expired),
        False if expired or no expiry date is set.
    """
    if domain.ssl_status != SSL_STATUS_ACTIVE:
        return False

    if domain.ssl_expires_at is None:
        return False

    now = timezone.now()
    if domain.ssl_expires_at <= now:
        update_ssl_status(domain, SSL_STATUS_EXPIRED)
        logger.warning(
            "check_ssl_expiry: SSL certificate expired for domain='%s' "
            "(expired at %s)",
            domain.domain,
            domain.ssl_expires_at,
        )
        return False

    return True
