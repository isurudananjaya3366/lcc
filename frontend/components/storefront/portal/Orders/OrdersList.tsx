'use client';

import type { PortalOrder } from '@/types/storefront/portal.types';
import { OrderCard } from './OrderCard';
import { EmptyOrdersState } from './EmptyOrdersState';

interface OrdersListProps {
  orders: PortalOrder[];
}

export function OrdersList({ orders }: OrdersListProps) {
  if (orders.length === 0) {
    return <EmptyOrdersState />;
  }

  return (
    <div className="space-y-4">
      {orders.map((order) => (
        <OrderCard key={order.id} order={order} />
      ))}
    </div>
  );
}
