'use client';

import { useState, useCallback } from 'react';
import { useSearchParams } from 'next/navigation';
import { type SortingState, type PaginationState } from '@tanstack/react-table';
import { useQuery } from '@tanstack/react-query';
import { inventoryKeys } from '@/lib/queryKeys';
import { inventoryService } from '@/services/api';

import { AdjustmentsHeader } from './AdjustmentsHeader';
import { AdjustmentsTable } from './AdjustmentsTable';

export function AdjustmentsList() {
  const searchParams = useSearchParams();

  const [sorting, setSorting] = useState<SortingState>([
    { id: 'adjustedAt', desc: true },
  ]);

  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 10,
  });

  const warehouseFilter = searchParams.get('warehouse') ?? undefined;
  const startDate = searchParams.get('startDate') ?? undefined;
  const endDate = searchParams.get('endDate') ?? undefined;

  const { data, isLoading } = useQuery({
    queryKey: [...inventoryKeys.all(), 'adjustments', { warehouseFilter, startDate, endDate }],
    queryFn: () =>
      inventoryService.getStockAdjustments({
        warehouseId: warehouseFilter,
        startDate,
        endDate,
      }),
    staleTime: 2 * 60 * 1000,
  });

  const adjustments = data?.results ?? [];
  const totalCount = data?.count ?? 0;

  return (
    <div className="space-y-6">
      <AdjustmentsHeader count={totalCount} />

      <AdjustmentsTable
        data={adjustments}
        isLoading={isLoading}
        sorting={sorting}
        onSortingChange={setSorting}
        pagination={pagination}
        onPaginationChange={setPagination}
        pageCount={Math.ceil(totalCount / pagination.pageSize) || 1}
      />
    </div>
  );
}
