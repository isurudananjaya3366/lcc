'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Edit, Printer, MoreVertical } from 'lucide-react';
import { OrderStatusBadge } from '../cells/OrderStatusBadge';
import { OrderActionsDropdown } from './OrderActionsDropdown';
import type { Order } from '@/types/sales';

interface OrderDetailsHeaderProps {
  order: Order;
  onEdit?: () => void;
  onPrint?: () => void;
  onCancel?: () => void;
  isLoading?: boolean;
}

const nonEditableStatuses = ['SHIPPED', 'DELIVERED', 'COMPLETED', 'CANCELLED', 'REFUNDED'];

export function OrderDetailsHeader({
  order,
  onEdit,
  onPrint,
  onCancel,
  isLoading,
}: OrderDetailsHeaderProps) {
  const canEdit = !nonEditableStatuses.includes(order.orderStatus);

  return (
    <div className="sticky top-0 z-10 flex flex-col gap-3 border-b bg-white pb-4 dark:bg-gray-950 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Order #{order.orderNumber}
          </h1>
          <OrderStatusBadge status={order.orderStatus} />
        </div>
        <div className="mt-1 flex items-center gap-2 text-sm text-gray-500">
          {order.customerName && <span>{order.customerName}</span>}
          <span>·</span>
          <span>
            {new Date(order.createdAt).toLocaleDateString('en-LK', {
              year: 'numeric',
              month: 'short',
              day: 'numeric',
            })}
          </span>
          {order.updatedAt !== order.createdAt && (
            <>
              <span>·</span>
              <span>
                Updated{' '}
                {new Date(order.updatedAt).toLocaleDateString('en-LK', {
                  year: 'numeric',
                  month: 'short',
                  day: 'numeric',
                })}
              </span>
            </>
          )}
        </div>
      </div>
      <div className="flex items-center gap-2">
        {canEdit && (
          <Button size="sm" onClick={onEdit} disabled={isLoading}>
            <Edit className="mr-2 h-4 w-4" />
            Edit
          </Button>
        )}
        <Button variant="outline" size="sm" onClick={onPrint} disabled={isLoading}>
          <Printer className="mr-2 h-4 w-4" />
          Print
        </Button>
        <OrderActionsDropdown order={order} callbacks={{ onEdit, onPrint, onCancel }} />
      </div>
    </div>
  );
}
