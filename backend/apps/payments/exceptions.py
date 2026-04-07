"""
Custom exceptions for the payments application.
"""


class PaymentError(Exception):
    """Base exception for payment operations."""

    pass


class InvalidPaymentStatusTransition(PaymentError):
    """Raised when an invalid status transition is attempted."""

    def __init__(self, current_status, target_status):
        self.current_status = current_status
        self.target_status = target_status
        super().__init__(
            f"Cannot transition payment from '{current_status}' to '{target_status}'."
        )


class PaymentNumberGenerationError(PaymentError):
    """Raised when payment number generation fails."""

    pass


class PaymentValidationError(PaymentError):
    """Raised when payment validation fails."""

    pass


class InsufficientPaymentError(PaymentError):
    """Raised when payment amount is insufficient."""

    pass


class DuplicatePaymentError(PaymentError):
    """Raised when a duplicate payment is detected."""

    pass


class RefundError(PaymentError):
    """Raised when a refund operation fails."""

    pass
