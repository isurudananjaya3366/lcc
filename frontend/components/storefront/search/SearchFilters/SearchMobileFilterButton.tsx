'use client';

import { cn } from '@/lib/utils';

// ─── Types ──────────────────────────────────────────────────────────────────

interface SearchMobileFilterButtonProps {
  onClick: () => void;
  activeFilterCount: number;
  className?: string;
}

// ─── Component ──────────────────────────────────────────────────────────────

export function SearchMobileFilterButton({
  onClick,
  activeFilterCount,
  className,
}: SearchMobileFilterButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        'inline-flex items-center gap-2 rounded-md border border-gray-300 px-3 py-1.5 text-sm font-medium lg:hidden',
        'bg-white text-gray-700 hover:bg-gray-50',
        'dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700',
        className,
      )}
    >
      <svg
        className="h-4 w-4"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" />
      </svg>
      <span>Filters</span>
      {activeFilterCount > 0 && (
        <span
          className={cn(
            'inline-flex h-5 min-w-[1.25rem] items-center justify-center rounded-full px-1 text-xs font-semibold',
            'bg-primary text-white',
          )}
        >
          {activeFilterCount}
        </span>
      )}
    </button>
  );
}
