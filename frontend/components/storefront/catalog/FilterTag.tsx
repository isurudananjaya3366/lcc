'use client';

import { cn } from '@/lib/utils';

export interface ActiveFilter {
  id: string;
  type: string;
  label: string;
  value: string;
}

interface FilterTagProps {
  filter: ActiveFilter;
  onRemove: (filterId: string) => void;
  className?: string;
}

export function FilterTag({ filter, onRemove, className }: FilterTagProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-full bg-gray-100 border border-gray-300 px-3 py-1 text-sm text-gray-700',
        className
      )}
    >
      <span className="truncate max-w-[160px]">
        {filter.label}: {filter.value}
      </span>
      <button
        type="button"
        onClick={() => onRemove(filter.id)}
        className="ml-0.5 inline-flex flex-shrink-0 items-center justify-center rounded-full p-0.5 text-gray-400 hover:text-gray-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 transition-colors"
        aria-label={`Remove ${filter.label}: ${filter.value} filter`}
      >
        <svg className="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
          <path d="M6.28 5.22a.75.75 0 0 0-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 1 0 1.06 1.06L10 11.06l3.72 3.72a.75.75 0 1 0 1.06-1.06L11.06 10l3.72-3.72a.75.75 0 0 0-1.06-1.06L10 8.94 6.28 5.22Z" />
        </svg>
      </button>
    </span>
  );
}
