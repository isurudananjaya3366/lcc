'use client';

import { cn } from '@/lib/utils';

// ─── Types ──────────────────────────────────────────────────────────────────

interface SortOption {
  label: string;
  value: string;
}

interface SearchSortProps {
  currentSort: string;
  onSortChange: (value: string) => void;
  className?: string;
}

// ─── Sort Options ───────────────────────────────────────────────────────────

const SORT_OPTIONS: SortOption[] = [
  { label: 'Relevance', value: '' },
  { label: 'Price: Low to High', value: 'selling_price' },
  { label: 'Price: High to Low', value: '-selling_price' },
  { label: 'Newest', value: '-created_on' },
  { label: 'Name: A–Z', value: 'name' },
  { label: 'Name: Z–A', value: '-name' },
];

// ─── Component ──────────────────────────────────────────────────────────────

export function SearchSort({ currentSort, onSortChange, className }: SearchSortProps) {
  return (
    <div className={cn('flex items-center gap-2', className)}>
      <label htmlFor="search-sort" className="shrink-0 text-sm text-gray-600 dark:text-gray-400">
        <svg
          className="mr-1 inline-block h-4 w-4"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <line x1="4" y1="6" x2="20" y2="6" />
          <line x1="4" y1="12" x2="14" y2="12" />
          <line x1="4" y1="18" x2="8" y2="18" />
        </svg>
        Sort by
      </label>
      <select
        id="search-sort"
        value={currentSort}
        onChange={(e) => onSortChange(e.target.value)}
        className={cn(
          'rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm',
          'text-gray-900 focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary',
          'dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100',
        )}
      >
        {SORT_OPTIONS.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}
