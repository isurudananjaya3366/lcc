'use client';

import { useState, useCallback, useMemo } from 'react';
import { useSearchParams, useRouter, usePathname } from 'next/navigation';
import {
  type SortingState,
  type RowSelectionState,
  type PaginationState,
} from '@tanstack/react-table';
import { useDebounce } from '@/hooks/useDebounce';
import type { Product, ProductCategory } from '@/types/product';

import { ProductListHeader } from './ProductListHeader';
import { ProductFilters, type FilterState } from './ProductFilters';
import { SearchInput } from './SearchInput';
import { StatusFilter } from './StatusFilter';
import { CategoryFilter } from './CategoryFilter';
import { StockFilter } from './StockFilter';
import { ProductTable } from './ProductTable';
import { BulkActionsBar } from './BulkActionsBar';

interface ProductListProps {
  initialProducts?: Product[];
  categories?: ProductCategory[];
  isLoading?: boolean;
}

const defaultFilters: FilterState = {
  search: '',
  status: 'all',
  category: '',
  stock: 'all',
};

export function ProductList({
  initialProducts = [],
  categories = [],
  isLoading = false,
}: ProductListProps) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  // Initialize filters from URL
  const [filters, setFilters] = useState<FilterState>({
    search: searchParams.get('search') ?? '',
    status: searchParams.get('status') ?? 'all',
    category: searchParams.get('category') ?? '',
    stock: searchParams.get('stock') ?? 'all',
  });

  const debouncedSearch = useDebounce(filters.search, 300);

  const [sorting, setSorting] = useState<SortingState>(() => {
    const sort = searchParams.get('sort');
    const order = searchParams.get('order');
    if (sort) {
      return [{ id: sort, desc: order === 'desc' }];
    }
    return [];
  });

  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: Number(searchParams.get('page') ?? 1) - 1,
    pageSize: Number(searchParams.get('pageSize') ?? 10),
  });

  const [rowSelection, setRowSelection] = useState<RowSelectionState>({});

  // Update URL when filters change
  const updateUrl = useCallback(
    (newFilters: FilterState, newSorting: SortingState, newPagination: PaginationState) => {
      const params = new URLSearchParams();
      if (newFilters.search) params.set('search', newFilters.search);
      if (newFilters.status !== 'all') params.set('status', newFilters.status);
      if (newFilters.category) params.set('category', newFilters.category);
      if (newFilters.stock !== 'all') params.set('stock', newFilters.stock);
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
    (key: keyof FilterState, value: string) => {
      const newFilters = { ...filters, [key]: value };
      setFilters(newFilters);
      // Reset pagination when filter changes
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

  const handleClearSelection = useCallback(() => {
    setRowSelection({});
  }, []);

  const handleBulkDelete = useCallback(() => {
    // TODO: Implement bulk delete via API
    const selectedIds = Object.keys(rowSelection);
    console.log('Bulk delete:', selectedIds);
  }, [rowSelection]);

  const handleBulkActivate = useCallback(() => {
    // TODO: Implement bulk activate via API
    const selectedIds = Object.keys(rowSelection);
    console.log('Bulk activate:', selectedIds);
  }, [rowSelection]);

  const handleBulkDeactivate = useCallback(() => {
    // TODO: Implement bulk deactivate via API
    const selectedIds = Object.keys(rowSelection);
    console.log('Bulk deactivate:', selectedIds);
  }, [rowSelection]);

  const handleDelete = useCallback((productId: string) => {
    // TODO: Implement single product delete via API
    console.log('Delete product:', productId);
  }, []);

  const selectedCount = Object.keys(rowSelection).length;

  // TODO: Replace with useProducts hook connected to API
  // using debouncedSearch, filters, sorting, pagination
  const products = initialProducts;

  return (
    <div className="space-y-6">
      <ProductListHeader />

      <ProductFilters
        filters={filters}
        onFilterChange={handleFilterChange}
        onClearFilters={handleClearFilters}
      >
        <SearchInput
          value={filters.search}
          onChange={(value) => handleFilterChange('search', value)}
        />
        <StatusFilter
          value={filters.status}
          onChange={(value) => handleFilterChange('status', value)}
        />
        <CategoryFilter
          value={filters.category}
          onChange={(value) => handleFilterChange('category', value)}
          categories={categories}
        />
        <StockFilter
          value={filters.stock}
          onChange={(value) => handleFilterChange('stock', value)}
        />
      </ProductFilters>

      <BulkActionsBar
        selectedCount={selectedCount}
        onBulkDelete={handleBulkDelete}
        onBulkActivate={handleBulkActivate}
        onBulkDeactivate={handleBulkDeactivate}
        onClearSelection={handleClearSelection}
      />

      <ProductTable
        data={products}
        isLoading={isLoading}
        sorting={sorting}
        onSortingChange={handleSortingChange}
        rowSelection={rowSelection}
        onRowSelectionChange={setRowSelection}
        pagination={pagination}
        onPaginationChange={handlePaginationChange}
        pageCount={Math.ceil(products.length / pagination.pageSize) || 1}
        onDelete={handleDelete}
      />
    </div>
  );
}
