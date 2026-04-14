'use client';

import { X } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { StockMovement } from '@/types/inventory';

interface MovementDetailModalProps {
  movement: StockMovement | null;
  onClose: () => void;
}

export function MovementDetailModal({ movement, onClose }: MovementDetailModalProps) {
  if (!movement) return null;

  const isPositive = movement.movementType === 'PURCHASE' || movement.movementType === 'RETURN';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Overlay */}
      <div className="absolute inset-0 bg-black/50" onClick={onClose} aria-hidden="true" />

      {/* Modal */}
      <div className="relative z-10 w-full max-w-lg rounded-lg bg-white p-6 shadow-xl dark:bg-gray-900">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            Movement Details
          </h3>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-800"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="mt-4 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <DetailRow label="Type" value={movement.movementType} />
            <DetailRow label="Status" value={movement.status} />
            <DetailRow label="Product" value={movement.productId} />
            <DetailRow label="SKU" value={movement.sku} />
            <DetailRow
              label="Quantity"
              value={
                <span
                  className={cn(
                    'font-semibold',
                    isPositive
                      ? 'text-green-600 dark:text-green-400'
                      : 'text-red-600 dark:text-red-400'
                  )}
                >
                  {isPositive ? '+' : '-'}
                  {Math.abs(movement.quantity)}
                </span>
              }
            />
            {movement.unitCost != null && (
              <DetailRow label="Unit Cost" value={`₨ ${movement.unitCost.toFixed(2)}`} />
            )}
            {movement.totalCost != null && (
              <DetailRow label="Total Cost" value={`₨ ${movement.totalCost.toFixed(2)}`} />
            )}
          </div>

          <hr className="border-gray-200 dark:border-gray-700" />

          <div className="grid grid-cols-2 gap-4">
            {movement.sourceWarehouseId && (
              <DetailRow label="From" value={movement.sourceWarehouseId} />
            )}
            {movement.destinationWarehouseId && (
              <DetailRow label="To" value={movement.destinationWarehouseId} />
            )}
            {movement.referenceType && (
              <DetailRow label="Ref Type" value={movement.referenceType} />
            )}
            {movement.referenceId && <DetailRow label="Ref ID" value={movement.referenceId} />}
          </div>

          <hr className="border-gray-200 dark:border-gray-700" />

          <div className="grid grid-cols-2 gap-4">
            <DetailRow label="Created By" value={movement.createdBy} />
            <DetailRow label="Created At" value={new Date(movement.createdAt).toLocaleString()} />
            {movement.completedAt && (
              <DetailRow
                label="Completed"
                value={new Date(movement.completedAt).toLocaleString()}
              />
            )}
          </div>

          {movement.notes && (
            <>
              <hr className="border-gray-200 dark:border-gray-700" />
              <div>
                <p className="text-xs font-medium text-gray-500 dark:text-gray-400">Notes</p>
                <p className="mt-1 text-sm text-gray-700 dark:text-gray-300">{movement.notes}</p>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function DetailRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div>
      <p className="text-xs font-medium text-gray-500 dark:text-gray-400">{label}</p>
      <p className="mt-0.5 text-sm text-gray-900 dark:text-gray-100">{value}</p>
    </div>
  );
}
