'use client';

import { useState } from 'react';
import { cn } from '@/lib/utils';

// ─── Types ──────────────────────────────────────────────────────────────────

interface SearchPriceFilterProps {
  minPrice: string;
  maxPrice: string;
  onPriceChange: (min: string, max: string) => void;
  className?: string;
}

// ─── Component ──────────────────────────────────────────────────────────────

export function SearchPriceFilter({
  minPrice,
  maxPrice,
  onPriceChange,
  className,
}: SearchPriceFilterProps) {
  const [localMin, setLocalMin] = useState(minPrice);
  const [localMax, setLocalMax] = useState(maxPrice);

  const handleApply = () => {
    onPriceChange(localMin, localMax);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleApply();
  };

  const hasChanges = localMin !== minPrice || localMax !== maxPrice;

  return (
    <div className={cn('space-y-3', className)}>
      <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Price Range</h3>

      <div className="flex items-center gap-2">
        <div className="relative flex-1">
          <span className="absolute left-2 top-1/2 -translate-y-1/2 text-xs text-gray-500 dark:text-gray-400">
            LKR
          </span>
          <input
            type="number"
            min="0"
            placeholder="Min"
            value={localMin}
            onChange={(e) => setLocalMin(e.target.value)}
            onKeyDown={handleKeyDown}
            className={cn(
              'w-full rounded-md border border-gray-300 py-1.5 pl-9 pr-2 text-sm',
              'bg-white text-gray-900 placeholder:text-gray-400',
              'focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary',
              'dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100 dark:placeholder:text-gray-500',
            )}
          />
        </div>

        <span className="text-xs text-gray-400">–</span>

        <div className="relative flex-1">
          <span className="absolute left-2 top-1/2 -translate-y-1/2 text-xs text-gray-500 dark:text-gray-400">
            LKR
          </span>
          <input
            type="number"
            min="0"
            placeholder="Max"
            value={localMax}
            onChange={(e) => setLocalMax(e.target.value)}
            onKeyDown={handleKeyDown}
            className={cn(
              'w-full rounded-md border border-gray-300 py-1.5 pl-9 pr-2 text-sm',
              'bg-white text-gray-900 placeholder:text-gray-400',
              'focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary',
              'dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100 dark:placeholder:text-gray-500',
            )}
          />
        </div>
      </div>

      <button
        type="button"
        onClick={handleApply}
        disabled={!hasChanges}
        className={cn(
          'w-full rounded-md px-3 py-1.5 text-sm font-medium transition-colors',
          hasChanges
            ? 'bg-primary text-white hover:bg-primary/90'
            : 'cursor-not-allowed bg-gray-100 text-gray-400 dark:bg-gray-800 dark:text-gray-500',
        )}
      >
        Apply
      </button>
    </div>
  );
}
