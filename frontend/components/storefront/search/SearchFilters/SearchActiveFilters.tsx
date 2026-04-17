'use client';

import { cn } from '@/lib/utils';

// ─── Types ──────────────────────────────────────────────────────────────────

interface SearchActiveFiltersProps {
  filters: Record<string, string>;
  onRemove: (key: string) => void;
  onClearAll: () => void;
  className?: string;
}

// ─── Label Map ──────────────────────────────────────────────────────────────

const FILTER_LABELS: Record<string, string> = {
  category: 'Category',
  min_price: 'Min Price',
  max_price: 'Max Price',
  sort: 'Sort',
  featured: 'Featured',
  on_sale: 'On Sale',
};

// ─── Component ──────────────────────────────────────────────────────────────

export function SearchActiveFilters({
  filters,
  onRemove,
  onClearAll,
  className,
}: SearchActiveFiltersProps) {
  const entries = Object.entries(filters).filter(([, v]) => v !== '');

  if (entries.length === 0) return null;

  return (
    <div className={cn('flex flex-wrap items-center gap-2', className)}>
      {entries.map(([key, value]) => (
        <span
          key={key}
          className={cn(
            'inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium',
            'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300',
          )}
        >
          <span className="text-gray-500 dark:text-gray-400">
            {FILTER_LABELS[key] ?? key}:
          </span>
          <span>{value}</span>
          <button
            type="button"
            onClick={() => onRemove(key)}
            className="ml-0.5 rounded-full p-0.5 hover:bg-gray-200 dark:hover:bg-gray-700"
            aria-label={`Remove ${FILTER_LABELS[key] ?? key} filter`}
          >
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="3" y1="3" x2="9" y2="9" />
              <line x1="9" y1="3" x2="3" y2="9" />
            </svg>
          </button>
        </span>
      ))}

      <button
        type="button"
        onClick={onClearAll}
        className="text-xs font-medium text-gray-500 underline hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
      >
        Clear all
      </button>
    </div>
  );
}
