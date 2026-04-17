'use client';

import { cn } from '@/lib/utils';

interface LoadMoreButtonProps {
  onLoadMore: () => void;
  hasMore: boolean;
  isLoading?: boolean;
  currentCount?: number;
  totalCount?: number;
  className?: string;
}

export function LoadMoreButton({
  onLoadMore,
  hasMore,
  isLoading,
  currentCount,
  totalCount,
  className,
}: LoadMoreButtonProps) {
  return (
    <div className={cn('flex flex-col items-center gap-3 pt-8', className)}>
      {/* Progress info */}
      {currentCount != null && totalCount != null && totalCount > 0 && (
        <p className="text-sm text-gray-500">
          Showing {currentCount} of {totalCount.toLocaleString()} products
        </p>
      )}

      {hasMore ? (
        <button
          type="button"
          onClick={onLoadMore}
          disabled={!!isLoading}
          aria-busy={!!isLoading}
          className={cn(
            'inline-flex items-center gap-2 rounded-lg border-2 px-6 py-3 text-sm font-medium transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500',
            isLoading
              ? 'cursor-wait border-gray-200 bg-gray-100 text-gray-500'
              : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
          )}
        >
          {isLoading && (
            <svg
              className="h-4 w-4 animate-spin text-gray-400"
              viewBox="0 0 24 24"
              fill="none"
              aria-hidden="true"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
              />
            </svg>
          )}
          {isLoading ? 'Loading…' : 'Load More Products'}
        </button>
      ) : (
        totalCount != null &&
        totalCount > 0 && <p className="text-sm text-gray-400">All products loaded</p>
      )}
    </div>
  );
}
