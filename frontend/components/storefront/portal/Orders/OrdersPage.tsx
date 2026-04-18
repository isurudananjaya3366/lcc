'use client';

import { useState, useEffect, useCallback } from 'react';
import { Skeleton } from '@/components/ui/skeleton';
import { getOrders } from '@/services/storefront/portalService';
import type { PortalOrder, OrderStatus } from '@/types/storefront/portal.types';
import { OrdersList } from './OrdersList';
import { OrdersFilter } from './OrdersFilter';
import { OrdersPagination } from './OrdersPagination';
import { OrdersHeader } from './OrdersHeader';

const PAGE_SIZE = 10;

export function OrdersPage() {
  const [orders, setOrders] = useState<PortalOrder[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState('all');
  const [loading, setLoading] = useState(true);

  const fetchOrders = useCallback(async () => {
    setLoading(true);
    try {
      const status = statusFilter === 'all' ? undefined : (statusFilter as OrderStatus);
      const res = await getOrders({ status, page, pageSize: PAGE_SIZE });
      setOrders(res.orders);
      setTotal(res.total);
    } finally {
      setLoading(false);
    }
  }, [statusFilter, page]);

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  const totalPages = Math.ceil(total / PAGE_SIZE);

  const handleFilterChange = (value: string) => {
    setStatusFilter(value);
    setPage(1);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <OrdersHeader total={total} />
        <OrdersFilter value={statusFilter} onChange={handleFilterChange} />
      </div>

      {loading ? (
        <div className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-24 w-full rounded-lg" />
          ))}
        </div>
      ) : (
        <>
          <OrdersList orders={orders} />
          <OrdersPagination
            page={page}
            totalPages={totalPages}
            onPageChange={setPage}
          />
        </>
      )}
    </div>
  );
}
