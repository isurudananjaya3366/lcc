'use client';

import { X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface FilterState {
  search: string;
  status: string;
  category: string;
  stock: string;
}

interface ProductFiltersProps {
  filters: FilterState;
  onFilterChange: (key: keyof FilterState, value: string) => void;
  onClearFilters: () => void;
  className?: string;
  children: React.ReactNode;
}

function countActiveFilters(filters: FilterState): number {
  let count = 0;
  if (filters.search.length > 0) count++;
  if (filters.status !== 'all') count++;
  if (filters.category !== '') count++;
  if (filters.stock !== 'all') count++;
  return count;
}

export function ProductFilters({
  filters,
  onClearFilters,
  className,
  children,
}: ProductFiltersProps) {
  const activeCount = countActiveFilters(filters);

  return (
    <div
      className={cn(
        'rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-900',
        className
      )}
    >
      <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center">
        {children}

        {activeCount > 0 && (
          <button
            type="button"
            onClick={onClearFilters}
            className="inline-flex items-center gap-1 whitespace-nowrap text-sm font-medium text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200"
            aria-label={`Clear ${activeCount} filter${activeCount > 1 ? 's' : ''}`}
          >
            <X className="h-4 w-4" />
            Clear {activeCount > 1 ? `${activeCount} Filters` : 'Filter'}
          </button>
        )}
      </div>
    </div>
  );
}

export type { FilterState };
