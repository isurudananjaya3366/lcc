"""Custom exceptions for stock operations."""


class StockOperationError(Exception):
    """General stock operation failure."""
    pass


class InsufficientStockError(StockOperationError):
    """Not enough stock available for the requested operation."""

    def __init__(self, message="Insufficient stock", available=None, requested=None):
        self.available = available
        self.requested = requested
        if available is not None and requested is not None:
            message = f"{message}: need {requested}, have {available}"
        super().__init__(message)


class InvalidProductError(StockOperationError):
    """Product/variant combination is invalid."""
    pass


class InactiveWarehouseError(StockOperationError):
    """Warehouse is not active."""
    pass
