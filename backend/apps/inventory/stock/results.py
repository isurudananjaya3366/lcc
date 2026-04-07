"""
Operation result models for stock operations.

Provides structured result objects returned from all stock service
methods, ensuring consistent success/failure reporting.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any

from django.utils import timezone


@dataclass
class OperationResult:
    """Structured result from a stock operation."""

    success: bool
    operation_type: str
    timestamp: datetime = field(default_factory=timezone.now)
    data: dict[str, Any] = field(default_factory=dict)
    errors: list[dict[str, str]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    message: str = ""

    @classmethod
    def ok(cls, operation_type, data=None, warnings=None, message=""):
        """Create a success result."""
        return cls(
            success=True,
            operation_type=operation_type,
            data=data or {},
            warnings=warnings or [],
            message=message,
        )

    @classmethod
    def fail(cls, operation_type, errors):
        """Create a failure result."""
        if isinstance(errors, str):
            errors = [{"message": errors}]
        return cls(
            success=False,
            operation_type=operation_type,
            errors=errors,
        )

    def has_warnings(self):
        return bool(self.warnings)

    def get_error_messages(self):
        return [e.get("message", str(e)) for e in self.errors]

    def raise_if_failed(self):
        """Raise StockOperationError if the operation failed."""
        if not self.success:
            from apps.inventory.stock.exceptions import StockOperationError

            raise StockOperationError("; ".join(self.get_error_messages()))

    def to_dict(self):
        return {
            "success": self.success,
            "operation_type": self.operation_type,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "errors": self.errors,
            "warnings": self.warnings,
        }


@dataclass
class BatchOperationResult:
    """Result from a batch stock operation."""

    total_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    results: list[OperationResult] = field(default_factory=list)

    def add(self, result: OperationResult):
        self.total_count += 1
        self.results.append(result)
        if result.success:
            self.success_count += 1
        else:
            self.failure_count += 1

    def get_failed(self):
        return [r for r in self.results if not r.success]

    def get_summary(self):
        return {
            "total": self.total_count,
            "success": self.success_count,
            "failed": self.failure_count,
        }

    @property
    def all_successful(self):
        return self.failure_count == 0

    def to_dict(self):
        return {
            **self.get_summary(),
            "results": [r.to_dict() for r in self.results],
        }
