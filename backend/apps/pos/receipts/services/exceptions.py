"""Custom exceptions for the receipts module."""


class ReceiptBuildError(Exception):
    """Base exception for receipt building errors."""


class CartValidationError(ReceiptBuildError):
    """Cart validation failed."""


class TemplateMissingError(ReceiptBuildError):
    """Receipt template not found."""


class DataBuildError(ReceiptBuildError):
    """Error building a receipt section."""


class ReceiptNumberGenerationError(Exception):
    """Failed to generate a unique receipt number."""
