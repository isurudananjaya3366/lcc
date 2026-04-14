'use client';

import { useState } from 'react';
import { ArrowDown, ArrowUp, Edit, ArrowRightLeft, RotateCcw } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { StockMovement, StockMovementType } from '@/types/inventory';
import { MovementDetailModal } from './MovementDetailModal';

interface MovementsTimelineProps {
  movements: StockMovement[];
  isLoading?: boolean;
}

const typeConfig: Record<
  StockMovementType,
  {
    icon: React.ComponentType<{ className?: string }>;
    color: string;
    bgColor: string;
    label: string;
  }
> = {
  PURCHASE: {
    icon: ArrowDown,
    color: 'text-green-600 dark:text-green-400',
    bgColor: 'bg-green-100 dark:bg-green-900/30',
    label: 'Purchase',
  },
  SALE: {
    icon: ArrowUp,
    color: 'text-red-600 dark:text-red-400',
    bgColor: 'bg-red-100 dark:bg-red-900/30',
    label: 'Sale',
  },
  ADJUSTMENT: {
    icon: Edit,
    color: 'text-yellow-600 dark:text-yellow-400',
    bgColor: 'bg-yellow-100 dark:bg-yellow-900/30',
    label: 'Adjustment',
  },
  TRANSFER: {
    icon: ArrowRightLeft,
    color: 'text-blue-600 dark:text-blue-400',
    bgColor: 'bg-blue-100 dark:bg-blue-900/30',
    label: 'Transfer',
  },
  RETURN: {
    icon: RotateCcw,
    color: 'text-purple-600 dark:text-purple-400',
    bgColor: 'bg-purple-100 dark:bg-purple-900/30',
    label: 'Return',
  },
  DAMAGE: {
    icon: Edit,
    color: 'text-orange-600 dark:text-orange-400',
    bgColor: 'bg-orange-100 dark:bg-orange-900/30',
    label: 'Damage',
  },
};

export function MovementsTimeline({ movements, isLoading }: MovementsTimelineProps) {
  const [selectedMovement, setSelectedMovement] = useState<StockMovement | null>(null);

  if (isLoading) {
    return (
      <div className="space-y-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="flex gap-4">
            <div className="h-10 w-10 animate-pulse rounded-full bg-gray-200 dark:bg-gray-700" />
            <div className="flex-1 space-y-2">
              <div className="h-4 w-3/4 animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
              <div className="h-3 w-1/2 animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (movements.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-gray-300 py-12 dark:border-gray-700">
        <p className="text-sm text-gray-500 dark:text-gray-400">
          No movements found for the selected filters.
        </p>
      </div>
    );
  }

  return (
    <>
      <div className="relative space-y-0">
        {/* Timeline line */}
        <div className="absolute left-5 top-0 h-full w-px bg-gray-200 dark:bg-gray-700" />

        {movements.map((movement, index) => {
          const config = typeConfig[movement.movementType] ?? typeConfig.ADJUSTMENT;
          const Icon = config.icon;
          const isPositive =
            movement.movementType === 'PURCHASE' || movement.movementType === 'RETURN';

          return (
            <button
              key={movement.id}
              type="button"
              onClick={() => setSelectedMovement(movement)}
              className="relative flex w-full gap-4 py-4 text-left hover:bg-gray-50 dark:hover:bg-gray-800/50"
            >
              {/* Icon */}
              <div
                className={cn(
                  'z-10 flex h-10 w-10 shrink-0 items-center justify-center rounded-full',
                  config.bgColor
                )}
              >
                <Icon className={cn('h-4 w-4', config.color)} />
              </div>

              {/* Content */}
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-gray-900 dark:text-gray-100">
                    {config.label}
                  </span>
                  <span
                    className={cn(
                      'text-sm font-semibold',
                      isPositive
                        ? 'text-green-600 dark:text-green-400'
                        : 'text-red-600 dark:text-red-400'
                    )}
                  >
                    {isPositive ? '+' : '-'}
                    {Math.abs(movement.quantity)}
                  </span>
                  <span className="text-xs text-gray-400">{movement.sku}</span>
                </div>
                <div className="mt-1 flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
                  <span>{new Date(movement.createdAt).toLocaleString()}</span>
                  {movement.referenceId && (
                    <span className="font-mono">Ref: {movement.referenceId}</span>
                  )}
                  <span>by {movement.createdBy}</span>
                </div>
                {movement.notes && (
                  <p className="mt-1 truncate text-xs text-gray-400 dark:text-gray-500">
                    {movement.notes}
                  </p>
                )}
              </div>
            </button>
          );
        })}
      </div>

      <MovementDetailModal movement={selectedMovement} onClose={() => setSelectedMovement(null)} />
    </>
  );
}
