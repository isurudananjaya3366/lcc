'use client';

import React, { type FC } from 'react';
import { cn } from '@/lib/utils';
import HighlightMatch from './HighlightMatch';

export interface CategorySuggestionItemProps {
  category: { name: string; slug: string };
  query: string;
  isActive: boolean;
  onSelect: (slug: string) => void;
}

const CategorySuggestionItem: FC<CategorySuggestionItemProps> = ({
  category,
  query,
  isActive,
  onSelect,
}) => (
  <button
    type="button"
    role="option"
    aria-selected={isActive}
    className={cn(
      'flex w-full items-center gap-3 px-3 py-2 text-left transition-colors',
      'hover:bg-gray-100 dark:hover:bg-gray-700',
      isActive && 'bg-gray-100 dark:bg-gray-700'
    )}
    onClick={() => onSelect(category.slug)}
    onMouseDown={(e) => e.preventDefault()}
  >
    {/* Folder icon */}
    <div className="flex h-8 w-8 items-center justify-center rounded-md bg-green-50 dark:bg-green-900/30 flex-shrink-0">
      <svg className="h-4 w-4 text-green-600 dark:text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 12.75V12A2.25 2.25 0 014.5 9.75h15A2.25 2.25 0 0121.75 12v.75m-8.69-6.44l-2.12-2.12a1.5 1.5 0 00-1.061-.44H4.5A2.25 2.25 0 002.25 6v12a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18V9a2.25 2.25 0 00-2.25-2.25h-5.379a1.5 1.5 0 01-1.06-.44z" />
      </svg>
    </div>
    <span className="text-sm text-gray-900 dark:text-gray-100">
      <HighlightMatch text={category.name} query={query} />
    </span>
  </button>
);

export default CategorySuggestionItem;
