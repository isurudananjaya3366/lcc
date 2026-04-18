'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { OrderItemRow } from './OrderItemRow';
import type { PortalOrderItem } from '@/types/storefront/portal.types';

interface OrderItemsSectionProps {
  items: PortalOrderItem[];
}

export function OrderItemsSection({ items }: OrderItemsSectionProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Order Items ({items.length})</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="divide-y">
          {items.map((item) => (
            <OrderItemRow key={item.id} item={item} />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
