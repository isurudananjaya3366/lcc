'use client';

import { cn } from '@/lib/utils';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  pageSize?: number;
  totalItems?: number;
  isLoading?: boolean;
  className?: string;
}

function calculatePageRange(
  currentPage: number,
  totalPages: number,
  maxDisplayed: number = 7
): (number | null)[] {
  if (totalPages <= maxDisplayed) {
    return Array.from({ length: totalPages }, (_, i) => i + 1);
  }

  const pages: (number | null)[] = [];
  const halfMax = Math.floor((maxDisplayed - 2) / 2);

  pages.push(1);

  let start = Math.max(2, currentPage - halfMax);
  let end = Math.min(totalPages - 1, currentPage + halfMax);

  if (currentPage <= halfMax + 2) {
    end = maxDisplayed - 1;
  } else if (currentPage >= totalPages - halfMax - 1) {
    start = totalPages - maxDisplayed + 2;
  }

  if (start > 2) {
    pages.push(null);
  }

  for (let i = start; i <= end; i++) {
    pages.push(i);
  }

  if (end < totalPages - 1) {
    pages.push(null);
  }

  if (totalPages > 1) {
    pages.push(totalPages);
  }

  return pages;
}

export function Pagination({
  currentPage,
  totalPages,
  onPageChange,
  pageSize = 24,
  totalItems,
  isLoading,
  className,
}: PaginationProps) {
  if (totalPages <= 1) return null;

  const pages = calculatePageRange(currentPage, totalPages);

  const isPrevDisabled = currentPage === 1 || !!isLoading;
  const isNextDisabled = currentPage === totalPages || !!isLoading;

  const start = (currentPage - 1) * pageSize + 1;
  const end = totalItems ? Math.min(currentPage * pageSize, totalItems) : currentPage * pageSize;

  return (
    <nav aria-label="Pagination" className={cn('flex flex-col items-center gap-4 pt-8', className)}>
      {/* Results info */}
      {totalItems != null && totalItems > 0 && (
        <p className="text-sm text-gray-600">
          Showing {start}–{end} of {totalItems.toLocaleString()} products
        </p>
      )}

      {/* Controls */}
      <div className="flex items-center gap-1.5">
        {/* Previous button */}
        <button
          type="button"
          onClick={() => onPageChange(currentPage - 1)}
          disabled={isPrevDisabled}
          className={cn(
            'inline-flex items-center gap-1 rounded-lg border px-3 py-2 text-sm font-medium transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500',
            isPrevDisabled
              ? 'cursor-not-allowed border-gray-200 bg-gray-50 text-gray-400'
              : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
          )}
          aria-label="Go to previous page"
        >
          <svg className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path
              fillRule="evenodd"
              d="M11.78 5.22a.75.75 0 0 1 0 1.06L8.06 10l3.72 3.72a.75.75 0 1 1-1.06 1.06l-4.25-4.25a.75.75 0 0 1 0-1.06l4.25-4.25a.75.75 0 0 1 1.06 0Z"
              clipRule="evenodd"
            />
          </svg>
          <span className="hidden sm:inline">Previous</span>
        </button>

        {/* Page numbers */}
        <div className="flex items-center gap-1">
          {pages.map((page, idx) => {
            if (page === null) {
              return (
                <span
                  key={`ellipsis-${idx}`}
                  className="inline-flex h-9 w-9 items-center justify-center text-sm text-gray-400"
                  aria-hidden="true"
                >
                  …
                </span>
              );
            }

            const isActive = page === currentPage;
            return (
              <button
                key={page}
                type="button"
                onClick={() => onPageChange(page)}
                disabled={isActive || !!isLoading}
                aria-current={isActive ? 'page' : undefined}
                aria-label={`Page ${page}`}
                className={cn(
                  'inline-flex h-9 w-9 items-center justify-center rounded-lg text-sm font-medium transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500',
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'border border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
                )}
              >
                {page}
              </button>
            );
          })}
        </div>

        {/* Next button */}
        <button
          type="button"
          onClick={() => onPageChange(currentPage + 1)}
          disabled={isNextDisabled}
          className={cn(
            'inline-flex items-center gap-1 rounded-lg border px-3 py-2 text-sm font-medium transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500',
            isNextDisabled
              ? 'cursor-not-allowed border-gray-200 bg-gray-50 text-gray-400'
              : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
          )}
          aria-label="Go to next page"
        >
          <span className="hidden sm:inline">Next</span>
          <svg className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path
              fillRule="evenodd"
              d="M8.22 5.22a.75.75 0 0 1 1.06 0l4.25 4.25a.75.75 0 0 1 0 1.06l-4.25 4.25a.75.75 0 0 1-1.06-1.06L11.94 10 8.22 6.28a.75.75 0 0 1 0-1.06Z"
              clipRule="evenodd"
            />
          </svg>
        </button>
      </div>
    </nav>
  );
}
