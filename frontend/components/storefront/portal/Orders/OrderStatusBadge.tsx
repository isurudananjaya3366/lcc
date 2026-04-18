'use client';

import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/cn';
import type { OrderStatus } from '@/types/storefront/portal.types';

interface OrderStatusBadgeProps {
  status: OrderStatus;
}

const statusConfig: Record<OrderStatus, { label: string; className: string }> = {
  pending: { label: 'Pending', className: 'bg-yellow-100 text-yellow-800' },
  confirmed: { label: 'Confirmed', className: 'bg-blue-100 text-blue-800' },
  processing: { label: 'Processing', className: 'bg-indigo-100 text-indigo-800' },
  shipped: { label: 'Shipped', className: 'bg-purple-100 text-purple-800' },
  out_for_delivery: { label: 'Out for Delivery', className: 'bg-orange-100 text-orange-800' },
  delivered: { label: 'Delivered', className: 'bg-green-100 text-green-800' },
  cancelled: { label: 'Cancelled', className: 'bg-red-100 text-red-800' },
  returned: { label: 'Returned', className: 'bg-gray-100 text-gray-800' },
};

export function OrderStatusBadge({ status }: OrderStatusBadgeProps) {
  const config = statusConfig[status] ?? { label: status, className: '' };

  return (
    <Badge variant="secondary" className={cn(config.className)}>
      {config.label}
    </Badge>
  );
}
