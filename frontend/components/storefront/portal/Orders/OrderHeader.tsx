'use client';

import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { OrderStatusBadge } from './OrderStatusBadge';
import type { PortalOrder } from '@/types/storefront/portal.types';

interface OrderHeaderProps {
  order: PortalOrder;
}

export function OrderHeader({ order }: OrderHeaderProps) {
  const formattedDate = new Date(order.createdAt).toLocaleDateString('en-LK', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex flex-col gap-2">
        <Link href="/account/orders">
          <Button variant="ghost" size="sm" className="w-fit gap-1.5 px-2">
            <ArrowLeft className="h-4 w-4" />
            Back to Orders
          </Button>
        </Link>
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold">Order #{order.orderNumber}</h1>
          <OrderStatusBadge status={order.status} />
        </div>
        <p className="text-sm text-muted-foreground">Placed on {formattedDate}</p>
      </div>
    </div>
  );
}
