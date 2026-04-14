'use client';

import { useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { type SortingState, type PaginationState } from '@tanstack/react-table';
import { useQuery } from '@tanstack/react-query';
import { inventoryKeys } from '@/lib/queryKeys';
import { inventoryService } from '@/services/api';

import { TransfersHeader } from './TransfersHeader';
import { TransfersTable } from './TransfersTable';

export function TransfersList() {
  const searchParams = useSearchParams();

  const [sorting, setSorting] = useState<SortingState>([{ id: 'requestDate', desc: true }]);

  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 10,
  });

  const sourceFilter = searchParams.get('source') ?? undefined;
  const destFilter = searchParams.get('destination') ?? undefined;
  const statusFilter = searchParams.get('status') ?? undefined;

  const { data, isLoading } = useQuery({
    queryKey: [...inventoryKeys.all(), 'transfers', { sourceFilter, destFilter, statusFilter }],
    queryFn: () =>
      inventoryService.getStockTransfers({
        sourceWarehouseId: sourceFilter,
        destinationWarehouseId: destFilter,
        status: statusFilter as 'PENDING' | 'COMPLETED' | 'CANCELLED' | undefined,
      }),
    staleTime: 2 * 60 * 1000,
  });

  const transfers = data?.results ?? [];
  const totalCount = data?.count ?? 0;

  return (
    <div className="space-y-6">
      <TransfersHeader count={totalCount} transfers={transfers} />

      <TransfersTable
        data={transfers}
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
