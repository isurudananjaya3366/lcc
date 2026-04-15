'use client';

import { useState, useCallback } from 'react';
import { useSearchParams, useRouter, usePathname } from 'next/navigation';
import { type SortingState, type PaginationState } from '@tanstack/react-table';
import { useDebounce } from '@/hooks/useDebounce';
import { useInventory } from '@/hooks/queries/useInventory';

import { StockOverviewHeader } from './StockOverviewHeader';
import { StockSummaryCards } from './StockSummaryCards';
import { StockFilters, type StockFilterState } from './StockFilters';
import { StockTable } from './StockTable';

const defaultFilters: StockFilterState = {
  search: '',
  warehouse: 'all',
  stockLevel: 'all',
};

export function StockOverview() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const [filters, setFilters] = useState<StockFilterState>({
    search: searchParams.get('search') ?? '',
    warehouse: searchParams.get('warehouse') ?? 'all',
    stockLevel: searchParams.get('stockLevel') ?? 'all',
  });

  const debouncedSearch = useDebounce(filters.search, 300);

  const [sorting, setSorting] = useState<SortingState>(() => {
    const sort = searchParams.get('sort');
    const order = searchParams.get('order');
    if (sort) return [{ id: sort, desc: order === 'desc' }];
    return [];
  });

  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: Number(searchParams.get('page') ?? 1) - 1,
    pageSize: Number(searchParams.get('pageSize') ?? 10),
  });

  const { data, isLoading } = useInventory({
    warehouse: filters.warehouse !== 'all' ? filters.warehouse : undefined,
    status: filters.stockLevel !== 'all' ? filters.stockLevel : undefined,
    product: debouncedSearch || undefined,
  });

  const updateUrl = useCallback(
    (newFilters: StockFilterState, newSorting: SortingState, newPagination: PaginationState) => {
      const params = new URLSearchParams();
      if (newFilters.search) params.set('search', newFilters.search);
      if (newFilters.warehouse !== 'all') params.set('warehouse', newFilters.warehouse);
      if (newFilters.stockLevel !== 'all') params.set('stockLevel', newFilters.stockLevel);
      const firstSort = newSorting[0];
      if (firstSort) {
        params.set('sort', firstSort.id);
        params.set('order', firstSort.desc ? 'desc' : 'asc');
      }
      if (newPagination.pageIndex > 0) {
        params.set('page', String(newPagination.pageIndex + 1));
      }
      const query = params.toString();
      router.replace(`${pathname}${query ? `?${query}` : ''}`, { scroll: false });
    },
    [pathname, router]
  );

  const handleFilterChange = useCallback(
    (key: keyof StockFilterState, value: string) => {
      const newFilters = { ...filters, [key]: value };
      setFilters(newFilters);
      const newPagination = { ...pagination, pageIndex: 0 };
      setPagination(newPagination);
      updateUrl(newFilters, sorting, newPagination);
    },
    [filters, pagination, sorting, updateUrl]
  );

  const handleClearFilters = useCallback(() => {
    setFilters(defaultFilters);
    const newPagination = { ...pagination, pageIndex: 0 };
    setPagination(newPagination);
    updateUrl(defaultFilters, sorting, newPagination);
  }, [pagination, sorting, updateUrl]);

  const handleSortingChange = useCallback(
    (newSorting: SortingState) => {
      setSorting(newSorting);
      updateUrl(filters, newSorting, pagination);
    },
    [filters, pagination, updateUrl]
  );

  const handlePaginationChange = useCallback(
    (newPagination: PaginationState) => {
      setPagination(newPagination);
      updateUrl(filters, sorting, newPagination);
    },
    [filters, sorting, updateUrl]
  );

  const stockLevels = data?.data ?? [];
  const totalCount = data?.pagination.totalCount ?? 0;

  return (
    <div className="space-y-6">
      <StockOverviewHeader />

      <StockSummaryCards data={stockLevels} isLoading={isLoading} />

      <StockFilters
        filters={filters}
        onFilterChange={handleFilterChange}
        onClearFilters={handleClearFilters}
      />

      <StockTable
        data={stockLevels}
        isLoading={isLoading}
        sorting={sorting}
        onSortingChange={handleSortingChange}
        pagination={pagination}
        onPaginationChange={handlePaginationChange}
        pageCount={Math.ceil(totalCount / pagination.pageSize) || 1}
      />
    </div>
  );
}
