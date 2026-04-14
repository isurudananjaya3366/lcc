'use client';

import { useState, useCallback } from 'react';
import { useSearchParams, useRouter, usePathname } from 'next/navigation';
import { type PaginationState, type SortingState } from '@tanstack/react-table';
import { useStockMovements, type MovementFilters } from '@/hooks/queries/useStockMovements';

import { MovementsHeader } from './MovementsHeader';
import { MovementsFilters } from './MovementsFilters';
import { ViewToggle } from './ViewToggle';
import { MovementsTimeline } from './MovementsTimeline';
import { MovementsTable } from './MovementsTable';

export function MovementsPage() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const [view, setView] = useState<'timeline' | 'table'>(() => {
    if (typeof window !== 'undefined') {
      return (localStorage.getItem('movements_view') as 'timeline' | 'table') ?? 'timeline';
    }
    return 'timeline';
  });

  const [filters, setFilters] = useState<MovementFilters>({
    productId: searchParams.get('product') ?? undefined,
    warehouseId: searchParams.get('warehouse') ?? undefined,
    movementType: (searchParams.get('type') as MovementFilters['movementType']) ?? 'all',
    startDate: searchParams.get('startDate') ?? undefined,
    endDate: searchParams.get('endDate') ?? undefined,
  });

  const [sorting, setSorting] = useState<SortingState>([{ id: 'createdAt', desc: true }]);

  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 10,
  });

  const { data, isLoading } = useStockMovements(filters);

  const movements = data?.results ?? [];
  const totalCount = data?.count ?? 0;

  const handleViewChange = useCallback((newView: 'timeline' | 'table') => {
    setView(newView);
    if (typeof window !== 'undefined') {
      localStorage.setItem('movements_view', newView);
    }
  }, []);

  const handleFilterChange = useCallback(
    (newFilters: MovementFilters) => {
      setFilters(newFilters);
      setPagination((prev) => ({ ...prev, pageIndex: 0 }));
      const params = new URLSearchParams();
      if (newFilters.productId) params.set('product', newFilters.productId);
      if (newFilters.warehouseId) params.set('warehouse', newFilters.warehouseId);
      if (newFilters.movementType && newFilters.movementType !== 'all')
        params.set('type', newFilters.movementType);
      if (newFilters.startDate) params.set('startDate', newFilters.startDate);
      if (newFilters.endDate) params.set('endDate', newFilters.endDate);
      const query = params.toString();
      router.replace(`${pathname}${query ? `?${query}` : ''}`, { scroll: false });
    },
    [pathname, router]
  );

  const handleExport = useCallback(() => {
    const csv = [
      'Date,Product,Type,Quantity,Reference,User',
      ...movements.map((m) =>
        [
          m.createdAt,
          m.productId,
          m.movementType,
          m.quantity,
          m.referenceId ?? '',
          m.createdBy,
        ].join(',')
      ),
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `stock_movements_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  }, [movements]);

  return (
    <div className="space-y-6">
      <MovementsHeader count={totalCount} onExport={handleExport} />

      <MovementsFilters filters={filters} onFilterChange={handleFilterChange} />

      <ViewToggle view={view} onViewChange={handleViewChange} />

      {view === 'timeline' ? (
        <MovementsTimeline movements={movements} isLoading={isLoading} />
      ) : (
        <MovementsTable
          data={movements}
          isLoading={isLoading}
          sorting={sorting}
          onSortingChange={setSorting}
          pagination={pagination}
          onPaginationChange={setPagination}
          pageCount={Math.ceil(totalCount / pagination.pageSize) || 1}
        />
      )}
    </div>
  );
}
