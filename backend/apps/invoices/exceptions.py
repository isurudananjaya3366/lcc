"""
Invoice-specific exceptions.
"""


class InvoiceError(Exception):
    """Base exception for invoice operations."""
    pass


class InvalidTransitionError(InvoiceError):
    """Raised when an invalid status transition is attempted."""
    pass


class InvoiceLockedError(InvoiceError):
    """Raised when trying to edit a non-editable invoice."""
    pass


class CreditLimitExceededError(InvoiceError):
    """Raised when credit note exceeds original invoice total."""
    pass
