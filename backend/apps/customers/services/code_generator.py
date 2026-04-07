"""
Customer code generator service.

Generates unique, sequential customer codes in the format CUST-XXXXX.
Thread-safe via select_for_update with retry on collision.
"""

import re

from django.db import IntegrityError, transaction

from apps.customers.constants import (
    CUSTOMER_CODE_PREFIX,
    CUSTOMER_CODE_SEPARATOR,
    CUSTOMER_CODE_SEQUENCE_LENGTH,
)


class CustomerCodeGenerator:
    """
    Generates unique customer codes in the format CUST-00001.

    Uses the highest existing customer_code to determine the next
    sequence number. Handles concurrency via select_for_update
    and retries on UniqueConstraint violations.
    """

    PREFIX = CUSTOMER_CODE_PREFIX
    SEPARATOR = CUSTOMER_CODE_SEPARATOR
    SEQUENCE_LENGTH = CUSTOMER_CODE_SEQUENCE_LENGTH
    MAX_RETRIES = 5

    @classmethod
    def generate(cls) -> str:
        """
        Generate the next customer code.

        Returns:
            str: A unique customer code like "CUST-00001".

        Raises:
            RuntimeError: If unable to generate a unique code after retries.
        """
        from apps.customers.models import Customer

        pattern = f"^{cls.PREFIX}{cls.SEPARATOR}"

        for attempt in range(cls.MAX_RETRIES):
            try:
                with transaction.atomic():
                    last_customer = (
                        Customer.objects.filter(
                            customer_code__regex=pattern,
                        )
                        .select_for_update()
                        .order_by("-customer_code")
                        .values_list("customer_code", flat=True)
                        .first()
                    )

                    next_seq = cls._extract_next_sequence(last_customer)
                    return cls._format_code(next_seq)
            except IntegrityError:
                if attempt == cls.MAX_RETRIES - 1:
                    raise RuntimeError(
                        f"Failed to generate unique customer code "
                        f"after {cls.MAX_RETRIES} attempts."
                    )
                continue

        raise RuntimeError("Customer code generation failed.")

    @classmethod
    def _extract_next_sequence(cls, last_code: str | None) -> int:
        """Extract the numeric sequence from the last code and increment."""
        if not last_code:
            return 1

        match = re.search(r"(\d+)$", last_code)
        if match:
            return int(match.group(1)) + 1
        return 1

    @classmethod
    def _format_code(cls, sequence: int) -> str:
        """Format a sequence number into a customer code string."""
        padded = str(sequence).zfill(cls.SEQUENCE_LENGTH)
        return f"{cls.PREFIX}{cls.SEPARATOR}{padded}"
