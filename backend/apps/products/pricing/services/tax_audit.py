"""
Tax audit logging – records tax calculations for compliance.

Creates structured log entries for every tax calculation, useful
for Sri Lankan IRD compliance and internal auditing.
"""

from __future__ import annotations

import logging
from decimal import Decimal

logger = logging.getLogger("pricing.tax_audit")


def log_tax_calculation(
    *,
    product_id: str | None = None,
    base_price: Decimal,
    tax_rate: Decimal,
    tax_amount: Decimal,
    total_price: Decimal,
    is_inclusive: bool,
    customer_id: str | None = None,
    svat_applied: bool = False,
    extra: dict | None = None,
) -> None:
    """
    Emit a structured INFO log entry for a tax calculation event.

    All keyword-only arguments ensure field names are always clear.
    """
    msg = (
        f"TAX_CALC product={product_id} base={base_price} "
        f"rate={tax_rate}% tax={tax_amount} total={total_price} "
        f"inclusive={is_inclusive} svat={svat_applied} customer={customer_id}"
    )
    logger.info(msg, extra={"audit": True, **(extra or {})})
