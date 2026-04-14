'use client';

import { useMemo } from 'react';
import { type SortingState, type PaginationState } from '@tanstack/react-table';
import { DataTable } from '@/components/ui/data-table';
import type { StockTransfer } from '@/types/inventory';
import { getTransferColumns } from './TransferTableColumns';

interface TransfersTableProps {
  data: StockTransfer[];
  isLoading?: boolean;
  sorting?: SortingState;
  onSortingChange?: (sorting: SortingState) => void;
  pagination?: PaginationState;
  onPaginationChange?: (pagination: PaginationState) => void;
  pageCount?: number;
}

export function TransfersTable({
  data,
  sorting,
  onSortingChange,
  pagination,
  onPaginationChange,
  pageCount,
}: TransfersTableProps) {
  const columns = useMemo(() => getTransferColumns(), []);

  return (
    <DataTable
      columns={columns}
      data={data}
      sorting={sorting}
      onSortingChange={onSortingChange}
      pagination={pagination}
      onPaginationChange={onPaginationChange}
      pageCount={pageCount}
      manualPagination={!!onPaginationChange}
      manualSorting={!!onSortingChange}
      showPagination
      emptyMessage="No transfers found."
    />
  );
}
