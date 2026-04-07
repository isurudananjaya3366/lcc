"""
Batch stock operations — process multiple operations in one transaction.
"""

import logging
from decimal import Decimal

from django.db import transaction

from apps.inventory.stock.results import BatchOperationResult, OperationResult
from apps.inventory.stock.services.stock_service import StockService

logger = logging.getLogger("inventory.stock.operations")


class BatchStockService:
    """Process multiple stock operations atomically."""

    def __init__(self, user=None, notes=""):
        self.service = StockService(user=user, notes=notes)

    def validate_batch(self, operations):
        """Validate a list of operation dicts without executing.

        Each dict must contain at minimum:
            operation: str ("stock_in", "stock_out", "transfer", "reserve", "release")
            product: Product instance
            quantity: Decimal
            warehouse: Warehouse instance (or from_warehouse/to_warehouse for transfer)
        """
        errors = []
        for idx, op in enumerate(operations):
            op_errors = []
            if "operation" not in op:
                op_errors.append("Missing 'operation' key.")
            if "product" not in op:
                op_errors.append("Missing 'product' key.")
            if "quantity" not in op:
                op_errors.append("Missing 'quantity' key.")
            else:
                try:
                    qty = Decimal(str(op["quantity"]))
                    if qty <= 0:
                        op_errors.append("Quantity must be positive.")
                except Exception:
                    op_errors.append("Invalid quantity value.")

            op_type = op.get("operation", "")
            if op_type == "transfer":
                if not op.get("from_warehouse"):
                    op_errors.append("Transfer requires 'from_warehouse'.")
                if not op.get("to_warehouse"):
                    op_errors.append("Transfer requires 'to_warehouse'.")
            elif op_type in ("stock_in", "stock_out", "reserve", "release"):
                if not op.get("warehouse"):
                    op_errors.append(f"'{op_type}' requires 'warehouse'.")

            if op_errors:
                errors.append({"index": idx, "errors": op_errors})
        return errors

    @transaction.atomic
    def execute_batch(self, operations, fail_fast=True):
        """Execute a batch of operations.

        Args:
            operations: list of operation dicts (see validate_batch).
            fail_fast: if True, rollback entire batch on first error.
        """
        batch_result = BatchOperationResult()

        for idx, op in enumerate(operations):
            op_type = op.get("operation", "")
            try:
                if fail_fast:
                    result = self._run_single(op)
                else:
                    sid = transaction.savepoint()
                    try:
                        result = self._run_single(op)
                        transaction.savepoint_commit(sid)
                    except Exception as exc:
                        transaction.savepoint_rollback(sid)
                        result = OperationResult.fail(op_type, str(exc))
            except Exception as exc:
                if fail_fast:
                    raise
                result = OperationResult.fail(op_type, str(exc))

            batch_result.add(result)

        logger.info(
            "BATCH completed: total=%d success=%d failed=%d",
            batch_result.total_count,
            batch_result.success_count,
            batch_result.failure_count,
        )
        return batch_result

    def _run_single(self, op):
        """Dispatch a single operation dict to the appropriate service method."""
        op_type = op["operation"]
        kwargs = {
            k: v
            for k, v in op.items()
            if k not in ("operation",)
        }

        method = getattr(self.service, op_type, None)
        if method is None:
            raise ValueError(f"Unknown operation type: {op_type}")
        return method(**kwargs)
