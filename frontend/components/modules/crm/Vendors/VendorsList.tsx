'use client';

import { useState, useCallback } from 'react';
import { useVendors } from '@/hooks/crm/useVendors';
import { VendorsHeader } from './VendorsHeader';
import { VendorSummaryCards } from './VendorSummaryCards';
import { VendorFilters } from './VendorFilters';
import { VendorsTable } from './VendorsTable';

export function VendorsList() {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [sortBy, setSortBy] = useState<string | undefined>(undefined);
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [filters, setFilters] = useState<{
    search?: string;
    status?: string;
    category?: string;
  }>({});

  const queryParams = {
    query: filters.search,
    status: filters.status as import('@/types/vendor').VendorStatus | undefined,
    category: filters.category as import('@/types/vendor').VendorCategory | undefined,
    sort: sortBy ? `${sortOrder === 'desc' ? '-' : ''}${sortBy}` : undefined,
    page,
    pageSize,
  };

  const { data, isLoading } = useVendors(queryParams);

  const handleFiltersChange = useCallback(
    (newFilters: { search?: string; status?: string; category?: string }) => {
      setFilters(newFilters);
      setPage(1);
    },
    []
  );

  const handleSortChange = useCallback(
    (column: string) => {
      if (sortBy === column) {
        setSortOrder((o) => (o === 'asc' ? 'desc' : 'asc'));
      } else {
        setSortBy(column);
        setSortOrder('asc');
      }
    },
    [sortBy]
  );

  return (
    <div className="space-y-6">
      <VendorsHeader />
      <VendorSummaryCards />
      <VendorFilters onFiltersChange={handleFiltersChange} />
      <VendorsTable
        vendors={data?.data ?? []}
        isLoading={isLoading}
        page={page}
        pageSize={pageSize}
        totalPages={data?.pagination?.totalPages ?? 1}
        totalCount={data?.pagination?.totalCount ?? 0}
        sortBy={sortBy}
        sortOrder={sortOrder}
        onPageChange={setPage}
        onPageSizeChange={(size) => {
          setPageSize(size);
          setPage(1);
        }}
        onSortChange={handleSortChange}
      />
    </div>
  );
}
