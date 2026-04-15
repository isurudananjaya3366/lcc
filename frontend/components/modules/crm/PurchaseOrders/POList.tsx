'use client';

import { useState, useMemo, useCallback } from 'react';
import { usePurchaseOrders } from '@/hooks/crm/usePurchaseOrders';
import { POHeader } from './POHeader';
import { POSummaryCards } from './POSummaryCards';
import { POFilters } from './POFilters';
import { POTable } from './POTable';

export function POList() {
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('');
  const [page, setPage] = useState(1);
  const [sortBy, setSortBy] = useState('orderDate');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');

  const { data, isLoading } = usePurchaseOrders({
    status: status || undefined,
    search: search || undefined,
  });

  const orders = data?.data ?? [];
  const totalPages = data?.pagination?.totalPages ?? 1;

  const handleSort = useCallback(
    (key: string) => {
      if (sortBy === key) {
        setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
      } else {
        setSortBy(key);
        setSortDir('asc');
      }
    },
    [sortBy]
  );

  const handleClear = useCallback(() => {
    setSearch('');
    setStatus('');
    setPage(1);
  }, []);

  return (
    <div className="space-y-6">
      <POHeader />
      <POSummaryCards orders={orders} />
      <POFilters
        search={search}
        status={status}
        onSearchChange={(v) => {
          setSearch(v);
          setPage(1);
        }}
        onStatusChange={(v) => {
          setStatus(v);
          setPage(1);
        }}
        onClear={handleClear}
      />
      <POTable
        orders={orders}
        isLoading={isLoading}
        page={page}
        totalPages={totalPages}
        onPageChange={setPage}
        sortBy={sortBy}
        sortDir={sortDir}
        onSort={handleSort}
      />
    </div>
  );
}
