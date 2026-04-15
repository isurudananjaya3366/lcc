'use client';

import { useState, useCallback } from 'react';
import { CustomersHeader } from './CustomersHeader';
import { CustomerSummaryCards } from './CustomerSummaryCards';
import { CustomerFilters } from './CustomerFilters';
import { CustomersTable } from './CustomersTable';
import { useCustomers } from '@/hooks/crm/useCustomers';
import type { CustomerSearchParams } from '@/types/customer';

export function CustomersList() {
  const [filters, setFilters] = useState({
    search: '',
    status: '',
    type: '',
    creditStatus: '',
  });
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [sortBy, setSortBy] = useState('display_name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

  const queryParams: CustomerSearchParams = {
    query: filters.search || undefined,
    status: filters.status ? (filters.status as CustomerSearchParams['status']) : undefined,
    customerType: filters.type ? (filters.type as CustomerSearchParams['customerType']) : undefined,
    creditStatus: filters.creditStatus
      ? (filters.creditStatus as CustomerSearchParams['creditStatus'])
      : undefined,
    sort: sortOrder === 'desc' ? `-${sortBy}` : sortBy,
    page,
    pageSize,
  };

  const { data, isLoading, isError, error } = useCustomers(queryParams);

  const handleSearchChange = useCallback((search: string) => {
    setFilters((prev) => ({ ...prev, search }));
    setPage(1);
  }, []);

  const handleStatusChange = useCallback((status: string) => {
    setFilters((prev) => ({ ...prev, status }));
    setPage(1);
  }, []);

  const handleTypeChange = useCallback((type: string) => {
    setFilters((prev) => ({ ...prev, type }));
    setPage(1);
  }, []);

  const handleCreditChange = useCallback((creditStatus: string) => {
    setFilters((prev) => ({ ...prev, creditStatus }));
    setPage(1);
  }, []);

  const handleSortChange = useCallback((column: string) => {
    setSortBy((prev) => {
      if (prev === column) {
        setSortOrder((o) => (o === 'asc' ? 'desc' : 'asc'));
        return prev;
      }
      setSortOrder('asc');
      return column;
    });
  }, []);

  return (
    <div className="space-y-6">
      <CustomersHeader />
      <CustomerSummaryCards />
      <CustomerFilters
        currentFilters={filters}
        onSearchChange={handleSearchChange}
        onStatusChange={handleStatusChange}
        onTypeChange={handleTypeChange}
        onCreditChange={handleCreditChange}
      />
      <CustomersTable
        data={data?.data ?? []}
        isLoading={isLoading}
        isError={isError}
        error={error}
        page={page}
        pageSize={pageSize}
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
