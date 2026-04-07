"""
Custom exceptions for the orders module (Task 43).
"""


class InsufficientStockError(Exception):
    """Raised when stock is insufficient for an order."""

    def __init__(
        self,
        message="Insufficient stock",
        product=None,
        requested_quantity=None,
        available_quantity=None,
        line_item=None,
    ):
        self.product = product
        self.requested_quantity = requested_quantity
        self.available_quantity = available_quantity
        self.line_item = line_item
        details = []
        if product:
            details.append(f"product={product}")
        if requested_quantity is not None:
            details.append(f"requested={requested_quantity}")
        if available_quantity is not None:
            details.append(f"available={available_quantity}")
        if details:
            message = f"{message} ({', '.join(details)})"
        super().__init__(message)


class OrderValidationError(Exception):
    """Raised when order data fails validation."""
    pass


class InvalidStatusTransition(Exception):
    """Raised for disallowed status transitions."""
    pass


class OrderLockedError(Exception):
    """Raised when editing a locked order."""
    pass
