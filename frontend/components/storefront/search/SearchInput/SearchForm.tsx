'use client';

import React, { useRef, useState, useCallback, type FC } from 'react';
import { useRouter } from 'next/navigation';
import dynamic from 'next/dynamic';
import { cn } from '@/lib/utils';
import { useRecentSearches } from '@/hooks/storefront/useRecentSearches';
import SearchInput from './SearchInput';

// Lazy load the dropdown to avoid SSR issues
const Autocomplete = dynamic(() => import('../Autocomplete/Autocomplete'), { ssr: false });
const RecentSearches = dynamic(
  () => import('../RecentSearches/RecentSearches').then((m) => ({ default: m.RecentSearches })),
  { ssr: false },
);

export interface SearchFormProps {
  initialQuery?: string;
  onSubmit?: (query: string) => void;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

const sizeClasses: Record<NonNullable<SearchFormProps['size']>, string> = {
  sm: 'max-w-sm',
  md: 'max-w-xl',
  lg: 'max-w-3xl',
};

const SearchForm: FC<SearchFormProps> = ({
  initialQuery = '',
  onSubmit,
  className,
  size = 'md',
}) => {
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement>(null);
  const [query, setQuery] = useState(initialQuery);
  const [isFocused, setIsFocused] = useState(false);
  const { addSearch } = useRecentSearches();

  const handleSubmit = useCallback(() => {
    const trimmed = query.trim();
    if (!trimmed) return;
    addSearch(trimmed);
    onSubmit?.(trimmed);
    setIsFocused(false);
    router.push(`/search?q=${encodeURIComponent(trimmed)}`);
  }, [query, addSearch, onSubmit, router]);

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSubmit();
  };

  const handleSelect = useCallback(
    (value: string) => {
      setQuery(value);
      addSearch(value);
      setIsFocused(false);
      router.push(`/search?q=${encodeURIComponent(value)}`);
    },
    [addSearch, router],
  );

  const handleClose = useCallback(() => setIsFocused(false), []);

  // Show autocomplete when focused + has query (min 2 chars)
  const showAutocomplete = isFocused && query.trim().length >= 2;
  // Show recent searches when focused + empty query
  const showRecent = isFocused && query.trim().length < 2;

  return (
    <div className={cn('relative w-full', sizeClasses[size], className)}>
      <form onSubmit={handleFormSubmit} role="search">
        <SearchInput
          ref={inputRef}
          value={query}
          onChange={setQuery}
          onSubmit={handleSubmit}
          onClear={() => { setQuery(''); inputRef.current?.focus(); }}
          onFocus={() => setIsFocused(true)}
          onBlur={() => {
            // Delay so clicks on dropdown items register first
            setTimeout(() => setIsFocused(false), 150);
          }}
        />
      </form>

      {/* Autocomplete dropdown */}
      {showAutocomplete && (
        <div className="absolute left-0 right-0 top-full z-50 mt-1">
          <Autocomplete
            query={query}
            isOpen={showAutocomplete}
            onClose={handleClose}
            onSelect={handleSelect}
            inputRef={inputRef}
          />
        </div>
      )}

      {/* Recent searches dropdown */}
      {showRecent && (
        <div className="absolute left-0 right-0 top-full z-50 mt-1">
          <RecentSearches
            isVisible={showRecent}
            onSelect={handleSelect}
          />
        </div>
      )}
    </div>
  );
};

export default SearchForm;
