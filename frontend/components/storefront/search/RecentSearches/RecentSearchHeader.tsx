'use client';

import { cn } from '@/lib/utils';

interface RecentSearchHeaderProps {
  onClearAll: () => void;
}

export function RecentSearchHeader({ onClearAll }: RecentSearchHeaderProps) {
  return (
    <div className={cn('flex items-center justify-between px-4 py-2')}>
      <h3 className={cn(
        'text-sm font-semibold text-gray-700',
        'dark:text-gray-300'
      )}>
        Recent Searches
      </h3>
      <button
        type="button"
        onClick={onClearAll}
        aria-label="Clear all recent searches"
        className={cn(
          'text-xs font-medium text-blue-600 hover:text-blue-800',
          'dark:text-blue-400 dark:hover:text-blue-300',
          'transition-colors'
        )}
      >
        Clear All
      </button>
    </div>
  );
}
