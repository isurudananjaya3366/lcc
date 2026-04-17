'use client';

import { cn } from '@/lib/utils';

interface ResultsHeaderProps {
  query: string;
  totalCount: number;
  isLoading: boolean;
  className?: string;
}

export function ResultsHeader({
  query,
  totalCount,
  isLoading,
  className,
}: ResultsHeaderProps) {
  if (!query) return null;

  return (
    <div className={cn('flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400', className)}>
      {isLoading ? (
        <div className="h-4 w-48 animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
      ) : (
        <p>
          <span className="font-medium text-gray-900 dark:text-gray-100">{totalCount}</span>
          {' '}
          {totalCount === 1 ? 'product' : 'products'} found
          {query && (
            <>
              {' '}for &ldquo;
              <span className="font-medium text-gray-900 dark:text-gray-100">{query}</span>
              &rdquo;
            </>
          )}
        </p>
      )}
    </div>
  );
}
