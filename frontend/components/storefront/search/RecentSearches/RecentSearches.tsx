'use client';

import { cn } from '@/lib/utils';
import { useRecentSearches } from '@/hooks/storefront/useRecentSearches';
import { RecentSearchHeader } from './RecentSearchHeader';
import { RecentSearchItem } from './RecentSearchItem';
import { PopularSearches } from './PopularSearches';

interface RecentSearchesProps {
  onSelect: (query: string) => void;
  isVisible: boolean;
}

export function RecentSearches({ onSelect, isVisible }: RecentSearchesProps) {
  const { recentSearches, removeSearch, clearAll } = useRecentSearches();

  if (!isVisible) return null;

  const hasRecent = recentSearches.length > 0;

  return (
    <div
      className={cn(
        'w-full rounded-lg border bg-white shadow-lg',
        'border-gray-200 dark:border-gray-700',
        'dark:bg-gray-900'
      )}
      role="listbox"
      aria-label={hasRecent ? 'Recent searches' : 'Popular searches'}
    >
      {hasRecent ? (
        <>
          <RecentSearchHeader onClearAll={clearAll} />
          <div className="max-h-80 overflow-y-auto">
            {recentSearches.map((query) => (
              <RecentSearchItem
                key={query}
                query={query}
                onSelect={onSelect}
                onRemove={removeSearch}
              />
            ))}
          </div>
        </>
      ) : (
        <PopularSearches onSelect={onSelect} />
      )}
    </div>
  );
}
