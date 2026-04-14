'use client';

import { useMemo } from 'react';
import { type SortingState, type PaginationState } from '@tanstack/react-table';
import { DataTable } from '@/components/ui/data-table';
import type { StockMovement } from '@/types/inventory';
import { getMovementColumns } from './MovementTableColumns';

interface MovementsTableProps {
  data: StockMovement[];
  isLoading?: boolean;
  sorting?: SortingState;
  onSortingChange?: (sorting: SortingState) => void;
  pagination?: PaginationState;
  onPaginationChange?: (pagination: PaginationState) => void;
  pageCount?: number;
}

export function MovementsTable({
  data,
  sorting,
  onSortingChange,
  pagination,
  onPaginationChange,
  pageCount,
}: MovementsTableProps) {
  const columns = useMemo(() => getMovementColumns(), []);

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
      emptyMessage="No movements found."
    />
  );
}
