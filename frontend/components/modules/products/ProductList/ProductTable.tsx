'use client';

import { useMemo } from 'react';
import {
  type SortingState,
  type RowSelectionState,
  type PaginationState,
} from '@tanstack/react-table';
import { DataTable } from '@/components/ui/data-table';
import type { Product } from '@/types/product';
import { getProductColumns } from './ProductTableColumns';

interface ProductTableProps {
  data: Product[];
  isLoading?: boolean;
  sorting?: SortingState;
  onSortingChange?: (sorting: SortingState) => void;
  rowSelection?: RowSelectionState;
  onRowSelectionChange?: (selection: RowSelectionState) => void;
  pagination?: PaginationState;
  onPaginationChange?: (pagination: PaginationState) => void;
  pageCount?: number;
  onDelete?: (productId: string) => void;
}

export function ProductTable({
  data,
  sorting,
  onSortingChange,
  rowSelection,
  onRowSelectionChange,
  pagination,
  onPaginationChange,
  pageCount,
  onDelete,
}: ProductTableProps) {
  const columns = useMemo(() => getProductColumns({ onDelete }), [onDelete]);

  return (
    <DataTable
      columns={columns}
      data={data}
      sorting={sorting}
      onSortingChange={onSortingChange}
      rowSelection={rowSelection}
      onRowSelectionChange={onRowSelectionChange}
      pagination={pagination}
      onPaginationChange={onPaginationChange}
      pageCount={pageCount}
      manualPagination={!!onPaginationChange}
      manualSorting={!!onSortingChange}
      showPagination
      emptyMessage="No products found."
    />
  );
}
