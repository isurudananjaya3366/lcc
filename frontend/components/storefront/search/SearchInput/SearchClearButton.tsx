'use client';

import React, { type FC } from 'react';
import { X } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface SearchClearButtonProps {
  onClick: () => void;
  visible: boolean;
  size?: 'sm' | 'md' | 'lg';
}

const sizeClasses: Record<NonNullable<SearchClearButtonProps['size']>, string> = {
  sm: 'h-3.5 w-3.5',
  md: 'h-4 w-4',
  lg: 'h-5 w-5',
};

export const SearchClearButton: FC<SearchClearButtonProps> = ({
  onClick,
  visible,
  size = 'md',
}) => {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        'absolute right-3 rounded-full p-0.5 text-gray-400 transition-all duration-150',
        'hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-700 dark:hover:text-gray-300',
        'focus:outline-none focus:ring-2 focus:ring-green-500',
        visible ? 'scale-100 opacity-100' : 'pointer-events-none scale-75 opacity-0'
      )}
      aria-label="Clear search"
      tabIndex={visible ? 0 : -1}
    >
      <X className={sizeClasses[size]} />
    </button>
  );
};

export default SearchClearButton;
