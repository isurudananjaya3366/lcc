'use client';

import { cn } from '@/lib/utils';

interface StockCellProps {
  quantity: number;
  lowStockThreshold?: number;
}

function getStockLevel(quantity: number, threshold: number = 10) {
  if (quantity === 0) return 'out';
  if (quantity <= threshold) return 'low';
  return 'normal';
}

const levelConfig = {
  normal: { dot: 'bg-green-500', text: 'text-green-700 dark:text-green-400' },
  low: { dot: 'bg-amber-500', text: 'text-amber-700 dark:text-amber-400' },
  out: { dot: 'bg-red-500', text: 'text-red-700 dark:text-red-400' },
} as const;

export function StockCell({ quantity, lowStockThreshold = 10 }: StockCellProps) {
  const level = getStockLevel(quantity, lowStockThreshold);
  const config = levelConfig[level];

  return (
    <div className="flex items-center justify-center gap-2">
      <span className={cn('h-2 w-2 rounded-full', config.dot)} aria-hidden="true" />
      <span className={cn('font-medium', config.text)}>{quantity}</span>
      <span className="sr-only">
        {level === 'out' ? 'Out of stock' : level === 'low' ? 'Low stock' : 'In stock'}
      </span>
    </div>
  );
}
