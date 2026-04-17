'use client';

import { cn } from '@/lib/utils';

const POPULAR_TERMS = [
  'smartphones',
  'laptop',
  'headphones',
  'watches',
  'camera',
  'bluetooth speaker',
  'tablet',
  'gaming',
];

interface PopularSearchesProps {
  onSelect: (query: string) => void;
}

export function PopularSearches({ onSelect }: PopularSearchesProps) {
  return (
    <div>
      <div className={cn('flex items-center gap-2 px-4 py-2')}>
        <svg
          className={cn('h-4 w-4 text-orange-500 dark:text-orange-400')}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
        </svg>
        <h3 className={cn(
          'text-sm font-semibold text-gray-700',
          'dark:text-gray-300'
        )}>
          Popular Searches
        </h3>
      </div>

      <ul role="listbox" aria-label="Popular searches">
        {POPULAR_TERMS.map((term) => (
          <li
            key={term}
            role="option"
            aria-label={`Popular search: ${term}`}
            onClick={() => onSelect(term)}
            className={cn(
              'flex items-center gap-3 px-4 py-2 cursor-pointer',
              'hover:bg-gray-100 dark:hover:bg-gray-800',
              'transition-colors'
            )}
          >
            <svg
              className={cn('h-4 w-4 shrink-0 text-gray-400 dark:text-gray-500')}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <span className={cn(
              'text-sm text-gray-700 dark:text-gray-300'
            )}>
              {term}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
