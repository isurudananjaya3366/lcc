'use client';

import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { MoreVertical, Eye, Edit, Copy, Printer, Trash2 } from 'lucide-react';
import type { Order, OrderStatus } from '@/types/sales';

interface OrderActionsCellProps {
  order: Order;
  onDuplicate?: (order: Order) => void;
  onDelete?: (order: Order) => void;
}

const nonEditableStatuses: OrderStatus[] = [
  'SHIPPED',
  'DELIVERED',
  'COMPLETED',
  'CANCELLED',
  'REFUNDED',
];

export function OrderActionsCell({ order, onDuplicate, onDelete }: OrderActionsCellProps) {
  const router = useRouter();
  const canEdit = !nonEditableStatuses.includes(order.orderStatus);

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" className="h-8 w-8 p-0">
          <span className="sr-only">Open menu</span>
          <MoreVertical className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => router.push(`/orders/${order.id}`)}>
          <Eye className="mr-2 h-4 w-4" />
          View Details
        </DropdownMenuItem>

        <DropdownMenuItem
          onClick={() => router.push(`/orders/${order.id}?edit=true`)}
          disabled={!canEdit}
        >
          <Edit className="mr-2 h-4 w-4" />
          Edit Order
        </DropdownMenuItem>

        {onDuplicate && (
          <DropdownMenuItem onClick={() => onDuplicate(order)}>
            <Copy className="mr-2 h-4 w-4" />
            Duplicate
          </DropdownMenuItem>
        )}

        <DropdownMenuItem onClick={() => window.print()}>
          <Printer className="mr-2 h-4 w-4" />
          Print
        </DropdownMenuItem>

        {onDelete && (
          <>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={() => onDelete(order)}
              className="text-red-600 focus:text-red-600"
            >
              <Trash2 className="mr-2 h-4 w-4" />
              Delete
            </DropdownMenuItem>
          </>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

export type { OrderActionsCellProps };
