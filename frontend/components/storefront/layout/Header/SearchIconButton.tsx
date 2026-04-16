'use client';

import React, { type FC } from 'react';
import { cn } from '@/lib/utils';

export interface SearchIconButtonProps {
  onClick: () => void;
  className?: string;
  label?: string;
}

const SearchIconButton: FC<SearchIconButtonProps> = ({ onClick, className, label = 'Search' }) => {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        'block md:hidden p-2 text-gray-600 dark:text-gray-400 hover:text-green-700 dark:hover:text-green-400 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors',
        className
      )}
      aria-label={label}
      title={label}
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="h-5 w-5"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
        />
      </svg>
    </button>
  );
};

export default SearchIconButton;
