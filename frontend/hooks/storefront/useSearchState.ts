import { useState, useCallback } from 'react';
import { useDebounce } from '@/hooks/useDebounce';

export interface UseSearchStateOptions {
  initialQuery?: string;
  debounceMs?: number;
}

export interface UseSearchStateReturn {
  query: string;
  setQuery: (query: string) => void;
  debouncedQuery: string;
  clearQuery: () => void;
}

export function useSearchState({
  initialQuery = '',
  debounceMs = 300,
}: UseSearchStateOptions = {}): UseSearchStateReturn {
  const [query, setQuery] = useState(initialQuery);
  const debouncedQuery = useDebounce(query, debounceMs);

  const clearQuery = useCallback(() => {
    setQuery('');
  }, []);

  return {
    query,
    setQuery,
    debouncedQuery,
    clearQuery,
  };
}
