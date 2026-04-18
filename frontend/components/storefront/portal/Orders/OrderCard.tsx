'use client';

import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { OrderStatusBadge } from './OrderStatusBadge';
import type { PortalOrder } from '@/types/storefront/portal.types';

interface OrderCardProps {
  order: PortalOrder;
}

const formatLKR = (amount: number) =>
  `₨ ${amount.toLocaleString('en-LK', { minimumFractionDigits: 2 })}`;

export function OrderCard({ order }: OrderCardProps) {
  const itemCount = order.items.reduce((sum, item) => sum + item.quantity, 0);

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <p className="font-semibold">{order.orderNumber}</p>
              <OrderStatusBadge status={order.status} />
            </div>
            <p className="text-sm text-muted-foreground">
              {new Intl.DateTimeFormat('en-LK', { dateStyle: 'medium' }).format(
                new Date(order.createdAt)
              )}
            </p>
            <p className="text-sm text-muted-foreground">
              {itemCount} {itemCount === 1 ? 'item' : 'items'}
            </p>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-lg font-bold">{formatLKR(order.total)}</span>
            <Button variant="outline" size="sm" asChild>
              <Link href={`/account/orders/${order.id}`}>View Details</Link>
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
