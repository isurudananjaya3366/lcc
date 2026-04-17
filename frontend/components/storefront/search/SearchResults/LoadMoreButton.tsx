'use client';

import { cn } from '@/lib/utils';

interface LoadMoreButtonProps {
  onLoadMore: () => void;
  isLoading: boolean;
  hasMore: boolean;
  currentCount: number;
  totalCount: number;
  className?: string;
}

export function LoadMoreButton({
  onLoadMore,
  isLoading,
  hasMore,
  currentCount,
  totalCount,
  className,
}: LoadMoreButtonProps) {
  if (!hasMore && !isLoading && currentCount >= totalCount && totalCount > 0) {
    return (
      <p className={cn('py-4 text-center text-sm text-muted-foreground', className)}>
        All {totalCount} results loaded
      </p>
    );
  }

  if (!hasMore) return null;

  return (
    <div className={cn('flex flex-col items-center gap-2 py-4', className)}>
      <p className="text-xs text-muted-foreground">
        Showing {currentCount} of {totalCount} results
      </p>
      <button
        type="button"
        onClick={onLoadMore}
        disabled={isLoading}
        className={cn(
          'rounded-lg border border-gray-300 bg-white px-6 py-2.5 text-sm font-medium',
          'text-gray-700 transition-colors hover:bg-gray-50 focus-visible:outline-none',
          'focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2',
          'disabled:cursor-not-allowed disabled:opacity-60',
          'dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700',
        )}
        aria-label={isLoading ? 'Loading more results...' : 'Load more results'}
      >
        {isLoading ? (
          <span className="flex items-center gap-2">
            <svg
              className="h-4 w-4 animate-spin"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
              />
            </svg>
            Loading...
          </span>
        ) : (
          'Load More Results'
        )}
      </button>
    </div>
  );
}
