'use client';

import { cn } from '@/lib/utils';

interface RecentSearchItemProps {
  query: string;
  onSelect: (query: string) => void;
  onRemove: (query: string) => void;
}

export function RecentSearchItem({ query, onSelect, onRemove }: RecentSearchItemProps) {
  return (
    <div
      className={cn(
        'group flex items-center gap-3 px-4 py-2 cursor-pointer',
        'hover:bg-gray-100 dark:hover:bg-gray-800',
        'transition-colors'
      )}
      onClick={() => onSelect(query)}
      role="option"
      aria-label={`Recent search: ${query}`}
    >
      <svg
        className={cn('h-4 w-4 shrink-0 text-gray-400 dark:text-gray-500')}
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth={2}
      >
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6l4 2m6-2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>

      <span className={cn(
        'flex-1 truncate text-sm text-gray-700',
        'dark:text-gray-300'
      )}>
        {query}
      </span>

      <button
        type="button"
        onClick={(e) => {
          e.stopPropagation();
          onRemove(query);
        }}
        aria-label={`Remove "${query}" from recent searches`}
        className={cn(
          'opacity-0 group-hover:opacity-100',
          'p-1 rounded-full text-gray-400 hover:text-gray-600',
          'dark:text-gray-500 dark:hover:text-gray-300',
          'transition-opacity'
        )}
      >
        <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
}
