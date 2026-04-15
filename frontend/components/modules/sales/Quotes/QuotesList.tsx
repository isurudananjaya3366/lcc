'use client';

import { useState } from 'react';
import { useQuotes } from '@/hooks/queries/useQuotes';
import { QuotesHeader } from './QuotesHeader';
import { QuoteFilters, type QuoteFilterValues } from './QuoteFilters';
import { QuotesTable } from './QuotesTable';
import type { QuoteSearchParams } from '@/types/quotes';

export function QuotesList() {
  const [filters, setFilters] = useState<QuoteFilterValues>({
    search: '',
    status: 'all',
    dateRange: 'all',
  });

  const queryParams: QuoteSearchParams = {
    search: filters.search || undefined,
    status: filters.status !== 'all' ? (filters.status as QuoteSearchParams['status']) : undefined,
  };

  const { data, isLoading } = useQuotes(queryParams);
  const quotes = Array.isArray(data) ? data : (data?.data ?? []);

  return (
    <div className="space-y-6">
      <QuotesHeader totalCount={quotes.length} />
      <QuoteFilters filters={filters} onFiltersChange={setFilters} />
      <QuotesTable quotes={quotes} isLoading={isLoading} />
    </div>
  );
}
