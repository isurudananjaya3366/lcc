'use client';

import { useSearchParams } from 'next/navigation';
import { useOrders } from '@/hooks/queries/useOrders';
import { OrdersHeader } from './OrdersHeader';
import { OrderSummaryCards } from './OrderSummaryCards';
import { OrderFilters } from './OrderFilters';
import { OrdersTable } from './OrdersTable';
import { useState } from 'react';

export function OrdersList() {
  const searchParams = useSearchParams();
  const statusFilter = searchParams.get('status') ?? undefined;
  const [search, setSearch] = useState('');

  const { data, isLoading } = useOrders({
    status: statusFilter,
    query: search || undefined,
  } as never);

  const orders = data?.data ?? [];

  return (
    <div className="space-y-6">
      <OrderSummaryCards orders={orders} isLoading={isLoading} />
      <OrderFilters search={search} onSearchChange={setSearch} />
      <OrdersTable orders={orders} isLoading={isLoading} />
    </div>
  );
}
