'use client';

import { cn } from '@/lib/utils';
import { FilterTag, type ActiveFilter } from './FilterTag';

interface ActiveFiltersProps {
  filters: ActiveFilter[];
  onRemove: (filterId: string) => void;
  onClearAll?: () => void;
  className?: string;
}

export function ActiveFilters({ filters, onRemove, onClearAll, className }: ActiveFiltersProps) {
  if (filters.length === 0) return null;

  return (
    <div className={cn('flex flex-wrap items-center gap-2', className)}>
      <span className="text-xs font-medium text-gray-500">Active:</span>
      {filters.map((filter) => (
        <FilterTag key={filter.id} filter={filter} onRemove={onRemove} />
      ))}
      {filters.length >= 2 && onClearAll && (
        <button
          type="button"
          onClick={onClearAll}
          className="text-xs font-medium text-blue-600 hover:text-blue-800 hover:underline transition-colors ml-1"
        >
          Clear All
        </button>
      )}
    </div>
  );
}
