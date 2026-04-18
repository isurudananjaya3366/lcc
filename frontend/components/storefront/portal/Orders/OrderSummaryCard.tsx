'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import type { PortalOrder } from '@/types/storefront/portal.types';

interface OrderSummaryCardProps {
  order: PortalOrder;
}

const formatLKR = (amount: number) =>
  `₨ ${amount.toLocaleString('en-LK', { minimumFractionDigits: 2 })}`;

export function OrderSummaryCard({ order }: OrderSummaryCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Order Summary</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-muted-foreground">Subtotal</span>
          <span>{formatLKR(order.subtotal)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">Shipping</span>
          <span>{formatLKR(order.shipping)}</span>
        </div>
        {order.tax > 0 && (
          <div className="flex justify-between">
            <span className="text-muted-foreground">Tax</span>
            <span>{formatLKR(order.tax)}</span>
          </div>
        )}
        {order.discount > 0 && (
          <div className="flex justify-between">
            <span className="text-muted-foreground">Discount</span>
            <span className="text-green-600">-{formatLKR(order.discount)}</span>
          </div>
        )}
        <Separator />
        <div className="flex justify-between font-bold">
          <span>Total</span>
          <span>{formatLKR(order.total)}</span>
        </div>
      </CardContent>
    </Card>
  );
}
