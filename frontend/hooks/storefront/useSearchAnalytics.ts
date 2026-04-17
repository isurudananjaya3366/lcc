'use client';

import { useCallback, useRef } from 'react';

interface SearchEvent {
  type: 'search' | 'suggestion_click' | 'filter_apply';
  query?: string;
  resultCount?: number;
  suggestion?: string;
  filterName?: string;
  filterValue?: string;
  timestamp: number;
}

interface UseSearchAnalyticsReturn {
  trackSearch: (query: string, resultCount: number) => void;
  trackSuggestionClick: (query: string, suggestion: string) => void;
  trackFilterApply: (filterName: string, value: string) => void;
}

export function useSearchAnalytics(): UseSearchAnalyticsReturn {
  const eventsRef = useRef<SearchEvent[]>([]);

  const logEvent = useCallback((event: SearchEvent) => {
    eventsRef.current.push(event);

    if (process.env.NODE_ENV === 'development') {
      // eslint-disable-next-line no-console
      console.debug('[SearchAnalytics]', event);
    }

    // TODO: Send to analytics API when available
    // POST /api/v1/analytics/search with event payload
  }, []);

  const trackSearch = useCallback(
    (query: string, resultCount: number) => {
      logEvent({
        type: 'search',
        query,
        resultCount,
        timestamp: Date.now(),
      });
    },
    [logEvent],
  );

  const trackSuggestionClick = useCallback(
    (query: string, suggestion: string) => {
      logEvent({
        type: 'suggestion_click',
        query,
        suggestion,
        timestamp: Date.now(),
      });
    },
    [logEvent],
  );

  const trackFilterApply = useCallback(
    (filterName: string, value: string) => {
      logEvent({
        type: 'filter_apply',
        filterName,
        filterValue: value,
        timestamp: Date.now(),
      });
    },
    [logEvent],
  );

  return { trackSearch, trackSuggestionClick, trackFilterApply };
}
