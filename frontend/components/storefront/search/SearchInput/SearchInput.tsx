'use client';

import React, { forwardRef } from 'react';
import { Search } from 'lucide-react';
import { cn } from '@/lib/utils';
import { SearchClearButton } from './SearchClearButton';

export interface SearchInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit?: () => void;
  onClear?: () => void;
  onFocus?: () => void;
  onBlur?: () => void;
  placeholder?: string;
  className?: string;
  autoFocus?: boolean;
}

const SearchInput = forwardRef<HTMLInputElement, SearchInputProps>(
  (
    {
      value,
      onChange,
      onSubmit,
      onClear,
      onFocus,
      onBlur,
      placeholder = 'Search products...',
      className,
      autoFocus = false,
    },
    ref,
  ) => {
    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        onSubmit?.();
      }
    };

    const handleClear = () => {
      onChange('');
      onClear?.();
      if (ref && typeof ref !== 'function' && ref.current) {
        ref.current.focus();
      }
    };

    return (
      <div className={cn('relative flex items-center', className)}>
        <Search
          className="pointer-events-none absolute left-3 h-4 w-4 text-gray-400 dark:text-gray-500"
          aria-hidden="true"
        />
        <input
          ref={ref}
          type="search"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={onFocus}
          onBlur={onBlur}
          placeholder={placeholder}
          autoFocus={autoFocus}
          className={cn(
            'w-full rounded-lg border border-gray-300 bg-white py-2.5 pl-10 pr-10 text-sm',
            'placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent',
            'dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100 dark:placeholder:text-gray-500',
            'transition-shadow duration-150',
          )}
          autoComplete="off"
          aria-label={placeholder}
        />
        <SearchClearButton
          onClick={handleClear}
          visible={value.length > 0}
        />
      </div>
    );
  },
);

SearchInput.displayName = 'SearchInput';

export default SearchInput;
