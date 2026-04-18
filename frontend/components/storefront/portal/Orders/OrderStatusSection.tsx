'use client';

import type { PortalOrder } from '@/types/storefront/portal.types';
import { OrderStatusBadge } from './OrderStatusBadge';

interface OrderStatusSectionProps {
  order: PortalOrder;
}

export function OrderStatusSection({ order }: OrderStatusSectionProps) {
  return (
    <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between rounded-lg border bg-muted/40 px-4 py-3">
      <div>
        <p className="text-sm text-muted-foreground">Order Status</p>
        <div className="mt-1">
          <OrderStatusBadge status={order.status} />
        </div>
      </div>
      {order.estimatedDelivery && (
        <div className="text-sm text-muted-foreground sm:text-right">
          <p>Estimated Delivery</p>
          <p className="font-medium text-foreground">
            {new Date(order.estimatedDelivery).toLocaleDateString('en-LK', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })}
          </p>
        </div>
      )}
    </div>
  );
}
