import { cn } from '@/lib/utils';

interface StockWarningProps {
  stockLevel: number | null;
  maxQuantity?: number | null;
}

export function StockWarning({ stockLevel, maxQuantity: _maxQuantity }: StockWarningProps) {
  if (stockLevel === null || stockLevel === undefined) return null;

  if (stockLevel === 0) {
    return (
      <p
        className={cn(
          'mt-1 text-sm font-medium text-red-600 dark:text-red-400'
        )}
        role="alert"
      >
        Out of stock
      </p>
    );
  }

  if (stockLevel <= 5) {
    return (
      <p
        className={cn(
          'mt-1 text-sm font-medium text-amber-600 dark:text-amber-400'
        )}
        role="status"
      >
        Only {stockLevel} left in stock
      </p>
    );
  }

  return null;
}
